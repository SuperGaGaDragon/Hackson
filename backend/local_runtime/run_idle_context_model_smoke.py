"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Last Modified by: Codex
"""

from agents.catalog import default_agent_snapshots
from context.builder import ContextBuilder
from context.schemas import ContextBuildInput, ContextMode, ConversationMessage, SenderType
from model_runtime.client import OpenAICompatibleClient
from model_runtime.config_repository import ModelRuntimeConfigRepository
from model_runtime.orchestrator import ModelRuntime
from model_runtime.schemas import ModelGenerateRequest, RuntimeMessage


def main() -> None:
    package = ContextBuilder().build(_idle_fixture())
    response = ModelRuntime(
        config_repository=ModelRuntimeConfigRepository(),
        client=OpenAICompatibleClient(),
    ).generate(
        ModelGenerateRequest(
            messages=[RuntimeMessage(role=message.role, content=message.content) for message in package.messages],
            max_output_tokens=240,
        )
    )
    print("mode:", package.mode.value)
    print("prompt_hash:", package.prompt_hash)
    print("token_estimate:", package.token_estimate)
    print("included_messages:", ",".join(package.included_message_ids))
    print("model:", response.model_name)
    print("response:")
    print(response.text)


def _idle_fixture() -> ContextBuildInput:
    agents = default_agent_snapshots()
    messages = [
        ConversationMessage(
            id="idle_1",
            sender_type=SenderType.AGENT,
            sender_id="agent_2",
            sender_name="Vale",
            content="今天如果只做一件事，我会选把上下文链路跑通。",
        ),
        ConversationMessage(
            id="idle_2",
            sender_type=SenderType.AGENT,
            sender_id="agent_1",
            sender_name="Nora",
            content="跑通以后，我们就能知道这个世界是不是只是在说话，还是能持续记住自己。",
        ),
    ]
    return ContextBuildInput(
        mode=ContextMode.IDLE,
        conversation_id="local_idle",
        target_agent_id="agent_2",
        agents=agents,
        recent_messages=messages,
        idle_seed="继续 idle 对话，但只说一小段，保持生活感。",
        token_budget=6000,
    )


if __name__ == "__main__":
    main()
