#!/usr/bin/env python3
"""Validate H14-BUNDLE-04 review, quality delta, and audit artifacts offline."""

from __future__ import annotations

import argparse
import importlib
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any, Mapping, Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from archive.prototypes.legacy_runtime.connectors.h14_source_discovery.quality_delta import detect_h14_quality_overclaim  # noqa: E402
from archive.prototypes.legacy_runtime.connectors.h14_source_discovery.review_integration import (  # noqa: E402
    detect_h14_review_product_boundary_violations,
    detect_h14_review_registry_or_pack_mutation_violations,
    detect_h14_review_truth_boundary_violations,
)

AUDIT_DIR = Path("control/audits/h14-bundle-04-source-discovery-review-quality-audit-v0")
REVIEW_DIR = Path("examples/connectors/h14_source_discovery/review_integration")
REQUIRED_JSON = (
    "contracts/schema/control/audits/h14/connectors/source_discovery_review_integration_result.v0.json",
    "contracts/schema/control/audits/h14/connectors/source_discovery_quality_delta_report.v0.json",
    "contracts/schema/control/audits/h14/connectors/source_discovery_connector_wave_postmortem.v0.json",
    "contracts/schema/control/audits/h14/connectors/source_discovery_integration_audit.v0.json",
    "contracts/schema/control/tasks/h14/connectors/source_discovery_next_phase_recommendation.v0.json",
    "control/inventory/connectors/h14_source_discovery_review_integration_policy.json",
    "control/inventory/connectors/h14_source_discovery_review_output_policy.json",
    "control/inventory/connectors/h14_source_discovery_review_path_policy.json",
    "control/inventory/connectors/h14_source_discovery_review_truth_policy.json",
    "control/inventory/connectors/h14_source_discovery_quality_delta_policy.json",
    "control/inventory/connectors/h14_source_discovery_connector_wave_postmortem_policy.json",
    "control/inventory/connectors/h14_source_discovery_integration_audit_policy.json",
    "control/inventory/connectors/h14_source_discovery_next_phase_policy.json",
    (AUDIT_DIR / "h14_bundle_04_report.json").as_posix(),
)
REQUIRED_EXAMPLES = (
    "h14_source_need_review_seed_v0.json",
    "h14_source_candidate_review_seed_v0.json",
    "h14_source_discovery_candidate_review_seed_v0.json",
    "h14_source_pack_manifest_review_seed_v0.json",
    "h14_connector_pack_manifest_review_seed_v0.json",
    "h14_coverage_manifest_review_seed_v0.json",
    "h14_connector_scorecard_review_seed_v0.json",
    "h14_reliability_freshness_review_seed_v0.json",
    "h14_dispute_revocation_review_seed_v0.json",
    "h14_lineage_provenance_review_seed_v0.json",
    "h14_pack_import_export_boundary_review_seed_v0.json",
    "h14_source_cache_review_seed_v0.json",
    "h14_evidence_candidate_review_seed_v0.json",
    "h14_candidate_promotion_preview_v0.json",
    "h14_source_coverage_update_preview_v0.json",
    "h14_connector_scorecard_update_v0.json",
    "h14_source_pack_update_preview_v0.json",
    "h14_quality_delta_report_v0.json",
    "h14_connector_wave_postmortem_v0.json",
    "h14_blocked_review_integration_v0.json",
    "h14_review_integration_result_v0.json",
    "h14_next_phase_recommendation_v0.json",
    "h14_integration_audit_v0.json",
)
REQUIRED_AUDIT_FILES = (
    "README.md",
    "h14_bundle_04_report.json",
    "h14_review_integration_report.md",
    "h14_quality_delta_report.md",
    "h14_connector_wave_postmortem.md",
    "h14_integration_audit.md",
    "h14_exit_gate_decision.md",
    "next_phase_recommendation.md",
    "f0_readiness_review.md",
    "i_pack_federation_deferral_review.md",
    "j_risky_action_deferral_review.md",
    "k_semantic_ai_deferral_review.md",
    "l_wider_client_deferral_review.md",
    "e_deployment_deferral_review.md",
    "validation.md",
    "generated/sample_h14_review_integration_result.json",
    "generated/sample_h14_quality_delta_report.json",
    "generated/sample_h14_connector_wave_postmortem.json",
    "generated/sample_h14_integration_audit.json",
    "generated/sample_h14_next_phase_recommendation.json",
    "generated/sample_h14_summary.md",
)
REQUIRED_DOCS = (
    "docs/reference/H14_SOURCE_DISCOVERY_REVIEW_INTEGRATION.md",
    "docs/reference/H14_SOURCE_DISCOVERY_QUALITY_DELTA_REPORT.md",
    "docs/reference/H14_SOURCE_DISCOVERY_CONNECTOR_WAVE_POSTMORTEM.md",
    "docs/architecture/H14_SOURCE_DISCOVERY_REVIEW_INTEGRATION_MODEL.md",
    "docs/operations/H14_SOURCE_DISCOVERY_WAVE_POSTMORTEM.md",
    "docs/operations/H14_SOURCE_DISCOVERY_WAVE_QUALITY_DELTA.md",
    "docs/operations/H14_TO_F0_HANDOFF.md",
    "docs/operations/H14_TO_I_J_K_L_DEFERRAL.md",
)
PYTHON_SCAN_PATHS = (
    "archive/prototypes/legacy_runtime/connectors/h14_source_discovery/review_integration.py",
    "archive/prototypes/legacy_runtime/connectors/h14_source_discovery/quality_delta.py",
    "archive/prototypes/legacy_runtime/connectors/h14_source_discovery/wave_postmortem.py",
    "scripts/integrate_h14_source_discovery_review.py",
    "scripts/summarize_h14_source_discovery_quality_delta.py",
    "scripts/audit_h14_source_discovery_wave.py",
    "scripts/validate_h14_source_discovery_review_quality_audit.py",
)
BANNED_IMPORT_RE = re.compile(r"^\s*(?:from|import)\s+(requests|urllib|httpx|aiohttp|socket|ftplib|smtplib|webbrowser|selenium|playwright|openai|anthropic)\b", re.MULTILINE)
FORBIDDEN_TRUE_KEYS = set([
    "accepts_source_need_truth", "accepts_source_candidate_truth", "accepts_source_discovery_truth",
    "accepts_source_approval", "accepts_connector_approval", "accepts_source_pack_truth",
    "accepts_connector_pack_truth", "accepts_coverage_truth", "accepts_scorecard_truth",
    "accepts_reliability_truth", "accepts_freshness_truth", "accepts_dispute_revocation_truth",
    "accepts_lineage_provenance_truth", "accepts_source_truth", "accepts_evidence_truth",
    "accepts_candidate_truth", "source_need_seed_accepts_source_approval",
    "source_candidate_seed_accepts_source_truth", "source_discovery_seed_mutates_registry",
    "source_pack_manifest_seed_exports_pack", "connector_pack_manifest_seed_approves_connector",
    "coverage_manifest_seed_accepts_coverage_truth", "connector_scorecard_seed_approves_connector",
    "reliability_freshness_seed_accepts_truth", "dispute_revocation_seed_accepts_truth",
    "lineage_provenance_seed_accepts_lineage_truth",
    "pack_boundary_seed_grants_import_export_permission", "source_cache_review_seed_accepts_source",
    "evidence_review_seed_accepts_evidence", "candidate_promotion_preview_promotes_candidate",
    "source_pack_preview_is_imported_or_submitted", "source_registry_mutated",
    "connector_registry_mutated", "public_index_mutated", "master_index_mutated",
    "rights_clearance_claimed", "source_completeness_claimed", "production_readiness_claimed",
    "launch_readiness_claimed", "enabled_source_discovery", "enabled_live_access",
    "enabled_network_access", "enabled_model_provider", "enabled_source_sync",
    "enabled_pack_export_import", "enabled_registry_mutation", "enabled_source_cache_writes",
    "enabled_evidence_writes", "mutated_public_index", "mutated_master_index",
])


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit validation JSON.")
    args = parser.parse_args(argv)
    result = validate_repo(REPO_ROOT)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print("H14 Source OS review quality audit validation", file=stdout)
        print(f"status: {result['status']}", file=stdout)
        print(f"error_count: {len(result['errors'])}", file=stdout)
        for error in result["errors"]:
            print(f"ERROR: {error}", file=stdout)
    return 0 if result["status"] == "valid" else 1


def validate_repo(root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    payloads = {rel: load_json_object(root / rel, errors) for rel in REQUIRED_JSON}
    validate_policies(payloads, errors)
    validate_docs(root, errors)
    validate_examples(root, errors)
    validate_audit_files(root, errors)
    validate_generated_outputs(root, errors)
    validate_python_imports(root, errors)
    validate_runtime_imports(errors)
    validate_scripts(root, errors)
    validate_no_private_roots(root, errors)
    return {
        "schema_version": "h14_review_quality_audit_validation.v0",
        "status": "valid" if not errors else "invalid",
        "task": "H14-BUNDLE-04",
        "offline_default": True,
        "network_calls_made": False,
        "model_provider_calls_made": False,
        "source_discovery_runtime_used": False,
        "pack_export_import_used": False,
        "registry_mutation_used": False,
        "errors": errors,
    }


def validate_policies(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    review = payloads.get("control/inventory/connectors/h14_source_discovery_review_integration_policy.json", {})
    for key in (
        "new_rollup_dry_runs_enabled", "source_discovery_runtime_enabled", "live_access_enabled",
        "network_access_enabled", "local_access_enabled", "private_source_access_enabled",
        "user_supplied_url_fetch_enabled", "authenticated_access_enabled",
        "restricted_source_access_enabled", "model_provider_enabled", "source_sync_enabled",
        "source_registry_mutation_enabled", "connector_registry_mutation_enabled",
        "source_pack_export_enabled", "source_pack_import_enabled", "connector_pack_export_enabled",
        "connector_pack_import_enabled", "pack_signing_enabled", "pack_publication_enabled",
        "source_cache_write_enabled", "evidence_write_enabled", "review_queue_write_enabled",
        "public_index_write_enabled", "master_index_write_enabled", "truth_acceptance_enabled",
        "production_readiness_claims_enabled",
    ):
        if review.get(key) is not False:
            errors.append(f"h14 review policy {key} must be false")
    output = payloads.get("control/inventory/connectors/h14_source_discovery_review_output_policy.json", {})
    for key in ["accepted_source_need_truth", "accepted_source_candidate_truth", "accepted_source_discovery_truth", "accepted_source_approval", "accepted_connector_approval", "accepted_coverage_truth", "accepted_scorecard_truth", "accepted_reliability_truth", "accepted_freshness_truth", "accepted_dispute_revocation_truth", "accepted_lineage_provenance_truth", "source_registry_mutation", "connector_registry_mutation", "public_index_mutation", "master_index_mutation", "pack_export_import_permission", "production_readiness_claim", "launch_readiness_claim"]:
        if key not in output.get("forbidden_outputs", []):
            errors.append(f"h14 review output policy must forbid {key}")
    audit = payloads.get("control/inventory/connectors/h14_source_discovery_integration_audit_policy.json", {})
    if "READY_FOR_F0_BUNDLE_01" not in audit.get("next_phase_values", []):
        errors.append("H14 audit policy must allow READY_FOR_F0_BUNDLE_01")
    next_phase = payloads.get("control/inventory/connectors/h14_source_discovery_next_phase_policy.json", {})
    for key in ("f0_preferred_after_h14_if_source_os_rollup_is_coherent", "f0_must_start_with_extraction_boundary_policy_packs", "remediation_overrides_expansion"):
        if next_phase.get(key) is not True:
            errors.append(f"H14 next phase policy must set {key}")
    for key in ("h14_opens_source_discovery_runtime", "h14_opens_pack_federation_export_import", "h14_opens_j_acquisition_actions", "h14_opens_k_semantic_ai", "h14_opens_l_wider_clients", "h14_opens_e_deployment"):
        if next_phase.get(key) is not False:
            errors.append(f"H14 next phase policy must keep {key} false")


def validate_docs(root: Path, errors: list[str]) -> None:
    for rel in REQUIRED_DOCS:
        if not (root / rel).is_file():
            errors.append(f"missing doc: {rel}")


def validate_examples(root: Path, errors: list[str]) -> None:
    for name in REQUIRED_EXAMPLES:
        path = root / REVIEW_DIR / name
        payload = load_json_object(path, errors)
        validate_boundaries(payload, f"example {name}", errors)
    delta = load_json_object(root / REVIEW_DIR / "h14_quality_delta_report_v0.json", errors)
    errors.extend(detect_h14_quality_overclaim(delta))
    postmortem = load_json_object(root / REVIEW_DIR / "h14_connector_wave_postmortem_v0.json", errors)
    for key in ("auto_approves_future_connectors", "auto_approves_source_discovery", "auto_approves_registry_mutation", "auto_approves_pack_import_export", "auto_approves_publication", "auto_approves_production_readiness"):
        if postmortem.get(key) is not False:
            errors.append(f"postmortem must keep {key} false")


def validate_audit_files(root: Path, errors: list[str]) -> None:
    for rel_name in REQUIRED_AUDIT_FILES:
        if not (root / AUDIT_DIR / rel_name).is_file():
            errors.append(f"missing audit file: {(AUDIT_DIR / rel_name).as_posix()}")


def validate_generated_outputs(root: Path, errors: list[str]) -> None:
    for rel_name in REQUIRED_AUDIT_FILES:
        if rel_name.startswith("generated/") and rel_name.endswith(".json"):
            payload = load_json_object(root / AUDIT_DIR / rel_name, errors)
            validate_boundaries(payload, rel_name, errors)
    report = load_json_object(root / AUDIT_DIR / "h14_bundle_04_report.json", errors)
    if report.get("h14_exit_gate") not in {"PASS", "PASS_WITH_WARNINGS", "PARTIAL", "BLOCKED", "FAIL"}:
        errors.append("H14 report must have explicit h14_exit_gate")
    if report.get("next_phase_recommendation") not in {"READY_FOR_F0_BUNDLE_01", "READY_WITH_WARNINGS"}:
        errors.append("H14 report should recommend F0 when fixture-equivalent outputs are sufficient")
    validate_boundaries(report, "h14_bundle_04_report", errors)


def validate_python_imports(root: Path, errors: list[str]) -> None:
    for rel in PYTHON_SCAN_PATHS:
        path = root / rel
        if not path.is_file():
            errors.append(f"missing Python file: {rel}")
            continue
        text = path.read_text(encoding="utf-8")
        if BANNED_IMPORT_RE.search(text):
            errors.append(f"{rel}: imports network/provider/browser library")


def validate_runtime_imports(errors: list[str]) -> None:
    for module in ("review_integration", "quality_delta", "wave_postmortem"):
        try:
            importlib.import_module(f"archive.prototypes.legacy_runtime.connectors.h14_source_discovery.{module}")
        except Exception as exc:  # noqa: BLE001
            errors.append(f"runtime module import failed {module}: {exc}")


def validate_scripts(root: Path, errors: list[str]) -> None:
    commands = [
        [sys.executable, "scripts/integrate_h14_source_discovery_review.py", "--input-dir", "examples/connectors/h14_source_discovery/replay_results", "--check"],
        [sys.executable, "scripts/summarize_h14_source_discovery_quality_delta.py", "--input-dir", "examples/connectors/h14_source_discovery/review_integration", "--check"],
        [sys.executable, "scripts/audit_h14_source_discovery_wave.py", "--check"],
    ]
    for command in commands:
        proc = subprocess.run(command, cwd=root, text=True, capture_output=True, check=False)
        if proc.returncode != 0:
            errors.append(f"script failed: {' '.join(command)} :: {proc.stdout}{proc.stderr}")
    forbidden_checks = [
        [sys.executable, "scripts/integrate_h14_source_discovery_review.py", "--input-dir", "examples/connectors/h14_source_discovery/replay_results", "--output-dir", "site/dist/h14"],
        [sys.executable, "scripts/summarize_h14_source_discovery_quality_delta.py", "--input-dir", "examples/connectors/h14_source_discovery/review_integration", "--output", "site/dist/data/public_index/h14.json"],
        [sys.executable, "scripts/audit_h14_source_discovery_wave.py", "--json-output", ".local/eureka/h14.json"],
    ]
    for command in forbidden_checks:
        proc = subprocess.run(command, cwd=root, text=True, capture_output=True, check=False)
        if proc.returncode == 0 or "refusing" not in (proc.stdout + proc.stderr):
            errors.append(f"forbidden output root was not rejected: {' '.join(command)}")


def validate_no_private_roots(root: Path, errors: list[str]) -> None:
    for rel in (".aide.local", ".local/eureka", ".cache/eureka", "source_discovery_runtime", "pack_import_staging", "pack_export_staging", "source_registry_mutation", "connector_registry_mutation", "external_source_fetch", "local_sources", "private_sources", "source_cache", "evidence_ledger"):
        if (root / rel).exists():
            errors.append(f"local private or action root must not exist: {rel}")


def load_json_object(path: Path, errors: list[str]) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        errors.append(f"invalid JSON {path}: {exc}")
        return {}
    if not isinstance(payload, Mapping):
        errors.append(f"JSON must be an object: {path}")
        return {}
    return dict(payload)


def validate_boundaries(payload: Mapping[str, Any], label: str, errors: list[str]) -> None:
    errors.extend(f"{label}: {error}" for error in detect_h14_review_truth_boundary_violations(payload))
    errors.extend(f"{label}: {error}" for error in detect_h14_review_product_boundary_violations(payload))
    errors.extend(f"{label}: {error}" for error in detect_h14_review_registry_or_pack_mutation_violations(payload))
    _scan_true_claims(payload, label, errors)


def _scan_true_claims(value: Any, label: str, errors: list[str]) -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            if str(key) in FORBIDDEN_TRUE_KEYS and item is True:
                errors.append(f"{label} forbidden true value: {key}")
            _scan_true_claims(item, label, errors)
    elif isinstance(value, list):
        for item in value:
            _scan_true_claims(item, label, errors)


if __name__ == "__main__":
    raise SystemExit(main())
