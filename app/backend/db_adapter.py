import os
import psycopg2
from psycopg2.extras import RealDictCursor
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()
class DatabaseAdapter:
    def __init__(self) -> None:
        """Инициализация адаптера базы данных."""
        self.conn = None
        self.db_settings = {
            "dbname": os.getenv('DBNAME'),
            "user": os.getenv('DBUSER'),
            "password": os.getenv('DB_PASSWORD'),
            "host": os.getenv('DB_HOST'),
            "port": os.getenv('DB_PORT')
        }
        
        if not all(self.db_settings.values()):
            print("Warning: Some database configuration is missing!")
            for key, value in self.db_settings.items():
                print(f"{key}: {'Set' if value else 'Not set'}")

    def connect(self) -> None:
        """Подключение к базе данных PostgreSQL."""
        if self.conn is None or self.conn.closed:
            try:
                self.conn = psycopg2.connect(
                    dbname=self.db_settings["dbname"],
                    user=self.db_settings["user"],
                    password=self.db_settings["password"],
                    host=self.db_settings["host"],
                    port=self.db_settings["port"]
                )
                print("Connected to PostgreSQL database!")
            except Exception as e:
                print(f"Error connecting to PostgreSQL database: {e}")
                self.conn = None

    def initialize_tables(self) -> None:
        """Инициализация таблиц в базе данных, если они не существуют."""
        self.connect()
        if not self.conn:
            print("Failed to initialize tables: No database connection.")
            return
            
        try:
            cursor = self.conn.cursor()
            
            cursor.execute("""
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
            """)
            # Создание таблицы пользователей
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id SERIAL PRIMARY KEY,
                    username VARCHAR(100) UNIQUE NOT NULL,
                    password VARCHAR(255) NOT NULL,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Создание таблицы токенов
            cursor.execute("""
               CREATE TABLE IF NOT EXISTS tokens (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    name VARCHAR(255) NOT NULL,
                    token VARCHAR(255) UNIQUE NOT NULL,
                    balance FLOAT DEFAULT 0.0,
                    active BOOLEAN DEFAULT TRUE,
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Создание таблицы платежей
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS payments (
                    id SERIAL PRIMARY KEY,
                    user_id INTEGER REFERENCES users(id) ON DELETE CASCADE,
                    token_id INTEGER REFERENCES tokens(id) ON DELETE CASCADE,
                    amount FLOAT NOT NULL,
                    status VARCHAR(50) DEFAULT 'pending',
                    payment_id VARCHAR(255),
                    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            self.conn.commit()
            print("Database tables initialized!")
        except Exception as e:
            print(f"Error initializing tables: {e}")
            self.conn.rollback()

    def get_all(self, table_name: str) -> List[Dict]:
        """Получение всех записей из указанной таблицы."""
        self.connect()
        if not self.conn:
            return []
            
        try:
            cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(f"SELECT * FROM {table_name};")
            return list(cursor.fetchall())
        except Exception as e:
            print(f"Error getting all from {table_name}: {e}")
            return []

    def get_by_id(self, table_name: str, id: str | int) -> Optional[Dict]:
        """Получение записи по ID из указанной таблицы."""
        self.connect()
        if not self.conn:
            return None
            
        try:
            cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(f"SELECT * FROM {table_name} WHERE id = %s;", (id,))
            result = cursor.fetchone()
            return dict(result) if result else None
        except Exception as e:
            print(f"Error getting by ID from {table_name}: {e}")
            return None

    def get_by_value(self, table_name: str, parameter: str, parameter_value: Any) -> List[Dict]:
        """Получение записей по указанному параметру и его значению."""
        self.connect()
        if not self.conn:
            return []
            
        try:
            cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(f"SELECT * FROM {table_name} WHERE {parameter} = %s;", (parameter_value,))
            return list(cursor.fetchall())
        except Exception as e:
            print(f"Error getting by value from {table_name}: {e}")
            return []

    def get_single_by_value(self, table_name: str, parameter: str, parameter_value: Any) -> Optional[Dict]:
        """Получение одной записи по указанному параметру и его значению."""
        self.connect()
        if not self.conn:
            return None
            
        try:
            cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(f"SELECT * FROM {table_name} WHERE {parameter} = %s;", (parameter_value,))
            result = cursor.fetchone()
            return dict(result) if result else None
        except Exception as e:
            print(f"Error getting single by value from {table_name}: {e}")
            return None

    def insert(self, table_name: str, insert_dict: Dict) -> Optional[Dict]:
        """Вставка новой записи в указанную таблицу."""
        self.connect()
        if not self.conn:
            return None

        try:
            columns = ", ".join(insert_dict.keys())
            placeholders = ", ".join(["%s" for _ in insert_dict])
            values = tuple(insert_dict.values())

            cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(
                f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders}) RETURNING *;",
                values
            )
            result = cursor.fetchone()
            self.conn.commit()
            return dict(result) if result else None

        except psycopg2.errors.UniqueViolation as e:
            self.conn.rollback()
            raise e 

        except Exception as e:
            print(f"Error inserting into {table_name}: {e}")
            self.conn.rollback()
            raise e  

    def delete_by_value(self, table_name: str, parameter: str, parameter_value: Any) -> Optional[Dict]:
        """Удаление записи по указанному параметру и его значению."""
        self.connect()
        if not self.conn:
            return None
            
        try:
            cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(
                f"DELETE FROM {table_name} WHERE {parameter} = %s RETURNING *;",
                (parameter_value,)
            )
            result = cursor.fetchone()
            self.conn.commit()
            return dict(result) if result else None
        except Exception as e:
            print(f"Error deleting from {table_name}: {e}")
            if self.conn:
                self.conn.rollback()
            return None

    def update_by_value(self, table_name: str, update_dict: Dict, parameter: str, value: Any) -> Optional[Dict]:
        """Обновление записи по указанному параметру и его значению."""
        self.connect()
        if not self.conn:
            return None
            
        try:
            set_clause = ", ".join([f"{key} = %s" for key in update_dict])
            values = list(update_dict.values())
            values.append(value)
            
            cursor = self.conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(
                f"UPDATE {table_name} SET {set_clause} WHERE {parameter} = %s RETURNING *;",
                tuple(values)
            )
            result = cursor.fetchone()
            self.conn.commit()
            return dict(result) if result else None
        except Exception as e:
            print(f"Error updating in {table_name}: {e}")
            if self.conn:
                self.conn.rollback()
            return None

    def update(self, table_name: str, update_dict: Dict, id: int) -> Optional[Dict]:
        """Обновление записи по ID."""
        return self.update_by_value(table_name, update_dict, "id", id)

    def delete(self, table_name: str, id: int) -> Optional[Dict]:
        """Удаление записи по ID."""
        return self.delete_by_value(table_name, "id", id)