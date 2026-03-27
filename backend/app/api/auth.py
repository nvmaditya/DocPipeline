"""Authentication routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, EmailStr, Field

from ..dependencies import get_auth_service, get_current_user_id
from ..services.auth_service import AuthService


router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/register")
def register(payload: RegisterRequest, auth_service: AuthService = Depends(get_auth_service)) -> dict:
    try:
        user = auth_service.register_user(payload.email, payload.password)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"user_id": user.user_id, "email": user.email}


@router.post("/login")
def login(payload: LoginRequest, auth_service: AuthService = Depends(get_auth_service)) -> dict:
    try:
        token = auth_service.login(payload.email, payload.password)
    except ValueError as exc:
        raise HTTPException(status_code=401, detail=str(exc)) from exc
    return {"access_token": token, "token_type": "bearer"}


@router.post("/logout")
def logout(_: str = Depends(get_current_user_id)) -> dict:
    return {"message": "logged out"}


@router.get("/me")
def me(user_id: str = Depends(get_current_user_id), auth_service: AuthService = Depends(get_auth_service)) -> dict:
    user = auth_service.get_user(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="user not found")
    return {"user_id": user.user_id, "email": user.email}
