#!/usr/bin/env python3
"""Validate H14 Source OS rollup dry-run artifacts offline."""

from __future__ import annotations

import importlib
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.connectors.h14_source_discovery.rollup_dry_run_common import (  # noqa: E402
    H14_SOURCE_IDS,
    REQUEST_FORBIDDEN_TRUE_KEYS,
    build_h14_rollup_blocked_result,
    build_h14_rollup_dry_run_result,
    build_h14_source_discovery_rollup_dry_run_request,
    detect_h14_registry_or_pack_mutation_violations,
    detect_h14_rollup_product_boundary_violations,
    detect_h14_rollup_truth_boundary_violations,
    load_h14_rollup_inputs,
    load_h14_rollup_policy_bundle,
    validate_h14_rollup_dry_run_request,
)

CONTRACTS = [
    "contracts/connectors/h14_source_discovery_rollup_dry_run_request.v0.json",
    "contracts/connectors/h14_source_discovery_rollup_dry_run_result.v0.json",
    "contracts/connectors/h14_source_discovery_rollup_output_bundle.v0.json",
    "contracts/connectors/h14_source_os_rollup_health_summary.v0.json",
]
POLICIES = [
    "control/inventory/connectors/h14_source_discovery_rollup_dry_run_policy.json",
    "control/inventory/connectors/h14_source_discovery_rollup_allowed_requests.json",
    "control/inventory/connectors/h14_source_discovery_rollup_operation_policy.json",
    "control/inventory/connectors/h14_source_discovery_rollup_input_policy.json",
    "control/inventory/connectors/h14_source_discovery_rollup_output_policy.json",
    "control/inventory/connectors/h14_source_discovery_rollup_path_policy.json",
    "control/inventory/connectors/h14_source_discovery_rollup_review_policy.json",
    "control/inventory/connectors/h14_source_discovery_rollup_truth_policy.json",
    "control/inventory/connectors/h14_source_discovery_rollup_no_live_call_policy.json",
    "control/inventory/connectors/h14_source_discovery_rollup_no_pack_import_export_policy.json",
    "control/inventory/connectors/h14_source_discovery_rollup_registry_mutation_policy.json",
    "control/inventory/connectors/h14_source_discovery_rollup_kill_switch_policy.json",
]
RUNTIME_MODULES = [
    "rollup_dry_run_common.py",
    "rollup_source_needs.py",
    "rollup_source_candidates.py",
    "rollup_source_discovery_candidates.py",
    "rollup_source_pack_manifests.py",
    "rollup_connector_pack_manifests.py",
    "rollup_coverage_manifests.py",
    "rollup_connector_scorecards.py",
    "rollup_reliability_freshness.py",
    "rollup_dispute_revocation.py",
    "rollup_lineage_provenance.py",
    "rollup_pack_import_export_boundary.py",
    "rollup_h0_h13_coverage.py",
    "rollup_h0_h13_scorecards.py",
]
EXAMPLES = [
    "examples/connectors/h14_source_discovery/rollup_dry_run/blocked_rollup_dry_run_request_v0.json",
    "examples/connectors/h14_source_discovery/rollup_dry_run/approved_source_need_rollup_request_v0.json",
    "examples/connectors/h14_source_discovery/rollup_dry_run/approved_source_candidate_rollup_request_v0.json",
    "examples/connectors/h14_source_discovery/rollup_dry_run/approved_coverage_manifest_rollup_request_v0.json",
    "examples/connectors/h14_source_discovery/rollup_dry_run/approved_scorecard_rollup_request_v0.json",
    "examples/connectors/h14_source_discovery/rollup_dry_run/approved_source_pack_manifest_rollup_request_v0.json",
    "examples/connectors/h14_source_discovery/rollup_dry_run/approved_dispute_revocation_rollup_request_v0.json",
    "examples/connectors/h14_source_discovery/rollup_dry_run/approved_lineage_provenance_rollup_request_v0.json",
    "examples/connectors/h14_source_discovery/rollup_dry_run/approved_pack_boundary_rollup_request_v0.json",
    "examples/connectors/h14_source_discovery/rollup_dry_run_results/blocked_rollup_dry_run_result_v0.json",
    "examples/connectors/h14_source_discovery/rollup_dry_run_outputs/source_os_rollup_health_from_h14_rollup_v0.json",
]
AUDIT_ROOT = "control/audits/h14-bundle-03-source-discovery-rollup-dry-runs-v0"
AUDIT_FILES = [
    "README.md", "h14_bundle_03_report.json", "rollup_dry_run_policy_review.md", "rollup_dry_run_execution_report.md",
    "source_need_rollup_preview.md", "source_candidate_rollup_preview.md", "source_discovery_candidate_rollup_preview.md",
    "source_pack_manifest_rollup_preview.md", "connector_pack_manifest_rollup_preview.md", "coverage_manifest_rollup_preview.md",
    "connector_scorecard_rollup_preview.md", "reliability_freshness_rollup_preview.md", "dispute_revocation_rollup_preview.md",
    "lineage_provenance_rollup_preview.md", "pack_import_export_boundary_rollup_preview.md",
    "h0_h13_coverage_rollup_preview.md", "h0_h13_scorecard_rollup_preview.md", "source_cache_candidate_preview.md",
    "evidence_candidate_preview.md", "review_queue_seed_preview.md", "source_os_rollup_health_summary.md",
    "no_live_call_report.md", "no_pack_import_export_report.md", "registry_mutation_report.md",
    "h14_rollup_dry_run_blocked_or_completed_summary.md", "validation.md",
    "generated/sample_h14_rollup_dry_run_result.json", "generated/sample_h14_source_need_candidate_from_rollup.json",
    "generated/sample_h14_source_candidate_candidate_from_rollup.json", "generated/sample_h14_source_discovery_candidate_from_rollup.json",
    "generated/sample_h14_source_pack_manifest_candidate_from_rollup.json", "generated/sample_h14_connector_pack_manifest_candidate_from_rollup.json",
    "generated/sample_h14_coverage_manifest_candidate_from_rollup.json", "generated/sample_h14_connector_scorecard_candidate_from_rollup.json",
    "generated/sample_h14_source_reliability_freshness_candidate_from_rollup.json",
    "generated/sample_h14_source_dispute_revocation_candidate_from_rollup.json",
    "generated/sample_h14_source_lineage_provenance_candidate_from_rollup.json",
    "generated/sample_h14_pack_import_export_boundary_candidate_from_rollup.json",
    "generated/sample_h14_source_cache_candidate_from_rollup.json", "generated/sample_h14_evidence_candidate_preview_from_rollup.json",
    "generated/sample_h14_review_queue_seed_from_rollup.json", "generated/sample_h14_source_os_rollup_health_summary.json",
    "generated/sample_h14_rollup_summary.md",
]
BANNED_IMPORT_RE = re.compile(r"^\s*(?:from|import)\s+(requests|httpx|aiohttp|urllib|socket|ftplib|smtplib|webbrowser|selenium|playwright|openai|anthropic)\b", re.MULTILINE)
FORBIDDEN_TRUE_KEYS = set(REQUEST_FORBIDDEN_TRUE_KEYS) | {
    "source_discovery_runtime_enabled", "source_discovery_runtime_used", "live_access_enabled", "live_access_used",
    "network_access_enabled", "network_used", "model_provider_enabled", "model_provider_used", "source_sync_enabled",
    "source_sync_used", "crawling_enabled", "scraping_enabled", "source_registry_mutation_enabled",
    "connector_registry_mutation_enabled", "registry_mutation_performed", "source_pack_export_enabled",
    "source_pack_import_enabled", "connector_pack_export_enabled", "connector_pack_import_enabled",
    "pack_export_import_performed", "pack_signing_enabled", "pack_publication_enabled", "source_cache_write_enabled",
    "source_cache_write_performed", "evidence_write_enabled", "evidence_write_performed", "review_queue_write_enabled",
    "review_queue_write_performed", "public_index_write_enabled", "public_index_write_performed",
    "master_index_write_enabled", "master_index_write_performed", "accepted_source_truth", "accepted_candidate_truth",
    "accepted_public_record", "source_need_candidate_is_source_approval", "source_candidate_candidate_is_source_truth",
    "source_discovery_candidate_is_registry_mutation", "source_pack_manifest_candidate_is_exported_pack",
    "connector_pack_manifest_candidate_is_connector_approval", "coverage_manifest_candidate_is_exhaustive",
    "connector_scorecard_candidate_is_connector_approval", "source_reliability_freshness_candidate_is_truth",
    "source_dispute_revocation_candidate_is_accepted_truth", "source_lineage_provenance_candidate_is_lineage_truth",
    "pack_import_export_boundary_candidate_grants_permission", "source_cache_candidate_is_accepted_source",
    "evidence_candidate_preview_is_accepted_evidence", "review_seed_is_review_decision", "production_readiness_claimed",
    "launch_readiness_claimed", "rights_clearance_claimed", "legal_approval_claimed", "source_completeness_claimed",
}
FORBIDDEN_PAYLOAD_KEYS = {
    "network_output", "api_output", "model_provider_output", "crawled_data", "scraped_data",
    "source_discovery_runtime_output", "source_registry_write", "connector_registry_write", "source_cache_write",
    "evidence_write", "public_index_write", "master_index_write", "imported_pack", "exported_pack", "signed_pack",
    "private_data_payload", "artifact_payload",
}


def validate_repo(root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    required = CONTRACTS + POLICIES + EXAMPLES + [
        "scripts/run_h14_source_discovery_rollup_dry_run.py",
        "scripts/validate_h14_source_discovery_rollup_dry_run.py",
        "scripts/summarize_h14_source_discovery_rollup_outputs.py",
    ] + [f"{AUDIT_ROOT}/{name}" for name in AUDIT_FILES]
    for rel in required:
        path = root / rel
        if not path.exists():
            errors.append(f"missing required artifact: {rel}")
        elif path.suffix == ".json":
            _scan_json_boundaries(_load_json(path, errors), rel, errors)
    runtime_root = root / "runtime/connectors/h14_source_discovery"
    for module in RUNTIME_MODULES:
        if not (runtime_root / module).exists():
            errors.append(f"missing runtime module: {module}")
    for module_name in [name[:-3] for name in RUNTIME_MODULES]:
        try:
            importlib.import_module(f"runtime.connectors.h14_source_discovery.{module_name}")
        except Exception as exc:  # noqa: BLE001
            errors.append(f"runtime module import failed {module_name}: {exc}")
    bundle = load_h14_rollup_policy_bundle(root)
    _validate_policies(bundle, errors)
    approved_request = build_h14_source_discovery_rollup_dry_run_request("source_need_registry", "example_source_need_rollup", bundle)
    validation = validate_h14_rollup_dry_run_request(approved_request, bundle)
    if not validation["approved"]:
        errors.append(f"approved source_need rollup did not validate: {validation['blocked_reasons']}")
    inputs = load_h14_rollup_inputs(None, bundle)
    result = build_h14_rollup_dry_run_result("source_need_registry", inputs, bundle)
    for detector in (detect_h14_rollup_truth_boundary_violations, detect_h14_rollup_product_boundary_violations, detect_h14_registry_or_pack_mutation_violations):
        errors.extend(detector(result, bundle))
    blocked_request = build_h14_source_discovery_rollup_dry_run_request("source_discovery_policy", "example_source_discovery_rollup", bundle)
    blocked = build_h14_rollup_blocked_result(blocked_request, validate_h14_rollup_dry_run_request(blocked_request, bundle)["blocked_reasons"], bundle)
    if not str(blocked["result_status"]).startswith("blocked"):
        errors.append("blocked request did not produce blocked result")
    _scan_runtime(root, errors)
    _run_check([sys.executable, "scripts/run_h14_source_discovery_rollup_dry_run.py", "--source-id", "source_discovery_policy", "--request-key", "example_source_discovery_rollup", "--check"], root, errors)
    _run_check([sys.executable, "scripts/run_h14_source_discovery_rollup_dry_run.py", "--source-id", "source_need_registry", "--request-key", "example_source_need_rollup", "--check"], root, errors)
    _run_check([sys.executable, "scripts/summarize_h14_source_discovery_rollup_outputs.py", "--input", "examples/connectors/h14_source_discovery/rollup_dry_run_results", "--check"], root, errors)
    _check_forbidden_output_roots(root, errors)
    for rel in (".aide.local", ".local/eureka", ".cache/eureka", "source_discovery_runtime", "pack_import_staging", "pack_export_staging", "source_registry_mutation", "connector_registry_mutation", "external_source_fetch", "local_sources", "private_sources"):
        if (root / rel).exists():
            errors.append(f"forbidden local/private/runtime root exists: {rel}")
    return {
        "schema_version": "h14_source_discovery_rollup_dry_run_validation.v0",
        "status": "valid" if not errors else "invalid",
        "source_count": len(H14_SOURCE_IDS),
        "network_calls_made": False,
        "model_provider_calls_made": False,
        "source_discovery_runtime_used": False,
        "pack_export_import_used": False,
        "registry_mutation_used": False,
        "errors": errors,
        "warnings": warnings,
    }


def main() -> int:
    result = validate_repo()
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["status"] == "valid" else 1


def _validate_policies(bundle: Mapping[str, Any], errors: list[str]) -> None:
    for key in ("dry_run_policy", "operation_policy"):
        for item_key, value in bundle.get(key, {}).items():
            if item_key.endswith("_enabled") and value is True:
                errors.append(f"{key} enables forbidden operation: {item_key}")
    for source in bundle.get("allowed_requests", {}).get("sources", []):
        if source.get("rollup_dry_run_approved") is True and source.get("approval_status") != "approved_for_rollup_dry_run":
            errors.append(f"rollup dry-run enabled without approval: {source.get('source_id')}")
        for key, value in source.items():
            if key.endswith("_approved") and key != "rollup_dry_run_approved" and value is not False:
                errors.append(f"{source.get('source_id')} approval flag must remain false: {key}")
    if bundle.get("kill_switch_policy", {}).get("kill_switch_defaults_fail_closed") is not True:
        errors.append("kill switch does not default fail-closed")


def _scan_runtime(root: Path, errors: list[str]) -> None:
    runtime_root = root / "runtime/connectors/h14_source_discovery"
    for path in runtime_root.glob("rollup_*.py"):
        text = path.read_text(encoding="utf-8")
        if BANNED_IMPORT_RE.search(text):
            errors.append(f"runtime module imports forbidden network/provider/browser library: {path}")
        for forbidden in ("httpx.", "aiohttp.", "openai.", "anthropic.", "selenium", "playwright", "webbrowser."):
            if forbidden in text:
                errors.append(f"runtime module contains forbidden external call marker: {path} :: {forbidden}")


def _scan_json_boundaries(value: Any, label: str, errors: list[str]) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            key_text = str(key)
            if key_text in FORBIDDEN_TRUE_KEYS and item is True:
                errors.append(f"{label} forbidden true value: {key_text}")
            if key_text in FORBIDDEN_PAYLOAD_KEYS:
                errors.append(f"{label} forbidden output/private/artifact key {key_text}")
            _scan_json_boundaries(item, label, errors)
    elif isinstance(value, list):
        for item in value:
            _scan_json_boundaries(item, label, errors)


def _check_forbidden_output_roots(root: Path, errors: list[str]) -> None:
    checks = [
        [sys.executable, "scripts/run_h14_source_discovery_rollup_dry_run.py", "--source-id", "source_need_registry", "--request-key", "example_source_need_rollup", "--output", "site/dist/h14.json"],
        [sys.executable, "scripts/run_h14_source_discovery_rollup_dry_run.py", "--source-id", "source_need_registry", "--request-key", "example_source_need_rollup", "--output", "data/public_index/h14.json"],
        [sys.executable, "scripts/run_h14_source_discovery_rollup_dry_run.py", "--source-id", "source_need_registry", "--request-key", "example_source_need_rollup", "--output", "source_registry_mutation/h14.json"],
        [sys.executable, "scripts/run_h14_source_discovery_rollup_dry_run.py", "--source-id", "source_need_registry", "--request-key", "example_source_need_rollup", "--output", "pack_import_staging/h14.json"],
    ]
    for cmd in checks:
        proc = subprocess.run(cmd, cwd=root, text=True, capture_output=True, check=False)
        if proc.returncode == 0:
            errors.append(f"forbidden output root was not rejected: {cmd[-1]}")


def _run_check(cmd: list[str], root: Path, errors: list[str]) -> None:
    proc = subprocess.run(cmd, cwd=root, text=True, capture_output=True, check=False)
    if proc.returncode != 0:
        errors.append(f"command failed: {' '.join(cmd)} :: {proc.stdout} {proc.stderr}")


def _load_json(path: Path, errors: list[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        errors.append(f"invalid JSON {path}: {exc}")
        return {}


if __name__ == "__main__":
    raise SystemExit(main())
