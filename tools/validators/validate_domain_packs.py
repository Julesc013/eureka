#!/usr/bin/env python3
"""Validate DOMAIN-00 pack contracts, seed data, policies, and boundaries."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local_eval.domain_packs import (
    BLOCKED_ACTIONS,
    EXPECTED_LANES,
    PROJECTION_PROFILES,
    READ_ONLY_ACTIONS,
    REQUIRED_DOMAIN_IDS,
    build_domain_console_view,
    compile_domain_query_hints,
    load_domain_packs_from_manifest,
    load_domain_seed_manifest,
    validate_domain_pack,
)


TASK = "AIDE-BATCH-DOMAIN-FOUNDATION-01"
MANIFEST_PATH = "examples/domain/domain_seed_manifest.json"

REQUIRED_CONTRACTS = (
    "contracts/domain/README.md",
    "contracts/domain/domain_pack.v0.json",
    "contracts/domain/domain_identity_rule.v0.json",
    "contracts/domain/domain_query_hint.v0.json",
    "contracts/domain/domain_source_preference.v0.json",
    "contracts/domain/domain_result_expectation.v0.json",
    "contracts/domain/domain_action_posture.v0.json",
    "contracts/domain/domain_seed_manifest.v0.json",
    "contracts/domain/domain_console_view.v0.json",
)

REQUIRED_POLICIES = (
    "control/policies/domain_pack_policy.json",
    "control/policies/domain_non_claim_policy.json",
    "control/policies/domain_action_posture_policy.json",
    "control/policies/domain_source_preference_policy.json",
)

REQUIRED_MATRICES = (
    "control/inventory/domain_pack_contract_matrix.json",
    "control/inventory/domain_seed_inventory.json",
    "control/inventory/domain_query_hint_matrix.json",
    "control/inventory/domain_source_preference_matrix.json",
    "control/inventory/domain_result_lane_matrix.json",
    "control/inventory/domain_action_posture_matrix.json",
    "control/inventory/domain_syn_integration_matrix.json",
    "control/inventory/domain_workbench_console_matrix.json",
)

REQUIRED_DOCS = (
    "docs/architecture/DOMAIN_PACKS.md",
    "docs/architecture/DOMAIN_QUERY_INTERPRETATION.md",
    "docs/operations/DOMAIN_PACK_RUNBOOK.md",
    "docs/operations/POST_DOMAIN_FOUNDATION_PLAN.md",
    "docs/reference/DOMAIN_PACK_RECORD.md",
    "docs/reference/DOMAIN_QUERY_HINTS.md",
)

FORBIDDEN_TEXT = (
    "production-ready",
    "public launch ready",
    "live source call completed",
    "source probe completed",
    "download completed",
    "extraction completed",
    "model call completed",
    "accepted evidence truth",
    "verified record created",
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(REPO_ROOT), help=argparse.SUPPRESS)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    report = validate_domain_packs(Path(args.repo_root).resolve())
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True), file=stdout)
    else:
        print("DOMAIN pack foundation validation", file=stdout)
        print(f"status: {report['status']}", file=stdout)
        print(f"error_count: {len(report['errors'])}", file=stdout)
        for error in report["errors"]:
            print(f"- {error}", file=stdout)
    return 0 if report["status"] == "valid" else 1


def validate_domain_packs(root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    payloads: dict[str, Mapping[str, Any]] = {}

    for rel_path in (*REQUIRED_CONTRACTS, *REQUIRED_DOCS):
        if not (root / rel_path).is_file():
            errors.append(f"{rel_path}: required file is missing.")

    for rel_path in (*REQUIRED_POLICIES, *REQUIRED_MATRICES):
        payload = _load_json(root / rel_path, errors)
        if isinstance(payload, Mapping):
            payloads[rel_path] = payload

    _validate_policy(payloads.get("control/policies/domain_pack_policy.json", {}), errors)
    _validate_action_policy(payloads.get("control/policies/domain_action_posture_policy.json", {}), errors)

    manifest = load_domain_seed_manifest(root / MANIFEST_PATH)
    if manifest.get("schema_version") != "domain_seed_manifest.v0":
        errors.append(f"{MANIFEST_PATH}: schema_version must be domain_seed_manifest.v0.")
    if manifest.get("seed_status") != "example_only":
        errors.append(f"{MANIFEST_PATH}: seed_status must be example_only.")

    packs = load_domain_packs_from_manifest(root / MANIFEST_PATH)
    pack_ids = [str(pack.get("domain_id", "")) for pack in packs]
    if set(pack_ids) != set(REQUIRED_DOMAIN_IDS):
        errors.append(f"seed manifest must include required DOMAIN ids: {sorted(REQUIRED_DOMAIN_IDS)}.")
    for domain_id in REQUIRED_DOMAIN_IDS:
        if not (root / f"examples/domain/{domain_id}.domain_pack.json").is_file():
            errors.append(f"examples/domain/{domain_id}.domain_pack.json: required seed pack is missing.")

    for pack in packs:
        report = validate_domain_pack(pack)
        errors.extend(report["errors"])
        hints = compile_domain_query_hints(pack)
        if not hints["promote_terms"] or not hints["suppress_terms"] or not hints["source_family_preferences"]:
            errors.append(f"{pack.get('domain_id')}: compiled query hints must include promote, suppress, and source preferences.")
        for profile in PROJECTION_PROFILES:
            view = build_domain_console_view(pack, profile)
            if view.get("read_only") is not True:
                errors.append(f"{pack.get('domain_id')}: {profile} console view must be read-only.")
            if set(view.get("blocked_actions", [])) != set(BLOCKED_ACTIONS):
                errors.append(f"{pack.get('domain_id')}: {profile} console view must carry blocked actions.")

    _validate_matrix_domain_coverage(payloads, errors)
    _validate_docs_text(root, errors)

    return {
        "schema_version": "domain_pack_validation_report.v0",
        "task": TASK,
        "status": "valid" if not errors else "invalid",
        "domain_count": len(pack_ids),
        "domain_ids": sorted(pack_ids),
        "required_contract_count": len(REQUIRED_CONTRACTS),
        "required_policy_count": len(REQUIRED_POLICIES),
        "required_matrix_count": len(REQUIRED_MATRICES),
        "errors": errors,
    }


def _validate_policy(policy: Mapping[str, Any], errors: list[str]) -> None:
    required_true = (
        "domain_packs_are_not_truth",
        "domain_packs_do_not_create_evidence",
        "domain_packs_do_not_create_reviewed_records",
        "domain_packs_do_not_mutate_indexes",
        "domain_packs_may_influence_query_compilation",
        "domain_packs_may_influence_source_preferences",
        "domain_packs_may_influence_expected_result_lanes",
        "domain_packs_may_seed_search_needs",
        "domain_packs_may_seed_workunits",
    )
    required_false = (
        "live_source_calls_enabled",
        "downloads_enabled",
        "extraction_enabled",
        "model_provider_enabled",
        "public_fanout_enabled",
        "master_index_mutation_enabled",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    )
    for flag in required_true:
        if policy.get(flag) is not True:
            errors.append(f"control/policies/domain_pack_policy.json: {flag} must be true.")
    for flag in required_false:
        if policy.get(flag) is not False:
            errors.append(f"control/policies/domain_pack_policy.json: {flag} must be false.")


def _validate_action_policy(policy: Mapping[str, Any], errors: list[str]) -> None:
    blocked = set(_string_list(policy.get("blocked_by_default")))
    missing = set(BLOCKED_ACTIONS) - blocked
    if missing:
        errors.append(f"control/policies/domain_action_posture_policy.json: blocked_by_default missing {sorted(missing)}.")
    allowed = set(_string_list(policy.get("allowed_read_only_actions")))
    if not set(READ_ONLY_ACTIONS).issubset(allowed):
        errors.append("control/policies/domain_action_posture_policy.json: read-only actions are incomplete.")


def _validate_matrix_domain_coverage(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    for rel_path in REQUIRED_MATRICES:
        payload = payloads.get(rel_path, {})
        if rel_path == "control/inventory/domain_pack_contract_matrix.json":
            continue
        domains = payload.get("domains")
        if domains is None:
            domains = payload.get("seed_packs")
        if not isinstance(domains, list):
            continue
        ids = {str(item.get("domain_id", "")) for item in domains if isinstance(item, Mapping)}
        missing = set(REQUIRED_DOMAIN_IDS) - ids
        if missing:
            errors.append(f"{rel_path}: missing DOMAIN ids {sorted(missing)}.")
    result_matrix = payloads.get("control/inventory/domain_result_lane_matrix.json", {})
    if set(_string_list(result_matrix.get("expected_lane_kinds"))) != set(EXPECTED_LANES):
        errors.append("control/inventory/domain_result_lane_matrix.json: expected_lane_kinds must match Workbench result lanes.")


def _validate_docs_text(root: Path, errors: list[str]) -> None:
    for rel_path in REQUIRED_DOCS:
        path = root / rel_path
        if not path.exists():
            continue
        text = path.read_text(encoding="utf-8").lower()
        for phrase in ("not truth", "no live source", "unsafe actions"):
            if phrase not in text:
                errors.append(f"{rel_path}: must state {phrase!r}.")
        for forbidden in FORBIDDEN_TEXT:
            if forbidden in text:
                errors.append(f"{rel_path}: forbidden claim text {forbidden!r}.")


def _load_json(path: Path, errors: list[str]) -> Mapping[str, Any]:
    if not path.is_file():
        errors.append(f"{path.relative_to(REPO_ROOT)}: required JSON file is missing.")
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"{path.relative_to(REPO_ROOT)}: invalid JSON: {exc}.")
        return {}
    if not isinstance(payload, Mapping):
        errors.append(f"{path.relative_to(REPO_ROOT)}: JSON root must be an object.")
        return {}
    return payload


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value]


if __name__ == "__main__":
    raise SystemExit(main())
