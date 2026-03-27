"""Dependency helpers for API routes."""

from __future__ import annotations

from typing import Annotated

from fastapi import Depends, Header, HTTPException, Request

from .services.auth_service import AuthService
from .services.document_service import DocumentService
from .services.search_service import SearchService


def get_auth_service(request: Request) -> AuthService:
    return request.app.state.auth_service


def get_document_service(request: Request) -> DocumentService:
    return request.app.state.document_service


def get_search_service(request: Request) -> SearchService:
    return request.app.state.search_service


def get_current_user_id(
    authorization: Annotated[str | None, Header()] = None,
    auth_service: AuthService = Depends(get_auth_service),
) -> str:
    if not authorization or not authorization.lower().startswith("bearer "):
        raise HTTPException(status_code=401, detail="missing bearer token")

    token = authorization.split(" ", 1)[1].strip()
    user_id = auth_service.verify_token(token)
    if not user_id:
        raise HTTPException(status_code=401, detail="invalid token")
    return user_id
