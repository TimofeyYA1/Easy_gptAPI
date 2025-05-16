from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from typing import List, Dict, Optional
import uvicorn
import json
from datetime import datetime, timedelta
from fastapi import HTTPException
from psycopg2.errors import UniqueViolation
import schemas
import crud
import auth
from db_adapter import DatabaseAdapter
import psycopg2

app = FastAPI(title="EasyGPT API Portal")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


db_adapter = DatabaseAdapter()
db_adapter.connect()
db_adapter.initialize_tables()



@app.get("/api/user")
async def get_current_user(current_user: Dict = Depends(auth.get_current_user)):
    if isinstance(current_user.get("created_at"), datetime):
        current_user["created_at"] = current_user["created_at"].isoformat()
    return current_user

@app.post("/api/register")
async def register_user(user: schemas.UserCreate):
    db_user = crud.get_user_by_username(username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Пользователь с таким именем уже существует")
    
    new_user = crud.create_user(user=user)

    # Преобразуем datetime для JSON
    if isinstance(new_user.get("created_at"), datetime):
        new_user["created_at"] = new_user["created_at"].isoformat()
    
    # Генерация access_token
    access_token_expires = timedelta(minutes=auth.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth.create_access_token(
        data={"sub": new_user["username"]},
        expires_delta=access_token_expires,
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@app.post("/api/logout")
async def logout():
    return {"message": "Успешный выход из системы"}

@app.get("/api/tokens")
async def read_tokens(current_user: Dict = Depends(auth.get_current_user)):
    tokens = crud.get_tokens_by_user_id(user_id=current_user["id"])
    for token in tokens:
        if isinstance(token.get("created_at"), datetime):
            token["created_at"] = token["created_at"].isoformat()
    return tokens
@app.post("/api/tokens")
async def create_token(token: schemas.TokenCreate, current_user: Dict = Depends(auth.get_current_user)):
    try:
        new_token = crud.create_token(token=token, user_id=current_user["id"])
    except psycopg2.errors.UniqueViolation:
        raise HTTPException(
            status_code=400,
            detail=f"Токен с названием '{token.name}' уже существует."
        )
    except Exception as e:
        print("Ошибка при вставке токена:", e)
        raise HTTPException(
            status_code=500,
            detail="Произошла ошибка при создании токена."
        )

    if isinstance(new_token.get("created_at"), datetime):
        new_token["created_at"] = new_token["created_at"].isoformat()

    return new_token

@app.patch("/api/tokens/{token_id}")
async def update_token_balance(
    token_id: int,
    token_update: schemas.TokenUpdate,
    current_user: Dict = Depends(auth.get_current_user)
):
    db_token = crud.get_token(token_id=token_id)
    if db_token is None:
        raise HTTPException(status_code=404, detail="Токен не найден")
    if db_token["user_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Нет доступа к этому токену")
    updated_token = crud.update_token_balance(token_id=token_id, balance=token_update.balance)
    if isinstance(updated_token.get("created_at"), datetime):
        updated_token["created_at"] = updated_token["created_at"].isoformat()
    return updated_token

@app.delete("/api/tokens/{token_id}")
async def delete_token(
    token_id: int,
    current_user: Dict = Depends(auth.get_current_user)
):
    db_token = crud.get_token(token_id=token_id)
    if db_token is None:
        raise HTTPException(status_code=404, detail="Токен не найден")
    if db_token["user_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Нет доступа к этому токену")
    crud.delete_token(token_id=token_id)
    return {"detail": "Токен успешно удален"}

# Маршруты для платежей
@app.get("/api/payments")
async def read_payments(current_user: Dict = Depends(auth.get_current_user)):
    payments = crud.get_payments_by_user_id(user_id=current_user["id"])
    for payment in payments:
        if isinstance(payment.get("created_at"), datetime):
            payment["created_at"] = payment["created_at"].isoformat()
    return payments

@app.post("/api/payments")
async def create_payment(
    payment: schemas.PaymentCreate,
    current_user: Dict = Depends(auth.get_current_user)
):
    db_token = crud.get_token(token_id=payment.token_id)
    if db_token is None:
        raise HTTPException(status_code=404, detail="Токен не найден")
    if db_token["user_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Нет доступа к этому токену")
    
    new_payment = crud.create_payment(payment=payment, user_id=current_user["id"])
    if isinstance(new_payment.get("created_at"), datetime):
        new_payment["created_at"] = new_payment["created_at"].isoformat()
    return new_payment

@app.patch("/api/payments/{payment_id}")
async def update_payment_status(
    payment_id: int,
    payment_update: schemas.PaymentUpdate,
    current_user: Dict = Depends(auth.get_current_user)
):
    db_payment = crud.get_payment(payment_id=payment_id)
    if db_payment is None:
        raise HTTPException(status_code=404, detail="Платеж не найден")
    if db_payment["user_id"] != current_user["id"]:
        raise HTTPException(status_code=403, detail="Нет доступа к этому платежу")
    updated_payment = crud.update_payment_status(payment_id=payment_id, status=payment_update.status)
    if isinstance(updated_payment.get("created_at"), datetime):
        updated_payment["created_at"] = updated_payment["created_at"].isoformat()
    return updated_payment

@app.patch("api/{token}/rename")
def rename_token(
    request: schemas.RenameTokenRequest,
    current_user: schemas.User = Depends(get_current_user)
):
    db_token = db_adapter.query(schemas.Token).filter(schemas.Token.token == request.token).first()

    if db_token is None:
        raise HTTPException(status_code=404, detail="Token not found")
    
    if db_token.user_id != current_user.id:
        raise HTTPException(status_code=403, detail="You do not have permission to rename this token")

    db_token.name = request.name
    db_adapter.commit()
    db_adapter.refresh(db_token)

    return {"detail": "Token renamed successfully", "token": {"token": db_token.token, "name": db_token.name}}
@app.get("/")
async def root():
    return {"message": "EasyGPT API работает"}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)