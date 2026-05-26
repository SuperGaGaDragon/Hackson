"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Last Modified by: Codex
"""

from fastapi import APIRouter

from agents.catalog import list_agent_display_profiles
from agents.schemas import AgentDisplayResponse


router = APIRouter()


@router.get("", response_model=list[AgentDisplayResponse])
def list_agents() -> list[dict]:
    """List backend-owned fixed V1 Agent display profiles."""
    return list_agent_display_profiles()

