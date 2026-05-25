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
from context.schemas import (
    AgentPersonaSnapshot,
    ContextBuildInput,
    ContextMode,
    ConversationMessage,
    SenderType,
    UserProfileSnapshot,
)
from core.database import close_mongo, connect_mongo, get_database
from model_runtime.client import OpenAICompatibleClient
from model_runtime.config_repository import ModelRuntimeConfigRepository
from model_runtime.orchestrator import ModelRuntime
from model_runtime.schemas import ModelGenerateRequest, RuntimeMessage


SMOKE_USER_ID = "local_companion2_smoke_user"


def main() -> None:
    connect_mongo()
    try:
        service = ConversationService(ConversationRepository(get_database()))
        conversation = service.create_conversation(
            SMOKE_USER_ID,
            ConversationCreateRequest(
                mode="companion_2",
                title="Companion 2 Smoke",
                metadata={"created_by": "run_companion2_full_smoke"},
            ),
        )
        service.append_message(
            SMOKE_USER_ID,
            conversation["id"],
            MessageAppendRequest(
                sender_type="user",
                sender_id=SMOKE_USER_ID,
                role="user",
                content="我们先做实用版本，不要科研化。",
            ),
        )
        user_message = service.append_message(
            SMOKE_USER_ID,
            conversation["id"],
            MessageAppendRequest(
                sender_type="user",
                sender_id=SMOKE_USER_ID,
                role="user",
                content="帮我用一句话解释 Hackson 的 V1 目标。",
            ),
        )
        page = service.list_messages(SMOKE_USER_ID, conversation["id"], after_sequence=0, limit=20)
        recent = [_context_message(row) for row in page["messages"]]
        package = ContextBuilder().build(
            ContextBuildInput(
                mode=ContextMode.COMPANION_2,
                conversation_id=conversation["id"],
                target_agent_id="agent_2",
                agents=_agents(),
                user_message=user_message["content"],
                recent_messages=recent,
                user_profile=UserProfileSnapshot(
                    id=SMOKE_USER_ID,
                    username="companion2_smoke",
                    display_name="Smoke User",
                    language_preference="zh",
                ),
                idle_recent_messages=[
                    ConversationMessage(
                        id="idle_should_not_appear",
                        sender_type=SenderType.AGENT,
                        sender_id="agent_1",
                        sender_name="Aster",
                        content="这段 idle 历史不应该进入 companion_2 默认上下文。",
                    )
                ],
                token_budget=6000,
            )
        )
        response = _runtime().generate(_model_request(package))
        saved = service.append_message(
            SMOKE_USER_ID,
            conversation["id"],
            MessageAppendRequest(
                sender_type="agent",
                sender_slot="agent_2",
                role="assistant",
                content=response.text,
                metadata={
                    "prompt_hash": package.prompt_hash,
                    "token_estimate": package.token_estimate,
                    "model_name": response.model_name,
                },
            ),
        )
        print("mode:", package.mode.value)
        print("conversation_id:", conversation["id"])
        print("message_count_before_response:", len(page["messages"]))
        print("prompt_hash:", package.prompt_hash)
        print("token_estimate:", package.token_estimate)
        print("included_messages:", ",".join(package.included_message_ids))
        print("model:", response.model_name)
        print("saved_response_sequence:", saved["sequence"])
        print("response:")
        print(response.text)
    finally:
        close_mongo()


def _runtime() -> ModelRuntime:
    return ModelRuntime(
        config_repository=ModelRuntimeConfigRepository(),
        client=OpenAICompatibleClient(),
    )


def _model_request(package) -> ModelGenerateRequest:
    return ModelGenerateRequest(
        messages=[RuntimeMessage(role=message.role, content=message.content) for message in package.messages],
        max_output_tokens=220,
        temperature=0.3,
    )


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


def _agents() -> list[AgentPersonaSnapshot]:
    return [
        AgentPersonaSnapshot(
            id="agent_1",
            name="Aster",
            core_persona="冷静、会追问概念的哲学型 Agent。",
            speaking_style="中文，短句，清楚。",
        ),
        AgentPersonaSnapshot(
            id="agent_2",
            name="Beryl",
            core_persona="务实、直接、擅长把想法变成计划的 Agent。",
            speaking_style="中文，简洁，偏行动。",
            episode_state="正在帮助用户收束 V1 demo。",
        ),
    ]


if __name__ == "__main__":
    main()
