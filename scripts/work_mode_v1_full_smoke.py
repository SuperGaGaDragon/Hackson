"""
Created at: 2026-05-27
Created by: Codex
Last Modified at: 2026-05-27
Last Modified by: Codex
"""

from __future__ import annotations

import re
import json
from pathlib import Path

import sys

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from work_mode.loop import MissionLoopRunner
from work_mode.schemas import MissionCreateRequest, MissionStartRequest, ProjectCreateRequest
from work_mode.service import WorkModeService
from work_mode.tests.test_work_mode_service import FakeWorkModeRepository
from work_mode.tool_executor import WorkModeToolExecutor
from work_mode.tool_protocol import parse_tool_action

CJK_RE = re.compile(r"[\u4e00-\u9fff]")


def main() -> None:
    service = WorkModeService(FakeWorkModeRepository())
    mission = _mission(service)
    detail = service.start_mission("smoke_user", mission["id"], MissionStartRequest())
    run_id = detail["activeRun"]["id"]
    lead_client = FullSmokeLeadClient()
    delegate_client = FullSmokeDelegateClient()

    MissionLoopRunner(
        service,
        action_client=lead_client,
        executor=WorkModeToolExecutor(service, delegate_client=delegate_client),
        max_turns=12,
        max_invalid_turns=2,
    ).run("smoke_user", mission["id"], run_id)

    completed = service.get_mission_detail("smoke_user", mission["id"])
    _assert_acceptance(completed)
    final_artifact = _final_artifact(completed)
    print(
        "work_mode_v1_full_smoke=ok "
        f"events={len(completed['events'])} "
        f"windows={len(completed['workWindows'])} "
        f"products={len(completed['products'])} "
        f"artifacts={len(completed['artifacts'])} "
        f"final_cjk={_cjk_count(final_artifact['content'])}"
    )


def _mission(service: WorkModeService) -> dict:
    project = service.create_project("smoke_user", ProjectCreateRequest(name="Novel Smoke"))
    return service.create_mission(
        "smoke_user",
        MissionCreateRequest(
            projectId=project["id"],
            title="写一个8000字小说",
            goal="写一个8000字中文小说，题材自定，要求分章节，有大纲，有最终成稿。",
            leadEmployeeId="agent_1",
        ),
        [
            {"slot": "agent_1", "name": "Planner", "voice": "lead", "personality": "Plans.", "story": ""},
            {"slot": "agent_2", "name": "Writer", "voice": "delegate", "personality": "Writes.", "story": ""},
        ],
    )


class FullSmokeLeadClient:
    def __init__(self) -> None:
        self.calls = 0

    def generate_action(self, context: dict):
        self.calls += 1
        products = context.get("productManifest") or []
        windows = context.get("workWindowManifest") or []
        product = products[0] if products else None
        if self.calls == 1:
            return parse_tool_action(
                """
                {
                  "tool": "mission_plan",
                  "arguments": {
                    "reason": "先规划长篇结构。",
                    "planTitle": "8000字小说计划",
                    "steps": [
                      {"title": "建立故事产品", "status": "pending", "notes": "先写大纲。"},
                      {"title": "委托章节草稿", "status": "pending", "notes": "至少两个窗口。"},
                      {"title": "合成为最终稿", "status": "pending", "notes": "不少于8000汉字。"}
                    ]
                  }
                }
                """
            )
        if self.calls == 2:
            return parse_tool_action(
                """
                {
                  "tool": "work_product",
                  "arguments": {
                    "reason": "创建小说产品和大纲。",
                    "operation": "create_product",
                    "productId": null,
                    "sourceArtifactIds": [],
                    "productTitle": "雨夜车站",
                    "artifactTitle": "故事大纲",
                    "artifactKind": "outline",
                    "content": "一座雨夜车站牵出旧城秘密，主人公在追查中理解亲情、选择和记忆。",
                    "summary": "完成故事大纲。"
                  }
                }
                """
            )
        if self.calls in {3, 4}:
            product_id = product["id"]
            chapter = "第一章" if self.calls == 3 else "第二章"
            return parse_tool_action(
                f"""
                {{
                  "tool": "delegate_agent",
                  "arguments": {{
                    "reason": "让写作 Agent 扩写{chapter}。",
                    "agentSlot": "agent_2",
                    "windowTitle": "{chapter}草稿",
                    "brief": "写出{chapter}的完整章节草稿。",
                    "expectedOutput": "chapter",
                    "targetProductId": "{product_id}",
                    "sourceArtifactIds": []
                  }}
                }}
                """
            )
        if self.calls == 5:
            product_id = product["id"]
            source_ids = [window["resultArtifactId"] for window in windows if window.get("resultArtifactId")]
            final_text = _long_final_text()
            source_ids_json = json.dumps(source_ids, ensure_ascii=False)
            final_text_json = json.dumps(final_text, ensure_ascii=False)
            return parse_tool_action(
                f"""
                {{
                  "tool": "work_product",
                  "arguments": {{
                    "reason": "合成为最终成稿。",
                    "operation": "finalize_product",
                    "productId": "{product_id}",
                    "sourceArtifactIds": {source_ids_json},
                    "productTitle": "雨夜车站",
                    "artifactTitle": "最终成稿",
                    "artifactKind": "final",
                    "content": {final_text_json},
                    "summary": "完成不少于8000汉字的最终成稿。"
                  }}
                }}
                """
            )
        product_id = product["id"]
        final_artifact_id = product["latestArtifactId"]
        return parse_tool_action(
            f"""
            {{
              "tool": "finish_mission",
              "arguments": {{
                "reason": "最终成稿已完成。",
                "summary": "8000字小说任务完成。",
                "finalProductIds": ["{product_id}"],
                "finalArtifactIds": ["{final_artifact_id}"]
              }}
            }}
            """
        )


class FullSmokeDelegateClient:
    def __init__(self) -> None:
        self.calls = 0

    def generate_delegate_result(self, context: dict) -> dict:
        self.calls += 1
        title = "第一章草稿" if self.calls == 1 else "第二章草稿"
        content = ("雨夜车站里，旧钟缓慢敲响，旅人沿着积水的月台寻找失踪的车票。" * 36).strip()
        return {
            "status": "completed",
            "title": title,
            "summary": f"{title}完成。",
            "content": content,
            "reason": "按 brief 完成章节草稿。",
        }


def _assert_acceptance(detail: dict) -> None:
    event_types = [event["type"] for event in detail["events"]]
    final_artifact = _final_artifact(detail)
    final_cjk = _cjk_count(final_artifact["content"])

    assert detail["mission"]["status"] == "completed"
    assert "MISSION_PLAN_UPDATED" in event_types
    assert event_types.count("WORK_WINDOW_COMPLETED") >= 2
    assert len(detail["workWindows"]) >= 2
    assert len(detail["products"]) >= 1
    assert len(detail["artifacts"]) >= 3
    assert detail["products"][0]["status"] == "final"
    assert final_artifact["kind"] == "final"
    assert final_cjk >= 8000, final_cjk
    assert "大纲" not in final_artifact["title"]
    assert detail["events"][-1]["type"] == "MISSION_COMPLETED"


def _final_artifact(detail: dict) -> dict:
    final_product = next(product for product in detail["products"] if product["status"] == "final")
    final_id = final_product["latestArtifactId"]
    return next(artifact for artifact in detail["artifacts"] if artifact["id"] == final_id)


def _cjk_count(text: str) -> int:
    return len(CJK_RE.findall(text))


def _long_final_text() -> str:
    seed = (
        "雨夜车站的灯光像被水洗过的铜，映在空荡月台上。林澈握着旧车票，沿着锈迹斑斑的栏杆向前走，"
        "他听见远处列车的回声，也听见多年以前父亲在电话里没有说完的话。小城被雨声包围，售票窗口后面"
        "的老人递给他一本登记簿，里面写着失踪乘客的名字。林澈开始明白，这趟寻找不是为了追回一张车票，"
        "而是为了把被沉默压住的人重新带回记忆。"
    )
    return "\n".join(f"第{i}节：{seed}" for i in range(1, 70))


if __name__ == "__main__":
    main()
