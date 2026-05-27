"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-27
Last Modified by: Codex
"""

from dataclasses import dataclass
from typing import Protocol

from conversations.schemas import ConversationCreateRequest, MessageAppendRequest
from conversations.service import ConversationService
from context.builder import ContextBuilder
from context.schemas import (
    ContextBuildInput,
    ContextMode,
    ConversationMessage,
    ConversationSummary,
    SenderType,
    UserProfileSnapshot,
)
from agents.catalog import DEFAULT_TARGET_AGENT_ID, default_agent_snapshots, ensure_agent_id, user_agent_snapshots
from interactions.schemas import IdleTickRequest, IdleUserMessageRequest, InteractionUserMessageRequest
from model_runtime.errors import ModelRuntimeError
from model_runtime.schemas import ModelGenerateRequest, ModelGenerateResponse, RuntimeMessage
from workers.derived_jobs import DerivedJobCreateRequest, DerivedJobService


class ModelRuntimeProtocol(Protocol):
    def generate(self, request: ModelGenerateRequest) -> ModelGenerateResponse: ...


class UserServiceProtocol(Protocol):
    def get_user(self, user_id: str) -> dict: ...


@dataclass(frozen=True)
class _ContextWindow:
    recent_messages: list[ConversationMessage]
    summary: ConversationSummary | None
    speaker_names: dict[str, str]
    user_name: str


class InteractionService:
    """Product orchestration for user and idle model interactions."""

    def __init__(
        self,
        conversation_service: ConversationService,
        context_builder: ContextBuilder,
        model_runtime: ModelRuntimeProtocol,
        derived_jobs: DerivedJobService | None = None,
        user_service: UserServiceProtocol | None = None,
    ):
        self.conversation_service = conversation_service
        self.context_builder = context_builder
        self.model_runtime = model_runtime
        self.derived_jobs = derived_jobs
        self.user_service = user_service

    def run_idle_tick(self, user_id: str, conversation_id: str, payload: IdleTickRequest) -> dict:
        conversation = self.conversation_service.get_conversation(user_id, conversation_id)
        context_window = self._context_window(user_id, conversation_id)
        target_agent_id = self._next_idle_agent_id(context_window.recent_messages, payload.target_agent_id)
        package = self.context_builder.build(
            ContextBuildInput(
                mode=ContextMode.IDLE,
                conversation_id=conversation_id,
                target_agent_id=target_agent_id,
                agents=self._agent_snapshots(user_id),
                recent_messages=context_window.recent_messages,
                summary=context_window.summary,
                user_profile=self._user_profile(user_id),
                user_direction=self._idle_direction(conversation, payload.discussion_direction),
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
        self._enqueue_derived_work(user_id, conversation_id, [agent_message["id"]], conversation["mode"])
        updated_conversation = self.conversation_service.get_conversation(user_id, conversation_id)
        return self._response(updated_conversation, None, agent_message, package, model_response)

    def run_idle_user_message(
        self,
        user_id: str,
        conversation_id: str,
        payload: IdleUserMessageRequest,
    ) -> dict:
        conversation = self.conversation_service.get_conversation(user_id, conversation_id)
        if conversation["mode"] != "idle":
            from fastapi import HTTPException, status

            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="conversation_must_be_idle",
            )
        context_window = self._context_window(user_id, conversation_id)
        context_messages = [
            *context_window.recent_messages,
            ConversationMessage(
                sender_type=SenderType.USER,
                sender_id=user_id,
                sender_name=context_window.user_name,
                content=payload.content,
                metadata={**payload.metadata, "source": "idle_say"},
            ),
        ]
        target_agent_id = self._next_idle_agent_id(context_window.recent_messages, None)
        package = self.context_builder.build(
            ContextBuildInput(
                mode=ContextMode.IDLE,
                conversation_id=conversation_id,
                target_agent_id=target_agent_id,
                agents=self._agent_snapshots(user_id),
                recent_messages=context_messages,
                summary=context_window.summary,
                user_profile=self._user_profile(user_id),
                user_direction=self._idle_direction(conversation, payload.discussion_direction),
                idle_seed="用户刚刚自然插入了 idle 对话。请接住用户的话，再把两位 Agent 的讨论继续推进。",
                token_budget=6000,
            )
        )
        model_response = self._generate(package)
        user_message = self.conversation_service.append_message(
            user_id,
            conversation_id,
            MessageAppendRequest(
                sender_type="user",
                sender_id=user_id,
                role="user",
                content=payload.content,
                metadata={**payload.metadata, "source": "idle_say"},
            ),
        )
        agent_message = self._save_agent_message(
            user_id,
            conversation_id,
            target_agent_id,
            model_response,
            package,
            extra_metadata=None,
        )
        self._enqueue_derived_work(
            user_id,
            conversation_id,
            [user_message["id"], agent_message["id"]],
            conversation["mode"],
        )
        updated_conversation = self.conversation_service.get_conversation(user_id, conversation_id)
        return self._response(updated_conversation, user_message, agent_message, package, model_response)

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
        idle_window = self._context_window(user_id, idle_conversation_id)
        target_agent_id = ensure_agent_id(payload.target_agent_id)
        package = self.context_builder.build(
            ContextBuildInput(
                mode=ContextMode.COMPANION_1,
                conversation_id=companion["id"],
                target_agent_id=target_agent_id,
                agents=self._agent_snapshots(user_id),
                user_message=payload.content,
                idle_recent_messages=idle_window.recent_messages,
                idle_summary=idle_window.summary,
                user_profile=self._user_profile(user_id),
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
        self._enqueue_derived_work(
            user_id,
            companion["id"],
            [user_message["id"], agent_message["id"]],
            companion["mode"],
        )
        updated_companion = self.conversation_service.get_conversation(user_id, companion["id"])
        return self._response(updated_companion, user_message, agent_message, package, model_response)

    def run_companion_message(
        self,
        user_id: str,
        conversation_id: str,
        payload: InteractionUserMessageRequest,
    ) -> dict:
        conversation = self.conversation_service.get_conversation(user_id, conversation_id)
        if conversation["mode"] == "companion_1":
            return self._run_companion_1_message(user_id, conversation, payload)
        if conversation["mode"] == "companion_2":
            return self.run_companion_2_message(user_id, conversation_id, payload)
        from fastapi import HTTPException, status

        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail="conversation_must_be_companion",
        )

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
        context_window = self._context_window(user_id, conversation_id)
        target_agent_id = ensure_agent_id(payload.target_agent_id)
        package = self.context_builder.build(
            ContextBuildInput(
                mode=ContextMode.COMPANION_2,
                conversation_id=conversation_id,
                target_agent_id=target_agent_id,
                agents=self._agent_snapshots(user_id),
                user_message=payload.content,
                recent_messages=context_window.recent_messages,
                summary=context_window.summary,
                user_profile=self._user_profile(user_id),
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
        self._enqueue_derived_work(
            user_id,
            conversation_id,
            [user_message["id"], agent_message["id"]],
            conversation["mode"],
        )
        updated_conversation = self.conversation_service.get_conversation(user_id, conversation_id)
        return self._response(updated_conversation, user_message, agent_message, package, model_response)

    def _run_companion_1_message(
        self,
        user_id: str,
        conversation: dict,
        payload: InteractionUserMessageRequest,
    ) -> dict:
        conversation_id = conversation["id"]
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
        context_window = self._context_window(user_id, conversation_id)
        idle_window = _ContextWindow(
            recent_messages=[],
            summary=None,
            speaker_names={},
            user_name=self._user_name(user_id),
        )
        parent_id = conversation.get("parentConversationId")
        if parent_id:
            idle_window = self._context_window(user_id, parent_id)
        target_agent_id = ensure_agent_id(payload.target_agent_id)
        package = self.context_builder.build(
            ContextBuildInput(
                mode=ContextMode.COMPANION_1,
                conversation_id=conversation_id,
                target_agent_id=target_agent_id,
                agents=self._agent_snapshots(user_id),
                user_message=payload.content,
                recent_messages=context_window.recent_messages,
                summary=context_window.summary,
                idle_recent_messages=idle_window.recent_messages,
                idle_summary=idle_window.summary,
                user_profile=self._user_profile(user_id),
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
            extra_metadata={"parentIdleConversationId": parent_id} if parent_id else None,
        )
        self._enqueue_derived_work(
            user_id,
            conversation_id,
            [user_message["id"], agent_message["id"]],
            conversation["mode"],
        )
        updated_conversation = self.conversation_service.get_conversation(user_id, conversation_id)
        return self._response(updated_conversation, user_message, agent_message, package, model_response)

    def run_work_message(
        self,
        user_id: str,
        conversation_id: str,
        payload: InteractionUserMessageRequest,
        task_state: dict,
    ) -> dict:
        conversation = self.conversation_service.get_conversation(user_id, conversation_id)
        if conversation["mode"] != "work":
            from fastapi import HTTPException, status

            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail="conversation_must_be_work",
            )
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
        context_window = self._context_window(user_id, conversation_id)
        target_agent_id = ensure_agent_id(payload.target_agent_id)
        package = self.context_builder.build(
            ContextBuildInput(
                mode=ContextMode.WORK,
                conversation_id=conversation_id,
                target_agent_id=target_agent_id,
                agents=self._agent_snapshots(user_id),
                user_message=payload.content,
                recent_messages=context_window.recent_messages,
                summary=context_window.summary,
                user_profile=self._user_profile(user_id),
                task_state=task_state,
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
            extra_metadata={"taskId": task_state.get("task_id")},
        )
        self._enqueue_derived_work(
            user_id,
            conversation_id,
            [user_message["id"], agent_message["id"]],
            conversation["mode"],
        )
        updated_conversation = self.conversation_service.get_conversation(user_id, conversation_id)
        return self._response(updated_conversation, user_message, agent_message, package, model_response)

    def _recent_context_messages(self, user_id: str, conversation_id: str) -> list[ConversationMessage]:
        return self._context_window(user_id, conversation_id).recent_messages

    def _context_window(self, user_id: str, conversation_id: str) -> "_ContextWindow":
        conversation = self.conversation_service.get_conversation(user_id, conversation_id)
        message_count = conversation.get("messageCount") or 0
        after_sequence = max(message_count - 20, 0)
        page = self.conversation_service.list_messages(
            user_id,
            conversation_id,
            after_sequence=after_sequence,
            created_after=None,
            created_before=None,
            limit=20,
        )
        speaker_names = self._agent_names(user_id)
        user_name = self._user_name(user_id)
        recent = [_context_message(row, speaker_names, user_name) for row in page["messages"]]
        return _ContextWindow(
            recent_messages=recent,
            summary=self._compact_summary(user_id, conversation_id, after_sequence, speaker_names, user_name),
            speaker_names=speaker_names,
            user_name=user_name,
        )

    def _compact_summary(
        self,
        user_id: str,
        conversation_id: str,
        before_or_at_sequence: int,
        speaker_names: dict[str, str],
        user_name: str,
    ) -> ConversationSummary | None:
        if before_or_at_sequence <= 0:
            return None
        page = self.conversation_service.list_messages(
            user_id,
            conversation_id,
            after_sequence=0,
            created_after=None,
            created_before=None,
            limit=min(before_or_at_sequence, 100),
        )
        older_rows = [row for row in page["messages"] if row["sequence"] <= before_or_at_sequence]
        if not older_rows:
            return None
        selected_rows = older_rows[:4]
        if len(older_rows) > 8:
            selected_rows = older_rows[:4] + older_rows[-4:]
        lines = [f"{len(older_rows)} older messages compacted."]
        for row in selected_rows:
            lines.append(f"- {_speaker_name(row, speaker_names, user_name) or row.get('senderType')}: {row['content']}")
        return ConversationSummary(
            id=f"compact-{conversation_id}-{before_or_at_sequence}",
            summary_type="compact_context",
            content="\n".join(lines),
        )

    def _user_profile(self, user_id: str) -> UserProfileSnapshot | None:
        if self.user_service is None:
            return None
        user = self.user_service.get_user(user_id)
        return UserProfileSnapshot(
            id=user["id"],
            username=user.get("username"),
            display_name=user.get("displayName"),
            language_preference=user.get("languagePreference") or "zh",
            personality=user.get("personality") or None,
            story=user.get("story") or None,
        )

    def _agent_snapshots(self, user_id: str):
        if self.user_service is None:
            return default_agent_snapshots()
        user = self.user_service.get_user(user_id)
        return user_agent_snapshots(user.get("agentProfiles"))

    def _agent_names(self, user_id: str) -> dict[str, str]:
        return {agent.id: agent.name for agent in self._agent_snapshots(user_id)}

    def _user_name(self, user_id: str) -> str:
        if self.user_service is None:
            return "User"
        user = self.user_service.get_user(user_id)
        return user.get("displayName") or user.get("username") or "User"

    def _generate(self, package) -> ModelGenerateResponse:
        try:
            return self.model_runtime.generate(
                ModelGenerateRequest(
                    messages=[RuntimeMessage(role=message.role, content=message.content) for message in package.messages],
                    max_output_tokens=360,
                    temperature=0.4,
                )
            )
        except ModelRuntimeError as exc:
            from fastapi import HTTPException, status

            if exc.http_status == status.HTTP_429_TOO_MANY_REQUESTS:
                raise HTTPException(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    detail="model_rate_limited",
                ) from exc
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="model_unavailable",
            ) from exc

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

    def _next_idle_agent_id(
        self,
        recent_messages: list[ConversationMessage],
        requested_agent_id: str | None,
    ) -> str:
        for message in reversed(recent_messages):
            if message.sender_type != SenderType.AGENT:
                continue
            if message.sender_id == "agent_1":
                return "agent_2"
            if message.sender_id == "agent_2":
                return "agent_1"
        return ensure_agent_id(requested_agent_id) if requested_agent_id else DEFAULT_TARGET_AGENT_ID

    def _idle_direction(self, conversation: dict, request_direction: str | None) -> str | None:
        if request_direction and request_direction.strip():
            return request_direction
        metadata = conversation.get("metadata") or {}
        return metadata.get("topicDirection") or metadata.get("discussionDirection")

    def _enqueue_derived_work(
        self,
        user_id: str,
        conversation_id: str,
        source_message_ids: list[str],
        mode: str,
    ) -> None:
        if self.derived_jobs is None:
            return
        for job_type in _derived_job_types_for_mode(mode):
            try:
                self.derived_jobs.enqueue(
                    DerivedJobCreateRequest(
                        job_type=job_type,
                        user_id=user_id,
                        conversation_id=conversation_id,
                        source_message_ids=source_message_ids,
                        metadata={"mode": mode},
                    )
                )
            except Exception:
                continue

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


def _context_message(
    row: dict,
    speaker_names: dict[str, str] | None = None,
    user_name: str | None = None,
) -> ConversationMessage:
    sender_slot = row.get("senderSlot")
    return ConversationMessage(
        id=row["id"],
        sender_type=SenderType(row["senderType"]),
        sender_id=row.get("senderId") or sender_slot,
        sender_name=_speaker_name(row, speaker_names, user_name),
        content=row["content"],
        metadata=row.get("metadata", {}),
    )


def _speaker_name(
    row: dict,
    speaker_names: dict[str, str] | None = None,
    user_name: str | None = None,
) -> str | None:
    sender_type = row.get("senderType")
    if sender_type == "user":
        return user_name or "User"
    if sender_type == "system":
        return "System"
    if sender_type == "tool":
        return "Tool"
    sender_slot = row.get("senderSlot")
    if speaker_names and sender_slot in speaker_names:
        return speaker_names[sender_slot]
    if sender_slot == "agent_1":
        return "Nora"
    if sender_slot == "agent_2":
        return "Vale"
    return row.get("senderId") or sender_slot


def _agent_slot(agent_id: str) -> str:
    if agent_id == "agent_2":
        return "agent_2"
    return "agent_1"


def _derived_job_types_for_mode(mode: str) -> list[str]:
    if mode == "idle":
        return ["summary", "relationship", "diary"]
    if mode in {"companion_1", "companion_2"}:
        return ["summary", "memory_candidate"]
    if mode == "work":
        return ["summary"]
    return []
