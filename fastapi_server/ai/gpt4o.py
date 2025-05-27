from fastapi import APIRouter, HTTPException
from fastapi.security import HTTPBearer
from models.schemas import DialogQuery, DialogRename, DialogCreateRequest
from adapters.db_source import DatabaseAdapter
from openai import OpenAI
from dotenv import load_dotenv
from psycopg2.extras import Json
import httpx
import os
import json
import tiktoken
import uuid

load_dotenv()

router = APIRouter()
bearer = HTTPBearer(auto_error=False)
db = DatabaseAdapter()
db.connect()
# Прокси и OpenAI client
# http_client = httpx.Client(
#     transport=httpx.HTTPTransport(proxy="http://user166198:dsolnu@176.223.181.66:4932"),
#     timeout=30.0
# )
# , http_client=http_client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# 💰 Получение баланса
def get_token_balance(token: str) -> float:
    token_data = db.get_by_value("tokens", "token", token)
    if not token_data:
        raise HTTPException(status_code=404, detail="Токен не найден")
    return float(token_data[0]["balance"])

# 💸 Подсчёт стоимости
def estimate_chatgpt4o_total_cost(prompt: str, response: str = None) -> float:
    encoding = tiktoken.encoding_for_model("gpt-4o")
    prompt_tokens = len(encoding.encode(prompt))
    prompt_cost = prompt_tokens * 0.000005
    completion_tokens = len(encoding.encode(response)) if response else 0
    completion_cost = completion_tokens * 0.000015
    return round(prompt_tokens + completion_cost, 6)
import tiktoken
from typing import Optional

def estimate_chatgpt4omini_total_cost(prompt: str, response: Optional[str] = None, expected_response_tokens: Optional[int] = None, model: str = "gpt-3.5-turbo") -> int:
    """
    Возвращает общее количество токенов, использованных для prompt + response.
    Если response не задан, можно передать ожидаемое количество токенов в expected_response_tokens.
    """
    try:
        encoding = tiktoken.encoding_for_model(model)
    except KeyError:
        encoding = tiktoken.get_encoding("cl100k_base")  # по умолчанию

    prompt_tokens = len(encoding.encode(prompt))

    if response is not None:
        completion_tokens = len(encoding.encode(response))
    elif expected_response_tokens is not None:
        completion_tokens = expected_response_tokens
    else:
        completion_tokens = 0

    return prompt_tokens + completion_tokens

    
@router.post("/ask_gpt-3.5-turbo")
async def ask_gpt35turbo(prompt: str, token: str, max_tokens: int, temperature: float = 0.3):

    balance = get_token_balance( token)
    if max_tokens > balance:
        raise HTTPException(status_code=402, detail=f"Недостаточно средств: {balance} < {max_tokens},попробуйте уменьшить максимальное количество токенов")
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        temperature=temperature,
        max_tokens=max_tokens
    )
    result = response.choices[0].message.content
    total_cost = estimate_chatgpt4omini_total_cost(prompt,result)
    db.update_by_value("tokens", {"balance": balance - total_cost}, "token", token)
    return {"response": result, "total_cost": max_tokens}

    # try:
    #     response = client.chat.completions.create(
    #         model="gpt-4",
    #         messages=[{"role": "user", "content": prompt}],
    #         temperature=temperature,
    #         max_tokens=50
    #     )
    #     result = response.choices[0].message.content
    #     total_cost = estimate_chatgpt4o_total_cost(prompt=prompt, response=result)
    #     return {"response": result, "total_cost": total_cost}
    # except Exception as e:
    #     print(str(e))
    #     raise HTTPException(status_code=500, detail=str(e))

# 🔹 Создание диалога
@router.post("/dialogs/create")
async def create_dialog(data: DialogCreateRequest):
    token_data = db.get_by_value("tokens", "token", data.token)
    if not token_data:
        raise HTTPException(status_code=404, detail="Неверный токен")

    dialog_id = str(uuid.uuid4())

    dialog = db.insert("dialogs", {
        "id": dialog_id,
        "user_token": data.token,
        "title": data.title,
        "messages": [],
        "model": data.model,
        "temperature": data.temperature or 0.3,
        "total_tokens": 0,
        "system": data.system
    })[0]

    return {"dialog_id": dialog_id, "title": dialog["title"]}
@router.post("/dialogs/chat")
async def chat_with_dialog(payload: DialogQuery):
    dialog_data = db.get_by_id("dialogs", str(payload.dialog_id))
    if not dialog_data:
        raise HTTPException(status_code=404, detail="Диалог не найден")
    dialog = dialog_data[0]

    if dialog["user_token"] != payload.token:
        raise HTTPException(status_code=403, detail="Вы не владеете этим диалогом")

    raw_messages = dialog.get("messages")
    try:
        if raw_messages is None:
            messages = []
        elif isinstance(raw_messages, str):
            messages = json.loads(raw_messages)
        elif isinstance(raw_messages, list):
            messages = raw_messages
        elif isinstance(raw_messages, dict):
            messages = [raw_messages]
        else:
            raise ValueError
    except Exception:
        raise HTTPException(status_code=500, detail="Неверный формат истории сообщений")

    messages = [
        m for m in messages
        if isinstance(m, dict)
        and m.get("role") in {"user", "assistant", "system"}
        and isinstance(m.get("content"), str)
    ]

    if not messages or messages[0].get("role") != "system":
        system_prompt = dialog.get('system') or "Ты умный помощник, отвечай кратко и понятно."
        messages.insert(0, {"role": "system", "content": system_prompt})

    messages.append({"role": "user", "content": payload.message})

    balance = get_token_balance(payload.token)

    encoding = tiktoken.encoding_for_model("gpt-3.5-turbo")
    prompt_token_count = sum(len(encoding.encode(m["content"])) for m in messages)

    max_tokens_requested = max(payload.max_tokens, 1)

    max_tokens_allowed = balance - prompt_token_count
    if max_tokens_allowed < 1:
        raise HTTPException(status_code=402, detail="Недостаточно средств для генерации ответа")

    max_tokens_to_use = min(max_tokens_requested, max_tokens_allowed)
    max_tokens_to_use = int(max_tokens_to_use)  # Приводим к целому

    estimated_total_tokens = prompt_token_count + max_tokens_to_use
    print(estimated_total_tokens)
    if balance < estimated_total_tokens:
        raise HTTPException(status_code=402, detail="Недостаточно средств для предполагаемого запроса")

    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages,
            temperature=dialog.get("temperature", 0.7),
            max_tokens=max_tokens_to_use
        )
        result = response.choices[0].message.content
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    messages.append({"role": "assistant", "content": result})

    total_tokens_used = estimate_chatgpt4omini_total_cost(
        "\n".join(m["content"] for m in messages[:-1]),
        result
    )

    db.update_by_value("dialogs", {
        "messages": messages,
        "total_tokens": dialog.get("total_tokens", 0) + total_tokens_used
    }, "id", str(payload.dialog_id))

    db.update_by_value("tokens", {
        "balance": balance - total_tokens_used
    }, "token", payload.token)

    return {
        "response": result,
        "total_tokens_used": total_tokens_used,
        "new_balance": balance - total_tokens_used,
        "total_tokens": dialog.get("total_tokens", 0) + total_tokens_used
    }



@router.get("/dialogs/{token}")
async def list_dialogs(token: str):

    token_data = db.get_by_value("tokens", "token", token)
    if not token_data:
        raise HTTPException(status_code=404, detail="Токен не найден")

    dialogs = db.get_by_value("dialogs", "user_token", token)
    result = [{"id": d["id"], "title": d["title"], "model": d["model"]} for d in dialogs]
    return {"dialogs": result}

# 🗑 Удаление диалога
@router.delete("/dialogs/{dialog_id}")
async def delete_dialog(dialog_id: str, token: str):

    dialog_data = db.get_by_id("dialogs", dialog_id)
    if not dialog_data:
        raise HTTPException(status_code=404, detail="Диалог не найден")
    dialog = dialog_data[0]

    if dialog.get("user_token") != token:
        raise HTTPException(status_code=403, detail="У вас нет доступа к этому диалогу")

    db.delete("dialogs", dialog_id)
    return {"detail": f"Диалог {dialog_id} удалён"}

# ✏️ Переименование диалога
@router.patch("/dialogs/rename")
async def rename_dialog(data: DialogRename):

    dialog_data = db.get_by_id("dialogs", str(data.dialog_id))
    if not dialog_data:
        raise HTTPException(status_code=404, detail="Диалог не найден")
    dialog = dialog_data[0]

    if dialog.get("user_token") != data.token:
        raise HTTPException(status_code=403, detail="Вы не владеете этим диалогом")

    db.update("dialogs", {"title": data.new_title}, str(data.dialog_id))
    return {"detail": f"Диалог {data.dialog_id} переименован в '{data.new_title}'"}
