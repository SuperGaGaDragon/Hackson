"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Last Modified by: Codex
"""

from conversations.repository import ConversationRepository
from conversations.schemas import ConversationCreateRequest, MessageAppendRequest
from conversations.service import ConversationService
from agents.catalog import default_agent_snapshots
from context.builder import ContextBuilder
from context.schemas import (
    AgentPersonaSnapshot,
    ContextBuildInput,
    ContextMode,
    ConversationMessage,
    ConversationSummary,
    SenderType,
)
from core.database import close_mongo, connect_mongo, get_database
from model_runtime.client import OpenAICompatibleClient
from model_runtime.config_repository import ModelRuntimeConfigRepository
from model_runtime.orchestrator import ModelRuntime
from model_runtime.schemas import ModelGenerateRequest, RuntimeMessage


SMOKE_USER_ID = "local_companion1_smoke_user"


def main() -> None:
    connect_mongo()
    try:
        service = ConversationService(ConversationRepository(get_database()))
        idle_conversation = service.get_or_create_active_idle(SMOKE_USER_ID)
        _seed_idle(service, idle_conversation["id"])
        companion = service.create_conversation(
            SMOKE_USER_ID,
            ConversationCreateRequest(
                mode="companion_1",
                title="Companion 1 Smoke",
                parent_conversation_id=idle_conversation["id"],
                metadata={"created_by": "run_companion1_full_smoke"},
            ),
        )
        user_message = service.append_message(
            SMOKE_USER_ID,
            companion["id"],
            MessageAppendRequest(
                sender_type="user",
                sender_id=SMOKE_USER_ID,
                role="user",
                content="你们刚才在聊什么？我可以加入吗？",
            ),
        )
        idle_page = service.list_messages(SMOKE_USER_ID, idle_conversation["id"], after_sequence=0, limit=20)
        idle_recent = [_context_message(row) for row in idle_page["messages"]]
        package = ContextBuilder().build(
            ContextBuildInput(
                mode=ContextMode.COMPANION_1,
                conversation_id=companion["id"],
                target_agent_id="agent_1",
                agents=_agents(),
                user_message=user_message["content"],
                idle_recent_messages=idle_recent,
                idle_summary=ConversationSummary(
                    id="local_companion1_summary",
                    summary_type="idle_scene",
                    content="两个 Agent 正在讨论 idle 生活是否需要目标，以及小目标是否会破坏生活感。",
                ),
                token_budget=6000,
            )
        )
        response = _runtime().generate(_model_request(package))
        saved = service.append_message(
            SMOKE_USER_ID,
            companion["id"],
            MessageAppendRequest(
                sender_type="agent",
                sender_slot="agent_1",
                role="assistant",
                content=response.text,
                metadata={
                    "prompt_hash": package.prompt_hash,
                    "token_estimate": package.token_estimate,
                    "model_name": response.model_name,
                    "source_idle_conversation_id": idle_conversation["id"],
                },
            ),
        )
        print("mode:", package.mode.value)
        print("idle_conversation_id:", idle_conversation["id"])
        print("companion_conversation_id:", companion["id"])
        print("idle_message_count:", len(idle_page["messages"]))
        print("prompt_hash:", package.prompt_hash)
        print("token_estimate:", package.token_estimate)
        print("model:", response.model_name)
        print("saved_response_sequence:", saved["sequence"])
        print("response:")
        print(response.text)
    finally:
        close_mongo()


def _seed_idle(service: ConversationService, conversation_id: str) -> None:
    service.append_message(
        SMOKE_USER_ID,
        conversation_id,
        MessageAppendRequest(
            sender_type="agent",
            sender_slot="agent_1",
            role="assistant",
            content="如果我们一直 idle，目标感会不会反而破坏生活感？",
        ),
    )
    service.append_message(
        SMOKE_USER_ID,
        conversation_id,
        MessageAppendRequest(
            sender_type="agent",
            sender_slot="agent_2",
            role="assistant",
            content="不会。目标可以很小，比如今天把一个想法讲清楚。",
        ),
    )


def _runtime() -> ModelRuntime:
    return ModelRuntime(
        config_repository=ModelRuntimeConfigRepository(),
        client=OpenAICompatibleClient(),
    )


def _model_request(package) -> ModelGenerateRequest:
    return ModelGenerateRequest(
        messages=[RuntimeMessage(role=message.role, content=message.content) for message in package.messages],
        max_output_tokens=360,
        temperature=0.4,
    )


def _context_message(row: dict) -> ConversationMessage:
    sender_slot = row.get("senderSlot")
    return ConversationMessage(
        id=row["id"],
        sender_type=SenderType(row["senderType"]),
        sender_id=row.get("senderId") or sender_slot,
        sender_name=sender_slot,
        content=row["content"],
        metadata=row.get("metadata", {}),
    )


def _agents() -> list[AgentPersonaSnapshot]:
    return default_agent_snapshots()


if __name__ == "__main__":
    main()
