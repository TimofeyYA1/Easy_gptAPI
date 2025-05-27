import os
from typing import List, Any
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

class DatabaseAdapter:
    def __init__(self) -> None:
        self.supabase: Client = None

    def connect(self) -> None:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")  # сервисный ключ с правами на все операции
        if not url or not key:
            raise ValueError("SUPABASE_URL и SUPABASE_SERVICE_ROLE_KEY должны быть в .env")
        self.supabase = create_client(url, key)
        print("✅ Соединение с Supabase установлено.")


    def get_all(self, table_name: str) -> List[dict]:
        response = self.supabase.table(table_name).select("*").execute()
        if response.error:
            raise Exception(f"Ошибка get_all: {response.error.message}")
        return response.data

    def get_by_id(self, table_name: str, id: str | int) -> List[dict]:
        response = self.supabase.table(table_name).select("*").eq("id", id).execute()
        if response.error:
            raise Exception(f"Ошибка get_by_id: {response.error.message}")
        return response.data

    def get_by_value(self, table_name: str, parameter: str, parameter_value: Any) -> List[dict]:
        response = self.supabase.table(table_name).select("*").eq(parameter, parameter_value).execute()
        if response.error:
            raise Exception(f"Ошибка get_by_value: {response.error.message}")
        return response.data

    def insert(self, table_name: str, insert_dict: dict) -> List[dict]:
        response = self.supabase.table(table_name).insert(insert_dict).select("*").execute()
        if response.error:
            raise Exception(f"Ошибка insert: {response.error.message}")
        return response.data

    def delete_by_value(self, table_name: str, parameter: str, parameter_value: Any) -> List[dict]:
        response = self.supabase.table(table_name).delete().eq(parameter, parameter_value).select("*").execute()
        if response.error:
            raise Exception(f"Ошибка delete_by_value: {response.error.message}")
        return response.data

    def update_by_value(self, table_name: str, update_dict: dict, parameter: str, value: Any) ->
