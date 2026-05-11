"""Offline H14 Source OS rollup fixture normalization helpers."""

from __future__ import annotations

import json
import re
from collections.abc import Mapping
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
SAFE_FIXTURE_ROOT = (REPO_ROOT / "examples/connectors/h14_source_discovery/fixtures").resolve()
H14_SOURCE_CONFIGS = {'source_need_registry': {'label': 'SourceNeed registry', 'connector_family': 'source_need_registry', 'trust_lane': 'internal_control', 'primary': 'source_need'}, 'source_candidate_registry': {'label': 'SourceCandidate registry', 'connector_family': 'source_candidate_registry', 'trust_lane': 'internal_control', 'primary': 'source_candidate'}, 'source_discovery_policy': {'label': 'Source discovery policy', 'connector_family': 'source_discovery_policy', 'trust_lane': 'governance', 'primary': 'source_discovery'}, 'source_pack_manifest': {'label': 'Source pack manifest', 'connector_family': 'source_pack_manifest', 'trust_lane': 'governance', 'primary': 'source_pack_manifest'}, 'connector_pack_manifest': {'label': 'Connector pack manifest', 'connector_family': 'connector_pack_manifest', 'trust_lane': 'governance', 'primary': 'connector_pack_manifest'}, 'coverage_manifest': {'label': 'Coverage manifest', 'connector_family': 'coverage_manifest', 'trust_lane': 'governance', 'primary': 'coverage_manifest'}, 'connector_scorecard': {'label': 'Connector scorecard', 'connector_family': 'connector_scorecard', 'trust_lane': 'governance', 'primary': 'connector_scorecard'}, 'source_reliability_freshness': {'label': 'Source reliability and freshness', 'connector_family': 'source_reliability_freshness', 'trust_lane': 'governance', 'primary': 'reliability_freshness'}, 'source_dispute_revocation': {'label': 'Source dispute and revocation', 'connector_family': 'source_dispute_revocation', 'trust_lane': 'governance', 'primary': 'dispute_revocation'}, 'source_lineage_provenance': {'label': 'Source lineage and provenance', 'connector_family': 'source_lineage_provenance', 'trust_lane': 'governance', 'primary': 'lineage_provenance'}, 'h14_policy_blocked': {'label': 'H14 policy-blocked boundary', 'connector_family': 'policy_blocked_boundary', 'trust_lane': 'governance', 'primary': 'policy_blocked'}}
H14_SOURCE_IDS = tuple(H14_SOURCE_CONFIGS)
H14_FIXTURE_FILES = {'minimal': 'minimal_record.json', 'source_need': 'source_need_record.json', 'source_candidate': 'source_candidate_record.json', 'source_discovery_candidate': 'source_discovery_candidate_record.json', 'source_pack_manifest': 'source_pack_manifest_record.json', 'connector_pack_manifest': 'connector_pack_manifest_record.json', 'coverage_manifest': 'coverage_manifest_record.json', 'connector_scorecard': 'connector_scorecard_record.json', 'reliability_freshness': 'reliability_freshness_record.json', 'dispute_revocation': 'dispute_revocation_record.json', 'lineage_provenance': 'lineage_provenance_record.json', 'pack_import_export_boundary': 'pack_import_export_boundary_record.json', 'policy_blocked': 'policy_blocked_record.json'}
CANDIDATE_CONFIGS = {'source_need': {'schema': 'h14_source_need_candidate.v0', 'contract': 'h14_source_need_candidate.v0.json', 'field': 'source_need_candidate', 'file': 'source_need_candidate_v0.json', 'truth_key': 'source_need_candidate_is_source_approval', 'limitation': 'SourceNeed candidate only; it is not source approval, connector approval, discovery permission, probing permission, crawling permission, import/export permission, or public-index permission.'}, 'source_candidate': {'schema': 'h14_source_candidate_candidate.v0', 'contract': 'h14_source_candidate_candidate.v0.json', 'field': 'source_candidate_candidate', 'file': 'source_candidate_candidate_v0.json', 'truth_key': 'source_candidate_candidate_is_source_truth', 'limitation': 'SourceCandidate candidate only; locator and capability fields do not authorize fetching, registry entry, source approval, or accepted truth.'}, 'source_discovery': {'schema': 'h14_source_discovery_candidate.v0', 'contract': 'h14_source_discovery_candidate.v0.json', 'field': 'source_discovery_candidate', 'file': 'source_discovery_candidate_v0.json', 'truth_key': 'source_discovery_candidate_is_registry_mutation', 'limitation': 'Source discovery candidate only; it is not a live discovery result, registry mutation, source approval, or public truth.'}, 'source_pack_manifest': {'schema': 'h14_source_pack_manifest_candidate.v0', 'contract': 'h14_source_pack_manifest_candidate.v0.json', 'field': 'source_pack_manifest_candidate', 'file': 'source_pack_manifest_candidate_v0.json', 'truth_key': 'source_pack_manifest_candidate_is_exported_pack', 'limitation': 'Source pack manifest candidate only; no pack is exported, imported, signed, accepted, published, or redistributed.'}, 'connector_pack_manifest': {'schema': 'h14_connector_pack_manifest_candidate.v0', 'contract': 'h14_connector_pack_manifest_candidate.v0.json', 'field': 'connector_pack_manifest_candidate', 'file': 'connector_pack_manifest_candidate_v0.json', 'truth_key': 'connector_pack_manifest_candidate_is_connector_approval', 'limitation': 'Connector pack manifest candidate only; it is not exported connector code, connector approval, or runtime enablement.'}, 'coverage_manifest': {'schema': 'h14_coverage_manifest_candidate.v0', 'contract': 'h14_coverage_manifest_candidate.v0.json', 'field': 'coverage_manifest_candidate', 'file': 'coverage_manifest_candidate_v0.json', 'truth_key': 'coverage_manifest_candidate_is_exhaustive', 'limitation': 'Coverage manifest candidate only; it is not exhaustive global coverage, source completeness, or public-index readiness proof.'}, 'connector_scorecard': {'schema': 'h14_connector_scorecard_candidate.v0', 'contract': 'h14_connector_scorecard_candidate.v0.json', 'field': 'connector_scorecard_candidate', 'file': 'connector_scorecard_candidate_v0.json', 'truth_key': 'connector_scorecard_candidate_is_connector_approval', 'limitation': 'Connector scorecard candidate only; readiness fields are review inputs, not connector approval or production readiness.'}, 'source_reliability_freshness': {'schema': 'h14_source_reliability_freshness_candidate.v0', 'contract': 'h14_source_reliability_freshness_candidate.v0.json', 'field': 'source_reliability_freshness_candidate', 'file': 'source_reliability_freshness_candidate_v0.json', 'truth_key': 'source_reliability_freshness_candidate_is_truth', 'limitation': 'Reliability/freshness candidate only; signals do not prove reliability truth, currentness truth, availability truth, or policy override.'}, 'source_dispute_revocation': {'schema': 'h14_source_dispute_revocation_candidate.v0', 'contract': 'h14_source_dispute_revocation_candidate.v0.json', 'field': 'source_dispute_revocation_candidate', 'file': 'source_dispute_revocation_candidate_v0.json', 'truth_key': 'source_dispute_revocation_candidate_is_accepted_truth', 'limitation': 'Dispute/revocation candidate only; it is not accepted truth, automatic deletion, source disabling, public notice, or retraction.'}, 'source_lineage_provenance': {'schema': 'h14_source_lineage_provenance_candidate.v0', 'contract': 'h14_source_lineage_provenance_candidate.v0.json', 'field': 'source_lineage_provenance_candidate', 'file': 'source_lineage_provenance_candidate_v0.json', 'truth_key': 'source_lineage_provenance_candidate_is_lineage_truth', 'limitation': 'Lineage/provenance candidate only; it does not prove authority, authenticity, rights, mirror relation, derivative relation, or auto-merge permission.'}, 'pack_import_export_boundary': {'schema': 'h14_pack_import_export_boundary_candidate.v0', 'contract': 'h14_pack_import_export_boundary_candidate.v0.json', 'field': 'pack_import_export_boundary_candidate', 'file': 'pack_import_export_boundary_candidate_v0.json', 'truth_key': 'pack_import_export_boundary_candidate_grants_permission', 'limitation': 'Pack import/export boundary candidate only; it grants no import, export, signing, publication, acceptance, or redistribution permission.'}}
TRUTH_FORBIDDEN_TRUE_KEYS = set(['normalized_record_is_public_truth', 'source_need_candidate_is_source_approval', 'source_candidate_candidate_is_source_truth', 'source_discovery_candidate_is_registry_mutation', 'source_pack_manifest_candidate_is_exported_pack', 'connector_pack_manifest_candidate_is_connector_approval', 'coverage_manifest_candidate_is_exhaustive', 'connector_scorecard_candidate_is_connector_approval', 'source_reliability_freshness_candidate_is_truth', 'source_dispute_revocation_candidate_is_accepted_truth', 'source_lineage_provenance_candidate_is_lineage_truth', 'pack_import_export_boundary_candidate_grants_permission', 'source_cache_preview_is_accepted_source', 'evidence_preview_is_accepted_evidence', 'accepted_source_need_truth', 'accepted_source_candidate_truth', 'accepted_source_discovery_truth', 'accepted_source_candidate', 'accepted_source_truth', 'accepted_connector_truth', 'accepted_coverage_truth', 'accepted_scorecard_truth', 'accepted_reliability_truth', 'accepted_freshness_truth', 'accepted_dispute_truth', 'accepted_revocation_truth', 'accepted_lineage_truth', 'accepted_provenance_truth', 'accepted_pack_truth', 'accepted_evidence_truth', 'accepted_candidate_truth', 'accepted_public_record', 'public_index_mutation_allowed', 'master_index_mutation_allowed', 'public_index_mutated', 'master_index_mutated', 'source_registry_mutated', 'connector_registry_mutated', 'source_approval_claimed', 'connector_approval_claimed', 'source_discovery_permission_claimed', 'pack_export_import_permission_claimed', 'pack_signing_permission_claimed', 'pack_publication_permission_claimed', 'source_completeness_claimed', 'legal_approval_claimed', 'rights_clearance_claimed', 'safe_source_status_claimed', 'production_readiness_claimed', 'launch_readiness_claimed', 'automatic_future_connector_approval', 'coverage_manifest_is_exhaustive_global_coverage', 'reliability_score_is_reliability_truth', 'freshness_score_is_currentness_truth', 'dispute_revocation_candidate_is_automatic_deletion', 'lineage_auto_merges_sources'])
PRODUCT_FORBIDDEN_TRUE_KEYS = set(['changed_public_search_behavior', 'enabled_hosting', 'enabled_source_discovery', 'enabled_live_access', 'enabled_network_access', 'enabled_external_api', 'enabled_model_provider', 'enabled_local_access', 'enabled_private_access', 'enabled_user_supplied_url_fetch', 'enabled_authenticated_access', 'enabled_restricted_access', 'enabled_source_sync', 'enabled_connector_runtime', 'enabled_pack_export_import', 'enabled_pack_signing', 'enabled_pack_publication', 'enabled_pack_acceptance', 'enabled_registry_mutation', 'enabled_source_cache_writes', 'enabled_evidence_writes', 'enabled_review_queue_writes', 'mutated_public_index', 'mutated_master_index', 'network_calls_made', 'api_calls_made', 'model_provider_calls_made', 'source_discovery_runtime_used', 'web_search_used', 'crawl_used', 'scrape_used'])
FIXTURE_FORBIDDEN_TRUE_KEYS = set(['source_discovery_used', 'live_access_used', 'network_used', 'external_api_used', 'model_provider_used', 'local_access_used', 'private_source_access_used', 'authenticated_access_used', 'restricted_source_access_used', 'source_sync_used', 'web_search_output_included', 'crawl_output_included', 'scrape_output_included', 'source_pack_export_included', 'source_pack_import_included', 'connector_pack_export_included', 'connector_pack_import_included', 'pack_signature_included', 'pack_publication_included', 'source_registry_write_included', 'connector_registry_write_included', 'source_cache_write_included', 'evidence_write_included', 'review_queue_write_included', 'public_index_write_included', 'master_index_write_included', 'private_data_included', 'artifact_payload_included'])
NORMALIZED_FIELDS = ('source_need_ref', 'source_candidate_ref', 'source_discovery_candidate_ref', 'source_pack_manifest_ref', 'connector_pack_manifest_ref', 'coverage_manifest_ref', 'connector_scorecard_ref', 'reliability_freshness_ref', 'dispute_revocation_ref', 'lineage_provenance_ref', 'pack_import_export_boundary_ref', 'triggering_gap_ref', 'triggering_search_need_ref', 'triggering_source_gap_ref', 'query_family_ref', 'missing_source_family_candidate', 'target_source_capability_candidate', 'target_index_depth_candidate', 'workunit_preview_ref', 'candidate_source_family', 'candidate_connector_family', 'candidate_locator_redacted_or_public', 'candidate_capabilities', 'candidate_trust_lane', 'candidate_reason', 'source_pack_kind', 'source_pack_scope', 'connector_pack_kind', 'coverage_scope', 'coverage_depth', 'coverage_basis', 'scorecard_status', 'reliability_signal_candidates', 'freshness_signal_candidates', 'availability_signal_candidates', 'error_signal_candidates', 'dispute_kind', 'source_status_candidate', 'lineage_related_source_refs', 'provenance_claim_candidates', 'exportability_label', 'importability_label', 'blocked_action_candidate', 'source_native_id', 'metadata_summary')
CANDIDATE_FIELD_MAP = {'source_need': ['source_need_ref', 'triggering_gap_ref', 'triggering_search_need_ref', 'triggering_source_gap_ref', 'query_family_ref', 'missing_source_family_candidate', 'target_source_capability_candidate', 'target_index_depth_candidate', 'workunit_preview_ref'], 'source_candidate': ['source_candidate_ref', 'candidate_source_family', 'candidate_connector_family', 'candidate_locator_redacted_or_public', 'candidate_capabilities', 'candidate_trust_lane', 'candidate_reason'], 'source_discovery': ['source_discovery_candidate_ref', 'triggering_gap_ref', 'candidate_source_family', 'candidate_connector_family', 'candidate_reason'], 'source_pack_manifest': ['source_pack_manifest_ref', 'source_pack_kind', 'source_pack_scope', 'exportability_label', 'importability_label'], 'connector_pack_manifest': ['connector_pack_manifest_ref', 'connector_pack_kind', 'candidate_connector_family', 'exportability_label', 'importability_label'], 'coverage_manifest': ['coverage_manifest_ref', 'coverage_scope', 'coverage_depth', 'coverage_basis'], 'connector_scorecard': ['connector_scorecard_ref', 'candidate_connector_family', 'scorecard_status'], 'source_reliability_freshness': ['reliability_freshness_ref', 'reliability_signal_candidates', 'freshness_signal_candidates', 'availability_signal_candidates', 'error_signal_candidates'], 'source_dispute_revocation': ['dispute_revocation_ref', 'dispute_kind', 'source_status_candidate'], 'source_lineage_provenance': ['lineage_provenance_ref', 'lineage_related_source_refs', 'provenance_claim_candidates'], 'pack_import_export_boundary': ['pack_import_export_boundary_ref', 'exportability_label', 'importability_label', 'blocked_action_candidate']}
SECRET_KEY_RE = re.compile(r"(^|_)(api_key|api_token|access_token|auth_token|client_secret|password|private_key|cookie|session_cookie|credential|token|receipt|license_key|entitlement)($|_)", re.IGNORECASE)
PRIVATE_PAYLOAD_KEY_RE = re.compile(r"(private_file_payload|local_file_content|account_payload|private_data_payload|artifact_payload|cas_blob|exported_pack|imported_pack|signed_pack|source_registry_write|connector_registry_write|source_cache_write|evidence_write|public_index_write|master_index_write)", re.IGNORECASE)
UNREDACTED_LOCATOR_RE = re.compile(r"(https?://|file://|[A-Za-z]:\\|\\\\|/Users/|/home/|/Volumes/)")


def load_h14_source_discovery_fixture(path: str | Path) -> dict[str, Any]:
    fixture_path = validate_h14_fixture_input_path(path)
    payload = json.loads(fixture_path.read_text(encoding="utf-8"))
    _require_fixture_boundaries(payload)
    return payload


def validate_h14_fixture_input_path(path: str | Path) -> Path:
    candidate = Path(path)
    if not candidate.is_absolute():
        candidate = REPO_ROOT / candidate
    resolved = candidate.resolve()
    try:
        resolved.relative_to(SAFE_FIXTURE_ROOT)
    except ValueError as exc:
        raise ValueError("fixture input must be under committed H14 fixture root") from exc
    return resolved


def normalize_h14_source_discovery_fixture(raw_fixture: Mapping[str, Any], source_id: str, policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    _require_fixture_boundaries(raw_fixture)
    if source_id not in H14_SOURCE_CONFIGS:
        raise ValueError(f"unknown H14 source_id: {source_id}")
    if raw_fixture.get("source_id") != source_id:
        raise ValueError("fixture source_id does not match requested source")
    config = H14_SOURCE_CONFIGS[source_id]
    payload = _mapping(raw_fixture.get("fixture_payload"), "fixture_payload")
    fixture_kind = _text(raw_fixture.get("fixture_kind")) or "unknown"
    native_id = _text(payload.get("source_native_id")) or _text(raw_fixture.get("fixture_id")) or fixture_kind
    record: dict[str, Any] = {
        "schema_version": "h14_source_discovery_normalized_record.v0",
        "normalized_record_id": f"h14.normalized.{source_id}.{_slug(native_id)}.v0",
        "source_id": source_id,
        "connector_family": config["connector_family"],
        "source_record_kind": _text(payload.get("source_record_kind")) or fixture_kind,
        "source_metadata": {
            "fixture_id": raw_fixture.get("fixture_id", "unknown"),
            "fixture_kind": fixture_kind,
            "fixture_status": raw_fixture.get("fixture_status", "unknown"),
            "source_label": config["label"],
            "trust_lane": config["trust_lane"],
            "metadata_summary": payload.get("metadata_summary", "synthetic H14 Source OS rollup fixture metadata only"),
        },
        "source_limitations": _dedupe(_list(raw_fixture.get("limitations")) + _missing_optional_limitations(payload)),
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": [
            "Offline H14 fixture normalization only.",
            "Candidate and preview outputs require review and do not grant source discovery, live access, model/provider calls, pack import/export, registry mutation, source cache write, evidence write, index mutation, publication, or public truth.",
        ],
    }
    for field in NORMALIZED_FIELDS:
        record[field] = _value(payload.get(field))
    record["source_need_candidate"] = build_h14_source_need_candidate(record, policy)
    record["source_candidate_candidate"] = build_h14_source_candidate_candidate(record, policy)
    record["source_discovery_candidate"] = build_h14_source_discovery_candidate(record, policy)
    record["source_pack_manifest_candidate"] = build_h14_source_pack_manifest_candidate(record, policy)
    record["connector_pack_manifest_candidate"] = build_h14_connector_pack_manifest_candidate(record, policy)
    record["coverage_manifest_candidate"] = build_h14_coverage_manifest_candidate(record, policy)
    record["connector_scorecard_candidate"] = build_h14_connector_scorecard_candidate(record, policy)
    record["source_reliability_freshness_candidate"] = build_h14_source_reliability_freshness_candidate(record, policy)
    record["source_dispute_revocation_candidate"] = build_h14_source_dispute_revocation_candidate(record, policy)
    record["source_lineage_provenance_candidate"] = build_h14_source_lineage_provenance_candidate(record, policy)
    record["pack_import_export_boundary_candidate"] = build_h14_pack_import_export_boundary_candidate(record, policy)
    record["source_cache_candidate_preview"] = build_h14_source_cache_candidate_preview(record, policy)
    record["evidence_candidate_preview"] = build_h14_evidence_candidate_preview(record, policy)
    _raise_on_boundary_errors(record)
    return record


def build_h14_source_need_candidate(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return _candidate(normalized_record, "source_need")


def build_h14_source_candidate_candidate(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return _candidate(normalized_record, "source_candidate")


def build_h14_source_discovery_candidate(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return _candidate(normalized_record, "source_discovery")


def build_h14_source_pack_manifest_candidate(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return _candidate(normalized_record, "source_pack_manifest")


def build_h14_connector_pack_manifest_candidate(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return _candidate(normalized_record, "connector_pack_manifest")


def build_h14_coverage_manifest_candidate(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return _candidate(normalized_record, "coverage_manifest")


def build_h14_connector_scorecard_candidate(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return _candidate(normalized_record, "connector_scorecard")


def build_h14_source_reliability_freshness_candidate(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return _candidate(normalized_record, "source_reliability_freshness")


def build_h14_source_dispute_revocation_candidate(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return _candidate(normalized_record, "source_dispute_revocation")


def build_h14_source_lineage_provenance_candidate(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return _candidate(normalized_record, "source_lineage_provenance")


def build_h14_pack_import_export_boundary_candidate(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return _candidate(normalized_record, "pack_import_export_boundary")


def build_h14_source_cache_candidate_preview(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    preview = {
        "schema_version": "h14_source_discovery_source_cache_candidate_preview.v0",
        "preview_id": f"h14.source_cache.preview.{normalized_record.get('source_id')}.{_slug(normalized_record.get('source_native_id'))}.v0",
        "source_id": normalized_record.get("source_id"),
        "source_record_ref": normalized_record.get("normalized_record_id"),
        "preview_only": True,
        "accepted_source": False,
        "mutates_source_cache": False,
        "supporting_fields": {
            "source_record_kind": normalized_record.get("source_record_kind"),
            "connector_family": normalized_record.get("connector_family"),
            "coverage_basis": normalized_record.get("coverage_basis"),
        },
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "limitations": ["Source-cache preview only; no source cache write or source truth acceptance occurs."],
    }
    _raise_on_boundary_errors(preview)
    return preview


def build_h14_evidence_candidate_preview(normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    preview = {
        "schema_version": "h14_source_discovery_evidence_candidate_preview.v0",
        "preview_id": f"h14.evidence.preview.{normalized_record.get('source_id')}.{_slug(normalized_record.get('source_native_id'))}.v0",
        "source_id": normalized_record.get("source_id"),
        "source_record_ref": normalized_record.get("normalized_record_id"),
        "preview_only": True,
        "accepted_evidence": False,
        "mutates_evidence_ledger": False,
        "claim_summary": "H14 fixture Source OS rollup metadata candidate only.",
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "limitations": ["Evidence preview only; no evidence acceptance occurs."],
    }
    _raise_on_boundary_errors(preview)
    return preview


def build_h14_fixture_replay_result(fixture: Mapping[str, Any], normalized_record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    result = {
        "schema_version": "h14_source_discovery_fixture_replay_result.v0",
        "fixture_replay_result_id": f"h14.replay.{fixture.get('source_id')}.{fixture.get('fixture_kind')}.v0",
        "source_id": fixture.get("source_id"),
        "connector_family": normalized_record.get("connector_family"),
        "fixture_ref": fixture.get("fixture_id"),
        "normalized_record_ref": normalized_record.get("normalized_record_id"),
        "result_status": "normalized_fixture",
        "source_discovery_used": False,
        "live_access_used": False,
        "network_used": False,
        "pack_export_import_used": False,
        "registry_mutation_used": False,
        "source_cache_write_used": False,
        "evidence_write_used": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "candidate_counts": {candidate["field"]: 1 for candidate in CANDIDATE_CONFIGS.values()},
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "limitations": ["Fixture replay output is not source, evidence, candidate, public, registry, pack, coverage, scorecard, reliability, freshness, dispute, revocation, lineage, or master truth."],
    }
    _raise_on_boundary_errors(result)
    return result


def summarize_h14_normalized_record(record: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "source_id": record.get("source_id"),
        "source_record_kind": record.get("source_record_kind"),
        "candidate_count": len(CANDIDATE_CONFIGS),
        "truth_boundary_violations": detect_h14_truth_boundary_violations(record),
        "product_boundary_violations": detect_h14_product_boundary_violations(record),
        "registry_or_pack_mutation_violations": detect_h14_registry_or_pack_mutation_violations(record),
    }


def detect_h14_truth_boundary_violations(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    violations: list[str] = []
    _collect_true_keys(record, TRUTH_FORBIDDEN_TRUE_KEYS, "truth", violations)
    return violations


def detect_h14_product_boundary_violations(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    violations: list[str] = []
    _collect_true_keys(record, PRODUCT_FORBIDDEN_TRUE_KEYS, "product", violations)
    return violations


def detect_h14_registry_or_pack_mutation_violations(record: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    violations: list[str] = []
    _collect_true_keys(record, {"source_registry_write_included", "connector_registry_write_included", "source_pack_export_included", "source_pack_import_included", "connector_pack_export_included", "connector_pack_import_included", "pack_signature_included", "pack_publication_included", "source_registry_mutated", "connector_registry_mutated", "pack_export_import_permission_claimed"}, "mutation", violations)
    _collect_secret_or_private_data(record, "record", violations)
    return violations


def _candidate(normalized_record: Mapping[str, Any], kind: str) -> dict[str, Any]:
    config = CANDIDATE_CONFIGS[kind]
    fields = CANDIDATE_FIELD_MAP[kind]
    supporting = {field: normalized_record.get(field) for field in fields if normalized_record.get(field) not in (None, "", [], {}, "unknown")}
    missing = [field for field in fields if field not in supporting]
    candidate = {
        "schema_version": config["schema"],
        "candidate_id": f"h14.{kind}.{normalized_record.get('source_id')}.{_slug(normalized_record.get('source_native_id'))}.v0",
        "source_id": normalized_record.get("source_id"),
        "source_record_ref": normalized_record.get("normalized_record_id"),
        "candidate_kind": kind,
        "supporting_fields": supporting,
        "missing_fields": missing,
        "confidence_or_uncertainty": "low_confidence_fixture_candidate",
        "limitations": [config["limitation"], "Review required before downstream use."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
    }
    _raise_on_boundary_errors(candidate)
    return candidate


def _require_fixture_boundaries(raw_fixture: Mapping[str, Any]) -> None:
    if not isinstance(raw_fixture, Mapping):
        raise ValueError("fixture must be a mapping")
    errors: list[str] = []
    _collect_true_keys(raw_fixture, FIXTURE_FORBIDDEN_TRUE_KEYS, "fixture", errors)
    _collect_true_keys(raw_fixture, TRUTH_FORBIDDEN_TRUE_KEYS, "truth", errors)
    _collect_true_keys(raw_fixture, PRODUCT_FORBIDDEN_TRUE_KEYS, "product", errors)
    _collect_secret_or_private_data(raw_fixture, "fixture", errors)
    if errors:
        raise ValueError("; ".join(errors))


def _raise_on_boundary_errors(record: Mapping[str, Any]) -> None:
    errors = detect_h14_truth_boundary_violations(record) + detect_h14_product_boundary_violations(record) + detect_h14_registry_or_pack_mutation_violations(record)
    if errors:
        raise ValueError("; ".join(errors))


def _collect_true_keys(value: Any, forbidden: set[str], prefix: str, errors: list[str]) -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            if str(key) in forbidden and item is True:
                errors.append(f"{prefix} boundary true claim: {key}")
            _collect_true_keys(item, forbidden, prefix, errors)
    elif isinstance(value, list):
        for item in value:
            _collect_true_keys(item, forbidden, prefix, errors)


def _collect_secret_or_private_data(value: Any, label: str, errors: list[str]) -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            key_text = str(key)
            if SECRET_KEY_RE.search(key_text) and item not in (False, None, "", "unknown", "blocked_current", "blocked_current_no_credentials", "blocked_current_no_sessions", "not_evaluated_no_account_access"):
                errors.append(f"{label} forbidden secret/account field: {key_text}")
            if PRIVATE_PAYLOAD_KEY_RE.search(key_text) and item not in (False, None, "", [], {}, "no_blob_present", "blocked_current", "preview_only_no_write"):
                errors.append(f"{label} forbidden private payload field: {key_text}")
            _collect_secret_or_private_data(item, label, errors)
    elif isinstance(value, list):
        for item in value:
            _collect_secret_or_private_data(item, label, errors)
    elif isinstance(value, str):
        if UNREDACTED_LOCATOR_RE.search(value):
            errors.append(f"{label} contains unrestricted local path or URL-like locator")


def _truth_boundary() -> dict[str, bool]:
    return {key: False for key in TRUTH_FORBIDDEN_TRUE_KEYS}


def _product_boundary() -> dict[str, bool]:
    return {key: False for key in PRODUCT_FORBIDDEN_TRUE_KEYS}


def _mapping(value: Any, label: str) -> Mapping[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise ValueError(f"{label} must be a mapping")
    return value


def _value(value: Any) -> Any:
    if value is None:
        return "unknown"
    if isinstance(value, str):
        return value.strip() or "unknown"
    return value


def _text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()


def _list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item) for item in value]
    return [str(value)]


def _missing_optional_limitations(payload: Mapping[str, Any]) -> list[str]:
    missing = [field for field in NORMALIZED_FIELDS if field not in payload]
    if not missing:
        return []
    return ["Missing optional H14 fixture fields are unknown, not fabricated: " + ", ".join(missing[:10])]


def _dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for value in values:
        text = _text(value)
        if text and text not in seen:
            result.append(text)
            seen.add(text)
    return result


def _slug(value: Any) -> str:
    text = re.sub(r"[^a-zA-Z0-9_.-]+", "-", _text(value).lower()).strip("-")
    return text[:64] or "unknown"
