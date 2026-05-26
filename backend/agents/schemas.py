"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Last Modified by: Codex
"""

from pydantic import BaseModel


class AgentDisplayResponse(BaseModel):
    slot: str
    name: str
    short: str
    color: str
    voice: str

