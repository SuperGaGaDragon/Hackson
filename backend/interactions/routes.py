"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
"""

from fastapi import APIRouter, Depends, status

from context.builder import ContextBuilder
from context.repository import ContextPackageRepository
from context.runtime import ContextRuntime
from context.service import ContextPackageService
from conversations.repository import ConversationRepository
from conversations.service import ConversationService
from core.database import get_database
from interactions.schemas import (
    IdleBrainstormCardResponse,
    IdleTickRequest,
    IdleUserMessageRequest,
    InteractionResponse,
    InteractionUserMessageRequest,
)
from interactions.locks import IdleTurnLockRepository, IdleTurnLockService
from interactions.service import InteractionService
from memory.repository import MemoryRepository
from memory.service import MemoryService
from model_runtime.client import CodexCliClient, OpenAICompatibleClient, OpenAIResponsesClient
from model_runtime.config_repository import ModelRuntimeConfigRepository
from model_runtime.orchestrator import ModelRuntime
from summaries.repository import SummaryRepository
from summaries.service import SummaryService
from workers.derived_jobs import DerivedJobRepository, DerivedJobService
from users.auth import get_current_user_id
from users.repository import UserRepository
from users.service import UserService

idle_router = APIRouter()
companion_router = APIRouter()


def get_interaction_service() -> InteractionService:
    database = get_database()
    conversation_service = ConversationService(ConversationRepository(database))
    context_builder = ContextBuilder()
    model_runtime = ModelRuntime(
        config_repository=ModelRuntimeConfigRepository(),
        client=OpenAICompatibleClient(),
        responses_client=OpenAIResponsesClient(),
        codex_cli_client=CodexCliClient(),
    )
    return InteractionService(
        conversation_service=conversation_service,
        context_builder=context_builder,
        context_runtime=ContextRuntime(
            context_builder,
            ContextPackageService(ContextPackageRepository(database)),
        ),
        model_runtime=model_runtime,
        derived_jobs=DerivedJobService(DerivedJobRepository(database)),
        user_service=UserService(UserRepository(database)),
        summary_service=SummaryService(SummaryRepository(database)),
        memory_service=MemoryService(MemoryRepository(database)),
        idle_turn_locks=IdleTurnLockService(IdleTurnLockRepository(database)),
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


@idle_router.get(
    "/{conversation_id}/brainstorm-card",
    response_model=IdleBrainstormCardResponse,
)
def idle_brainstorm_card(
    conversation_id: str,
    current_user_id: str = Depends(get_current_user_id),
    service: InteractionService = Depends(get_interaction_service),
) -> dict:
    return service.build_idle_brainstorm_card(current_user_id, conversation_id)


@idle_router.post(
    "/{conversation_id}/messages",
    response_model=InteractionResponse,
    status_code=status.HTTP_201_CREATED,
)
def idle_message(
    conversation_id: str,
    payload: IdleUserMessageRequest,
    current_user_id: str = Depends(get_current_user_id),
    service: InteractionService = Depends(get_interaction_service),
) -> dict:
    return service.run_idle_user_message(current_user_id, conversation_id, payload)


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
