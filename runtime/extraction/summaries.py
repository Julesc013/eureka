"""Summaries for fixture extraction results."""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from runtime.extraction.guards import detect_truth_or_product_violations


def summarize_extraction_result(result: Mapping[str, Any]) -> dict[str, Any]:
    members = result.get("member_listing", [])
    manifests = result.get("manifest_candidates", [])
    blocked = result.get("blocked_members", [])
    violations = detect_truth_or_product_violations(result)
    return {
        "schema_version": "extraction_summary.v0",
        "status": "pass" if not violations else "invalid",
        "extraction_result_id": result.get("extraction_result_id"),
        "extraction_status": result.get("extraction_status"),
        "container_type": result.get("container_type"),
        "tiers_completed": list(result.get("tiers_completed", [])),
        "member_count": len(members) if isinstance(members, list) else 0,
        "manifest_candidate_count": len(manifests) if isinstance(manifests, list) else 0,
        "blocked_member_count": len(blocked) if isinstance(blocked, list) else 0,
        "warnings": list(result.get("warnings", [])),
        "truth_boundary_violations": violations,
    }


def render_extraction_summary_markdown(summary: Mapping[str, Any]) -> str:
    lines = [
        "# Extraction Summary",
        "",
        f"- status: `{summary.get('status')}`",
        f"- extraction_status: `{summary.get('extraction_status')}`",
        f"- container_type: `{summary.get('container_type')}`",
        f"- tiers_completed: `{', '.join(summary.get('tiers_completed', []))}`",
        f"- member_count: `{summary.get('member_count', 0)}`",
        f"- manifest_candidate_count: `{summary.get('manifest_candidate_count', 0)}`",
        f"- blocked_member_count: `{summary.get('blocked_member_count', 0)}`",
        "- accepted_evidence: `false`",
        "- accepted_candidate: `false`",
        "- public_index_mutated: `false`",
        "- master_index_mutated: `false`",
        "",
    ]
    return "\n".join(lines)
