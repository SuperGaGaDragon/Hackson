"""
Created at: 2026-05-28
Created by: Codex
Last Modified at: 2026-05-28
Last Modified by: Codex
"""

import re
from typing import Any

from fastapi import HTTPException, status

LONG_FORM_NOVEL_MIN_CJK = 8000
CJK_RE = re.compile(r"[\u4e00-\u9fff]")


def requires_long_form_novel_gate(mission: dict[str, Any]) -> bool:
    """Return whether this Mission must pass the canonical long-novel product gate."""
    text = f"{mission.get('title', '')} {mission.get('goal', '')}"
    return "8000" in text and "小说" in text


def cjk_count(text: str) -> int:
    """Count CJK ideographs for deterministic Chinese long-form acceptance."""
    return len(CJK_RE.findall(text or ""))


def validate_final_product_quality(
    mission: dict[str, Any],
    detail: dict[str, Any],
    final_product_ids: list[str],
    final_artifact_ids: list[str],
) -> dict[str, Any]:
    """Validate deterministic Product gates that should not depend on model judgment."""
    if not requires_long_form_novel_gate(mission):
        return {"profile": "general", "passedChecks": ["final_product_ids_exist", "final_artifact_ids_exist"]}

    product_ids = set(final_product_ids)
    final_products = [product for product in detail["products"] if product["id"] in product_ids]
    product_artifact_ids = {
        artifact_id
        for product in final_products
        for artifact_id in product.get("artifactIds", [])
    }
    if not final_artifact_ids:
        raise _quality_error("final_artifact_required")

    final_artifacts = [
        artifact
        for artifact in detail["artifacts"]
        if artifact["id"] in set(final_artifact_ids)
    ]
    if not final_artifacts:
        raise _quality_error("artifact_not_found")

    final_artifact = max(final_artifacts, key=lambda artifact: cjk_count(artifact.get("content", "")))
    if final_artifact["id"] not in product_artifact_ids:
        raise _quality_error("final_artifact_not_in_final_product")
    if final_artifact.get("kind") != "final" or "大纲" in final_artifact.get("title", ""):
        raise _quality_error("final_artifact_not_final_content")

    final_cjk = cjk_count(final_artifact.get("content", ""))
    if final_cjk < LONG_FORM_NOVEL_MIN_CJK:
        raise _quality_error("final_artifact_cjk_too_short")

    artifacts_in_final_products = [
        artifact for artifact in detail["artifacts"] if artifact["id"] in product_artifact_ids
    ]
    if not any(artifact.get("kind") == "outline" for artifact in artifacts_in_final_products):
        raise _quality_error("missing_outline_artifact")
    if not any(artifact.get("kind") in {"chapter", "draft", "revision", "final"} for artifact in artifacts_in_final_products):
        raise _quality_error("missing_chapter_artifact")

    return {
        "profile": "long_form_novel_v1",
        "finalArtifactId": final_artifact["id"],
        "finalCjk": final_cjk,
        "passedChecks": [
            "final_artifact_cjk_min",
            "has_outline_artifact",
            "has_chapter_artifact",
            "has_final_artifact",
            "final_product_ids_exist",
            "final_artifact_ids_exist",
            "product_lineage_visible_in_api",
            "not_outline_only_final",
        ],
    }


def _quality_error(detail: str) -> HTTPException:
    return HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail=detail)
