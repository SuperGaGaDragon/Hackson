"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Last Modified by: Codex
"""

from fastapi import APIRouter, Depends, status

from users.auth import get_current_user_id, get_user_service
from users.schemas import AuthResponse, UserLoginRequest, UserRegisterRequest, UserResponse, UserUpdateRequest
from users.service import UserService

router = APIRouter()


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
def register(
    payload: UserRegisterRequest,
    service: UserService = Depends(get_user_service),
) -> dict:
    return service.register(payload)


@router.post("/login", response_model=AuthResponse)
def login(
    payload: UserLoginRequest,
    service: UserService = Depends(get_user_service),
) -> dict:
    return service.login(payload)


@router.get("/me", response_model=UserResponse)
def me(
    current_user_id: str = Depends(get_current_user_id),
    service: UserService = Depends(get_user_service),
) -> dict:
    return service.get_user(current_user_id)


@router.patch("/me", response_model=UserResponse)
def update_me(
    payload: UserUpdateRequest,
    current_user_id: str = Depends(get_current_user_id),
    service: UserService = Depends(get_user_service),
) -> dict:
    return service.update_user(current_user_id, payload)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout() -> None:
    """JWT logout is client-side in V1; server-side revocation can be added later."""
    return None
