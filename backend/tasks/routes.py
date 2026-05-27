"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Last Modified by: Codex
"""

from fastapi import APIRouter, Depends, Query, status

from context.builder import ContextBuilder
from conversations.repository import ConversationRepository
from conversations.service import ConversationService
from core.database import get_database
from interactions.schemas import InteractionResponse, InteractionUserMessageRequest
from interactions.service import InteractionService
from model_runtime.client import CodexCliClient, OpenAICompatibleClient, OpenAIResponsesClient
from model_runtime.config_repository import ModelRuntimeConfigRepository
from model_runtime.orchestrator import ModelRuntime
from tasks.repository import TaskRepository
from tasks.schemas import TaskCreateRequest, TaskResponse
from tasks.service import TaskService
from users.auth import get_current_user_id
from workers.derived_jobs import DerivedJobRepository, DerivedJobService

router = APIRouter()


def get_task_service() -> TaskService:
    conversation_service = ConversationService(ConversationRepository(get_database()))
    return TaskService(TaskRepository(get_database()), conversation_service)


def get_work_interaction_service() -> InteractionService:
    conversation_service = ConversationService(ConversationRepository(get_database()))
    model_runtime = ModelRuntime(
        config_repository=ModelRuntimeConfigRepository(),
        client=OpenAICompatibleClient(),
        responses_client=OpenAIResponsesClient(),
        codex_cli_client=CodexCliClient(),
    )
    return InteractionService(
        conversation_service=conversation_service,
        context_builder=ContextBuilder(),
        model_runtime=model_runtime,
        derived_jobs=DerivedJobService(DerivedJobRepository(get_database())),
    )


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
def create_task(
    payload: TaskCreateRequest,
    current_user_id: str = Depends(get_current_user_id),
    service: TaskService = Depends(get_task_service),
) -> dict:
    return service.create_task(current_user_id, payload)


@router.get("", response_model=list[TaskResponse])
def list_tasks(
    limit: int = Query(default=50, ge=1, le=100),
    current_user_id: str = Depends(get_current_user_id),
    service: TaskService = Depends(get_task_service),
) -> list[dict]:
    return service.list_tasks(current_user_id, limit)


@router.get("/{task_id}", response_model=TaskResponse)
def get_task(
    task_id: str,
    current_user_id: str = Depends(get_current_user_id),
    service: TaskService = Depends(get_task_service),
) -> dict:
    return service.get_task(current_user_id, task_id)


@router.post("/{task_id}/messages", response_model=InteractionResponse, status_code=status.HTTP_201_CREATED)
def send_work_message(
    task_id: str,
    payload: InteractionUserMessageRequest,
    current_user_id: str = Depends(get_current_user_id),
    task_service: TaskService = Depends(get_task_service),
    interaction_service: InteractionService = Depends(get_work_interaction_service),
) -> dict:
    task = task_service.get_task(current_user_id, task_id)
    task_state = task_service.get_task_state(current_user_id, task_id)
    return interaction_service.run_work_message(
        current_user_id,
        task["conversationId"],
        payload,
        task_state=task_state,
    )
