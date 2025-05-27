import os
from typing import List, Any
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

class DatabaseAdapter:
    def __init__(self) -> None:
        self.client: Client | None = None

    def connect(self) -> None:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        if not url or not key:
            raise ValueError("SUPABASE_URL и SUPABASE_KEY должны быть в .env")
        self.client = create_client(url, key)
        print("✅ Соединение с Supabase установлено.")


    def get_all(self, table_name: str) -> List[dict]:
        if not self.client:
            raise RuntimeError("Client не инициализирован. Вызовите connect() первым.")
        res = self.client.table(table_name).select("*").execute()
        if res.error:
            raise RuntimeError(f"Ошибка запроса get_all: {res.error}")
        return res.data

    def get_by_id(self, table_name: str, id: int | str) -> List[dict]:
        if not self.client:
            raise RuntimeError("Client не инициализирован. Вызовите connect() первым.")
        res = self.client.table(table_name).select("*").eq("id", id).execute()
        if res.error:
            raise RuntimeError(f"Ошибка запроса get_by_id: {res.error}")
        return res.data

    def get_by_value(self, table_name: str, parameter: str, parameter_value: Any) -> List[dict]:
        if not self.client:
            raise RuntimeError("Client не инициализирован. Вызовите connect() первым.")
        res = self.client.table(table_name).select("*").eq(parameter, parameter_value).execute()
        if res.error:
            raise RuntimeError(f"Ошибка запроса get_by_value: {res.error}")
        return res.data

    def insert(self, table_name: str, insert_dict: dict) -> List[dict]:
        if not self.client:
            raise RuntimeError("Client не инициализирован. Вызовите connect() первым.")
        res = self.client.table(table_name).insert(insert_dict).select("*").execute()
        if res.error:
            raise RuntimeError(f"Ошибка запроса insert: {res.error}")
        return res.data

    def delete_by_value(self, table_name: str, parameter: str, parameter_value: Any) -> List[dict]:
        if not self.client:
            raise RuntimeError("Client не инициализирован. Вызовите connect() первым.")
        res = self.client.table(table_name).delete().eq(parameter, parameter_value).select("*").execute()
        if res.error:
            raise RuntimeError(f"Ошибка запроса delete_by_value: {res.error}")
        return res.data

    def update_by_value(self, table_name: str, update_dict: dict, parameter: str, value: Any) -> List[dict]:
        if not self.client:
            raise RuntimeError("Client не инициализирован. Вызовите connect() первым.")
        res = self.client.table(table_name).update(update_dict).eq(parameter, value).select("*").execute()
        if res.error:
            raise RuntimeError(f"Ошибка запроса update_by_value: {res.error}")
        return res.data

    def update(self, table_name: str, update_dict: dict, id: int) -> List[dict]:
        return self.update_by_value(table_name, update_dict, "id", id)

    def delete(self, table_name: str, id: int) -> List[dict]:
        return self.delete_by_value(table_name, "id", id)
