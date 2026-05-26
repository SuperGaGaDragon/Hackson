"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-26
Last Modified by: Codex
"""

from fastapi import APIRouter, Depends, status

from context.builder import ContextBuilder
from conversations.repository import ConversationRepository
from conversations.service import ConversationService
from core.database import get_database
from interactions.schemas import IdleTickRequest, InteractionResponse, InteractionUserMessageRequest
from interactions.service import InteractionService
from model_runtime.client import OpenAICompatibleClient
from model_runtime.config_repository import ModelRuntimeConfigRepository
from model_runtime.orchestrator import ModelRuntime
from workers.derived_jobs import DerivedJobRepository, DerivedJobService
from users.auth import get_current_user_id

idle_router = APIRouter()
companion_router = APIRouter()


def get_interaction_service() -> InteractionService:
    conversation_service = ConversationService(ConversationRepository(get_database()))
    model_runtime = ModelRuntime(
        config_repository=ModelRuntimeConfigRepository(),
        client=OpenAICompatibleClient(),
    )
    return InteractionService(
        conversation_service=conversation_service,
        context_builder=ContextBuilder(),
        model_runtime=model_runtime,
        derived_jobs=DerivedJobService(DerivedJobRepository(get_database())),
    )


@idle_router.post(
    "/{conversation_id}/tick",
    response_model=InteractionResponse,
    status_code=status.HTTP_201_CREATED,
)
def idle_tick(
    conversation_id: str,
    payload: IdleTickRequest,
    current_user_id: str = Depends(get_current_user_id),
    service: InteractionService = Depends(get_interaction_service),
) -> dict:
    return service.run_idle_tick(current_user_id, conversation_id, payload)


@idle_router.post(
    "/{conversation_id}/join",
    response_model=InteractionResponse,
    status_code=status.HTTP_201_CREATED,
)
def idle_join(
    conversation_id: str,
    payload: InteractionUserMessageRequest,
    current_user_id: str = Depends(get_current_user_id),
    service: InteractionService = Depends(get_interaction_service),
) -> dict:
    return service.run_companion_1_join(current_user_id, conversation_id, payload)


@companion_router.post(
    "/{conversation_id}/messages",
    response_model=InteractionResponse,
    status_code=status.HTTP_201_CREATED,
)
def companion_message(
    conversation_id: str,
    payload: InteractionUserMessageRequest,
    current_user_id: str = Depends(get_current_user_id),
    service: InteractionService = Depends(get_interaction_service),
) -> dict:
    return service.run_companion_message(current_user_id, conversation_id, payload)
