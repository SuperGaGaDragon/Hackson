"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
"""

from fastapi import APIRouter, Depends, Query, status

from context.repository import ContextPackageRepository
from context.service import ContextPackageService
from core.database import get_database
from users.auth import get_current_user_id, get_user_service
from users.schemas import (
    AuthResponse,
    DesktopHandoffBindRequest,
    DesktopHandoffClaimRequest,
    DesktopHandoffStatusResponse,
    PromptLogDeleteResponse,
    PromptLogListResponse,
    UserLoginRequest,
    UserRegisterRequest,
    UserResponse,
    UserUpdateRequest,
)
from users.service import UserService

router = APIRouter()


def get_context_package_service() -> ContextPackageService:
    return ContextPackageService(ContextPackageRepository(get_database()))


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


@router.post("/desktop-handoff", response_model=dict)
def bind_desktop_handoff(
    payload: DesktopHandoffBindRequest,
    current_user_id: str = Depends(get_current_user_id),
    service: UserService = Depends(get_user_service),
) -> dict:
    return service.bind_desktop_handoff(current_user_id, payload)


@router.post("/desktop-handoff/claim", response_model=DesktopHandoffStatusResponse)
def claim_desktop_handoff(
    payload: DesktopHandoffClaimRequest,
    service: UserService = Depends(get_user_service),
) -> dict:
    return service.claim_desktop_handoff(payload)


@router.get("/me/prompt-logs", response_model=PromptLogListResponse)
def list_prompt_logs(
    limit: int = Query(default=20, ge=1, le=100),
    current_user_id: str = Depends(get_current_user_id),
    service: ContextPackageService = Depends(get_context_package_service),
) -> dict:
    return service.list_prompt_logs(current_user_id, limit)


@router.delete("/me/prompt-logs", response_model=PromptLogDeleteResponse)
def delete_prompt_logs(
    current_user_id: str = Depends(get_current_user_id),
    service: ContextPackageService = Depends(get_context_package_service),
) -> dict:
    return service.delete_prompt_logs(current_user_id)


@router.post("/logout", status_code=status.HTTP_204_NO_CONTENT)
def logout() -> None:
    """JWT logout is client-side in V1; server-side revocation can be added later."""
    return None
