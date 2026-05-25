"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Last Modified by: Codex
"""

from conversations.repository import ConversationRepository
from conversations.schemas import ConversationCreateRequest, MessageAppendRequest
from conversations.service import ConversationService
from context.builder import ContextBuilder
from context.schemas import AgentPersonaSnapshot, ContextBuildInput, ContextMode, ConversationMessage, SenderType
from core.database import close_mongo, connect_mongo, get_database
from model_runtime.client import OpenAICompatibleClient
from model_runtime.config_repository import ModelRuntimeConfigRepository
from model_runtime.orchestrator import ModelRuntime
from model_runtime.schemas import ModelGenerateRequest, RuntimeMessage


SMOKE_USER_ID = "local_idle_smoke_user"


def main() -> None:
    connect_mongo()
    try:
        service = ConversationService(ConversationRepository(get_database()))
        conversation = service.get_or_create_active_idle(SMOKE_USER_ID)
        service.append_message(
            SMOKE_USER_ID,
            conversation["id"],
            MessageAppendRequest(
                sender_type="agent",
                sender_slot="agent_1",
                role="assistant",
                content="如果我们一直 idle，目标感会不会反而破坏生活感？",
            ),
        )
        service.append_message(
            SMOKE_USER_ID,
            conversation["id"],
            MessageAppendRequest(
                sender_type="agent",
                sender_slot="agent_2",
                role="assistant",
                content="不会。目标可以很小，比如今天把一个想法讲清楚。",
            ),
        )
        page = service.list_messages(SMOKE_USER_ID, conversation["id"], after_sequence=0, limit=20)
        recent_messages = [_context_message(row) for row in page["messages"]]
        package = ContextBuilder().build(
            ContextBuildInput(
                mode=ContextMode.IDLE,
                conversation_id=conversation["id"],
                target_agent_id="agent_1",
                agents=_agents(),
                recent_messages=recent_messages,
                idle_seed="继续讨论 idle 生活是否需要目标，但保持轻松。",
                token_budget=6000,
            )
        )
        response = ModelRuntime(
            config_repository=ModelRuntimeConfigRepository(),
            client=OpenAICompatibleClient(),
        ).generate(
            ModelGenerateRequest(
                messages=[RuntimeMessage(role=message.role, content=message.content) for message in package.messages],
                max_output_tokens=300,
                temperature=0.4,
            )
        )
        saved = service.append_message(
            SMOKE_USER_ID,
            conversation["id"],
            MessageAppendRequest(
                sender_type="agent",
                sender_slot="agent_1",
                role="assistant",
                content=response.text,
                metadata={
                    "prompt_hash": package.prompt_hash,
                    "token_estimate": package.token_estimate,
                    "model_name": response.model_name,
                },
            ),
        )
        print("conversation_id:", conversation["id"])
        print("message_count_before_response:", len(page["messages"]))
        print("prompt_hash:", package.prompt_hash)
        print("token_estimate:", package.token_estimate)
        print("model:", response.model_name)
        print("saved_response_sequence:", saved["sequence"])
        print("response:")
        print(response.text)
    finally:
        close_mongo()


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
    return [
        AgentPersonaSnapshot(
            id="agent_1",
            name="Aster",
            core_persona="冷静、会追问概念的哲学型 Agent。",
            speaking_style="中文，短句，清楚。",
            episode_state="正在讨论 idle 生活是否需要目标。",
        ),
        AgentPersonaSnapshot(
            id="agent_2",
            name="Beryl",
            core_persona="务实、直接、擅长把想法变成计划的 Agent。",
            speaking_style="中文，简洁，偏行动。",
        ),
    ]


if __name__ == "__main__":
    main()
