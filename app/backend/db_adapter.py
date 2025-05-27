import os
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv
from supabase import create_client, Client
from postgrest.exceptions import APIError

load_dotenv()

class SupabaseAdapter:
    def __init__(self) -> None:
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_KEY")
        if not self.supabase_url or not self.supabase_key:
            raise ValueError("SUPABASE_URL and SUPABASE_KEY must be set in environment.")
        self.client: Client = create_client(self.supabase_url, self.supabase_key)

    def get_all(self, table: str) -> List[Dict[str, Any]]:
        response = self.client.table(table).select("*").execute()
        return response.data or []

    def get_by_id(self, table: str, id: Any) -> Optional[Dict[str, Any]]:
        try:
            response = self.client.table(table).select("*").eq("id", id).single().execute()
            return response.data
        except APIError as e:
            if e.code == "PGRST116":
                return None
            raise

    def get_by_value(self, table: str, column: str, value: Any) -> List[Dict[str, Any]]:
        response = self.client.table(table).select("*").eq(column, value).execute()
        return response.data or []

    def get_single_by_value(self, table: str, column: str, value: Any) -> Optional[Dict[str, Any]]:
        try:
            response = self.client.table(table).select("*").eq(column, value).single().execute()
            return response.data
        except APIError as e:
            if e.code == "PGRST116":
                return None  # 0 или более строк — безопасно возвращаем None
            raise

    def insert(self, table: str, insert_dict: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        response = self.client.table(table).insert(insert_dict).execute()
        return response.data[0] if response.data else None

    def update_by_value(self, table: str, update_dict: Dict[str, Any], column: str, value: Any) -> Optional[Dict[str, Any]]:
        response = self.client.table(table).update(update_dict).eq(column, value).execute()
        return response.data[0] if response.data else None

    def update(self, table: str, update_dict: Dict[str, Any], id: int) -> Optional[Dict[str, Any]]:
        return self.update_by_value(table, update_dict, "id", id)

    def delete_by_value(self, table: str, column: str, value: Any) -> Optional[Dict[str, Any]]:
        response = self.client.table(table).delete().eq(column, value).execute()
        return response.data[0] if response.data else None

    def delete(self, table: str, id: int) -> Optional[Dict[str, Any]]:
        return self.delete_by_value(table, "id", id)
