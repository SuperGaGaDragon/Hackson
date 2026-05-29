"""
Created at: 2026-05-29
Created by: Codex
Last Modified at: 2026-05-29
Last Modified by: Codex
"""

import json
import sys
import time
import urllib.error
import urllib.request


def main() -> None:
    base = sys.argv[1].rstrip("/") if len(sys.argv) > 1 else "http://127.0.0.1:8167"
    username = f"brainstorm_{int(time.time())}"

    def request(method: str, path: str, body: dict | None = None, token: str | None = None):
        data = None if body is None else json.dumps(body).encode("utf-8")
        req = urllib.request.Request(base + path, data=data, method=method)
        if body is not None:
            req.add_header("Content-Type", "application/json")
        if token:
            req.add_header("Authorization", f"Bearer {token}")
        try:
            with urllib.request.urlopen(req, timeout=20) as res:
                raw = res.read().decode("utf-8")
                return res.status, json.loads(raw) if raw else None
        except urllib.error.HTTPError as exc:
            raw = exc.read().decode("utf-8")
            raise RuntimeError(f"{method} {path} -> {exc.code} {raw}") from exc

    _, auth = request(
        "POST",
        "/api/users/register",
        {
            "username": username,
            "email": f"{username}@example.com",
            "password": "Password12345!",
        },
    )
    token = auth["accessToken"]
    _, idle = request(
        "POST",
        "/api/conversations",
        {
            "mode": "idle",
            "title": "Idle",
            "metadata": {"topicDirection": "Design a judge-facing demo that turns brainstorm into Work."},
        },
        token,
    )
    messages = [
        ("agent", "agent_1", None, "We should turn the brainstorm into a clear Work brief with source evidence."),
        ("agent", "agent_2", None, "But the risk is creating a mission before the user edits the title and goal."),
        ("user", None, username, "Can we make the promotion editable and keep the mission as draft first?"),
    ]
    source_ids = []
    for sender_type, sender_slot, sender_id, content in messages:
        _, message = request(
            "POST",
            f"/api/conversations/{idle['id']}/messages",
            {
                "sender_type": sender_type,
                "sender_slot": sender_slot,
                "sender_id": sender_id,
                "role": "assistant" if sender_type == "agent" else "user",
                "content": content,
                "metadata": {"source": "target_smoke"},
            },
            token,
        )
        source_ids.append(message["id"])

    _, card = request("GET", f"/api/idle/{idle['id']}/brainstorm-card", token=token)
    assert card["conversationId"] == idle["id"]
    assert card["sourceMessageIds"] == source_ids, card
    assert card["sourceMessageCount"] == 3
    assert card["suggestedMission"]["title"]
    assert card["keyIdeas"], card
    assert card["disagreements"], card

    _, project = request(
        "POST",
        "/api/work/projects",
        {"name": "Idle Brainstorm Smoke", "metadata": {"source": "target_smoke"}},
        token,
    )
    _, mission = request(
        "POST",
        "/api/work/missions",
        {
            "projectId": project["id"],
            "title": card["suggestedMission"]["title"],
            "goal": card["suggestedMission"]["goal"],
            "leadEmployeeId": "agent_1",
            "metadata": {
                "source": "idle_brainstorm",
                "idleConversationId": idle["id"],
                "sourceMessageIds": card["sourceMessageIds"],
                "sourceMessageCount": card["sourceMessageCount"],
                "brainstormGeneratedAt": card["generatedAt"],
                "brainstormTopic": card["topic"],
            },
        },
        token,
    )
    _, detail = request("GET", f"/api/work/missions/{mission['id']}", token=token)
    assert detail["mission"]["status"] == "draft"
    assert detail["mission"]["metadata"]["source"] == "idle_brainstorm"
    assert detail["mission"]["metadata"]["sourceMessageIds"] == source_ids
    print(
        json.dumps(
            {
                "idle_brainstorm_smoke": "ok",
                "user": username,
                "conversation": idle["id"],
                "sourceMessageCount": card["sourceMessageCount"],
                "mission": mission["id"],
                "missionStatus": detail["mission"]["status"],
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
