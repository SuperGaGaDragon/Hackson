"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Last Modified by: Codex
"""

from unittest import TestCase

from context.builder import ContextBuilder
from context.schemas import (
    AgentPersonaSnapshot,
    ContextBuildInput,
    ContextMode,
    ConversationMessage,
    ConversationSummary,
    SenderType,
    UserProfileSnapshot,
)


class ContextBuilderTest(TestCase):
    def setUp(self) -> None:
        self.builder = ContextBuilder()
        self.agent_a = AgentPersonaSnapshot(
            id="agent_a",
            name="Aster",
            core_persona="A calm philosopher who asks precise questions.",
            speaking_style="short, thoughtful Chinese",
            episode_state="curious about daily rituals",
        )
        self.agent_b = AgentPersonaSnapshot(
            id="agent_b",
            name="Beryl",
            core_persona="A direct builder who turns ideas into practical plans.",
            speaking_style="concise and pragmatic",
        )

    def test_idle_context_preserves_agent_persona_without_mutation(self) -> None:
        original_persona = self.agent_a.core_persona
        package = self.builder.build(
            ContextBuildInput(
                mode=ContextMode.IDLE,
                conversation_id="conv_idle",
                target_agent_id="agent_a",
                agents=[self.agent_a, self.agent_b],
                recent_messages=[
                    ConversationMessage(
                        id="msg_1",
                        sender_type=SenderType.AGENT,
                        sender_id="agent_b",
                        sender_name="Beryl",
                        content="今天要不要继续讨论目标感？",
                    )
                ],
                idle_seed="讨论今天要做什么",
            )
        )

        prompt = _prompt_text(package)
        self.assertIn("Current mode: idle", prompt)
        self.assertIn("core_persona: A calm philosopher", prompt)
        self.assertIn("Beryl", prompt)
        self.assertIn("讨论今天要做什么", prompt)
        self.assertEqual(self.agent_a.core_persona, original_persona)
        self.assertIn("agent_a", package.included_agent_ids)
        self.assertIn("msg_1", package.included_message_ids)

    def test_companion_1_context_forces_transition_to_user(self) -> None:
        package = self.builder.build(
            ContextBuildInput(
                mode=ContextMode.COMPANION_1,
                conversation_id="conv_join",
                target_agent_id="agent_a",
                agents=[self.agent_a, self.agent_b],
                user_message="你们刚才在讨论什么？",
                idle_recent_messages=[
                    ConversationMessage(
                        id="idle_1",
                        sender_type=SenderType.AGENT,
                        sender_id="agent_a",
                        sender_name="Aster",
                        content="我觉得目标感会改变 idle 的意义。",
                    ),
                    ConversationMessage(
                        id="idle_2",
                        sender_type=SenderType.AGENT,
                        sender_id="agent_b",
                        sender_name="Beryl",
                        content="那就把目标拆成今天能做的动作。",
                    ),
                ],
                idle_summary=ConversationSummary(
                    id="summary_1",
                    summary_type="idle_scene",
                    content="两个 Agent 正在讨论 idle 生活是否需要目标。",
                ),
                task_state={"objective": "must not appear in companion prompt"},
            )
        )

        prompt = _prompt_text(package)
        self.assertIn("Current mode: companion_1 user joined idle", prompt)
        self.assertIn("用户刚刚加入", prompt)
        self.assertIn("你们刚才在讨论什么？", prompt)
        self.assertIn("必须把注意力转向用户", prompt)
        self.assertIn("idle 生活是否需要目标", prompt)
        self.assertNotIn("must not appear", prompt)
        self.assertIn("transition_context=enabled", package.debug_notes)
        self.assertIn("summary_1", package.included_summary_ids)

    def test_companion_2_context_does_not_auto_include_idle_history(self) -> None:
        package = self.builder.build(
            ContextBuildInput(
                mode=ContextMode.COMPANION_2,
                conversation_id="conv_companion",
                target_agent_id="agent_b",
                agents=[self.agent_a, self.agent_b],
                user_message="帮我想一个 demo 开场。",
                user_profile=UserProfileSnapshot(
                    id="user_1",
                    username="demo_user",
                    display_name="Demo",
                    language_preference="zh",
                ),
                recent_messages=[
                    ConversationMessage(
                        id="chat_1",
                        sender_type=SenderType.USER,
                        sender_id="user_1",
                        sender_name="Demo",
                        content="我们先做实用版本。",
                    )
                ],
                idle_recent_messages=[
                    ConversationMessage(
                        id="idle_hidden",
                        sender_type=SenderType.AGENT,
                        sender_id="agent_a",
                        sender_name="Aster",
                        content="这段 idle 历史不应该自动出现。",
                    )
                ],
            )
        )

        prompt = _prompt_text(package)
        self.assertIn("Current mode: companion_2 fresh companion chat", prompt)
        self.assertIn("帮我想一个 demo 开场", prompt)
        self.assertIn("我们先做实用版本", prompt)
        self.assertIn("language_preference: zh", prompt)
        self.assertNotIn("这段 idle 历史不应该自动出现", prompt)
        self.assertNotIn("idle_hidden", package.included_message_ids)

    def test_builder_rejects_missing_target_agent(self) -> None:
        with self.assertRaisesRegex(ValueError, "target_agent_not_found"):
            self.builder.build(
                ContextBuildInput(
                    mode=ContextMode.IDLE,
                    conversation_id="conv_idle",
                    target_agent_id="missing",
                    agents=[self.agent_a, self.agent_b],
                )
            )


def _prompt_text(package) -> str:
    return "\n\n".join(message.content for message in package.messages)

