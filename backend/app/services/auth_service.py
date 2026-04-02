"""Auth service with a persistent SQLite implementation."""

from __future__ import annotations

import hashlib
import sqlite3
import uuid
from dataclasses import dataclass
from pathlib import Path


@dataclass
class AuthUser:
    user_id: str
    email: str
    password_hash: str


class AuthService:
    def __init__(self, db_dir: str = "store/backend_users") -> None:
        self.db_path = Path(db_dir) / "auth.db"
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(
            self.db_path,
            check_same_thread=False,
            isolation_level=None
        ) as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id TEXT PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    password_hash TEXT NOT NULL
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS tokens (
                    token TEXT PRIMARY KEY,
                    user_id TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')

    def _get_conn(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    @staticmethod
    def _hash_password(password: str) -> str:
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def register_user(self, email: str, password: str) -> AuthUser:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT 1 FROM users WHERE email = ?", (email,))
            if cursor.fetchone() is not None:
                raise ValueError("email already exists")
            
            user_id = str(uuid.uuid4())
            password_hash = self._hash_password(password)
            
            try:
                cursor.execute(
                    "INSERT INTO users (user_id, email, password_hash) VALUES (?, ?, ?)",
                    (user_id, email, password_hash)
                )
            except sqlite3.IntegrityError:
                raise ValueError("email already exists")
                
            return AuthUser(user_id=user_id, email=email, password_hash=password_hash)

    def login(self, email: str, password: str) -> str:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id, password_hash FROM users WHERE email = ?", (email,))
            row = cursor.fetchone()
            
            if row is None or row["password_hash"] != self._hash_password(password):
                raise ValueError("invalid credentials")
                
            token = f"dev-token-{row['user_id']}-{uuid.uuid4().hex[:8]}"
            cursor.execute("INSERT INTO tokens (token, user_id) VALUES (?, ?)", (token, row["user_id"]))
            return token

    def verify_token(self, token: str) -> str | None:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id FROM tokens WHERE token = ?", (token,))
            row = cursor.fetchone()
            if row:
                return row["user_id"]
            return None

    def get_user(self, user_id: str) -> AuthUser | None:
        with self._get_conn() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT user_id, email, password_hash FROM users WHERE user_id = ?", (user_id,))
            row = cursor.fetchone()
            if row:
                return AuthUser(
                    user_id=row["user_id"],
                    email=row["email"],
                    password_hash=row["password_hash"]
                )
            return None
