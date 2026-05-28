"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-27
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
    MemoryCardSnapshot,
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

    def test_idle_context_separates_user_profile_and_direction_from_transcript(self) -> None:
        package = self.builder.build(
            ContextBuildInput(
                mode=ContextMode.IDLE,
                conversation_id="conv_idle",
                target_agent_id="agent_a",
                agents=[self.agent_a, self.agent_b],
                user_profile=UserProfileSnapshot(
                    id="user_1",
                    username="demo_user",
                    display_name="Demo",
                    language_preference="zh",
                    personality="quiet, direct, product-minded",
                    story="I am preparing a 30 second demo.",
                ),
                user_direction="希望从产品演示怎么讲清楚这个方向展开",
                recent_messages=[
                    ConversationMessage(
                        id="msg_1",
                        sender_type=SenderType.AGENT,
                        sender_id="agent_b",
                        sender_name="Beryl",
                        content="我们刚才在讨论用户预期。",
                    )
                ],
            )
        )

        prompt = _prompt_text(package)
        self.assertIn("User profile:", prompt)
        self.assertIn("personality: quiet, direct, product-minded", prompt)
        self.assertIn("story: I am preparing a 30 second demo.", prompt)
        self.assertIn("Current idle topic selected by user:", prompt)
        self.assertIn("希望从产品演示怎么讲清楚这个方向展开", prompt)
        self.assertIn("- Beryl: 我们刚才在讨论用户预期。", prompt)
        self.assertLess(
            prompt.index("Current idle topic selected by user:"),
            prompt.index("Recent idle transcript:"),
        )
        self.assertIn("If recent transcript drifts, use the selected topic", prompt)
        self.assertNotIn("- Demo: 希望从产品演示怎么讲清楚这个方向展开", prompt)

    def test_idle_context_keeps_user_and_other_agent_speaker_boundaries(self) -> None:
        package = self.builder.build(
            ContextBuildInput(
                mode=ContextMode.IDLE,
                conversation_id="conv_idle",
                target_agent_id="agent_a",
                agents=[self.agent_a, self.agent_b],
                user_direction="只讨论演示开场，不要回到技术细节",
                recent_messages=[
                    ConversationMessage(
                        id="msg_user",
                        sender_type=SenderType.USER,
                        sender_id="user_1",
                        sender_name="Demo",
                        content="希望从用户视角讲。",
                    ),
                    ConversationMessage(
                        id="msg_agent",
                        sender_type=SenderType.AGENT,
                        sender_id="agent_b",
                        sender_name="Beryl",
                        content="那就先讲 30 秒路径。",
                    ),
                ],
            )
        )

        prompt = _prompt_text(package)
        self.assertIn("- Demo: 希望从用户视角讲。", prompt)
        self.assertIn("- Beryl: 那就先讲 30 秒路径。", prompt)
        self.assertIn("The other Agent is not the User.", prompt)
        self.assertIn("Speaker labels in Recent idle transcript are authoritative", prompt)

    def test_idle_context_uses_relationship_stance_and_turn_intent(self) -> None:
        package = self.builder.build(
            ContextBuildInput(
                mode=ContextMode.IDLE,
                conversation_id="conv_idle",
                target_agent_id="agent_a",
                agents=[self.agent_a, self.agent_b],
                recent_messages=[
                    ConversationMessage(
                        id="msg_agent",
                        sender_type=SenderType.AGENT,
                        sender_id="agent_b",
                        sender_name="Beryl",
                        content="这听起来又像在给人生做表格。",
                    ),
                ],
            )
        )

        prompt = _prompt_text(package)
        self.assertIn("Relationship stance:", prompt)
        self.assertIn("Turn intent:", prompt)
        self.assertIn("Respond to the previous Agent's concrete line", prompt)
        self.assertIn("Make one conversational move", prompt)
        self.assertIn("Do not output stacked frameworks, numbered exercises, or coaching checklists", prompt)

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

    def test_companion_1_context_includes_child_conversation_recent_messages(self) -> None:
        package = self.builder.build(
            ContextBuildInput(
                mode=ContextMode.COMPANION_1,
                conversation_id="conv_join",
                target_agent_id="agent_a",
                agents=[self.agent_a, self.agent_b],
                user_message="继续说。",
                recent_messages=[
                    ConversationMessage(
                        id="child_1",
                        sender_type=SenderType.USER,
                        sender_id="user_1",
                        sender_name="User",
                        content="我刚才已经加入了。",
                    ),
                    ConversationMessage(
                        id="child_2",
                        sender_type=SenderType.AGENT,
                        sender_id="agent_a",
                        sender_name="Aster",
                        content="我们正在把 idle 话题转向你。",
                    ),
                ],
                idle_recent_messages=[
                    ConversationMessage(
                        id="idle_1",
                        sender_type=SenderType.AGENT,
                        sender_id="agent_b",
                        sender_name="Beryl",
                        content="目标可以很轻。",
                    ),
                ],
            )
        )

        prompt = _prompt_text(package)
        self.assertIn("Current companion conversation recent messages", prompt)
        self.assertIn("我刚才已经加入了。", prompt)
        self.assertIn("我们正在把 idle 话题转向你。", prompt)
        self.assertIn("目标可以很轻。", prompt)
        self.assertIn("child_1", package.included_message_ids)
        self.assertIn("child_2", package.included_message_ids)
        self.assertIn("idle_1", package.included_message_ids)

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

    def test_companion_2_context_includes_requested_memory_cards(self) -> None:
        package = self.builder.build(
            ContextBuildInput(
                mode=ContextMode.COMPANION_2,
                conversation_id="conv_companion",
                target_agent_id="agent_b",
                agents=[self.agent_a, self.agent_b],
                user_message="你还记得我喜欢什么风格吗？",
                memory_cards=[
                    MemoryCardSnapshot(
                        id="memory_1",
                        scope="companion",
                        owner_type="user",
                        owner_id="user_1",
                        memory_type="preference",
                        summary="User prefers concise Chinese replies.",
                        source_message_ids=["chat_1"],
                        importance_score=0.8,
                        confidence=0.9,
                    )
                ],
            )
        )

        prompt = _prompt_text(package)
        self.assertIn("Relevant memory", prompt)
        self.assertIn("User prefers concise Chinese replies.", prompt)
        self.assertIn("memory_1", package.included_memory_ids)

    def test_idle_context_does_not_include_companion_memory_by_default(self) -> None:
        package = self.builder.build(
            ContextBuildInput(
                mode=ContextMode.IDLE,
                conversation_id="conv_idle",
                target_agent_id="agent_a",
                agents=[self.agent_a, self.agent_b],
                memory_cards=[
                    MemoryCardSnapshot(
                        id="memory_hidden",
                        scope="companion",
                        owner_type="user",
                        owner_id="user_1",
                        memory_type="preference",
                        summary="This companion preference should stay out of idle.",
                        source_message_ids=["chat_1"],
                        importance_score=0.8,
                        confidence=0.9,
                    )
                ],
            )
        )

        prompt = _prompt_text(package)
        self.assertNotIn("This companion preference should stay out of idle.", prompt)
        self.assertNotIn("memory_hidden", package.included_memory_ids)

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
