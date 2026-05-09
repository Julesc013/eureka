"""Fixture-only extraction sandbox orchestration."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any

from runtime.extraction.candidate_effects import build_extraction_candidate_effects
from runtime.extraction.container_detect import detect_container_type
from runtime.extraction.guards import (
    check_archive_bomb_risk,
    detect_truth_or_product_violations,
    ensure_allowed_input_path,
    is_under_temp,
    load_extraction_policy,
    looks_like_private_path,
    product_boundary,
    repo_relative,
    resolve_path,
    stable_id,
    truth_boundary,
)
from runtime.extraction.tier0_outer_metadata import extract_tier0_outer_metadata
from runtime.extraction.tier1_member_listing import extract_tier1_member_listing
from runtime.extraction.tier2_manifest_extract import extract_tier2_manifest_candidates


TARGET_STATUSES = {"example_only", "fixture_only", "repo_local_fixture", "policy_blocked", "not_evaluable"}


def validate_extraction_target(target: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    """Validate and resolve an extraction target without arbitrary path access."""

    if target.get("target_status") not in TARGET_STATUSES:
        raise ValueError(f"unsupported target_status: {target.get('target_status')}")
    if target.get("fixture_public_safe") is not True and target.get("target_status") != "policy_blocked":
        raise ValueError("target fixture_public_safe must be true for runnable fixtures")
    target_path = str(target.get("target_path", ""))
    resolved_candidate = resolve_path(target_path)
    if looks_like_private_path(target_path) and not is_under_temp(resolved_candidate):
        raise ValueError("refusing private-looking target path")
    resolved = ensure_allowed_input_path(target_path, policy)
    requested = [str(item) for item in target.get("requested_tiers", [])]
    allowed = {str(item) for item in (policy or {}).get("allowed_tiers", ["0", "1", "2"])}
    if not set(requested).issubset(allowed):
        raise ValueError(f"requested tiers exceed policy: {requested}")
    violations = detect_truth_or_product_violations(target)
    if violations:
        raise ValueError("; ".join(violations))
    return {"target": dict(target), "path": resolved, "requested_tiers": requested}


def run_fixture_extraction(
    target: Mapping[str, Any],
    tiers: Sequence[str] | None = None,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Run Tier 0-2 fixture extraction without writing payloads."""

    policy = dict(policy or load_extraction_policy())
    validated = validate_extraction_target(target, policy)
    path = validated["path"]
    requested_tiers = [str(item) for item in (tiers if tiers is not None else validated["requested_tiers"])]
    container_type = detect_container_type(path, policy)
    tier_results: dict[str, Any] = {}
    checks: dict[str, Any] = {
        "path_traversal_checked": True,
        "archive_bomb_checked": False,
        "resource_limits_checked": True,
        "symlink_checked": True,
        "special_file_checked": True,
        "execution_prevented": True,
        "network_prevented": True,
    }
    warnings: list[str] = []
    status = "completed_fixture"
    if container_type not in set(policy.get("allowed_container_types", ["zip", "tar"])):
        status = "unsupported_container"
        safety = build_extraction_safety_report(target, checks, policy, [], warnings, status)
        return build_extraction_result(target, {"container_type": container_type}, policy, safety, [], warnings, status)
    if "0" in requested_tiers:
        tier_results["outer_metadata"] = extract_tier0_outer_metadata(path, policy)
    members: list[dict[str, Any]] = []
    if "1" in requested_tiers or "2" in requested_tiers:
        members = extract_tier1_member_listing(path, policy)
        tier_results["member_listing"] = members
        checks["archive_bomb_checked"] = True
        bomb = check_archive_bomb_risk(members, policy)
        checks["archive_bomb"] = bomb
        blocked_members = [item for item in members if item.get("blocked")]
        if blocked_members:
            status = "blocked_path_traversal" if any("traversal" in str(item.get("block_reason")) or "absolute" in str(item.get("block_reason")) or "drive_prefix" in str(item.get("block_reason")) for item in blocked_members) else "blocked_by_policy"
        if bomb["archive_bomb_risk"]:
            status = "blocked_archive_bomb_risk"
            warnings.extend(bomb["block_reasons"])
    if "2" in requested_tiers and not status.startswith("blocked"):
        tier_results["manifest_candidates"] = extract_tier2_manifest_candidates(path, policy)
    safety = build_extraction_safety_report(target, checks, policy, members, warnings, status)
    result = build_extraction_result(target, {"container_type": container_type, **tier_results}, policy, safety, members, warnings, status)
    effects = build_extraction_candidate_effects(result, policy)
    result["candidate_effects"] = effects
    result["candidate_effect_refs"] = [item["candidate_effect_id"] for item in effects]
    violations = detect_truth_or_product_violations(result)
    if violations:
        raise ValueError("; ".join(violations))
    return result


def build_extraction_result(
    target: Mapping[str, Any],
    tier_results: Mapping[str, Any],
    policy: Mapping[str, Any] | None,
    safety_report: Mapping[str, Any] | None = None,
    members: Sequence[Mapping[str, Any]] | None = None,
    warnings: Sequence[str] | None = None,
    status: str = "completed_fixture",
) -> dict[str, Any]:
    member_listing = list(tier_results.get("member_listing", []))
    manifest_candidates = list(tier_results.get("manifest_candidates", []))
    blocked_members = [dict(item) for item in member_listing if isinstance(item, Mapping) and item.get("blocked")]
    tiers_completed: list[str] = []
    if tier_results.get("outer_metadata"):
        tiers_completed.append("0")
    if member_listing:
        tiers_completed.append("1")
    if manifest_candidates:
        tiers_completed.append("2")
    result = {
        "schema_version": "extraction_result.v0",
        "extraction_result_id": stable_id("extraction.result", {"target": target.get("target_id"), "tiers": tiers_completed, "status": status}),
        "target_ref": target.get("target_id"),
        "extraction_status": status,
        "tiers_attempted": list(target.get("requested_tiers", [])),
        "tiers_completed": tiers_completed,
        "container_type": tier_results.get("container_type", target.get("declared_container_type")),
        "outer_metadata": tier_results.get("outer_metadata", {}),
        "member_listing": member_listing,
        "manifest_candidates": manifest_candidates,
        "blocked_members": blocked_members,
        "warnings": list(warnings or []),
        "limitations": [
            "Fixture-only extraction result.",
            "No payload was executed or extracted to persistent storage.",
            "Candidates and evidence previews require review before downstream use.",
        ],
        "safety_report_ref": safety_report.get("safety_report_id") if isinstance(safety_report, Mapping) else None,
        "safety_report": dict(safety_report or {}),
        "candidate_effect_refs": [],
        "truth_boundary": truth_boundary(),
        "product_boundary": product_boundary(),
        "notes": ["Extraction creates candidate previews only, not truth."],
    }
    return result


def build_extraction_safety_report(
    target: Mapping[str, Any],
    checks: Mapping[str, Any],
    policy: Mapping[str, Any] | None,
    members: Sequence[Mapping[str, Any]] | None = None,
    warnings: Sequence[str] | None = None,
    result: str = "completed_fixture",
) -> dict[str, Any]:
    blocked = [dict(item) for item in (members or []) if isinstance(item, Mapping) and item.get("blocked")]
    return {
        "schema_version": "extraction_safety_report.v0",
        "safety_report_id": stable_id("extraction.safety_report", {"target": target.get("target_id"), "result": result}),
        "target_ref": target.get("target_id"),
        "path_traversal_checked": bool(checks.get("path_traversal_checked", True)),
        "archive_bomb_checked": bool(checks.get("archive_bomb_checked", True)),
        "resource_limits_checked": bool(checks.get("resource_limits_checked", True)),
        "symlink_checked": bool(checks.get("symlink_checked", True)),
        "special_file_checked": bool(checks.get("special_file_checked", True)),
        "execution_prevented": True,
        "network_prevented": True,
        "blocked_members": blocked,
        "warnings": list(warnings or []),
        "limitations": ["Safety report is a fixture sandbox guard report, not malware safety."],
        "result": result,
        "notes": ["No execution, network, downloads, source sync, or index mutation occurred."],
    }


def target_from_fixture(path: str | Path, tiers: Sequence[str] | None = None) -> dict[str, Any]:
    resolved = Path(path)
    return {
        "schema_version": "extraction_target.v0",
        "target_id": stable_id("extraction.target", str(resolved)),
        "target_status": "repo_local_fixture",
        "target_kind": "fixture_container",
        "target_path": repo_relative(resolved) if resolved.is_absolute() else str(resolved).replace("\\", "/"),
        "target_path_policy": "repo_fixture_only",
        "declared_container_type": "auto",
        "requested_tiers": list(tiers or ["0", "1", "2"]),
        "fixture_public_safe": True,
        "expected_result_refs": [],
        "limitations": ["Generated from an explicit fixture path."],
        "truth_boundary": truth_boundary(),
        "product_boundary": product_boundary(),
    }
