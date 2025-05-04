import asyncio
import os
import sys
import pathlib
import hashlib
import httpx

sys.path.append(str(pathlib.Path(__file__).resolve().parent.parent))

from aiogram import Bot, Dispatcher, F
from aiogram.types import (
    Message, CallbackQuery,
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from dotenv import load_dotenv
from adapters.db_source import DatabaseAdapter

# Загрузка .env переменных
load_dotenv()
bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
admin_id = os.getenv("ADMIN_ID")
freekassa_merchant_id = os.getenv("FREEKASSA_MERCHANT_ID")
freekassa_secret_word = os.getenv("FREEKASSA_SECRET_WORD")
freekassa_secret_word2 = os.getenv("FREEKASSA_SECRET_WORD2")

bot = Bot(token=bot_token)
dp = Dispatcher(storage=MemoryStorage())
db = DatabaseAdapter()
db.connect()
db.initialize_tables()

# FSM состояния
class TokenRecharge(StatesGroup):
    waiting_for_amount_choice = State()
    waiting_for_token = State()

# Главное меню
main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Создать токен")],
        [KeyboardButton(text="Мои токены")],
        [KeyboardButton(text="Пополнить токен")],
        [KeyboardButton(text="Удалить токен")]
    ],
    resize_keyboard=True
)

# Генерация клавиатуры токенов
def generate_token_keyboard(tokens: list[dict], action: str) -> InlineKeyboardMarkup:
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=f"{t['token']} ({t['balance']}₽)",
            callback_data=f"{action}:{t['token']}"
        )]
        for t in tokens
    ])
    return keyboard

# Генерация ссылки оплаты через Freekassa
def generate_freekassa_payment_link(token: str, amount: float) -> str:
    amount_str = str(amount)
    sign_string = f"{freekassa_merchant_id}:{amount_str}:{freekassa_secret_word}:{token}"
    sign = hashlib.md5(sign_string.encode()).hexdigest()

    link = f"https://pay.freekassa.ru/?m={freekassa_merchant_id}&oa={amount_str}&o={token}&s={sign}"
    return link

# Проверка оплаты через Freekassa API
async def check_freekassa_payment(token: str) -> bool:
    sign_str = f"{freekassa_merchant_id}:{freekassa_secret_word2}:{token}"
    sign = hashlib.md5(sign_str.encode()).hexdigest()

    url = "https://www.free-kassa.ru/api.php"
    params = {
        "m": "check_order_status",
        "merchant_id": freekassa_merchant_id,
        "order_id": token,
        "s": sign
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        text = response.text.strip()

    return text == "paid"

# /start
@dp.message(F.text == "/start")
async def start_handler(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username or "Без ника"

    user = db.get_by_id("users", user_id)
    if user:
        await message.answer("✅ Вы уже зарегистрированы!", reply_markup=main_keyboard)
    else:
        db.insert("users", {"id": user_id, "username": username})
        await message.answer(
            "👋 Привет!\n\nЯ бот для подключения к OpenAI API.\n"
            "Создай свой токен и начни пользоваться!", reply_markup=main_keyboard
        )

# Создать токен
@dp.message(F.text == "Создать токен")
async def create_token_handler(message: Message):
    user_id = message.from_user.id
    new_token = f"tok_{os.urandom(8).hex()}"
    db.insert("tokens", {"user_id": user_id, "token": new_token, "balance": 10.0})
    await message.answer(f"✅ Токен создан:\n`{new_token}`\n💰 Баланс: 0.0", parse_mode="Markdown")

# Мои токены
@dp.message(F.text == "Мои токены")
async def list_tokens_handler(message: Message):
    user_id = message.from_user.id
    tokens = db.get_by_value("tokens", "user_id", user_id)

    if not tokens:
        await message.answer("😕 У тебя пока нет токенов.")
        return

    text = "🔐 Твои токены:\n\n"
    for t in tokens:
        text += f"🆔 `{t['token']}` — 💰 {t['balance']}₽\n"
    await message.answer(text, parse_mode="Markdown")

# Пополнение — выбор токена
@dp.message(F.text == "Пополнить токен")
async def start_recharge(message: Message, state: FSMContext):
    user_id = message.from_user.id
    tokens = db.get_by_value("tokens", "user_id", user_id)
    if not tokens:
        await message.answer("У тебя нет токенов для пополнения.")
        return
    keyboard = generate_token_keyboard(tokens, "recharge")
    await message.answer("🔑 Выбери токен для пополнения:", reply_markup=keyboard)

# Пополнение — выбран токен
@dp.callback_query(F.data.startswith("recharge:"))
async def choose_token_to_recharge(callback: CallbackQuery, state: FSMContext):
    token = callback.data.split("recharge:")[1]
    await state.update_data(token=token)

    amount_keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💵 100₽", callback_data="pay:100")],
        [InlineKeyboardButton(text="💵 500₽", callback_data="pay:500")],
        [InlineKeyboardButton(text="💵 1000₽", callback_data="pay:1000")],
        [InlineKeyboardButton(text="💵 5000₽", callback_data="pay:5000")],
    ])
    await callback.message.edit_text("💸 Выбери сумму пополнения:", reply_markup=amount_keyboard)
    await state.set_state(TokenRecharge.waiting_for_amount_choice)

# Пополнение — создание платежа Freekassa
@dp.callback_query(TokenRecharge.waiting_for_amount_choice, F.data.startswith("pay:"))
async def process_payment(callback: CallbackQuery, state: FSMContext):
    amount = int(callback.data.split("pay:")[1])
    data = await state.get_data()
    token = data["token"]

    payment_link = generate_freekassa_payment_link(token, amount)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="💳 Перейти к оплате", url=payment_link)],
        [InlineKeyboardButton(text="✅ Я оплатил", callback_data=f"check_payment:{amount}")]
    ])

    await state.update_data(payment_amount=amount)
    await callback.message.edit_text(
        f"🔗 Ссылка для оплаты: [Нажми сюда]({payment_link})\n\n"
        "После оплаты нажми кнопку ниже!",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )

# Проверка после оплаты и пополнение баланса
@dp.callback_query(F.data.startswith("check_payment:"))
async def confirm_payment(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    token = data.get("token")
    amount = int(callback.data.split("check_payment:")[1])

    if not token:
        await callback.message.edit_text("❗ Ошибка: токен не найден.")
        return

    await callback.message.edit_text("⏳ Проверяем оплату, подождите...")

    is_paid = await check_freekassa_payment(token)

    if is_paid:
        token_data = db.get_by_value("tokens", "token", token)
        old_balance = float(token_data[0]["balance"])
        new_balance = old_balance + amount
        db.update_by_value("tokens", {"balance": new_balance}, "token", token)

        await callback.message.edit_text(f"✅ Оплата подтверждена!\nБаланс пополнен на {amount}₽.\nНовый баланс: {new_balance}₽")
    else:
        await callback.message.edit_text("❌ Платёж не найден. Возможно, вы ещё не оплатили. Попробуйте позже.")

# Запуск бота
async def main():
    import logging
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
