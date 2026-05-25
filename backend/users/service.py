"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Last Modified by: Codex
"""

from typing import Any, Protocol

from fastapi import HTTPException, status
from pymongo.errors import DuplicateKeyError

from core.security import create_access_token, hash_password, verify_password
from users.model import now_utc, public_user
from users.schemas import UserLoginRequest, UserRegisterRequest, UserUpdateRequest


class UserRepositoryProtocol(Protocol):
    def ensure_indexes(self) -> None: ...
    def create(self, document: dict[str, Any]) -> dict[str, Any]: ...
    def find_by_id(self, user_id: str) -> dict[str, Any] | None: ...
    def find_by_identifier(self, identifier: str) -> dict[str, Any] | None: ...
    def update(self, user_id: str, changes: dict[str, Any]) -> dict[str, Any] | None: ...


class UserService:
    """Product business rules for the V1 user identity boundary."""

    def __init__(self, repository: UserRepositoryProtocol):
        self.repository = repository
        self.repository.ensure_indexes()

    def register(self, payload: UserRegisterRequest) -> dict[str, Any]:
        timestamp = now_utc()
        display_name = payload.display_name or payload.username
        document = {
            "username": payload.username,
            "username_normalized": payload.username.lower(),
            "display_name": display_name,
            "email": str(payload.email),
            "email_normalized": str(payload.email).lower(),
            "password_hash": hash_password(payload.password),
            "idle_on": True,
            "language_preference": "zh",
            "created_at": timestamp,
            "updated_at": timestamp,
        }
        try:
            user = self.repository.create(document)
        except DuplicateKeyError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="username_or_email_already_exists",
            ) from exc
        return self._auth_response(user)

    def login(self, payload: UserLoginRequest) -> dict[str, Any]:
        user = self.repository.find_by_identifier(payload.identifier)
        if user is None or not verify_password(payload.password, user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="invalid_credentials",
            )
        return self._auth_response(user)

    def get_user(self, user_id: str) -> dict[str, Any]:
        user = self.repository.find_by_id(user_id)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user_not_found")
        return public_user(user)

    def update_user(self, user_id: str, payload: UserUpdateRequest) -> dict[str, Any]:
        changes: dict[str, Any] = {"updated_at": now_utc()}
        if payload.display_name is not None:
            changes["display_name"] = payload.display_name
        if payload.idle_on is not None:
            changes["idle_on"] = payload.idle_on
        if payload.language_preference is not None:
            changes["language_preference"] = payload.language_preference

        user = self.repository.update(user_id, changes)
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="user_not_found")
        return public_user(user)

    def _auth_response(self, user: dict[str, Any]) -> dict[str, Any]:
        public = public_user(user)
        return {
            "accessToken": create_access_token(public["id"]),
            "tokenType": "bearer",
            "user": public,
        }
