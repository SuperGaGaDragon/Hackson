"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Last Modified by: Codex
"""

from typing import Protocol

from conversations.schemas import ConversationCreateRequest, MessageAppendRequest
from conversations.service import ConversationService
from context.builder import ContextBuilder
from context.schemas import ContextBuildInput, ContextMode, ConversationMessage, SenderType, UserProfileSnapshot
from agents.catalog import default_agent_snapshots, ensure_agent_id
from interactions.schemas import IdleTickRequest, InteractionUserMessageRequest
from model_runtime.schemas import ModelGenerateRequest, ModelGenerateResponse, RuntimeMessage


class ModelRuntimeProtocol(Protocol):
    def generate(self, request: ModelGenerateRequest) -> ModelGenerateResponse: ...


class InteractionService:
    """Product orchestration for user and idle model interactions."""

    def __init__(
        self,
        conversation_service: ConversationService,
        context_builder: ContextBuilder,
        model_runtime: ModelRuntimeProtocol,
    ):
        self.conversation_service = conversation_service
        self.context_builder = context_builder
        self.model_runtime = model_runtime

    def run_idle_tick(self, user_id: str, conversation_id: str, payload: IdleTickRequest) -> dict:
        conversation = self.conversation_service.get_conversation(user_id, conversation_id)
        recent = self._recent_context_messages(user_id, conversation_id)
        target_agent_id = ensure_agent_id(payload.target_agent_id)
        package = self.context_builder.build(
            ContextBuildInput(
                mode=ContextMode.IDLE,
                conversation_id=conversation_id,
                target_agent_id=target_agent_id,
                agents=default_agent_snapshots(),
                recent_messages=recent,
                idle_seed=payload.idle_seed or "继续 idle 对话，保持自然、简短、有生活感。",
                token_budget=6000,
            )
        )
        model_response = self._generate(package)
        agent_message = self._save_agent_message(
            user_id,
            conversation_id,
            target_agent_id,
            model_response,
            package,
            extra_metadata=payload.metadata,
        )
        updated_conversation = self.conversation_service.get_conversation(user_id, conversation_id)
        return self._response(updated_conversation, None, agent_message, package, model_response)

    def run_companion_1_join(
        self,
        user_id: str,
        idle_conversation_id: str,
        payload: InteractionUserMessageRequest,
    ) -> dict:
        idle_conversation = self.conversation_service.get_conversation(user_id, idle_conversation_id)
        companion = self.conversation_service.create_conversation(
            user_id,
            ConversationCreateRequest(
                mode="companion_1",
                title="Companion 1",
                parent_conversation_id=idle_conversation_id,
                metadata={"source": "idle_join", "parentMode": idle_conversation["mode"]},
            ),
        )
        user_message = self.conversation_service.append_message(
            user_id,
            companion["id"],
            MessageAppendRequest(
                sender_type="user",
                sender_id=user_id,
                role="user",
                content=payload.content,
                metadata=payload.metadata,
            ),
        )
        idle_recent = self._recent_context_messages(user_id, idle_conversation_id)
        target_agent_id = ensure_agent_id(payload.target_agent_id)
        package = self.context_builder.build(
            ContextBuildInput(
                mode=ContextMode.COMPANION_1,
                conversation_id=companion["id"],
                target_agent_id=target_agent_id,
                agents=default_agent_snapshots(),
                user_message=payload.content,
                idle_recent_messages=idle_recent,
                token_budget=6000,
            )
        )
        model_response = self._generate(package)
        agent_message = self._save_agent_message(
            user_id,
            companion["id"],
            target_agent_id,
            model_response,
            package,
            extra_metadata={"parentIdleConversationId": idle_conversation_id},
        )
        updated_companion = self.conversation_service.get_conversation(user_id, companion["id"])
        return self._response(updated_companion, user_message, agent_message, package, model_response)

    def run_companion_2_message(
        self,
        user_id: str,
        conversation_id: str,
        payload: InteractionUserMessageRequest,
    ) -> dict:
        conversation = self.conversation_service.get_conversation(user_id, conversation_id)
        user_message = self.conversation_service.append_message(
            user_id,
            conversation_id,
            MessageAppendRequest(
                sender_type="user",
                sender_id=user_id,
                role="user",
                content=payload.content,
                metadata=payload.metadata,
            ),
        )
        recent = self._recent_context_messages(user_id, conversation_id)
        target_agent_id = ensure_agent_id(payload.target_agent_id)
        package = self.context_builder.build(
            ContextBuildInput(
                mode=ContextMode.COMPANION_2,
                conversation_id=conversation_id,
                target_agent_id=target_agent_id,
                agents=default_agent_snapshots(),
                user_message=payload.content,
                recent_messages=recent,
                user_profile=UserProfileSnapshot(id=user_id, language_preference="zh"),
                token_budget=6000,
            )
        )
        model_response = self._generate(package)
        agent_message = self._save_agent_message(
            user_id,
            conversation_id,
            target_agent_id,
            model_response,
            package,
            extra_metadata=None,
        )
        updated_conversation = self.conversation_service.get_conversation(user_id, conversation_id)
        return self._response(updated_conversation, user_message, agent_message, package, model_response)

    def _recent_context_messages(self, user_id: str, conversation_id: str) -> list[ConversationMessage]:
        page = self.conversation_service.list_messages(
            user_id,
            conversation_id,
            after_sequence=None,
            created_after=None,
            created_before=None,
            limit=20,
        )
        return [_context_message(row) for row in page["messages"]]

    def _generate(self, package) -> ModelGenerateResponse:
        return self.model_runtime.generate(
            ModelGenerateRequest(
                messages=[RuntimeMessage(role=message.role, content=message.content) for message in package.messages],
                max_output_tokens=360,
                temperature=0.4,
            )
        )

    def _save_agent_message(
        self,
        user_id: str,
        conversation_id: str,
        target_agent_id: str,
        model_response: ModelGenerateResponse,
        package,
        extra_metadata: dict | None,
    ) -> dict:
        metadata = {
            "prompt_hash": package.prompt_hash,
            "token_estimate": package.token_estimate,
            "model_name": model_response.model_name,
        }
        if extra_metadata:
            metadata.update(extra_metadata)
        return self.conversation_service.append_message(
            user_id,
            conversation_id,
            MessageAppendRequest(
                sender_type="agent",
                sender_slot=_agent_slot(target_agent_id),
                role="assistant",
                content=model_response.text,
                metadata=metadata,
            ),
        )

    def _response(self, conversation, user_message, agent_message, package, model_response) -> dict:
        return {
            "conversation": conversation,
            "userMessage": user_message,
            "agentMessage": agent_message,
            "context": {
                "promptHash": package.prompt_hash,
                "tokenEstimate": package.token_estimate,
                "modelName": model_response.model_name,
            },
        }


def _context_message(row: dict) -> ConversationMessage:
    sender_slot = row.get("senderSlot")
    return ConversationMessage(
        id=row["id"],
        sender_type=SenderType(row["senderType"]),
        sender_id=row.get("senderId") or sender_slot,
        sender_name=row.get("senderId") or sender_slot,
        content=row["content"],
        metadata=row.get("metadata", {}),
    )


def _agent_slot(agent_id: str) -> str:
    if agent_id == "agent_2":
        return "agent_2"
    return "agent_1"
