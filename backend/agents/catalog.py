"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-27
Last Modified by: Codex
"""

from dataclasses import dataclass

from context.schemas import AgentPersonaSnapshot


DEFAULT_TARGET_AGENT_ID = "agent_1"
DEFAULT_SECOND_AGENT_ID = "agent_2"


@dataclass(frozen=True)
class AgentCatalogRecord:
    slot: str
    name: str
    short: str
    color: str
    voice: str
    core_persona: str
    speaking_style: str
    episode_state: str | None = None


AGENT_CATALOG = (
    AgentCatalogRecord(
        slot=DEFAULT_TARGET_AGENT_ID,
        name="Nora",
        short="A1",
        color="teal",
        voice="precise",
        core_persona="冷静、会追问概念的哲学型 Agent。",
        speaking_style="中文，短句，清楚。",
        episode_state="正在帮助 Hackson 跑通 V1 demo。",
    ),
    AgentCatalogRecord(
        slot=DEFAULT_SECOND_AGENT_ID,
        name="Vale",
        short="A2",
        color="amber",
        voice="sharp",
        core_persona="务实、直接、擅长把想法变成计划的 Agent。",
        speaking_style="中文，简洁，偏行动。",
        episode_state="正在把产品计划落成可运行链路。",
    ),
)

AGENT_BY_SLOT = {agent.slot: agent for agent in AGENT_CATALOG}


def list_agent_display_profiles() -> list[dict]:
    """Return frontend-safe fixed Agent display profiles."""
    return [
        {
            "slot": agent.slot,
            "name": agent.name,
            "short": agent.short,
            "color": agent.color,
            "voice": agent.voice,
        }
        for agent in AGENT_CATALOG
    ]


def default_agent_snapshots() -> list[AgentPersonaSnapshot]:
    """Return prompt persona snapshots from the same catalog used by the frontend."""
    return [
        AgentPersonaSnapshot(
            id=agent.slot,
            name=agent.name,
            core_persona=agent.core_persona,
            speaking_style=agent.speaking_style,
            episode_state=agent.episode_state,
        )
        for agent in AGENT_CATALOG
    ]


def default_user_agent_profiles() -> list[dict]:
    """Seed two editable user-owned Agent profiles from the fixed catalog."""
    return [
        {
            "slot": agent.slot,
            "name": agent.name,
            "short": agent.short,
            "color": agent.color,
            "voice": agent.voice,
            "personality": agent.core_persona,
            "story": agent.episode_state or "",
        }
        for agent in AGENT_CATALOG
    ]


def normalize_user_agent_profiles(raw_profiles: list[dict] | None) -> list[dict]:
    """Return exactly two safe user Agent profiles, falling back per field."""
    raw_by_slot = {
        profile.get("slot"): profile
        for profile in raw_profiles or []
        if isinstance(profile, dict) and profile.get("slot") in AGENT_BY_SLOT
    }
    normalized: list[dict] = []
    for fallback in AGENT_CATALOG:
        raw = raw_by_slot.get(fallback.slot, {})
        normalized.append(
            {
                "slot": fallback.slot,
                "name": _bounded(raw.get("name"), fallback.name, 32),
                "short": fallback.short,
                "color": fallback.color,
                "voice": _bounded(raw.get("voice"), fallback.voice, 80),
                "personality": _bounded(raw.get("personality"), fallback.core_persona, 1200),
                "story": _bounded(raw.get("story"), fallback.episode_state or "", 4000),
            }
        )
    return normalized


def user_agent_snapshots(raw_profiles: list[dict] | None) -> list[AgentPersonaSnapshot]:
    """Convert user-owned editable profiles into prompt persona snapshots."""
    return [
        AgentPersonaSnapshot(
            id=profile["slot"],
            name=profile["name"],
            core_persona=profile["personality"],
            speaking_style=profile["voice"],
            episode_state=profile["story"] or None,
        )
        for profile in normalize_user_agent_profiles(raw_profiles)
    ]


def ensure_agent_id(agent_id: str | None) -> str:
    if agent_id in AGENT_BY_SLOT:
        return agent_id
    return DEFAULT_TARGET_AGENT_ID


def _bounded(value, fallback: str, max_length: int) -> str:
    if value is None:
        return fallback
    text = str(value).strip()
    if not text:
        return fallback
    return text[:max_length]
