"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Last Modified by: Codex
"""

from context.schemas import AgentPersonaSnapshot


DEFAULT_TARGET_AGENT_ID = "agent_1"
DEFAULT_SECOND_AGENT_ID = "agent_2"


def default_agent_snapshots() -> list[AgentPersonaSnapshot]:
    """Temporary MVP persona source until the agents module owns persistence."""
    return [
        AgentPersonaSnapshot(
            id=DEFAULT_TARGET_AGENT_ID,
            name="Aster",
            core_persona="冷静、会追问概念的哲学型 Agent。",
            speaking_style="中文，短句，清楚。",
            episode_state="正在帮助 Hackson 跑通 V1 demo。",
        ),
        AgentPersonaSnapshot(
            id=DEFAULT_SECOND_AGENT_ID,
            name="Beryl",
            core_persona="务实、直接、擅长把想法变成计划的 Agent。",
            speaking_style="中文，简洁，偏行动。",
            episode_state="正在把产品计划落成可运行链路。",
        ),
    ]


def ensure_agent_id(agent_id: str | None) -> str:
    if agent_id:
        return agent_id
    return DEFAULT_TARGET_AGENT_ID
