"""
Created at: 2026-05-25
Created by: Codex
Last Modified at: 2026-05-25
Last Modified by: Codex
"""

from unittest import TestCase

from fastapi import FastAPI
from fastapi.testclient import TestClient

from agents.catalog import default_agent_snapshots, list_agent_display_profiles
from agents.routes import router


class AgentCatalogTest(TestCase):
    def test_display_profiles_and_prompt_snapshots_use_same_names(self) -> None:
        displays = list_agent_display_profiles()
        snapshots = default_agent_snapshots()

        self.assertEqual([agent["slot"] for agent in displays], ["agent_1", "agent_2"])
        self.assertEqual([agent["name"] for agent in displays], ["Nora", "Vale"])
        self.assertEqual([agent.name for agent in snapshots], ["Nora", "Vale"])

    def test_agents_route_returns_frontend_safe_display_profiles(self) -> None:
        app = FastAPI()
        app.include_router(router, prefix="/api/agents")
        client = TestClient(app)

        response = client.get("/api/agents")

        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertEqual(body[0]["slot"], "agent_1")
        self.assertEqual(body[0]["name"], "Nora")
        self.assertNotIn("core_persona", body[0])

