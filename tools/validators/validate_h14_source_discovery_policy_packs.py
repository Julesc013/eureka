#!/usr/bin/env python3
"""Validate H14-BUNDLE-01 source discovery policy packs offline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any, Mapping, Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[2]
SOURCE_IDS = [
    "source_need_registry",
    "source_candidate_registry",
    "source_discovery_policy",
    "source_pack_manifest",
    "connector_pack_manifest",
    "coverage_manifest",
    "connector_scorecard",
    "source_reliability_freshness",
    "source_dispute_revocation",
    "source_lineage_provenance",
]
POLICY_BLOCKED_SOURCE_ID = "h14_policy_blocked"
ALL_SOURCE_IDS = SOURCE_IDS + [POLICY_BLOCKED_SOURCE_ID]
SOURCE_FILES = {source_id: f"{source_id}_source_v2.json" for source_id in SOURCE_IDS}
SOURCE_FILES[POLICY_BLOCKED_SOURCE_ID] = "h14_policy_blocked_source_v2.json"
POLICY_FILES_BY_SOURCE = {
    "source_need_registry": "source_need_registry_policy_pack_v0.json",
    "source_candidate_registry": "source_candidate_registry_policy_pack_v0.json",
    "source_discovery_policy": "source_discovery_policy_pack_v0.json",
    "source_pack_manifest": "source_pack_manifest_policy_pack_v0.json",
    "connector_pack_manifest": "connector_pack_manifest_policy_pack_v0.json",
    "coverage_manifest": "coverage_manifest_policy_pack_v0.json",
    "connector_scorecard": "connector_scorecard_policy_pack_v0.json",
    "source_reliability_freshness": "source_reliability_freshness_policy_pack_v0.json",
    "source_dispute_revocation": "source_dispute_revocation_policy_pack_v0.json",
    "source_lineage_provenance": "source_lineage_provenance_policy_pack_v0.json",
    "h14_policy_blocked": "h14_policy_blocked_pack_v0.json",
}
INVENTORY_FILES = (
    "control/inventory/source_packs/h14_source_discovery_pack_policy.json",
    "control/inventory/source_packs/h14_source_discovery_sources.json",
    "control/inventory/source_packs/h14_source_discovery_connector_families.json",
    "control/inventory/source_packs/h14_source_need_policy.json",
    "control/inventory/source_packs/h14_source_candidate_policy.json",
    "control/inventory/source_packs/h14_source_discovery_policy.json",
    "control/inventory/source_packs/h14_source_pack_manifest_policy.json",
    "control/inventory/source_packs/h14_connector_pack_manifest_policy.json",
    "control/inventory/source_packs/h14_coverage_manifest_policy.json",
    "control/inventory/source_packs/h14_connector_scorecard_policy.json",
    "control/inventory/source_packs/h14_source_reliability_freshness_policy.json",
    "control/inventory/source_packs/h14_source_dispute_revocation_policy.json",
    "control/inventory/source_packs/h14_source_lineage_provenance_policy.json",
    "control/inventory/source_packs/h14_pack_import_export_boundary_policy.json",
    "control/inventory/source_packs/h14_source_discovery_approval_gates.json",
    "control/inventory/source_packs/h14_source_discovery_output_policy.json",
    "control/inventory/source_packs/h14_source_discovery_truth_policy.json",
    "control/inventory/source_packs/h14_source_discovery_no_live_call_policy.json",
    "control/inventory/source_packs/h14_source_discovery_no_pack_import_export_policy.json",
)
SOURCE_PACK_EXAMPLES = (
    "examples/source_packs/h14_source_discovery_source_pack_manifest_v0.json",
    "examples/source_packs/h14_source_discovery_policy_pack_v0.json",
)
EXTRA_EXAMPLES = (
    "examples/connectors/h14_source_discovery/coverage/h14_source_discovery_coverage_preview_v0.json",
    "examples/connectors/h14_source_discovery/scorecards/h14_source_discovery_scorecard_preview_v0.json",
)
DOCS = (
    "docs/reference/H14_SOURCE_DISCOVERY_SOURCE_PACKS.md",
    "docs/reference/H14_SOURCE_NEED_POLICY.md",
    "docs/reference/H14_SOURCE_CANDIDATE_POLICY.md",
    "docs/reference/H14_SOURCE_DISCOVERY_POLICY.md",
    "docs/reference/H14_SOURCE_PACK_MANIFEST_POLICY.md",
    "docs/reference/H14_CONNECTOR_PACK_MANIFEST_POLICY.md",
    "docs/reference/H14_COVERAGE_MANIFEST_POLICY.md",
    "docs/reference/H14_CONNECTOR_SCORECARD_POLICY.md",
    "docs/reference/H14_SOURCE_RELIABILITY_FRESHNESS_POLICY.md",
    "docs/reference/H14_SOURCE_DISPUTE_REVOCATION_POLICY.md",
    "docs/reference/H14_SOURCE_LINEAGE_PROVENANCE_POLICY.md",
    "docs/reference/H14_PACK_IMPORT_EXPORT_BOUNDARY_POLICY.md",
    "docs/architecture/H14_SOURCE_DISCOVERY_MODEL.md",
    "docs/architecture/H14_SOURCE_PACK_MODEL.md",
    "docs/architecture/H14_CONNECTOR_SCORECARD_MODEL.md",
    "docs/architecture/H14_COVERAGE_MANIFEST_MODEL.md",
    "docs/operations/H14_SOURCE_DISCOVERY_POLICY_GATES.md",
    "docs/operations/H14_SOURCE_DISCOVERY_NO_LIVE_CALL_POLICY.md",
    "docs/operations/H14_SOURCE_DISCOVERY_NO_PACK_IMPORT_EXPORT_POLICY.md",
    "docs/operations/H14_SOURCE_DISCOVERY_FIXTURE_PLAN.md",
)
AUDIT_FILES = tuple(
    f"control/audits/h14-bundle-01-source-discovery-policy-packs-v0/{name}"
    for name in (
        "README.md",
        "h14_bundle_01_report.json",
        "h14_source_pack_summary.md",
        "h14_source_policy_gate_summary.md",
        "h14_connector_family_summary.md",
        "h14_source_need_policy_summary.md",
        "h14_source_candidate_policy_summary.md",
        "h14_source_discovery_policy_summary.md",
        "h14_source_pack_manifest_policy_summary.md",
        "h14_connector_pack_manifest_policy_summary.md",
        "h14_coverage_manifest_policy_summary.md",
        "h14_connector_scorecard_policy_summary.md",
        "h14_source_reliability_freshness_policy_summary.md",
        "h14_source_dispute_revocation_policy_summary.md",
        "h14_source_lineage_provenance_policy_summary.md",
        "h14_pack_import_export_boundary_policy_summary.md",
        "h14_fixture_plan.md",
        "h14_no_live_call_report.md",
        "h14_no_pack_import_export_report.md",
        "h14_readiness_for_fixture_runtime.md",
        "validation.md",
        "generated/sample_h14_source_summary.json",
        "generated/sample_h14_source_summary.md",
        "generated/sample_h14_option_matrix.json",
    )
)
PYTHON_FILES = (
    "scripts/validate_h14_source_discovery_policy_packs.py",
    "scripts/summarize_h14_source_discovery_sources.py",
)
ALLOWED_CURRENT_OPERATIONS = {
    "inspect_fixture",
    "record_source_policy",
    "record_discovery_boundary",
    "record_pack_boundary",
    "record_coverage_policy",
    "record_scorecard_policy",
    "record_dispute_revocation_policy",
    "record_lineage_policy",
    "create_coverage_preview",
    "create_scorecard_preview",
}
FALSE_REQUIRED_KEYS = {
    "source_discovery_enabled",
    "source_discovery_runtime_enabled",
    "live_access_enabled",
    "network_access_enabled",
    "local_access_enabled",
    "private_source_access_enabled",
    "user_supplied_url_fetch_enabled",
    "authenticated_access_enabled",
    "restricted_source_access_enabled",
    "model_provider_enabled",
    "source_sync_enabled",
    "connector_runtime_enabled",
    "source_registry_mutation_enabled",
    "connector_registry_mutation_enabled",
    "source_pack_export_enabled",
    "source_pack_import_enabled",
    "source_pack_acceptance_enabled",
    "connector_pack_export_enabled",
    "connector_pack_import_enabled",
    "coverage_manifest_export_enabled",
    "coverage_manifest_import_enabled",
    "pack_export_import_enabled",
    "pack_signing_enabled",
    "pack_publication_enabled",
    "pack_acceptance_enabled",
    "public_index_write_enabled",
    "master_index_write_enabled",
    "source_cache_write_enabled",
    "evidence_write_enabled",
    "review_queue_write_enabled",
    "automatic_scorecard_acceptance_enabled",
    "automatic_source_approval_enabled",
    "automatic_connector_approval_enabled",
}
FORBIDDEN_TRUE_KEYS = FALSE_REQUIRED_KEYS | {
    "source_pack_is_truth",
    "source_pack_is_accepted_evidence",
    "source_pack_is_imported_state",
    "policy_pack_grants_discovery_access",
    "capability_grants_permission",
    "source_need_is_source_approval",
    "source_need_is_connector_approval",
    "source_need_authorizes_discovery",
    "source_need_authorizes_probing",
    "source_need_authorizes_crawling",
    "source_need_authorizes_import_export",
    "source_need_authorizes_public_index_mutation",
    "source_candidate_is_approved_source",
    "source_candidate_is_source_truth",
    "candidate_locator_authorizes_fetching",
    "candidate_must_enter_source_registry_without_review",
    "source_discovery_candidate_is_registry_mutation",
    "discovery_output_is_registry_mutation",
    "discovery_output_is_source_approval",
    "discovery_output_is_public_truth",
    "source_pack_manifest_is_exported_pack",
    "source_pack_manifest_is_accepted_truth",
    "source_pack_manifest_redistributes_artifacts",
    "source_pack_manifest_grants_import_export_permission",
    "connector_pack_manifest_is_exported_connector_code",
    "connector_pack_manifest_is_connector_approval",
    "connector_pack_manifest_auto_enables_runtime",
    "coverage_manifest_is_exhaustive",
    "coverage_manifest_is_exhaustive_global_coverage",
    "coverage_manifest_proves_source_completeness",
    "coverage_manifest_proves_public_index_readiness",
    "connector_scorecard_is_connector_approval",
    "scorecard_readiness_is_production_readiness",
    "scorecard_auto_enables_live_access",
    "scorecard_auto_enables_source_sync",
    "scorecard_auto_enables_public_index_writes",
    "scorecard_auto_enables_master_index_writes",
    "reliability_score_is_reliability_truth",
    "freshness_score_is_currentness_truth",
    "availability_signal_is_source_availability_truth",
    "score_overrides_policy_gates",
    "dispute_revocation_candidate_is_automatic_deletion",
    "dispute_revocation_candidate_is_accepted_truth",
    "lineage_provenance_candidate_is_lineage_truth",
    "lineage_proves_authority",
    "lineage_proves_authenticity",
    "lineage_proves_rights",
    "lineage_auto_merges_sources",
    "pack_boundary_grants_import_export_permission",
    "source_intelligence_packs_redistribute_artifacts_by_default",
    "public_index_mutation_allowed",
    "master_index_mutation_allowed",
    "public_index_mutated",
    "master_index_mutated",
    "mutated_public_index",
    "mutated_master_index",
    "source_registry_mutated",
    "connector_registry_mutated",
    "accepted_source_candidate",
    "accepted_source_truth",
    "accepted_connector_truth",
    "accepted_coverage_truth",
    "accepted_scorecard_truth",
    "accepted_reliability_truth",
    "accepted_freshness_truth",
    "accepted_dispute_truth",
    "accepted_revocation_truth",
    "accepted_lineage_truth",
    "accepted_pack_truth",
    "accepted_public_truth",
    "source_approval_claimed",
    "connector_approval_claimed",
    "source_completeness_claimed",
    "legal_approval_claimed",
    "rights_clearance_claimed",
    "safe_source_status_claimed",
    "production_readiness_claimed",
    "launch_readiness_claimed",
    "automatic_future_connector_approval",
    "auto_approves_future_connectors",
    "production_ready",
    "launch_ready",
    "changed_public_search_behavior",
    "enabled_hosting",
    "enabled_source_discovery",
    "enabled_live_access",
    "enabled_network_access",
    "enabled_model_provider",
    "enabled_source_sync",
    "enabled_pack_export_import",
    "enabled_registry_mutation",
    "enabled_source_cache_writes",
    "enabled_evidence_writes",
    "mutated_public_index",
    "mutated_master_index",
    "network_calls_made",
    "api_calls_made",
    "model_provider_calls_made",
}
FORBIDDEN_PAYLOAD_KEYS = {
    "network_output",
    "api_output",
    "model_provider_output",
    "crawled_data",
    "scraped_data",
    "source_registry_write",
    "connector_registry_write",
    "source_cache_write",
    "evidence_write",
    "public_index_write",
    "master_index_write",
    "imported_pack",
    "exported_pack",
    "signed_pack",
    "private_data_payload",
    "artifact_payload",
}
BANNED_IMPORT_RE = re.compile(r"^\s*(?:from|import)\s+(requests|httpx|aiohttp|socket|ftplib|smtplib|webbrowser|selenium|playwright|openai|anthropic|urllib)\b", re.MULTILINE)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print JSON validation result.")
    args = parser.parse_args(argv)
    result = validate_repo(REPO_ROOT)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print("H14 source discovery policy pack validation", file=stdout)
        print(f"status: {result['status']}", file=stdout)
        print(f"error_count: {len(result['errors'])}", file=stdout)
        for error in result["errors"][:80]:
            print(f"ERROR: {error}", file=stdout)
    return 0 if result["status"] == "valid" else 1


def validate_repo(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    required = list(INVENTORY_FILES) + list(SOURCE_PACK_EXAMPLES) + list(EXTRA_EXAMPLES) + list(DOCS) + list(AUDIT_FILES) + list(PYTHON_FILES)
    required.extend(f"examples/sources/source_records/{SOURCE_FILES[source_id]}" for source_id in ALL_SOURCE_IDS)
    required.extend(f"examples/connectors/h14_source_discovery/policies/{POLICY_FILES_BY_SOURCE[source_id]}" for source_id in ALL_SOURCE_IDS)
    for rel in required:
        if not (repo_root / rel).exists():
            errors.append(f"missing required file: {rel}")
    known = _load_known_values(repo_root, errors)
    for rel in required:
        path = repo_root / rel
        if rel.endswith(".json") and path.exists():
            try:
                payload = _load_json(path)
            except Exception as exc:  # noqa: BLE001
                errors.append(f"invalid JSON in {rel}: {exc}")
                continue
            _scan_forbidden_true(rel, payload, errors)
            _scan_forbidden_payload_keys(rel, payload, errors)
    inventory = _load_json(repo_root / "control/inventory/source_packs/h14_source_discovery_sources.json")
    sources = inventory.get("sources", [])
    if not isinstance(sources, list):
        errors.append("source inventory must contain sources list")
    else:
        ids = [item.get("source_id") for item in sources if isinstance(item, Mapping)]
        if len(ids) != len(set(ids)):
            errors.append("source IDs must be unique")
        if set(ids) != set(SOURCE_IDS):
            errors.append("source inventory IDs must match H14 conceptual source list")
        for item in sources:
            if isinstance(item, Mapping):
                errors.extend(validate_source_record(str(item.get("source_id")), item, known))
    for source_id in ALL_SOURCE_IDS:
        path = repo_root / f"examples/sources/source_records/{SOURCE_FILES[source_id]}"
        if path.exists():
            errors.extend(validate_source_record(source_id, _load_json(path), known, allow_policy_blocked=True))
        pack_path = repo_root / f"examples/connectors/h14_source_discovery/policies/{POLICY_FILES_BY_SOURCE[source_id]}"
        if pack_path.exists():
            errors.extend(validate_policy_pack(source_id, _load_json(pack_path)))
    coverage = repo_root / "examples/connectors/h14_source_discovery/coverage/h14_source_discovery_coverage_preview_v0.json"
    if coverage.exists():
        errors.extend(validate_coverage_preview(_load_json(coverage)))
    scorecard = repo_root / "examples/connectors/h14_source_discovery/scorecards/h14_source_discovery_scorecard_preview_v0.json"
    if scorecard.exists():
        errors.extend(validate_scorecard_preview(_load_json(scorecard)))
    _validate_python_files(repo_root, errors)
    _validate_no_private_roots(repo_root, errors)
    return {
        "schema_version": "h14_source_discovery_policy_pack_validation.v0",
        "status": "valid" if not errors else "invalid",
        "task": "H14-BUNDLE-01",
        "source_count": len(SOURCE_IDS),
        "network_calls_made": False,
        "model_provider_calls_made": False,
        "errors": errors,
    }


def validate_source_record(source_id: str, record: Mapping[str, Any], known: Mapping[str, Any], allow_policy_blocked: bool = False) -> list[str]:
    errors: list[str] = []
    known_ids = set(ALL_SOURCE_IDS if allow_policy_blocked else SOURCE_IDS)
    if source_id not in known_ids or record.get("source_id") != source_id:
        errors.append(f"{source_id}: source_id mismatch or unknown")
    if record.get("source_family") != "source_discovery_and_scorecards":
        errors.append(f"{source_id}: source_family must be source_discovery_and_scorecards")
    if record.get("source_family") not in known.get("source_families", set()):
        errors.append(f"{source_id}: source family is not in source family registry")
    if record.get("connector_family") not in known.get("connector_families", set()):
        errors.append(f"{source_id}: connector family is not in connector family registry")
    if record.get("trust_lane") not in {"internal_control", "governance"}:
        errors.append(f"{source_id}: trust lane must be internal_control or governance")
    if record.get("current_index_depth") != "D0_source_known":
        errors.append(f"{source_id}: current_index_depth must be D0_source_known")
    if record.get("current_access_mode") not in {"no_runtime_discovery", "committed_fixture_only"}:
        errors.append(f"{source_id}: invalid current_access_mode")
    _scan_forbidden_true(source_id, record, errors)
    _scan_forbidden_payload_keys(source_id, record, errors)
    return errors


def validate_policy_pack(source_id: str, pack: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if pack.get("source_id") != source_id:
        errors.append(f"{source_id}: policy pack source_id mismatch")
    if pack.get("policy_pack_grants_discovery_access") is not False:
        errors.append(f"{source_id}: policy pack must not grant discovery access")
    allowed = set(pack.get("allowed_current_operations") or [])
    if not allowed <= ALLOWED_CURRENT_OPERATIONS:
        errors.append(f"{source_id}: allowed_current_operations include forbidden operations")
    for operation in ("live_source_discovery", "web_search", "crawl", "scrape", "source_registry_mutation", "connector_registry_mutation", "source_pack_export", "source_pack_import", "public_index_mutation", "master_index_mutation"):
        if operation not in pack.get("forbidden_current_operations", []):
            errors.append(f"{source_id}: missing forbidden operation {operation}")
    _scan_forbidden_true(source_id, pack, errors)
    _scan_forbidden_payload_keys(source_id, pack, errors)
    return errors


def validate_coverage_preview(coverage: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if coverage.get("coverage_basis") != "policy_pack_only":
        errors.append("coverage preview must be policy_pack_only")
    if coverage.get("coverage_manifest_is_exhaustive_global_coverage") is not False:
        errors.append("coverage preview must not claim exhaustive coverage")
    for key in ("source_discovery_enabled", "live_access_enabled"):
        if coverage.get(key) is True:
            errors.append(f"coverage preview must keep {key} false")
    for key in ("source_pack_exports_performed", "source_pack_imports_performed", "registry_mutations_performed", "source_cache_writes_performed", "evidence_writes_performed", "public_index_writes_performed", "master_index_writes_performed"):
        if coverage.get(key) not in (0, None):
            errors.append(f"coverage preview must keep {key} at 0")
    _scan_forbidden_true("coverage", coverage, errors)
    return errors


def validate_scorecard_preview(scorecard: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if scorecard.get("production_ready") is not False:
        errors.append("scorecard must not claim production readiness")
    if scorecard.get("auto_approves_future_connectors") is not False:
        errors.append("scorecard must not auto-approve future connectors")
    for key in ("source_discovery_status", "source_pack_export_status", "source_pack_import_status", "source_registry_mutation_status", "connector_registry_mutation_status", "public_index_status"):
        if scorecard.get(key) not in {"blocked_current", "forbidden_current"}:
            errors.append(f"scorecard {key} must be blocked_current or forbidden_current")
    _scan_forbidden_true("scorecard", scorecard, errors)
    return errors


def _load_known_values(repo_root: Path, errors: list[str]) -> dict[str, set[str]]:
    known = {"source_families": set(), "connector_families": set()}
    source_path = repo_root / "control/inventory/sources/source_family_registry.json"
    connector_path = repo_root / "control/inventory/connectors/connector_family_registry.json"
    if source_path.exists():
        payload = _load_json(source_path)
        for item in payload.get("families", []):
            if isinstance(item, Mapping) and item.get("family_id"):
                known["source_families"].add(str(item["family_id"]))
    if connector_path.exists():
        payload = _load_json(connector_path)
        for item in payload.get("families", []):
            if isinstance(item, Mapping) and item.get("family_id"):
                known["connector_families"].add(str(item["family_id"]))
    return known


def _scan_forbidden_true(label: str, payload: Any, errors: list[str]) -> None:
    if isinstance(payload, Mapping):
        for key, value in payload.items():
            if str(key) in FORBIDDEN_TRUE_KEYS and value is True:
                errors.append(f"{label}: forbidden true claim {key}")
            _scan_forbidden_true(label, value, errors)
    elif isinstance(payload, list):
        for item in payload:
            _scan_forbidden_true(label, item, errors)


def _scan_forbidden_payload_keys(label: str, payload: Any, errors: list[str]) -> None:
    if isinstance(payload, Mapping):
        for key, value in payload.items():
            if str(key) in FORBIDDEN_PAYLOAD_KEYS:
                errors.append(f"{label}: forbidden output/private/artifact key {key}")
            _scan_forbidden_payload_keys(label, value, errors)
    elif isinstance(payload, list):
        for item in payload:
            _scan_forbidden_payload_keys(label, item, errors)


def _validate_python_files(repo_root: Path, errors: list[str]) -> None:
    for rel in PYTHON_FILES:
        path = repo_root / rel
        if path.exists() and BANNED_IMPORT_RE.search(path.read_text(encoding="utf-8")):
            errors.append(f"{rel}: imports network/model/provider/browser library")


def _validate_no_private_roots(repo_root: Path, errors: list[str]) -> None:
    for rel in (".aide.local", ".local/eureka", ".cache/eureka", "source_discovery_runtime", "pack_import_staging", "pack_export_staging", "source_registry_mutation", "connector_registry_mutation", "external_source_fetch", "local_sources", "private_sources", "cas_store"):
        if (repo_root / rel).exists():
            errors.append(f"forbidden local/private/runtime root must not exist: {rel}")


def _load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    raise SystemExit(main())
