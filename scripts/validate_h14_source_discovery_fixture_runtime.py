#!/usr/bin/env python3
"""Validate H14 Source OS rollup fixture-runtime artifacts offline."""

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

from control.prototypes.legacy_runtime.connectors.h14_source_discovery.fixture_loader import load_h14_source_discovery_fixture  # noqa: E402
from control.prototypes.legacy_runtime.connectors.h14_source_discovery.normalizer_common import H14_FIXTURE_FILES, H14_SOURCE_IDS, detect_h14_product_boundary_violations, detect_h14_registry_or_pack_mutation_violations, detect_h14_truth_boundary_violations  # noqa: E402
from scripts.normalize_h14_source_discovery_fixture import SOURCE_MODULES  # noqa: E402

CONTRACTS = ['control/schemas/fixtures/h14/connectors/source_discovery_fixture.v0.json', 'control/schemas/previews/h14/connectors/source_discovery_normalized_record.v0.json', 'control/schemas/previews/h14/connectors/source_need_candidate.v0.json', 'control/schemas/previews/h14/connectors/source_candidate_candidate.v0.json', 'control/schemas/previews/h14/connectors/source_discovery_candidate.v0.json', 'control/schemas/previews/h14/connectors/source_pack_manifest_candidate.v0.json', 'control/schemas/previews/h14/connectors/connector_pack_manifest_candidate.v0.json', 'control/schemas/previews/h14/connectors/coverage_manifest_candidate.v0.json', 'control/schemas/previews/h14/connectors/connector_scorecard_candidate.v0.json', 'control/schemas/previews/h14/connectors/source_reliability_freshness_candidate.v0.json', 'control/schemas/previews/h14/connectors/source_dispute_revocation_candidate.v0.json', 'control/schemas/previews/h14/connectors/source_lineage_provenance_candidate.v0.json', 'control/schemas/previews/h14/connectors/pack_import_export_boundary_candidate.v0.json', 'control/schemas/fixtures/h14/connectors/source_discovery_fixture_replay_result.v0.json']
POLICIES = ['control/inventory/connectors/h14_source_discovery_fixture_runtime_policy.json', 'control/inventory/connectors/h14_source_discovery_normalization_policy.json', 'control/inventory/connectors/h14_source_need_mapping_policy.json', 'control/inventory/connectors/h14_source_candidate_mapping_policy.json', 'control/inventory/connectors/h14_source_discovery_candidate_mapping_policy.json', 'control/inventory/connectors/h14_source_pack_manifest_mapping_policy.json', 'control/inventory/connectors/h14_connector_pack_manifest_mapping_policy.json', 'control/inventory/connectors/h14_coverage_manifest_mapping_policy.json', 'control/inventory/connectors/h14_connector_scorecard_mapping_policy.json', 'control/inventory/connectors/h14_source_reliability_freshness_mapping_policy.json', 'control/inventory/connectors/h14_source_dispute_revocation_mapping_policy.json', 'control/inventory/connectors/h14_source_lineage_provenance_mapping_policy.json', 'control/inventory/connectors/h14_pack_import_export_boundary_mapping_policy.json', 'control/inventory/connectors/h14_source_discovery_fixture_output_policy.json', 'control/inventory/connectors/h14_source_discovery_fixture_path_policy.json', 'control/inventory/connectors/h14_source_discovery_fixture_truth_policy.json', 'control/inventory/connectors/h14_source_discovery_source_cache_mapping_policy.json', 'control/inventory/connectors/h14_source_discovery_evidence_mapping_policy.json', 'control/inventory/connectors/h14_source_discovery_no_live_call_policy.json', 'control/inventory/connectors/h14_source_discovery_no_pack_import_export_policy.json']
EXAMPLES = ['examples/connectors/h14_source_discovery/identity/source_need_candidate_v0.json', 'examples/connectors/h14_source_discovery/identity/source_candidate_candidate_v0.json', 'examples/connectors/h14_source_discovery/identity/source_discovery_candidate_v0.json', 'examples/connectors/h14_source_discovery/identity/source_pack_manifest_candidate_v0.json', 'examples/connectors/h14_source_discovery/identity/connector_pack_manifest_candidate_v0.json', 'examples/connectors/h14_source_discovery/identity/coverage_manifest_candidate_v0.json', 'examples/connectors/h14_source_discovery/identity/connector_scorecard_candidate_v0.json', 'examples/connectors/h14_source_discovery/identity/source_reliability_freshness_candidate_v0.json', 'examples/connectors/h14_source_discovery/identity/source_dispute_revocation_candidate_v0.json', 'examples/connectors/h14_source_discovery/identity/source_lineage_provenance_candidate_v0.json', 'examples/connectors/h14_source_discovery/identity/pack_import_export_boundary_candidate_v0.json', 'examples/connectors/h14_source_discovery/identity/policy_blocked_identity_candidate_v0.json']
DOCS = ['docs/reference/H14_SOURCE_DISCOVERY_FIXTURE_RUNTIME.md', 'docs/reference/H14_SOURCE_DISCOVERY_NORMALIZED_RECORD.md', 'docs/reference/H14_SOURCE_NEED_CANDIDATE.md', 'docs/reference/H14_SOURCE_CANDIDATE_CANDIDATE.md', 'docs/reference/H14_SOURCE_DISCOVERY_CANDIDATE.md', 'docs/reference/H14_SOURCE_PACK_MANIFEST_CANDIDATE.md', 'docs/reference/H14_CONNECTOR_PACK_MANIFEST_CANDIDATE.md', 'docs/reference/H14_COVERAGE_MANIFEST_CANDIDATE.md', 'docs/reference/H14_CONNECTOR_SCORECARD_CANDIDATE.md', 'docs/reference/H14_SOURCE_RELIABILITY_FRESHNESS_CANDIDATE.md', 'docs/reference/H14_SOURCE_DISPUTE_REVOCATION_CANDIDATE.md', 'docs/reference/H14_SOURCE_LINEAGE_PROVENANCE_CANDIDATE.md', 'docs/reference/H14_PACK_IMPORT_EXPORT_BOUNDARY_CANDIDATE.md', 'docs/architecture/H14_SOURCE_DISCOVERY_NORMALIZER_MODEL.md', 'docs/architecture/H14_SOURCE_NEED_MODEL.md', 'docs/architecture/H14_SOURCE_CANDIDATE_MODEL.md', 'docs/architecture/H14_SOURCE_DISCOVERY_CANDIDATE_MODEL.md', 'docs/architecture/H14_SOURCE_RELIABILITY_FRESHNESS_MODEL.md', 'docs/architecture/H14_SOURCE_DISPUTE_REVOCATION_MODEL.md', 'docs/architecture/H14_SOURCE_LINEAGE_PROVENANCE_MODEL.md', 'docs/operations/H14_SOURCE_DISCOVERY_FIXTURE_REPLAY.md', 'docs/operations/H14_SOURCE_DISCOVERY_FIXTURE_NO_LIVE_CALL_POLICY.md', 'docs/operations/H14_SOURCE_DISCOVERY_FIXTURE_NO_PACK_IMPORT_EXPORT_POLICY.md']
RUNTIME_MODULES = ['__init__.py', 'fixture_loader.py', 'normalizer_common.py', 'source_need.py', 'source_candidate.py', 'source_discovery_candidate.py', 'source_pack_manifest.py', 'connector_pack_manifest.py', 'coverage_manifest.py', 'connector_scorecard.py', 'reliability_freshness.py', 'dispute_revocation.py', 'lineage_provenance.py', 'pack_import_export_boundary.py', 'source_need_registry.py', 'source_candidate_registry.py', 'source_discovery_policy.py', 'source_pack_manifest_source.py', 'connector_pack_manifest_source.py', 'coverage_manifest_source.py', 'connector_scorecard_source.py', 'source_reliability_freshness_source.py', 'source_dispute_revocation_source.py', 'source_lineage_provenance_source.py', 'h14_policy_blocked.py']
AUDIT_FILES = ['README.md', 'h14_bundle_02_report.json', 'fixture_runtime_summary.md', 'normalizer_coverage_summary.md', 'source_need_mapping_summary.md', 'source_candidate_mapping_summary.md', 'source_discovery_candidate_mapping_summary.md', 'source_pack_manifest_mapping_summary.md', 'connector_pack_manifest_mapping_summary.md', 'coverage_manifest_mapping_summary.md', 'connector_scorecard_mapping_summary.md', 'source_reliability_freshness_mapping_summary.md', 'source_dispute_revocation_mapping_summary.md', 'source_lineage_provenance_mapping_summary.md', 'pack_import_export_boundary_mapping_summary.md', 'source_cache_mapping_preview.md', 'evidence_mapping_preview.md', 'no_live_call_report.md', 'no_pack_import_export_report.md', 'validation.md', 'generated/sample_h14_normalized_record.json', 'generated/sample_h14_source_need_candidate.json', 'generated/sample_h14_source_candidate_candidate.json', 'generated/sample_h14_source_discovery_candidate.json', 'generated/sample_h14_source_pack_manifest_candidate.json', 'generated/sample_h14_connector_pack_manifest_candidate.json', 'generated/sample_h14_coverage_manifest_candidate.json', 'generated/sample_h14_connector_scorecard_candidate.json', 'generated/sample_h14_source_reliability_freshness_candidate.json', 'generated/sample_h14_source_dispute_revocation_candidate.json', 'generated/sample_h14_source_lineage_provenance_candidate.json', 'generated/sample_h14_pack_import_export_boundary_candidate.json', 'generated/sample_h14_source_cache_candidate.json', 'generated/sample_h14_evidence_candidate_preview.json', 'generated/sample_h14_fixture_replay_result.json', 'generated/sample_h14_fixture_summary.md']
CANDIDATE_EXAMPLE_FILES = ['examples/connectors/h14_source_discovery/identity/source_need_candidate_v0.json', 'examples/connectors/h14_source_discovery/identity/source_candidate_candidate_v0.json', 'examples/connectors/h14_source_discovery/identity/source_discovery_candidate_v0.json', 'examples/connectors/h14_source_discovery/identity/source_pack_manifest_candidate_v0.json', 'examples/connectors/h14_source_discovery/identity/connector_pack_manifest_candidate_v0.json', 'examples/connectors/h14_source_discovery/identity/coverage_manifest_candidate_v0.json', 'examples/connectors/h14_source_discovery/identity/connector_scorecard_candidate_v0.json', 'examples/connectors/h14_source_discovery/identity/source_reliability_freshness_candidate_v0.json', 'examples/connectors/h14_source_discovery/identity/source_dispute_revocation_candidate_v0.json', 'examples/connectors/h14_source_discovery/identity/source_lineage_provenance_candidate_v0.json', 'examples/connectors/h14_source_discovery/identity/pack_import_export_boundary_candidate_v0.json', 'examples/connectors/h14_source_discovery/identity/policy_blocked_identity_candidate_v0.json']
BANNED_IMPORT_RE = re.compile(r"^\s*(?:from|import)\s+(requests|httpx|aiohttp|urllib|socket|ftplib|smtplib|webbrowser|selenium|playwright|openai|anthropic)\b", re.MULTILINE)
FORBIDDEN_TRUE_KEYS = set(['normalized_record_is_public_truth', 'source_need_candidate_is_source_approval', 'source_candidate_candidate_is_source_truth', 'source_discovery_candidate_is_registry_mutation', 'source_pack_manifest_candidate_is_exported_pack', 'connector_pack_manifest_candidate_is_connector_approval', 'coverage_manifest_candidate_is_exhaustive', 'connector_scorecard_candidate_is_connector_approval', 'source_reliability_freshness_candidate_is_truth', 'source_dispute_revocation_candidate_is_accepted_truth', 'source_lineage_provenance_candidate_is_lineage_truth', 'pack_import_export_boundary_candidate_grants_permission', 'source_cache_preview_is_accepted_source', 'evidence_preview_is_accepted_evidence', 'accepted_source_need_truth', 'accepted_source_candidate_truth', 'accepted_source_discovery_truth', 'accepted_source_candidate', 'accepted_source_truth', 'accepted_connector_truth', 'accepted_coverage_truth', 'accepted_scorecard_truth', 'accepted_reliability_truth', 'accepted_freshness_truth', 'accepted_dispute_truth', 'accepted_revocation_truth', 'accepted_lineage_truth', 'accepted_provenance_truth', 'accepted_pack_truth', 'accepted_evidence_truth', 'accepted_candidate_truth', 'accepted_public_record', 'public_index_mutation_allowed', 'master_index_mutation_allowed', 'public_index_mutated', 'master_index_mutated', 'source_registry_mutated', 'connector_registry_mutated', 'source_approval_claimed', 'connector_approval_claimed', 'source_discovery_permission_claimed', 'pack_export_import_permission_claimed', 'pack_signing_permission_claimed', 'pack_publication_permission_claimed', 'source_completeness_claimed', 'legal_approval_claimed', 'rights_clearance_claimed', 'safe_source_status_claimed', 'production_readiness_claimed', 'launch_readiness_claimed', 'automatic_future_connector_approval', 'coverage_manifest_is_exhaustive_global_coverage', 'reliability_score_is_reliability_truth', 'freshness_score_is_currentness_truth', 'dispute_revocation_candidate_is_automatic_deletion', 'lineage_auto_merges_sources']) | set(['changed_public_search_behavior', 'enabled_hosting', 'enabled_source_discovery', 'enabled_live_access', 'enabled_network_access', 'enabled_external_api', 'enabled_model_provider', 'enabled_local_access', 'enabled_private_access', 'enabled_user_supplied_url_fetch', 'enabled_authenticated_access', 'enabled_restricted_access', 'enabled_source_sync', 'enabled_connector_runtime', 'enabled_pack_export_import', 'enabled_pack_signing', 'enabled_pack_publication', 'enabled_pack_acceptance', 'enabled_registry_mutation', 'enabled_source_cache_writes', 'enabled_evidence_writes', 'enabled_review_queue_writes', 'mutated_public_index', 'mutated_master_index', 'network_calls_made', 'api_calls_made', 'model_provider_calls_made', 'source_discovery_runtime_used', 'web_search_used', 'crawl_used', 'scrape_used']) | set(['source_discovery_used', 'live_access_used', 'network_used', 'external_api_used', 'model_provider_used', 'local_access_used', 'private_source_access_used', 'authenticated_access_used', 'restricted_source_access_used', 'source_sync_used', 'web_search_output_included', 'crawl_output_included', 'scrape_output_included', 'source_pack_export_included', 'source_pack_import_included', 'connector_pack_export_included', 'connector_pack_import_included', 'pack_signature_included', 'pack_publication_included', 'source_registry_write_included', 'connector_registry_write_included', 'source_cache_write_included', 'evidence_write_included', 'review_queue_write_included', 'public_index_write_included', 'master_index_write_included', 'private_data_included', 'artifact_payload_included']) | {
    "source_pack_export_enabled", "source_pack_import_enabled", "connector_pack_export_enabled", "connector_pack_import_enabled",
    "pack_signing_enabled", "pack_publication_enabled", "source_registry_mutation_enabled", "connector_registry_mutation_enabled",
    "source_cache_write_enabled", "evidence_write_enabled", "review_queue_write_enabled", "public_index_write_enabled",
    "master_index_write_enabled", "source_discovery_runtime_enabled", "source_discovery_enabled", "live_access_enabled",
    "network_access_enabled", "model_provider_enabled", "source_sync_enabled", "connector_runtime_enabled",
}
FORBIDDEN_PAYLOAD_KEYS = {
    "network_output", "api_output", "model_provider_output", "crawled_data", "scraped_data", "source_discovery_runtime_output",
    "source_registry_write", "connector_registry_write", "source_cache_write", "evidence_write", "public_index_write",
    "master_index_write", "imported_pack", "exported_pack", "signed_pack", "private_data_payload", "artifact_payload",
}
SECRET_KEY_RE = re.compile(r"(^|_)(api_key|api_token|access_token|auth_token|client_secret|password|private_key|cookie|session_cookie|credential|token|receipt|license_key|entitlement)($|_)", re.IGNORECASE)
UNREDACTED_LOCATOR_RE = re.compile(r"(https?://|file://|[A-Za-z]:\\|\\\\|/Users/|/home/|/Volumes/)")


def validate_repo(root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    required = CONTRACTS + POLICIES + EXAMPLES + DOCS + [
        "scripts/normalize_h14_source_discovery_fixture.py",
        "scripts/replay_h14_source_discovery_fixtures.py",
        "scripts/summarize_h14_source_discovery_fixture_outputs.py",
        "scripts/validate_h14_source_discovery_fixture_runtime.py",
    ] + [f"control/audits/h14-bundle-02-source-discovery-fixture-runtime-v0/{name}" for name in AUDIT_FILES]
    for rel in required:
        path = root / rel
        if not path.exists():
            errors.append(f"missing required artifact: {rel}")
        elif path.suffix == ".json":
            payload = _load_json(path, errors)
            _scan_json_boundaries(payload, rel, errors, scan_strings=False)
    runtime_root = root / "control/prototypes/legacy_runtime/connectors/h14_source_discovery"
    for module in RUNTIME_MODULES:
        if not (runtime_root / module).exists():
            errors.append(f"missing runtime module: {module}")
    for source_id in H14_SOURCE_IDS:
        source_dir = root / "examples/connectors/h14_source_discovery/fixtures" / source_id
        if not source_dir.is_dir():
            errors.append(f"missing fixture directory: {source_id}")
            continue
        module = importlib.import_module(f"control.prototypes.legacy_runtime.connectors.h14_source_discovery.{SOURCE_MODULES[source_id]}")
        for kind, filename in H14_FIXTURE_FILES.items():
            fixture_path = source_dir / filename
            if not fixture_path.exists():
                errors.append(f"missing fixture: {fixture_path.relative_to(root).as_posix()}")
                continue
            fixture = _load_json(fixture_path, errors)
            if isinstance(fixture, dict):
                if fixture.get("fixture_kind") != kind:
                    errors.append(f"fixture kind mismatch: {fixture_path}")
                _scan_json_boundaries(fixture, str(fixture_path.relative_to(root)), errors)
                try:
                    loaded = load_h14_source_discovery_fixture(fixture_path)
                    normalized = module.normalize(loaded)
                    errors.extend(detect_h14_truth_boundary_violations(normalized))
                    errors.extend(detect_h14_product_boundary_violations(normalized))
                    errors.extend(detect_h14_registry_or_pack_mutation_violations(normalized))
                except Exception as exc:  # noqa: BLE001
                    errors.append(f"normalizer failed for {source_id}/{filename}: {exc}")
        normalized_path = root / "examples/connectors/h14_source_discovery/normalized" / f"{source_id}_normalized_record_v0.json"
        replay_path = root / "examples/connectors/h14_source_discovery/replay_results" / f"{source_id}_replay_result_v0.json"
        if not normalized_path.exists():
            errors.append(f"missing normalized example for {source_id}")
        if not replay_path.exists():
            errors.append(f"missing replay example for {source_id}")
    _scan_runtime(root, errors)
    _run_check([sys.executable, "scripts/normalize_h14_source_discovery_fixture.py", "--source-id", "source_need_registry", "--input", "examples/connectors/h14_source_discovery/fixtures/source_need_registry/source_need_record.json", "--check"], root, errors)
    _run_check([sys.executable, "scripts/replay_h14_source_discovery_fixtures.py", "--check"], root, errors)
    _run_check([sys.executable, "scripts/summarize_h14_source_discovery_fixture_outputs.py", "--input", "examples/connectors/h14_source_discovery", "--check"], root, errors)
    _check_forbidden_output_roots(root, errors)
    for rel in (".aide.local", ".local/eureka", ".cache/eureka", "source_discovery_runtime", "pack_import_staging", "pack_export_staging", "source_registry_mutation", "connector_registry_mutation", "external_source_fetch", "local_sources", "private_sources", "cas_store"):
        if (root / rel).exists():
            errors.append(f"forbidden local/private/runtime root exists: {rel}")
    return {
        "schema_version": "h14_source_discovery_fixture_runtime_validation.v0",
        "status": "valid" if not errors else "invalid",
        "source_count": len(H14_SOURCE_IDS),
        "fixture_kind_count": len(H14_FIXTURE_FILES),
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


def _scan_runtime(root: Path, errors: list[str]) -> None:
    runtime_root = root / "control/prototypes/legacy_runtime/connectors/h14_source_discovery"
    for path in runtime_root.glob("*.py"):
        text = path.read_text(encoding="utf-8")
        if BANNED_IMPORT_RE.search(text):
            errors.append(f"runtime module imports forbidden network/provider/browser library: {path}")
        for forbidden in ("httpx.", "aiohttp.", "openai.", "anthropic.", "selenium", "playwright"):
            if forbidden in text:
                errors.append(f"runtime module contains forbidden external call marker: {path} :: {forbidden}")


def _scan_json_boundaries(value: Any, label: str, errors: list[str], scan_strings: bool = True) -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            key_text = str(key)
            if key_text in FORBIDDEN_TRUE_KEYS and item is True:
                errors.append(f"{label} forbidden true value: {key_text}")
            if key_text in FORBIDDEN_PAYLOAD_KEYS:
                errors.append(f"{label} forbidden output/private/artifact key {key_text}")
            if SECRET_KEY_RE.search(key_text) and item not in (False, None, "", "unknown", "blocked_current", "blocked_current_no_credentials", "blocked_current_no_sessions", "not_evaluated_no_account_access"):
                errors.append(f"{label} forbidden secret/account key value: {key_text}")
            _scan_json_boundaries(item, label, errors, scan_strings)
    elif isinstance(value, list):
        for item in value:
            _scan_json_boundaries(item, label, errors, scan_strings)
    elif scan_strings and isinstance(value, str):
        if UNREDACTED_LOCATOR_RE.search(value):
            errors.append(f"{label} unrestricted local path or URL-like locator must be redacted")


def _check_forbidden_output_roots(root: Path, errors: list[str]) -> None:
    checks = [
        [sys.executable, "scripts/normalize_h14_source_discovery_fixture.py", "--source-id", "source_need_registry", "--input", "examples/connectors/h14_source_discovery/fixtures/source_need_registry/minimal_record.json", "--output", "site/dist/h14.json"],
        [sys.executable, "scripts/normalize_h14_source_discovery_fixture.py", "--source-id", "source_need_registry", "--input", "examples/connectors/h14_source_discovery/fixtures/source_need_registry/minimal_record.json", "--output", "data/public_index/h14.json"],
        [sys.executable, "scripts/normalize_h14_source_discovery_fixture.py", "--source-id", "source_need_registry", "--input", "examples/connectors/h14_source_discovery/fixtures/source_need_registry/minimal_record.json", "--output", "source_registry_mutation/h14.json"],
        [sys.executable, "scripts/normalize_h14_source_discovery_fixture.py", "--source-id", "source_need_registry", "--input", "examples/connectors/h14_source_discovery/fixtures/source_need_registry/minimal_record.json", "--output", "pack_import_staging/h14.json"],
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
