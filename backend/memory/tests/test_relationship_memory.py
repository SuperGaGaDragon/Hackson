"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Last Modified by: Codex
"""

from unittest import TestCase

from context.builder import ContextBuilder
from context.schemas import AgentPersonaSnapshot, ContextBuildInput, ContextMode, MemoryCardSnapshot


class RelationshipMemoryContextTest(TestCase):
    def test_idle_context_can_include_idle_relationship_memory(self) -> None:
        builder = ContextBuilder()
        package = builder.build(
            ContextBuildInput(
                mode=ContextMode.IDLE,
                conversation_id="idle_1",
                target_agent_id="agent_1",
                agents=[
                    AgentPersonaSnapshot(id="agent_1", name="Nora", core_persona="Curious companion."),
                    AgentPersonaSnapshot(id="agent_2", name="Vale", core_persona="Practical companion."),
                ],
                memory_cards=[
                    MemoryCardSnapshot(
                        id="memory_relationship_1",
                        scope="idle",
                        owner_type="agent_pair",
                        owner_id="agent_1:agent_2",
                        memory_type="relationship",
                        summary="Nora and Vale often debate goals with friendly tension.",
                        source_message_ids=["message_1", "message_2"],
                        importance_score=0.9,
                        confidence=0.8,
                    )
                ],
            )
        )
        prompt = "\n\n".join(message.content for message in package.messages)

        self.assertIn("Agent relationship memory", prompt)
        self.assertIn("friendly tension", prompt)
        self.assertIn("memory_relationship_1", package.included_memory_ids)
