#!/usr/bin/env python3
"""Validate H0-BUNDLE-01 Source OS foundation artifacts offline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
CONTRACTS = (
    "contracts/sources/source_registry.v2.json",
    "contracts/sources/source_record.v2.json",
    "contracts/sources/source_family.v0.json",
    "contracts/sources/source_capability.v0.json",
    "contracts/sources/source_policy.v0.json",
    "contracts/sources/source_operation_policy.v0.json",
    "contracts/sources/source_index_depth.v0.json",
    "contracts/sources/source_trust_lane.v0.json",
    "contracts/sources/source_approval_gate.v0.json",
)
INVENTORIES = (
    "control/inventory/sources/source_registry_v2_policy.json",
    "control/inventory/sources/source_family_registry.json",
    "control/inventory/sources/source_capability_ladder.json",
    "control/inventory/sources/source_index_depth_registry.json",
    "control/inventory/sources/source_trust_lane_policy.json",
    "control/inventory/sources/source_access_mode_policy.json",
    "control/inventory/sources/source_operation_policy.json",
    "control/inventory/sources/source_approval_gate_policy.json",
    "control/inventory/sources/source_expansion_no_live_call_policy.json",
)
EXAMPLES = (
    "examples/sources/source_registry_v2/minimal_source_registry_v2.json",
    "examples/sources/source_records/internet_archive_source_v2.json",
    "examples/sources/source_records/wayback_source_v2.json",
    "examples/sources/source_records/github_releases_source_v2.json",
    "examples/sources/source_records/pypi_source_v2.json",
    "examples/sources/source_records/npm_source_v2.json",
    "examples/sources/source_records/software_heritage_source_v2.json",
    "examples/sources/source_records/retro_community_source_example_v2.json",
    "examples/sources/source_records/policy_blocked_source_example_v2.json",
)
DOCS = (
    "docs/reference/SOURCE_REGISTRY_V2.md",
    "docs/reference/SOURCE_RECORD_CONTRACT.md",
    "docs/reference/SOURCE_CAPABILITY_CONTRACT.md",
    "docs/reference/SOURCE_POLICY_CONTRACT.md",
    "docs/reference/SOURCE_INDEX_DEPTH_MODEL.md",
    "docs/architecture/SOURCE_OPERATING_SYSTEM.md",
    "docs/architecture/SOURCE_FAMILY_MODEL.md",
    "docs/operations/SOURCE_POLICY_GATES.md",
    "docs/operations/SOURCE_EXPANSION_NO_LIVE_CALL_POLICY.md",
)
AUDIT_FILES = (
    "control/audits/h0-bundle-01-source-os-foundation-v0/README.md",
    "control/audits/h0-bundle-01-source-os-foundation-v0/h0_bundle_01_report.json",
    "control/audits/h0-bundle-01-source-os-foundation-v0/source_registry_v2_summary.md",
    "control/audits/h0-bundle-01-source-os-foundation-v0/source_family_ladder_summary.md",
    "control/audits/h0-bundle-01-source-os-foundation-v0/source_policy_gate_summary.md",
    "control/audits/h0-bundle-01-source-os-foundation-v0/source_index_depth_summary.md",
    "control/audits/h0-bundle-01-source-os-foundation-v0/source_expansion_no_live_call_report.md",
    "control/audits/h0-bundle-01-source-os-foundation-v0/validation.md",
    "control/audits/h0-bundle-01-source-os-foundation-v0/generated/sample_source_registry_summary.json",
    "control/audits/h0-bundle-01-source-os-foundation-v0/generated/sample_source_registry_summary.md",
)
SOURCE_RECORD_REQUIRED = {
    "schema_version",
    "source_id",
    "source_label",
    "source_family",
    "source_kind",
    "trust_lane",
    "default_policy_state",
    "legal_or_rights_posture",
    "risk_posture",
    "homepage_or_locator",
    "documented_api_posture",
    "discovery_modes",
    "access_modes",
    "supports_search",
    "supports_record_fetch",
    "supports_bulk",
    "supports_member_listing",
    "supports_hashes",
    "supports_reviews_or_notes",
    "auth_required",
    "rate_limit_policy_ref",
    "cache_policy_ref",
    "kill_switch_policy_ref",
    "index_depth_current",
    "index_depth_target_future",
    "connector_family_refs",
    "policy_refs",
    "limitations",
    "truth_boundary",
    "product_boundary",
    "notes",
}
KNOWN_POLICY_STATES = {
    "example_only",
    "planning_only",
    "local_policy_only",
    "fixture_only",
    "no_live_source_access",
    "manual_review_required",
    "policy_blocked",
}
FORBIDDEN_TRUE_KEYS = {
    "source_record_is_public_truth",
    "source_record_is_accepted_evidence",
    "source_record_grants_live_access",
    "source_record_can_mutate_public_index",
    "source_record_can_mutate_master_index",
    "source_record_can_claim_rights_clearance",
    "source_record_can_claim_malware_safety",
    "source_record_can_claim_verified_installability",
    "source_capability_grants_permission",
    "capability_grants_permission",
    "permission_granted",
    "live_access_enabled",
    "live_access_approved",
    "source_sync_enabled",
    "enabled_source_sync",
    "enabled_live_probes",
    "enabled_source_connectors",
    "enabled_downloads",
    "enabled_uploads",
    "enabled_accounts",
    "enabled_telemetry",
    "enabled_hosting",
    "mutated_public_index",
    "mutated_master_index",
    "public_index_mutated",
    "master_index_mutated",
    "accepted_source_truth",
    "accepted_evidence_truth",
    "accepted_candidate_truth",
    "accepted_public_truth",
    "rights_clearance_claimed",
    "malware_safety_claimed",
    "verified_installability_claimed",
    "claimed_production_readiness",
}
BANNED_IMPORT_RE = re.compile(
    r"^\s*(?:from|import)\s+"
    r"(requests|urllib|http|socket|ftplib|smtplib|webbrowser|selenium|playwright|openai|anthropic)\b",
    re.MULTILINE,
)
SCAN_PYTHON = (
    "scripts/validate_source_os_foundation.py",
    "scripts/summarize_source_registry_v2.py",
)


def validate_repo(root: Path = REPO_ROOT) -> dict[str, Any]:
    root = root.resolve()
    errors: list[str] = []
    payloads = {rel: load_json_object(root / rel, errors) for rel in CONTRACTS + INVENTORIES + EXAMPLES}
    validate_required_files(root, errors)
    validate_inventories(payloads, errors)
    validate_examples(root, payloads, errors)
    validate_audit_report(root, errors)
    validate_python_imports(root, errors)
    validate_no_private_roots(root, errors)
    return {
        "schema_version": "source_os_foundation_validation.v0",
        "status": "valid" if not errors else "invalid",
        "task": "H0-BUNDLE-01",
        "offline_default": True,
        "errors": errors,
    }


def validate_required_files(root: Path, errors: list[str]) -> None:
    for rel in CONTRACTS + INVENTORIES + EXAMPLES + DOCS + AUDIT_FILES:
        if not (root / rel).is_file():
            errors.append(f"missing required file: {rel}")


def validate_inventories(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    capability = payloads.get("control/inventory/sources/source_capability_ladder.json", {})
    if capability.get("capability_grants_permission") is not False:
        errors.append("source_capability_ladder.capability_grants_permission must be false")
    for cap in capability.get("capabilities", []):
        if not isinstance(cap, Mapping):
            errors.append("source capability entries must be objects")
            continue
        if cap.get("permission_granted") is not False:
            errors.append(f"capability grants permission: {cap.get('capability_id')}")

    operation = payloads.get("control/inventory/sources/source_operation_policy.json", {})
    allowed = set(_strings(operation.get("allowed_operations_current")))
    forbidden = set(_strings(operation.get("forbidden_by_default_operations")))
    overlap = sorted(allowed & forbidden)
    if overlap:
        errors.append(f"forbidden operations allowed by default: {', '.join(overlap)}")
    for op in ("arbitrary_url_fetch", "unbounded_search", "broad_crawl", "download_binary", "mutate_public_index", "mutate_master_index", "accept_evidence_truth", "accept_public_truth"):
        if op not in forbidden:
            errors.append(f"source_operation_policy must forbid by default: {op}")

    approval = payloads.get("control/inventory/sources/source_approval_gate_policy.json", {})
    if approval.get("current_h0_bundle_approves_live_access") is not False:
        errors.append("source_approval_gate_policy must not approve live access")
    for gate in approval.get("gates", []):
        if isinstance(gate, Mapping) and gate.get("default_blocks_live_access") is not True:
            errors.append(f"approval gate must default block live access: {gate.get('gate_id')}")

    no_live = payloads.get("control/inventory/sources/source_expansion_no_live_call_policy.json", {})
    if no_live.get("h0_bundle_01_enables_live_source_calls") is not False:
        errors.append("no-live-call policy must keep H0 live source calls disabled")
    if no_live.get("new_source_records_grant_permission") is not False:
        errors.append("new source records must not grant permission")


def validate_examples(root: Path, payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    family_ids = {
        str(item.get("family_id"))
        for item in payloads.get("control/inventory/sources/source_family_registry.json", {}).get("families", [])
        if isinstance(item, Mapping)
    }
    trust_lanes = {
        str(item.get("trust_lane"))
        for item in payloads.get("control/inventory/sources/source_trust_lane_policy.json", {}).get("trust_lanes", [])
        if isinstance(item, Mapping)
    }
    depths = {
        str(item.get("depth_id"))
        for item in payloads.get("control/inventory/sources/source_index_depth_registry.json", {}).get("depths", [])
        if isinstance(item, Mapping)
    }
    capabilities = {
        str(item.get("capability_id"))
        for item in payloads.get("control/inventory/sources/source_capability_ladder.json", {}).get("capabilities", [])
        if isinstance(item, Mapping)
    }
    access_modes = set(_strings(payloads.get("control/inventory/sources/source_access_mode_policy.json", {}).get("access_modes")))
    source_ids: set[str] = set()
    for rel in EXAMPLES:
        payload = payloads.get(rel, {})
        validate_boundaries(payload, rel, errors)
        if rel.endswith("minimal_source_registry_v2.json"):
            validate_registry_example(root, payload, errors)
            continue
        source_id = str(payload.get("source_id", ""))
        if source_id in source_ids:
            errors.append(f"duplicate source_id: {source_id}")
        source_ids.add(source_id)
        missing = sorted(SOURCE_RECORD_REQUIRED - set(payload))
        if missing:
            errors.append(f"{rel} missing fields: {', '.join(missing)}")
        if payload.get("schema_version") != "source_record.v2":
            errors.append(f"{rel} schema_version must be source_record.v2")
        if payload.get("source_family") not in family_ids:
            errors.append(f"{rel} unknown source_family: {payload.get('source_family')}")
        if payload.get("trust_lane") not in trust_lanes:
            errors.append(f"{rel} unknown trust_lane: {payload.get('trust_lane')}")
        if payload.get("index_depth_current") not in depths:
            errors.append(f"{rel} unknown index_depth_current: {payload.get('index_depth_current')}")
        if payload.get("index_depth_target_future") not in depths:
            errors.append(f"{rel} unknown index_depth_target_future: {payload.get('index_depth_target_future')}")
        if payload.get("default_policy_state") not in KNOWN_POLICY_STATES:
            errors.append(f"{rel} unknown default_policy_state: {payload.get('default_policy_state')}")
        for mode in _strings(payload.get("access_modes")):
            if mode not in access_modes:
                errors.append(f"{rel} unknown access mode: {mode}")
            if mode.startswith("approved_"):
                errors.append(f"{rel} must not use approved live access mode in H0-BUNDLE-01: {mode}")
        for capability in _strings(payload.get("capability_refs")):
            if capability not in capabilities:
                errors.append(f"{rel} unknown capability: {capability}")
        truth = payload.get("truth_boundary", {})
        if isinstance(truth, Mapping):
            for key in (
                "source_record_is_public_truth",
                "source_record_is_accepted_evidence",
                "source_record_grants_live_access",
                "source_record_can_mutate_public_index",
                "source_record_can_mutate_master_index",
                "source_record_can_claim_rights_clearance",
                "source_record_can_claim_malware_safety",
                "source_record_can_claim_verified_installability",
            ):
                if truth.get(key) is not False:
                    errors.append(f"{rel} truth_boundary.{key} must be false")
        else:
            errors.append(f"{rel} truth_boundary must be an object")


def validate_registry_example(root: Path, payload: Mapping[str, Any], errors: list[str]) -> None:
    if payload.get("schema_version") != "source_registry.v2":
        errors.append("source registry example schema_version must be source_registry.v2")
    if payload.get("registry_status") not in {"example_only", "planning_only", "local_policy_only", "fixture_only", "no_live_source_access"}:
        errors.append("source registry example has invalid registry_status")
    for record in payload.get("source_records", []):
        if not isinstance(record, Mapping):
            errors.append("source registry source_records must contain objects")
            continue
        ref = record.get("source_record_ref")
        if ref and not (root / str(ref)).is_file():
            errors.append(f"source registry record ref missing: {ref}")


def validate_audit_report(root: Path, errors: list[str]) -> None:
    report = load_json_object(root / "control/audits/h0-bundle-01-source-os-foundation-v0/h0_bundle_01_report.json", errors)
    if not report:
        return
    if report.get("schema_version") != "h0_bundle_01_report.v0":
        errors.append("h0 report schema_version must be h0_bundle_01_report.v0")
    scope = report.get("source_os_scope", {})
    if isinstance(scope, Mapping):
        for key in ("live_access_enabled", "source_sync_enabled", "connector_runtime_added"):
            if scope.get(key) is not False:
                errors.append(f"h0 report source_os_scope.{key} must be false")
    validate_boundaries(report, "h0_bundle_01_report", errors)


def validate_python_imports(root: Path, errors: list[str]) -> None:
    for rel in SCAN_PYTHON:
        path = root / rel
        if not path.is_file():
            errors.append(f"missing Python file: {rel}")
            continue
        text = path.read_text(encoding="utf-8")
        for match in BANNED_IMPORT_RE.finditer(text):
            errors.append(f"forbidden import in {rel}: {match.group(1)}")


def validate_no_private_roots(root: Path, errors: list[str]) -> None:
    for rel in (".aide.local", ".local/eureka", ".cache/eureka"):
        if (root / rel).exists():
            errors.append(f"local private root must not be created: {rel}")


def validate_boundaries(payload: Mapping[str, Any], label: str, errors: list[str]) -> None:
    for path, key, value in _iter_key_values(payload):
        if key in FORBIDDEN_TRUE_KEYS and value is True:
            errors.append(f"{label}: forbidden true boundary claim at {path}")


def load_json_object(path: Path, errors: list[str]) -> Mapping[str, Any]:
    if not path.is_file():
        errors.append(f"missing JSON: {rel(path)}")
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        errors.append(f"invalid JSON: {rel(path)}: {exc}")
        return {}
    if not isinstance(payload, Mapping):
        errors.append(f"JSON must be an object: {rel(path)}")
        return {}
    return payload


def _iter_key_values(value: Any, prefix: str = ""):
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            path = f"{prefix}.{key_text}" if prefix else key_text
            yield path, key_text, child
            yield from _iter_key_values(child, path)
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from _iter_key_values(child, f"{prefix}[{index}]")


def _strings(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if item not in (None, "")]
    if value in (None, ""):
        return []
    return [str(value)]


def rel(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    args = parser.parse_args(argv)
    report = validate_repo(Path(args.repo_root))
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True), file=stdout)
    else:
        print(f"status: {report['status']}", file=stdout)
        for error in report["errors"]:
            print(f"ERROR: {error}", file=stdout)
    return 0 if report["status"] == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
