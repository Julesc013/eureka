"""Future WorkUnit seed previews for extraction findings."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from runtime.extraction.guards import detect_truth_or_product_violations, stable_id
from runtime.extraction.review_bridge import extraction_search_product_boundary, extraction_search_truth_boundary


def build_extraction_workunit_seed(
    extraction_result: Mapping[str, Any],
    member_or_manifest: Mapping[str, Any] | None,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    item = dict(member_or_manifest or {})
    result_ref = str(extraction_result.get("extraction_result_id", "unknown_result"))
    if extraction_result.get("extraction_status", "").startswith("blocked"):
        proposed = "policy_review_future"
    elif item.get("manifest_candidate_id"):
        proposed = "verify_manifest_candidate_future"
    elif item.get("member_id"):
        proposed = "check_member_relevance_future"
    else:
        proposed = "deepen_container_future"
    seed = {
        "schema_version": "extraction_workunit_seed.v0",
        "workunit_seed_id": stable_id("extraction.workunit_seed", {"result": result_ref, "item": item, "type": proposed}),
        "workunit_seed_status": "fixture_preview",
        "proposed_workunit_type": proposed,
        "related_extraction_result_ref": result_ref,
        "related_member_refs": [item.get("normalized_member_path") or item.get("member_ref")] if item.get("member_id") or item.get("member_ref") else [],
        "related_manifest_refs": [item.get("manifest_candidate_id")] if item.get("manifest_candidate_id") else [],
        "allowed_actions_future": [
            "request_human_review",
            "prepare_future_fixture_deepening",
            "prepare_future_relevance_check",
        ],
        "forbidden_actions": [
            "execute_workunit_current",
            "download_file",
            "execute_file",
            "mutate_public_index",
            "mutate_master_index",
            "accept_evidence",
            "accept_candidate",
        ],
        "review_required": True,
        "policy_required": True,
        "workunit_seed_executes_work": False,
        "limitations": ["WorkUnit seed is a future planning preview only and does not execute work."],
        "truth_boundary": extraction_search_truth_boundary(),
        "product_boundary": extraction_search_product_boundary(),
    }
    validate_extraction_workunit_seed(seed, policy)
    return seed


def validate_extraction_workunit_seed(seed: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> bool:
    violations = detect_truth_or_product_violations(seed)
    if violations:
        raise ValueError("; ".join(violations))
    if seed.get("workunit_seed_executes_work") is not False:
        raise ValueError("workunit_seed_executes_work must be false")
    return True


def summarize_extraction_workunit_seed(seed: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "extraction_workunit_seed_summary.v0",
        "workunit_seed_id": seed.get("workunit_seed_id"),
        "proposed_workunit_type": seed.get("proposed_workunit_type"),
        "review_required": bool(seed.get("review_required")),
        "workunit_seed_executes_work": bool(seed.get("workunit_seed_executes_work")),
    }
