#!/usr/bin/env python3
"""Validate H1-BUNDLE-01 metadata-wave policy packs offline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]

EXPECTED_SOURCES = {
    "wayback_cdx_memento": {
        "source_record": "examples/sources/source_records/wayback_cdx_memento_source_v2.json",
        "policy_pack": "examples/connectors/h1_metadata_wave/policies/wayback_cdx_memento_policy_pack_v0.json",
        "coverage": "examples/connectors/h1_metadata_wave/coverage/wayback_cdx_memento_coverage_preview_v0.json",
        "scorecard": "examples/connectors/h1_metadata_wave/scorecards/wayback_cdx_memento_scorecard_preview_v0.json",
    },
    "github_releases": {
        "source_record": "examples/sources/source_records/github_releases_source_v2.json",
        "policy_pack": "examples/connectors/h1_metadata_wave/policies/github_releases_policy_pack_v0.json",
        "coverage": "examples/connectors/h1_metadata_wave/coverage/github_releases_coverage_preview_v0.json",
        "scorecard": "examples/connectors/h1_metadata_wave/scorecards/github_releases_scorecard_preview_v0.json",
    },
    "pypi": {
        "source_record": "examples/sources/source_records/pypi_source_v2.json",
        "policy_pack": "examples/connectors/h1_metadata_wave/policies/pypi_policy_pack_v0.json",
        "coverage": "examples/connectors/h1_metadata_wave/coverage/pypi_coverage_preview_v0.json",
        "scorecard": "examples/connectors/h1_metadata_wave/scorecards/pypi_scorecard_preview_v0.json",
    },
    "npm_registry": {
        "source_record": "examples/sources/source_records/npm_registry_source_v2.json",
        "policy_pack": "examples/connectors/h1_metadata_wave/policies/npm_registry_policy_pack_v0.json",
        "coverage": "examples/connectors/h1_metadata_wave/coverage/npm_registry_coverage_preview_v0.json",
        "scorecard": "examples/connectors/h1_metadata_wave/scorecards/npm_registry_scorecard_preview_v0.json",
    },
    "software_heritage": {
        "source_record": "examples/sources/source_records/software_heritage_source_v2.json",
        "policy_pack": "examples/connectors/h1_metadata_wave/policies/software_heritage_policy_pack_v0.json",
        "coverage": "examples/connectors/h1_metadata_wave/coverage/software_heritage_coverage_preview_v0.json",
        "scorecard": "examples/connectors/h1_metadata_wave/scorecards/software_heritage_scorecard_preview_v0.json",
    },
    "repology": {
        "source_record": "examples/sources/source_records/repology_source_v2.json",
        "policy_pack": "examples/connectors/h1_metadata_wave/policies/repology_policy_pack_v0.json",
        "coverage": "examples/connectors/h1_metadata_wave/coverage/repology_coverage_preview_v0.json",
        "scorecard": "examples/connectors/h1_metadata_wave/scorecards/repology_scorecard_preview_v0.json",
    },
    "osv": {
        "source_record": "examples/sources/source_records/osv_source_v2.json",
        "policy_pack": "examples/connectors/h1_metadata_wave/policies/osv_policy_pack_v0.json",
        "coverage": "examples/connectors/h1_metadata_wave/coverage/osv_coverage_preview_v0.json",
        "scorecard": "examples/connectors/h1_metadata_wave/scorecards/osv_scorecard_preview_v0.json",
    },
}

INVENTORY_FILES = (
    "control/inventory/source_packs/h1_metadata_wave_source_pack_policy.json",
    "control/inventory/source_packs/h1_metadata_wave_sources.json",
    "control/inventory/source_packs/h1_metadata_wave_connector_families.json",
    "control/inventory/source_packs/h1_metadata_wave_approval_gates.json",
    "control/inventory/source_packs/h1_metadata_wave_output_policy.json",
    "control/inventory/source_packs/h1_metadata_wave_truth_policy.json",
    "control/inventory/source_packs/h1_metadata_wave_no_live_call_policy.json",
)
SOURCE_PACK_EXAMPLES = (
    "examples/source_packs/h1_metadata_wave_source_pack_manifest_v0.json",
    "examples/source_packs/h1_metadata_wave_policy_pack_v0.json",
)
DOCS = (
    "docs/reference/H1_METADATA_WAVE_SOURCE_PACKS.md",
    "docs/architecture/H1_METADATA_WAVE_MODEL.md",
    "docs/operations/H1_METADATA_WAVE_POLICY_GATES.md",
    "docs/operations/H1_METADATA_WAVE_NO_LIVE_CALL_POLICY.md",
    "docs/operations/H1_METADATA_WAVE_FIXTURE_PLAN.md",
)
AUDIT_FILES = (
    "control/audits/h1-bundle-01-metadata-wave-policy-packs-v0/README.md",
    "control/audits/h1-bundle-01-metadata-wave-policy-packs-v0/h1_bundle_01_report.json",
    "control/audits/h1-bundle-01-metadata-wave-policy-packs-v0/h1_source_pack_summary.md",
    "control/audits/h1-bundle-01-metadata-wave-policy-packs-v0/h1_source_policy_gate_summary.md",
    "control/audits/h1-bundle-01-metadata-wave-policy-packs-v0/h1_connector_family_summary.md",
    "control/audits/h1-bundle-01-metadata-wave-policy-packs-v0/h1_fixture_plan.md",
    "control/audits/h1-bundle-01-metadata-wave-policy-packs-v0/h1_no_live_call_report.md",
    "control/audits/h1-bundle-01-metadata-wave-policy-packs-v0/h1_readiness_for_fixture_runtime.md",
    "control/audits/h1-bundle-01-metadata-wave-policy-packs-v0/validation.md",
    "control/audits/h1-bundle-01-metadata-wave-policy-packs-v0/generated/sample_h1_source_summary.json",
    "control/audits/h1-bundle-01-metadata-wave-policy-packs-v0/generated/sample_h1_source_summary.md",
)
H1_PYTHON_FILES = (
    "scripts/validate_h1_metadata_wave_policy_packs.py",
    "scripts/summarize_h1_metadata_wave_sources.py",
)
ALLOWED_CURRENT_OPERATIONS = {
    "inspect_fixture",
    "normalize_fixture",
    "record_source_policy",
    "record_source_metadata_preview",
    "create_coverage_preview",
    "create_scorecard_preview",
}
FORBIDDEN_TRUE_KEYS = {
    "live_access_enabled",
    "source_sync_enabled",
    "connector_runtime_enabled",
    "approved_live_probe_enabled",
    "policy_pack_grants_live_access",
    "source_pack_is_truth",
    "source_pack_is_accepted_evidence",
    "source_pack_is_imported_state",
    "capability_grants_permission",
    "coverage_preview_is_exhaustive",
    "coverage_claims_exhaustive_global_coverage",
    "coverage_manifest_is_exhaustive_global_coverage",
    "scorecard_preview_is_production_ready",
    "scorecard_claims_production_readiness",
    "scorecard_auto_approves_future_connectors",
    "production_ready",
    "auto_approves_future_connectors",
    "public_index_mutation_allowed",
    "master_index_mutation_allowed",
    "public_index_mutated",
    "master_index_mutated",
    "mutated_public_index",
    "mutated_master_index",
    "rights_clearance_claimed",
    "malware_safety_claimed",
    "verified_installability_claimed",
    "source_record_grants_live_access",
    "source_record_can_mutate_public_index",
    "source_record_can_mutate_master_index",
    "source_record_can_claim_rights_clearance",
    "source_record_can_claim_malware_safety",
    "source_record_can_claim_verified_installability",
    "coverage_record_can_mutate_public_index",
    "coverage_record_can_mutate_master_index",
    "coverage_record_can_claim_rights_clearance",
    "coverage_record_can_claim_malware_safety",
    "coverage_record_can_claim_verified_installability",
    "source_pack_is_accepted_truth",
    "source_pack_is_submitted",
    "source_pack_can_mutate_public_index",
    "source_pack_can_mutate_master_index",
}
BANNED_IMPORT_RE = re.compile(
    r"^\s*(?:from|import)\s+"
    r"(requests|urllib|httpx|aiohttp|socket|ftplib|smtplib|webbrowser|selenium|playwright|openai|anthropic)\b",
    re.MULTILINE,
)
SECRET_KEY_RE = re.compile(
    r'"[^"]*(api[_-]?key|api[_-]?token|access[_-]?token|auth[_-]?token|client_secret|password|private_key|cookie)[^"]*"\s*:',
    re.IGNORECASE,
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print JSON validation result.")
    args = parser.parse_args(argv)
    result = validate_repo(REPO_ROOT)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print("H1 metadata wave policy pack validation", file=stdout)
        print(f"status: {result['status']}", file=stdout)
        for error in result["errors"]:
            print(f"ERROR: {error}", file=stdout)
    return 0 if result["status"] == "valid" else 1


def validate_repo(root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    payloads: dict[str, dict[str, Any]] = {}
    required_paths = list(INVENTORY_FILES + SOURCE_PACK_EXAMPLES + DOCS + AUDIT_FILES + H1_PYTHON_FILES)
    for source in EXPECTED_SOURCES.values():
        required_paths.extend(source.values())
    for rel in required_paths:
        path = root / rel
        if not path.is_file():
            errors.append(f"missing required file: {rel}")
            continue
        if path.suffix == ".json":
            payloads[rel] = load_json_object(path, errors)
    known = load_h0_known_values(root, errors)
    validate_inventory(payloads, known, errors)
    for source_id, paths in EXPECTED_SOURCES.items():
        errors.extend(f"{paths['source_record']}: {item}" for item in validate_source_record(payloads.get(paths["source_record"], {}), source_id, known))
        errors.extend(f"{paths['policy_pack']}: {item}" for item in validate_policy_pack(payloads.get(paths["policy_pack"], {}), source_id))
        errors.extend(f"{paths['coverage']}: {item}" for item in validate_coverage_preview(payloads.get(paths["coverage"], {}), source_id, known))
        errors.extend(f"{paths['scorecard']}: {item}" for item in validate_scorecard_preview(payloads.get(paths["scorecard"], {}), source_id))
    for rel in SOURCE_PACK_EXAMPLES:
        errors.extend(f"{rel}: {item}" for item in validate_source_pack_example(payloads.get(rel, {})))
    validate_audit_report(payloads.get("control/audits/h1-bundle-01-metadata-wave-policy-packs-v0/h1_bundle_01_report.json", {}), errors)
    validate_json_text_security(root, errors)
    validate_python_no_network(root, errors)
    validate_summary_script(root, errors)
    validate_no_private_roots(root, errors)
    return {
        "schema_version": "h1_metadata_wave_policy_pack_validation.v0",
        "status": "valid" if not errors else "invalid",
        "task": "H1-BUNDLE-01",
        "source_count": len(EXPECTED_SOURCES),
        "offline_default": True,
        "network_calls_made": False,
        "errors": errors,
    }


def load_json_object(path: Path, errors: list[str]) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        errors.append(f"invalid JSON: {path.relative_to(REPO_ROOT)}: {exc}")
        return {}
    if not isinstance(payload, dict):
        errors.append(f"JSON root must be object: {path.relative_to(REPO_ROOT)}")
        return {}
    return payload


def load_h0_known_values(root: Path, errors: list[str]) -> dict[str, set[str]]:
    source_families = load_json_object(root / "control/inventory/sources/source_family_registry.json", errors)
    connector_families = load_json_object(root / "control/inventory/connectors/connector_family_registry.json", errors)
    trust_lanes = load_json_object(root / "control/inventory/sources/source_trust_lane_policy.json", errors)
    index_depths = load_json_object(root / "control/inventory/sources/source_index_depth_registry.json", errors)
    access_modes = load_json_object(root / "control/inventory/sources/source_access_mode_policy.json", errors)
    return {
        "source_families": {str(item.get("family_id")) for item in source_families.get("families", []) if isinstance(item, Mapping)},
        "connector_families": {str(item.get("family_id")) for item in connector_families.get("families", []) if isinstance(item, Mapping)},
        "trust_lanes": {str(item.get("trust_lane")) for item in trust_lanes.get("trust_lanes", []) if isinstance(item, Mapping)},
        "index_depths": {str(item.get("depth_id")) for item in index_depths.get("depths", []) if isinstance(item, Mapping)},
        "access_modes": set(str(item) for item in access_modes.get("access_modes", [])),
    }


def validate_inventory(payloads: Mapping[str, Mapping[str, Any]], known: Mapping[str, set[str]], errors: list[str]) -> None:
    policy = payloads.get("control/inventory/source_packs/h1_metadata_wave_source_pack_policy.json", {})
    if policy.get("current_status") != "policy_pack_only":
        errors.append("source pack policy must remain policy_pack_only")
    for key in ("live_access_enabled", "source_sync_enabled", "connector_runtime_enabled", "approved_live_probe_enabled", "source_pack_import_enabled"):
        if policy.get(key) is not False:
            errors.append(f"h1_metadata_wave_source_pack_policy.{key} must be false")
    sources_payload = payloads.get("control/inventory/source_packs/h1_metadata_wave_sources.json", {})
    sources = sources_payload.get("sources", [])
    if not isinstance(sources, list):
        errors.append("h1_metadata_wave_sources.sources must be a list")
        return
    source_ids = [str(item.get("source_id")) for item in sources if isinstance(item, Mapping)]
    if sorted(source_ids) != sorted(EXPECTED_SOURCES):
        errors.append(f"H1 source inventory must contain exactly {sorted(EXPECTED_SOURCES)}")
    if len(source_ids) != len(set(source_ids)):
        errors.append("H1 source inventory source IDs must be unique")
    for item in sources:
        if not isinstance(item, Mapping):
            errors.append("H1 source inventory entries must be objects")
            continue
        source_id = str(item.get("source_id", ""))
        if item.get("source_family") not in known["source_families"]:
            errors.append(f"{source_id}: unknown source_family {item.get('source_family')}")
        if item.get("connector_family") not in known["connector_families"]:
            errors.append(f"{source_id}: unknown connector_family {item.get('connector_family')}")
        if item.get("trust_lane") not in known["trust_lanes"]:
            errors.append(f"{source_id}: unknown trust_lane {item.get('trust_lane')}")
        for depth_key in ("current_index_depth", "target_index_depth_future"):
            if item.get(depth_key) not in known["index_depths"]:
                errors.append(f"{source_id}: unknown {depth_key} {item.get(depth_key)}")
        if item.get("current_access_mode") not in {"no_autonomous_access", "committed_fixture_only"}:
            errors.append(f"{source_id}: current access mode must be no-autonomous or fixture-only")
    for rel in (
        "control/inventory/source_packs/h1_metadata_wave_connector_families.json",
        "control/inventory/source_packs/h1_metadata_wave_approval_gates.json",
        "control/inventory/source_packs/h1_metadata_wave_output_policy.json",
        "control/inventory/source_packs/h1_metadata_wave_truth_policy.json",
        "control/inventory/source_packs/h1_metadata_wave_no_live_call_policy.json",
    ):
        errors.extend(f"{rel}: {item}" for item in detect_forbidden_boundary_claims(payloads.get(rel, {})))


def validate_source_record(record: Mapping[str, Any], expected_source_id: str | None = None, known: Mapping[str, set[str]] | None = None) -> list[str]:
    errors: list[str] = []
    known = known or {}
    source_id = str(record.get("source_id", ""))
    if record.get("schema_version") != "source_record.v2":
        errors.append("schema_version must be source_record.v2")
    if expected_source_id and source_id != expected_source_id:
        errors.append(f"source_id must be {expected_source_id}")
    if source_id not in EXPECTED_SOURCES:
        errors.append(f"unexpected H1 source_id: {source_id}")
    _check_known(record.get("source_family"), known.get("source_families", set()), "source_family", errors)
    connector_values = set(record.get("connector_family_refs", []))
    if record.get("connector_family"):
        connector_values.add(str(record.get("connector_family")))
    for connector_family in connector_values:
        _check_known(connector_family, known.get("connector_families", set()), "connector_family", errors)
    _check_known(record.get("trust_lane"), known.get("trust_lanes", set()), "trust_lane", errors)
    for depth_key in ("current_index_depth", "target_index_depth_future", "index_depth_current", "index_depth_target_future"):
        _check_known(record.get(depth_key), known.get("index_depths", set()), depth_key, errors)
    if record.get("current_access_mode") not in {"no_autonomous_access", "committed_fixture_only"}:
        errors.append("current_access_mode must be no_autonomous_access or committed_fixture_only")
    for key in ("live_access_enabled", "source_sync_enabled", "connector_runtime_enabled", "approved_live_probe_enabled"):
        if record.get(key) is not False:
            errors.append(f"{key} must be false")
    errors.extend(detect_forbidden_boundary_claims(record))
    return errors


def validate_policy_pack(pack: Mapping[str, Any], expected_source_id: str | None = None) -> list[str]:
    errors: list[str] = []
    if pack.get("schema_version") != "h1_metadata_wave_policy_pack.v0":
        errors.append("schema_version must be h1_metadata_wave_policy_pack.v0")
    if expected_source_id and pack.get("source_id") != expected_source_id:
        errors.append(f"source_id must be {expected_source_id}")
    if pack.get("current_status") != "policy_pack_only":
        errors.append("current_status must be policy_pack_only")
    if pack.get("policy_pack_grants_live_access") is not False:
        errors.append("policy_pack_grants_live_access must be false")
    allowed = set(str(item) for item in pack.get("allowed_current_operations", []))
    extra = sorted(allowed - ALLOWED_CURRENT_OPERATIONS)
    if extra:
        errors.append(f"allowed_current_operations contains forbidden operations: {extra}")
    errors.extend(detect_forbidden_boundary_claims(pack))
    return errors


def validate_coverage_preview(record: Mapping[str, Any], expected_source_id: str | None = None, known: Mapping[str, set[str]] | None = None) -> list[str]:
    errors: list[str] = []
    known = known or {}
    if record.get("schema_version") != "source_coverage_ledger.v0":
        errors.append("schema_version must be source_coverage_ledger.v0")
    if expected_source_id and record.get("source_id") != expected_source_id:
        errors.append(f"source_id must be {expected_source_id}")
    _check_known(record.get("source_family"), known.get("source_families", set()), "source_family", errors)
    if record.get("coverage_basis") not in {"example_only", "policy_pack_only"}:
        errors.append("coverage_basis must be example_only or policy_pack_only")
    if record.get("coverage_depth_current") not in {"D0_source_known", "D1_catalog_indexed"}:
        errors.append("coverage_depth_current must be D0 or D1 for H1-BUNDLE-01")
    if record.get("records_seen") not in (0, None):
        errors.append("records_seen must be 0 unless committed fixtures exist")
    if record.get("live_access_enabled") is not False:
        errors.append("live_access_enabled must be false")
    errors.extend(detect_forbidden_boundary_claims(record))
    return errors


def validate_scorecard_preview(scorecard: Mapping[str, Any], expected_source_id: str | None = None) -> list[str]:
    errors: list[str] = []
    if scorecard.get("schema_version") != "connector_scorecard.v0":
        errors.append("schema_version must be connector_scorecard.v0")
    if expected_source_id and scorecard.get("source_id") != expected_source_id:
        errors.append(f"source_id must be {expected_source_id}")
    required_statuses = {
        "fixture_replay_status": "not_started",
        "policy_evaluation_status": "planned",
        "live_probe_envelope_status": "not_approved",
        "source_cache_mapping_status": "planned",
        "evidence_mapping_status": "planned",
        "quality_delta_status": "not_started",
    }
    for key, expected in required_statuses.items():
        if scorecard.get(key) != expected:
            errors.append(f"{key} must be {expected}")
    if scorecard.get("production_ready") is not False:
        errors.append("production_ready must be false")
    if scorecard.get("auto_approves_future_connectors") is not False:
        errors.append("auto_approves_future_connectors must be false")
    errors.extend(detect_forbidden_boundary_claims(scorecard))
    return errors


def validate_source_pack_example(payload: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    schema = payload.get("schema_version")
    if schema not in {"source_pack_manifest.v0", "h1_metadata_wave_policy_pack.v0"}:
        errors.append("unexpected source pack example schema_version")
    source_ids = set(str(item) for item in payload.get("source_ids", []))
    if source_ids and source_ids != set(EXPECTED_SOURCES):
        errors.append("aggregate policy pack must reference all seven H1 source IDs")
    if schema == "source_pack_manifest.v0":
        if payload.get("pack_status") != "draft_only":
            errors.append("source pack manifest must remain draft_only")
        refs = payload.get("source_records", [])
        if isinstance(refs, list) and len(refs) != len(EXPECTED_SOURCES):
            errors.append("source pack manifest must reference all seven source records")
    errors.extend(detect_forbidden_boundary_claims(payload))
    return errors


def validate_audit_report(report: Mapping[str, Any], errors: list[str]) -> None:
    if not report:
        return
    if report.get("schema_version") != "h1_bundle_01_report.v0":
        errors.append("h1 bundle 01 report schema_version mismatch")
    if sorted(report.get("sources", [])) != sorted(EXPECTED_SOURCES):
        errors.append("h1 bundle 01 report must list all seven H1 sources")
    wave_scope = report.get("wave_scope", {})
    if isinstance(wave_scope, Mapping):
        for key in ("live_access_enabled", "source_sync_enabled", "connector_runtime_enabled", "network_calls_made"):
            if wave_scope.get(key) is not False:
                errors.append(f"h1 bundle 01 report wave_scope.{key} must be false")
    errors.extend(f"h1_bundle_01_report: {item}" for item in detect_forbidden_boundary_claims(report))


def detect_forbidden_boundary_claims(value: Any, path: str = "$") -> list[str]:
    errors: list[str] = []
    if isinstance(value, Mapping):
        for key, item in value.items():
            key_text = str(key)
            next_path = f"{path}.{key_text}"
            if key_text in FORBIDDEN_TRUE_KEYS and item is True:
                errors.append(f"{next_path} must not be true")
            errors.extend(detect_forbidden_boundary_claims(item, next_path))
    elif isinstance(value, list):
        for index, item in enumerate(value):
            errors.extend(detect_forbidden_boundary_claims(item, f"{path}[{index}]"))
    return errors


def validate_json_text_security(root: Path, errors: list[str]) -> None:
    rels = list(INVENTORY_FILES + SOURCE_PACK_EXAMPLES)
    for source in EXPECTED_SOURCES.values():
        rels.extend(source.values())
    for rel in rels:
        path = root / rel
        if not path.is_file() or path.suffix != ".json":
            continue
        text = path.read_text(encoding="utf-8")
        if SECRET_KEY_RE.search(text):
            errors.append(f"{rel}: credential/cookie/token-like key is not allowed")


def validate_python_no_network(root: Path, errors: list[str]) -> None:
    for rel in H1_PYTHON_FILES:
        path = root / rel
        if not path.is_file():
            errors.append(f"missing H1 Python file: {rel}")
            continue
        text = path.read_text(encoding="utf-8")
        match = BANNED_IMPORT_RE.search(text)
        if match:
            errors.append(f"{rel}: forbidden network/model/browser import {match.group(1)}")
        if ("url" + "open(") in text or (".Re" + "quest(") in text:
            errors.append(f"{rel}: forbidden live-call primitive")


def validate_summary_script(root: Path, errors: list[str]) -> None:
    script = root / "scripts/summarize_h1_metadata_wave_sources.py"
    if not script.is_file():
        errors.append("missing summary script")
        return
    result = subprocess.run(
        [sys.executable, str(script), "--check", "--json"],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
        timeout=120,
    )
    if result.returncode != 0:
        errors.append(f"summary script failed: {result.stdout}{result.stderr}")
        return
    try:
        summary = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        errors.append(f"summary script did not emit JSON: {exc}")
        return
    if summary.get("source_count") != len(EXPECTED_SOURCES):
        errors.append("summary script must report seven H1 sources")
    if summary.get("live_access_enabled_count") != 0:
        errors.append("summary script must report zero live access enabled sources")


def validate_no_private_roots(root: Path, errors: list[str]) -> None:
    for rel in (".aide.local", ".local/eureka", ".cache/eureka"):
        if (root / rel).exists():
            errors.append(f"local private-state root must not exist: {rel}")


def _check_known(value: Any, known_values: set[str], label: str, errors: list[str]) -> None:
    if not value:
        errors.append(f"{label} is required")
        return
    if known_values and str(value) not in known_values:
        errors.append(f"unknown {label}: {value}")


if __name__ == "__main__":
    raise SystemExit(main())
