from dotenv import load_dotenv
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import hashlib
import os

# Путь относительный от fastapi_server/, так как app.py внутри этой папки
from ai import router as ai_router
from adapters.db_source import DatabaseAdapter

# 🔄 Загрузка .env переменных
load_dotenv()

# 🔧 FastAPI конфигурация
app = FastAPI(
    docs_url="/api/docs",
    openapi_url="/api/openapi.json"
)

# 🧾 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешить все домены (можно ограничить позже)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 🔌 Подключаем AI роуты
app.include_router(ai_router, prefix="/ai", tags=["AI"])

# 🔍 Пинг для теста
@app.post("/ping")
async def negative_scenario():
    return {"status": "workkkkkk"}

# 💸 Callback от Freekassa
@app.post("/payment/freekassa_callback")
async def freekassa_callback(request: Request):
    form = await request.form()

    try:
        # Извлекаем поля из запроса
        amount = form.get('AMOUNT')
        order_id = form.get('MERCHANT_ORDER_ID')
        sign = form.get('SIGN')
        merchant_id = form.get('MERCHANT_ID')

        # Проверка наличия всех параметров
        if not all([amount, order_id, sign, merchant_id]):
            raise HTTPException(status_code=400, detail="Некорректные параметры")

        # Проверка подписи (секрет 1)
        secret_word = os.getenv("FREEKASSA_SECRET_WORD")
        sign_str = f"{merchant_id}:{amount}:{secret_word}:{order_id}"
        expected_sign = hashlib.md5(sign_str.encode()).hexdigest()

        if expected_sign != sign:
            raise HTTPException(status_code=400, detail="Неверная подпись")

        # Пополнение баланса токена (где order_id — это токен)
        db = DatabaseAdapter()
        db.connect()

        token = order_id
        token_data = db.get_by_value("tokens", "token", token)

        if not token_data:
            raise HTTPException(status_code=404, detail="Токен не найден")

        old_balance = float(token_data[0]["balance"])
        new_balance = old_balance + float(amount)

        db.update_by_value("tokens", {"balance": new_balance}, "token", token)

        print(f"✅ Freekassa пополнение: {token} +{amount}₽")

        return "YES"  # 🔥 ОЧЕНЬ важно — вернуть ровно "YES" без пробела

    except Exception as e:
        print(f"❌ Ошибка callback: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
@app.get("/payment/success")
async def payment_success():
    return {"status": "success", "message": "Оплата прошла успешно"}

@app.get("/payment/fail")
async def payment_fail():
    return {"status": "fail", "message": "Оплата не удалась"}

# 🚀 Запуск
if __name__ == "__main__":
    host, port = os.getenv("FAST_API_HOST"), os.getenv("FAST_API_PORT")
    uvicorn.run(app, host=host, port=int(port), http="httptools")
