"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Last Modified by: Codex
"""

from fastapi import APIRouter, Depends, Query, status

from conversations.repository import ConversationRepository
from conversations.schemas import (
    ConversationCreateRequest,
    ConversationResponse,
    ConversationStatus,
    ConversationMode,
    MessageAppendRequest,
    MessagePageResponse,
    MessageResponse,
)
from conversations.service import ConversationService
from core.database import get_database
from users.auth import get_current_user_id

router = APIRouter()
idle_router = APIRouter()


def get_conversation_service() -> ConversationService:
    return ConversationService(ConversationRepository(get_database()))


@router.post("", response_model=ConversationResponse, status_code=status.HTTP_201_CREATED)
def create_conversation(
    payload: ConversationCreateRequest,
    current_user_id: str = Depends(get_current_user_id),
    service: ConversationService = Depends(get_conversation_service),
) -> dict:
    return service.create_conversation(current_user_id, payload)


@router.get("", response_model=list[ConversationResponse])
def list_conversations(
    mode: ConversationMode | None = None,
    conversation_status: ConversationStatus | None = Query(default=None, alias="status"),
    limit: int = Query(default=50, ge=1, le=100),
    current_user_id: str = Depends(get_current_user_id),
    service: ConversationService = Depends(get_conversation_service),
) -> list[dict]:
    return service.list_conversations(current_user_id, mode, conversation_status, limit)


@router.get("/{conversation_id}", response_model=ConversationResponse)
def get_conversation(
    conversation_id: str,
    current_user_id: str = Depends(get_current_user_id),
    service: ConversationService = Depends(get_conversation_service),
) -> dict:
    return service.get_conversation(current_user_id, conversation_id)


@router.post("/{conversation_id}/messages", response_model=MessageResponse, status_code=status.HTTP_201_CREATED)
def append_message(
    conversation_id: str,
    payload: MessageAppendRequest,
    current_user_id: str = Depends(get_current_user_id),
    service: ConversationService = Depends(get_conversation_service),
) -> dict:
    return service.append_message(current_user_id, conversation_id, payload)


@router.get("/{conversation_id}/messages", response_model=MessagePageResponse)
def list_messages(
    conversation_id: str,
    after_sequence: int | None = Query(default=None, alias="afterSequence", ge=0),
    limit: int = Query(default=50, ge=1, le=100),
    current_user_id: str = Depends(get_current_user_id),
    service: ConversationService = Depends(get_conversation_service),
) -> dict:
    return service.list_messages(current_user_id, conversation_id, after_sequence, limit)


@idle_router.get("/conversation", response_model=ConversationResponse)
def get_active_idle_conversation(
    current_user_id: str = Depends(get_current_user_id),
    service: ConversationService = Depends(get_conversation_service),
) -> dict:
    return service.get_or_create_active_idle(current_user_id)
