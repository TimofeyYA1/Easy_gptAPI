import random
import string
from typing import Dict, List, Optional
import schemas
from db_adapter import SupabaseAdapter
import auth
import os
db = SupabaseAdapter()

def get_user(user_id: int) -> Optional[Dict]:
    """Получение пользователя по ID."""
    return db.get_by_id("users", user_id)

def get_user_by_username(username: str) -> Optional[Dict]:
    """Получение пользователя по имени пользователя."""
    return db.get_single_by_value("users", "username", username)

def create_user(user: schemas.UserCreate) -> Dict:
    """Создание нового пользователя."""
    hashed_password = auth.get_password_hash(user.password)
    user_data = {
        "username": user.username,
        "password": hashed_password
    }
    result = db.insert("users", user_data)
    if result is None:
        raise Exception("Не удалось создать пользователя в базе данных")
    return result

def get_token(token_id: int) -> Optional[Dict]:
    """Получение токена по ID."""
    return db.get_by_id("tokens", token_id)

def get_token_by_value(token_value: str) -> Optional[Dict]:
    """Получение токена по значению токена."""
    return db.get_single_by_value("tokens", "token", token_value)

def get_tokens_by_user_id(user_id: int) -> List[Dict]:
    """Получение всех токенов пользователя."""
    return db.get_by_value("tokens", "user_id", user_id)

def generate_token(length: int = 32) -> str:
    """Генерация уникального токена."""
    characters = string.ascii_letters + string.digits
    token = ''.join(random.choice(characters) for i in range(length))
    
    while get_token_by_value(token):
        token = ''.join(random.choice(characters) for i in range(length))
    
    return token

def create_token( token: schemas.TokenCreate, user_id: int):
    new_token_value = f"tok_{os.urandom(8).hex()}"
    insert_data = {
        "user_id": user_id,
        "name": token.name,
        "token": new_token_value
    }

    result = db.insert("tokens", insert_data)
    return result if result else {}
def update_token_balance(token_id: int, balance: str) -> Optional[Dict]:
    """Обновление баланса токена."""
    token_data = {"balance": balance}
    return db.update("tokens", token_data, token_id)

def delete_token(token_id: int) -> None:
    """Удаление токена."""
    db.delete("tokens", token_id)

def get_payment(payment_id: int) -> Optional[Dict]:
    """Получение платежа по ID."""
    return db.get_by_id("payments", payment_id)

def get_payments_by_user_id(user_id: int) -> List[Dict]:
    """Получение всех платежей пользователя."""
    return db.get_by_value("payments", "user_id", user_id)

def get_payments_by_token_id(token_id: int) -> List[Dict]:
    """Получение всех платежей для токена."""
    return db.get_by_value("payments", "token_id", token_id)

def create_payment(payment: schemas.PaymentCreate, user_id: int) -> Dict:
    """Создание нового платежа."""
    payment_data = {
        "user_id": user_id,
        "token_id": payment.token_id,
        "amount": payment.amount,
        "status": "pending"
    }
    
    result = db.insert("payments", payment_data)
    if result is None:
        raise Exception("Не удалось создать платеж в базе данных")
    return result

def update_payment_status(payment_id: int, status: str) -> Optional[Dict]:
    """Обновление статуса платежа."""
    payment_data = {"status": status}
    return db.update("payments", payment_data, payment_id)

def rename_token(token_id: int, new_name: str) -> dict:
    return db.update_by_value("tokens", {"name": new_name}, "id", token_id)