"""Auth service with a lightweight in-memory implementation for Phase 5 scaffolding."""

from __future__ import annotations

import hashlib
import uuid
from dataclasses import dataclass


@dataclass
class AuthUser:
    user_id: str
    email: str
    password_hash: str


class AuthService:
    def __init__(self) -> None:
        self._users: dict[str, AuthUser] = {}
        self._tokens: dict[str, str] = {}

    @staticmethod
    def _hash_password(password: str) -> str:
        return hashlib.sha256(password.encode("utf-8")).hexdigest()

    def register_user(self, email: str, password: str) -> AuthUser:
        if email in self._users:
            raise ValueError("email already exists")
        user = AuthUser(
            user_id=str(uuid.uuid4()),
            email=email,
            password_hash=self._hash_password(password),
        )
        self._users[email] = user
        return user

    def login(self, email: str, password: str) -> str:
        user = self._users.get(email)
        if user is None:
            raise ValueError("invalid credentials")
        if user.password_hash != self._hash_password(password):
            raise ValueError("invalid credentials")
        token = f"dev-token-{user.user_id}"
        self._tokens[token] = user.user_id
        return token

    def verify_token(self, token: str) -> str | None:
        return self._tokens.get(token)

    def get_user(self, user_id: str) -> AuthUser | None:
        for user in self._users.values():
            if user.user_id == user_id:
                return user
        return None
