"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Last Modified by: Codex
"""

from context.builder import ContextBuilder
from context.schemas import (
    AgentPersonaSnapshot,
    ContextBuildInput,
    ContextMode,
    ConversationMessage,
    ConversationSummary,
    SenderType,
)
from model_runtime.client import OpenAICompatibleClient
from model_runtime.config_repository import ModelRuntimeConfigRepository
from model_runtime.orchestrator import ModelRuntime
from model_runtime.schemas import ModelGenerateRequest, RuntimeMessage


def main() -> None:
    package = ContextBuilder().build(_companion_1_fixture())
    runtime = ModelRuntime(
        config_repository=ModelRuntimeConfigRepository(),
        client=OpenAICompatibleClient(),
    )
    response = runtime.generate(
        ModelGenerateRequest(
            messages=[RuntimeMessage(role=message.role, content=message.content) for message in package.messages],
            max_output_tokens=400,
            temperature=0.4,
        )
    )

    print("mode:", package.mode.value)
    print("prompt_hash:", package.prompt_hash)
    print("token_estimate:", package.token_estimate)
    print("model:", response.model_name)
    print("response:")
    print(response.text)


def _companion_1_fixture() -> ContextBuildInput:
    agents = [
        AgentPersonaSnapshot(
            id="agent_1",
            name="Aster",
            core_persona="冷静、会追问概念的哲学型 Agent。",
            speaking_style="中文，短句，清楚。",
            episode_state="刚才在认真讨论 idle 生活是否需要目标。",
        ),
        AgentPersonaSnapshot(
            id="agent_2",
            name="Beryl",
            core_persona="务实、直接、擅长把想法变成计划的 Agent。",
            speaking_style="中文，简洁，偏行动。",
        ),
    ]
    idle_messages = [
        ConversationMessage(
            id="idle_1",
            sender_type=SenderType.AGENT,
            sender_id="agent_1",
            sender_name="Aster",
            content="如果我们一直 idle，目标感会不会反而破坏生活感？",
        ),
        ConversationMessage(
            id="idle_2",
            sender_type=SenderType.AGENT,
            sender_id="agent_2",
            sender_name="Beryl",
            content="不会。目标可以很小，比如今天把一个想法讲清楚。",
        ),
    ]
    return ContextBuildInput(
        mode=ContextMode.COMPANION_1,
        conversation_id="local_companion_1",
        target_agent_id="agent_1",
        agents=agents,
        user_message="你们刚才在聊什么？我可以加入吗？",
        idle_recent_messages=idle_messages,
        idle_summary=ConversationSummary(
            id="summary_1",
            summary_type="idle_scene",
            content="两个 Agent 正在讨论 idle 生活是否需要目标，以及小目标是否会破坏生活感。",
        ),
        token_budget=6000,
    )


if __name__ == "__main__":
    main()
