"""
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
"""

from fastapi import APIRouter, Depends, Query

from core.database import get_database
from memory.repository import MemoryRepository
from memory.schemas import MemoryCardDeleteResponse, MemoryCardListResponse, MemoryCardResponse, MemoryCardUpdateRequest
from memory.service import MemoryService
from users.auth import get_current_user_id

router = APIRouter()


def get_memory_service() -> MemoryService:
    return MemoryService(MemoryRepository(get_database()))


@router.get("/me", response_model=MemoryCardListResponse)
def list_my_memory(
    include_deleted: bool = Query(default=False, alias="includeDeleted"),
    limit: int = Query(default=50, ge=1, le=100),
    current_user_id: str = Depends(get_current_user_id),
    service: MemoryService = Depends(get_memory_service),
) -> dict:
    return service.list_user_memory(current_user_id, include_deleted=include_deleted, limit=limit)


@router.patch("/me/{memory_id}", response_model=MemoryCardResponse)
def update_my_memory(
    memory_id: str,
    payload: MemoryCardUpdateRequest,
    current_user_id: str = Depends(get_current_user_id),
    service: MemoryService = Depends(get_memory_service),
) -> dict:
    return service.update_status(current_user_id, memory_id, payload.status)


@router.delete("/me/{memory_id}", response_model=MemoryCardDeleteResponse)
def delete_my_memory(
    memory_id: str,
    current_user_id: str = Depends(get_current_user_id),
    service: MemoryService = Depends(get_memory_service),
) -> dict:
    return service.delete_memory(current_user_id, memory_id)
