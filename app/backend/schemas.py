from pydantic import BaseModel
from typing import Optional
from datetime import datetime

# Модели для пользователей
class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str

class User(UserBase):
    id: int
    created_at: datetime

    class Config:
        orm_mode = True

# Модели для токенов
class TokenBase(BaseModel):
    name: str

class TokenCreate(TokenBase):
    pass  # теперь только имя

class TokenUpdate(BaseModel):
    balance: str


class RenameTokenRequest(BaseModel):
    new_name: str  # новое имя
    

class Token(TokenBase):
    id: int
    token: str
    balance: str
    active: bool

    class Config:
        orm_mode = True

# Модели для платежей
class PaymentBase(BaseModel):
    token_id: int
    amount: str

class PaymentCreate(PaymentBase):
    pass

class PaymentUpdate(BaseModel):
    status: str

class Payment(PaymentBase):
    id: int
    user_id: int
    status: str
    created_at: datetime

    class Config:
        orm_mode = True

# Модели для JWT аутентификации
class TokenData(BaseModel):
    sub: Optional[str] = None

class JWTToken(BaseModel):
    access_token: str
    token_type: str