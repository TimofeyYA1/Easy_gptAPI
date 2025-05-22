import os
import psycopg2
from dotenv import load_dotenv
from psycopg2.extras import RealDictCursor
from typing import List, Any

load_dotenv()

class DatabaseAdapter:
    def __init__(self) -> None:
        self.connection = None

    def connect(self) -> None:
        try:
            self.connection = psycopg2.connect(
                dbname=os.getenv("DBNAME"),
                user="postgres",
                password=os.getenv("DB_PASSWORD"),
                host=os.getenv("DB_HOST"),
                port=os.getenv("DB_PORT")
            )
            print("✅ Соединение с базой данных установлено.")
        except psycopg2.Error as e:
            print(f"❌ Ошибка подключения к БД: {e}")
            raise

    def initialize_tables(self) -> None:
        # ВАЖНО: сначала удаляем, если есть (для dev-среды)
        with self.connection.cursor() as cursor:
            # cursor.execute("DROP TABLE IF EXISTS dialogs;")
            # cursor.execute("DROP TABLE IF EXISTS tokens;")
            # cursor.execute("DROP TABLE IF EXISTS users;")
            self.connection.commit()

        # Создание заново
        table_definitions = {
            "users": """
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(100) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

            """,
            "tokens": """
                CREATE TABLE IF NOT EXISTS tokens (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    name VARCHAR(255) NOT NULL,
                    token VARCHAR(255) UNIQUE NOT NULL,
                    balance FLOAT DEFAULT 0.0,
                    active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                );

            """,
            "dialogs": """
                CREATE TABLE IF NOT EXISTS dialogs (
                        id UUID PRIMARY KEY,
                        user_token VARCHAR(255) NOT NULL REFERENCES tokens(token) ON DELETE CASCADE,
                        title TEXT DEFAULT 'Диалог',
                        messages JSONB DEFAULT '[]',
                        model TEXT DEFAULT 'gpt-4o',
                        temperature FLOAT DEFAULT 0.3,
                        max_tokens INT DEFAULT 1000,
                        system TEXT
                    );
            """,
            "payments":"""
                    CREATE TABLE IF NOT EXISTS payments (
                        id SERIAL PRIMARY KEY,
                        user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                        token_id INTEGER REFERENCES tokens(id) ON DELETE CASCADE,
                        amount FLOAT NOT NULL,
                        status VARCHAR(50) DEFAULT 'pending',
                        payment_id VARCHAR(255),
                        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                    );
            """
        }

        with self.connection.cursor() as cursor:
            for name, sql in table_definitions.items():
                cursor.execute(sql)
                print(f"📄 Таблица '{name}' создана.")
            self.connection.commit()

    def get_all(self, table_name: str) -> List[dict]:
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(f"SELECT * FROM {table_name};")
            return cursor.fetchall()

    def get_by_id(self, table_name: str, id: str | int) -> List[dict]:
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(f"SELECT * FROM {table_name} WHERE id = %s;", (id,))
            return cursor.fetchall()

    def get_by_value(self, table_name: str, parameter: str, parameter_value: Any) -> List[dict]:
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            cursor.execute(f"SELECT * FROM {table_name} WHERE {parameter} = %s;", (parameter_value,))
            return cursor.fetchall()

    def insert(self, table_name: str, insert_dict: dict) -> List[dict]:
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            columns = ', '.join(insert_dict.keys())
            values = ', '.join(['%s'] * len(insert_dict))
            query = f"INSERT INTO {table_name} ({columns}) VALUES ({values}) RETURNING *;"
            cursor.execute(query, tuple(insert_dict.values()))
            self.connection.commit()
            return cursor.fetchall()

    def delete_by_value(self, table_name: str, parameter: str, parameter_value: Any) -> List[dict]:
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            query = f"DELETE FROM {table_name} WHERE {parameter} = %s RETURNING *;"
            cursor.execute(query, (parameter_value,))
            self.connection.commit()
            return cursor.fetchall()

    def update_by_value(self, table_name: str, update_dict: dict, parameter: str, value: Any) -> List[dict]:
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            set_clause = ', '.join([f"{key} = %s" for key in update_dict.keys()])
            query = f"""
                UPDATE {table_name}
                SET {set_clause}
                WHERE {parameter} = %s
                RETURNING *;
            """
            cursor.execute(query, tuple(update_dict.values()) + (value,))
            self.connection.commit()
            return cursor.fetchall()

    def update(self, table_name: str, update_dict: dict, id: int) -> List[dict]:
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            set_clause = ', '.join([f"{key} = %s" for key in update_dict.keys()])
            query = f"UPDATE {table_name} SET {set_clause} WHERE id = %s RETURNING *;"
            cursor.execute(query, tuple(update_dict.values()) + (id,))
            self.connection.commit()
            return cursor.fetchall()

    def delete(self, table_name: str, id: int) -> List[dict]:
        with self.connection.cursor(cursor_factory=RealDictCursor) as cursor:
            query = f"DELETE FROM {table_name} WHERE id = %s RETURNING *;"
            cursor.execute(query, (id,))
            self.connection.commit()
            return cursor.fetchall()
