"""Offline H14 Source OS review integration helpers.

These helpers consume committed fixture replay outputs and committed rollup
dry-run result examples. They create review seeds and previews only.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
import hashlib
import json
from pathlib import Path
from typing import Any

from runtime.connectors.h14_source_discovery.normalizer_common import (
    H14_SOURCE_CONFIGS,
    H14_SOURCE_IDS,
    PRODUCT_FORBIDDEN_TRUE_KEYS as H14_PRODUCT_FORBIDDEN_TRUE_KEYS,
    TRUTH_FORBIDDEN_TRUE_KEYS as H14_TRUTH_FORBIDDEN_TRUE_KEYS,
)

EXTRA_TRUTH_FORBIDDEN_TRUE_KEYS = set([
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
    "source_pack_preview_is_imported_or_submitted", "review_seed_is_review_decision",
    "source_registry_mutated", "connector_registry_mutated", "public_index_mutated",
    "master_index_mutated", "rights_clearance_claimed", "source_completeness_claimed",
    "production_readiness_claimed", "launch_readiness_claimed",
])
EXTRA_PRODUCT_FORBIDDEN_TRUE_KEYS = set([
    "enables_source_discovery_runtime", "enables_live_access", "enables_network_access",
    "enables_model_provider", "enables_source_sync", "enables_pack_export_import",
    "enables_source_cache_write", "enables_evidence_write", "mutates_source_registry",
    "mutates_connector_registry", "mutates_source_cache", "mutates_evidence_ledger",
    "mutates_review_queue", "mutates_public_index", "mutates_master_index",
    "source_cache_write_performed", "evidence_write_performed",
    "review_queue_write_performed", "public_index_write_performed",
    "master_index_write_performed", "registry_mutation_performed",
    "pack_export_import_performed",
])
FORBIDDEN_TRUTH_TRUE_KEYS = set(H14_TRUTH_FORBIDDEN_TRUE_KEYS) | EXTRA_TRUTH_FORBIDDEN_TRUE_KEYS
FORBIDDEN_PRODUCT_TRUE_KEYS = set(H14_PRODUCT_FORBIDDEN_TRUE_KEYS) | EXTRA_PRODUCT_FORBIDDEN_TRUE_KEYS

REVIEW_SEED_KEYS = (
    "source_need_review_seeds",
    "source_candidate_review_seeds",
    "source_discovery_candidate_review_seeds",
    "source_pack_manifest_review_seeds",
    "connector_pack_manifest_review_seeds",
    "coverage_manifest_review_seeds",
    "connector_scorecard_review_seeds",
    "reliability_freshness_review_seeds",
    "dispute_revocation_review_seeds",
    "lineage_provenance_review_seeds",
    "pack_import_export_boundary_review_seeds",
    "source_cache_review_seeds",
    "evidence_candidate_review_seeds",
)

KIND_CONFIG = {
    "source_need": ("h14_source_need_review_seed.v0", "source_need_candidate", "accepts_source_need_truth", "source_need_seed_accepts_source_approval", "SourceNeed review seed is not source approval, source discovery permission, registry mutation, or public truth."),
    "source_candidate": ("h14_source_candidate_review_seed.v0", "source_candidate_candidate", "accepts_source_candidate_truth", "source_candidate_seed_accepts_source_truth", "SourceCandidate review seed is not accepted source truth or source approval."),
    "source_discovery_candidate": ("h14_source_discovery_candidate_review_seed.v0", "source_discovery_candidate", "accepts_source_discovery_truth", "source_discovery_seed_mutates_registry", "Source discovery candidate review seed does not run discovery or mutate registries."),
    "source_pack_manifest": ("h14_source_pack_manifest_review_seed.v0", "source_pack_manifest_candidate", "accepts_source_pack_truth", "source_pack_manifest_seed_exports_pack", "Source pack manifest review seed is not an exported, imported, signed, submitted, accepted, or published pack."),
    "connector_pack_manifest": ("h14_connector_pack_manifest_review_seed.v0", "connector_pack_manifest_candidate", "accepts_connector_pack_truth", "connector_pack_manifest_seed_approves_connector", "Connector pack manifest review seed does not approve connector code or runtime use."),
    "coverage_manifest": ("h14_coverage_manifest_review_seed.v0", "coverage_manifest_candidate", "accepts_coverage_truth", "coverage_manifest_seed_accepts_coverage_truth", "Coverage manifest review seed is scoped coverage evidence only, not exhaustive coverage or source completeness."),
    "connector_scorecard": ("h14_connector_scorecard_review_seed.v0", "connector_scorecard_candidate", "accepts_scorecard_truth", "connector_scorecard_seed_approves_connector", "Connector scorecard review seed is a review input only, not connector approval or production readiness."),
    "reliability_freshness": ("h14_reliability_freshness_review_seed.v0", "source_reliability_freshness_candidate", "accepts_reliability_truth", "reliability_freshness_seed_accepts_truth", "Reliability/freshness review seed is not reliability truth, freshness truth, or currentness proof."),
    "dispute_revocation": ("h14_dispute_revocation_review_seed.v0", "source_dispute_revocation_candidate", "accepts_dispute_revocation_truth", "dispute_revocation_seed_accepts_truth", "Dispute/revocation review seed is not accepted truth, automatic deletion, or public notice."),
    "lineage_provenance": ("h14_lineage_provenance_review_seed.v0", "source_lineage_provenance_candidate", "accepts_lineage_provenance_truth", "lineage_provenance_seed_accepts_lineage_truth", "Lineage/provenance review seed does not prove lineage truth or merge sources."),
    "pack_import_export_boundary": ("h14_pack_import_export_boundary_review_seed.v0", "pack_import_export_boundary_candidate", "accepts_candidate_truth", "pack_boundary_seed_grants_import_export_permission", "Pack boundary review seed grants no import, export, signing, publication, acceptance, or redistribution permission."),
    "source_cache": ("h14_source_cache_review_seed.v0", "source_cache_candidate_preview", "accepts_source_truth", "source_cache_review_seed_accepts_source", "Source-cache review seed is not source acceptance and does not write source cache state."),
    "evidence_candidate": ("h14_evidence_candidate_review_seed.v0", "evidence_candidate_preview", "accepts_evidence_truth", "evidence_review_seed_accepts_evidence", "Evidence candidate review seed is not accepted evidence and does not write an evidence ledger."),
}


def load_h14_source_discovery_outputs(paths: Sequence[str | Path]) -> list[dict[str, Any]]:
    outputs: list[dict[str, Any]] = []
    for path_text in paths:
        path = Path(path_text)
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, Mapping):
            raise ValueError(f"{path} must contain a JSON object")
        outputs.append(dict(payload))
    return outputs


def _build_review_seed(kind: str, inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    schema, subject_type, accept_key, permission_key, limitation = KIND_CONFIG[kind]
    source_id = _source_id(inputs)
    seed = _seed_base(kind, source_id, _first_ref(inputs, subject_type), inputs)
    seed.update({
        "schema_version": schema,
        "review_subject_type": subject_type,
        accept_key: False,
        permission_key: False,
        "review_seed_is_review_decision": False,
        "source_cache_write_allowed_current": False,
        "evidence_ledger_write_allowed_current": False,
        "limitations": _limitations(inputs) + [limitation],
    })
    _raise_if_boundaries_fail(seed, policy)
    return seed


def build_h14_source_need_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return _build_review_seed("source_need", inputs, policy)


def build_h14_source_candidate_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return _build_review_seed("source_candidate", inputs, policy)


def build_h14_source_discovery_candidate_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return _build_review_seed("source_discovery_candidate", inputs, policy)


def build_h14_source_pack_manifest_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return _build_review_seed("source_pack_manifest", inputs, policy)


def build_h14_connector_pack_manifest_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return _build_review_seed("connector_pack_manifest", inputs, policy)


def build_h14_coverage_manifest_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return _build_review_seed("coverage_manifest", inputs, policy)


def build_h14_connector_scorecard_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return _build_review_seed("connector_scorecard", inputs, policy)


def build_h14_reliability_freshness_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return _build_review_seed("reliability_freshness", inputs, policy)


def build_h14_dispute_revocation_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return _build_review_seed("dispute_revocation", inputs, policy)


def build_h14_lineage_provenance_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return _build_review_seed("lineage_provenance", inputs, policy)


def build_h14_pack_import_export_boundary_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return _build_review_seed("pack_import_export_boundary", inputs, policy)


def build_h14_source_cache_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return _build_review_seed("source_cache", inputs, policy)


def build_h14_evidence_candidate_review_seed(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    return _build_review_seed("evidence_candidate", inputs, policy)


def build_h14_candidate_promotion_preview(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source_id = _source_id(inputs)
    preview = {
        "schema_version": "h14_candidate_promotion_preview.v0",
        "candidate_promotion_preview_id": f"h14.candidate_promotion.{source_id}.{_digest(inputs)[:12]}.v0",
        "source_id": source_id,
        "preview_only": True,
        "promotes_candidate": False,
        "candidate_promotion_preview_promotes_candidate": False,
        "accepted_candidate_truth": False,
        "review_required_before_promotion": True,
        "limitations": _limitations(inputs) + ["Candidate promotion preview does not promote, accept, persist, publish, import, export, access, or write H14 candidates."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
    }
    _raise_if_boundaries_fail(preview, policy)
    return preview


def build_h14_coverage_update_preview(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source_id = _source_id(inputs)
    preview = {
        "schema_version": "h14_source_coverage_update_preview.v0",
        "coverage_update_preview_id": f"h14.coverage_update.{source_id}.{_digest(inputs)[:12]}.v0",
        "source_id": source_id,
        "coverage_basis": "fixture_replay_and_rollup_dry_run_review_evidence",
        "coverage_preview_only": True,
        "coverage_manifest_is_exhaustive_global_coverage": False,
        "source_completeness_claimed": False,
        "limitations": ["Coverage update preview is not exhaustive global coverage, source completeness, rights proof, safety proof, or production quality proof."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
    }
    _raise_if_boundaries_fail(preview, policy)
    return preview


def build_h14_connector_scorecard_update(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source_id = _source_id(inputs)
    update = {
        "schema_version": "h14_connector_scorecard_update.v0",
        "connector_scorecard_update_id": f"h14.scorecard_update.{source_id}.{_digest(inputs)[:12]}.v0",
        "source_id": source_id,
        "fixture_replay_status": "integrated",
        "rollup_dry_run_status": "completed_or_blocked_under_policy",
        "review_integration_status": "preview_created",
        "production_ready": False,
        "connector_approved": False,
        "auto_approves_future_connectors": False,
        "automatic_future_connector_approval": False,
        "limitations": ["Connector scorecard update is not production readiness, access permission, import/export permission, publication permission, safety proof, rights clearance, or future connector approval."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
    }
    _raise_if_boundaries_fail(update, policy)
    return update


def build_h14_source_pack_update_preview(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    source_id = _source_id(inputs)
    preview = {
        "schema_version": "h14_source_pack_update_preview.v0",
        "source_pack_update_preview_id": f"h14.source_pack_update.{source_id}.{_digest(inputs)[:12]}.v0",
        "source_id": source_id,
        "preview_only": True,
        "source_pack_imported": False,
        "source_pack_exported": False,
        "source_pack_submitted": False,
        "source_pack_accepted": False,
        "source_pack_preview_is_imported_or_submitted": False,
        "limitations": ["Source pack update preview is not import, export, submission, acceptance, public truth, source sync, pack movement, or publication permission."],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
    }
    _raise_if_boundaries_fail(preview, policy)
    return preview


def build_h14_review_integration_result(inputs: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> dict[str, Any]:
    outputs = list(inputs.get("outputs") or [])
    input_refs = [_public_safe_input_ref(ref) for ref in list(inputs.get("input_refs") or [])]
    by_source = _best_inputs_by_source(outputs)
    sources = list(H14_SOURCE_IDS)
    source_inputs = {source_id: by_source.get(source_id, _minimal_source_input(source_id)) for source_id in sources}
    result: dict[str, Any] = {
        "schema_version": "h14_source_discovery_review_integration_result.v0",
        "review_integration_result_id": f"h14.review_integration.{_digest({'inputs': input_refs, 'sources': sources})[:12]}.v0",
        "wave_id": "H14",
        "sources": sources,
        "source_count": len(sources),
        "input_refs": input_refs,
        "used_fixture_outputs": [item for item in outputs if _is_fixture_output(item)],
        "used_rollup_dry_run_outputs": [item for item in outputs if _is_rollup_output(item)],
        "blocked_sources": _blocked_sources(outputs),
        "warnings": [],
        "limitations": [
            "H14 review integration is a wave-level Source OS audit rehearsal only.",
            "Fixture replay, rollup dry-run, and blocked outputs do not grant source discovery, live access, model/provider use, pack import/export, registry mutation, source-cache writes, evidence writes, index writes, or truth acceptance.",
        ],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["H14 outputs remain candidates, seeds, and previews only."],
        "accepts_source_need_truth": False,
        "accepts_source_candidate_truth": False,
        "accepts_source_discovery_truth": False,
        "accepts_source_approval": False,
        "accepts_connector_approval": False,
        "accepts_source_pack_truth": False,
        "accepts_connector_pack_truth": False,
        "accepts_coverage_truth": False,
        "accepts_scorecard_truth": False,
        "accepts_reliability_truth": False,
        "accepts_freshness_truth": False,
        "accepts_dispute_revocation_truth": False,
        "accepts_lineage_provenance_truth": False,
        "accepts_source_truth": False,
        "accepts_evidence_truth": False,
        "accepts_candidate_truth": False,
        "mutates_source_registry": False,
        "mutates_connector_registry": False,
        "mutates_public_index": False,
        "mutates_master_index": False,
        "enables_source_discovery_runtime": False,
        "enables_live_access": False,
        "enables_network_access": False,
        "enables_model_provider": False,
        "enables_source_sync": False,
        "enables_pack_export_import": False,
        "enables_source_cache_write": False,
        "enables_evidence_write": False,
    }
    builders = {
        "source_need_review_seeds": build_h14_source_need_review_seed,
        "source_candidate_review_seeds": build_h14_source_candidate_review_seed,
        "source_discovery_candidate_review_seeds": build_h14_source_discovery_candidate_review_seed,
        "source_pack_manifest_review_seeds": build_h14_source_pack_manifest_review_seed,
        "connector_pack_manifest_review_seeds": build_h14_connector_pack_manifest_review_seed,
        "coverage_manifest_review_seeds": build_h14_coverage_manifest_review_seed,
        "connector_scorecard_review_seeds": build_h14_connector_scorecard_review_seed,
        "reliability_freshness_review_seeds": build_h14_reliability_freshness_review_seed,
        "dispute_revocation_review_seeds": build_h14_dispute_revocation_review_seed,
        "lineage_provenance_review_seeds": build_h14_lineage_provenance_review_seed,
        "pack_import_export_boundary_review_seeds": build_h14_pack_import_export_boundary_review_seed,
        "source_cache_review_seeds": build_h14_source_cache_review_seed,
        "evidence_candidate_review_seeds": build_h14_evidence_candidate_review_seed,
        "candidate_promotion_previews": build_h14_candidate_promotion_preview,
        "coverage_update_previews": build_h14_coverage_update_preview,
        "scorecard_updates": build_h14_connector_scorecard_update,
        "source_pack_update_previews": build_h14_source_pack_update_preview,
    }
    for key, builder in builders.items():
        result[key] = [builder(source_inputs[source_id], policy) for source_id in sources]
    if result["blocked_sources"]:
        result["warnings"].append("H14 rollup dry-run outputs include blocked sources; fixture-equivalent review evidence is used without inventing rollup evidence.")
    _raise_if_boundaries_fail(result, policy)
    return result


def summarize_h14_review_integration(result: Mapping[str, Any]) -> dict[str, Any]:
    errors = detect_h14_review_truth_boundary_violations(result) + detect_h14_review_product_boundary_violations(result) + detect_h14_review_registry_or_pack_mutation_violations(result)
    return {
        "schema_version": "h14_review_integration_summary.v0",
        "status": "pass" if not errors else "invalid",
        "review_integration_result_id": result.get("review_integration_result_id"),
        "source_count": result.get("source_count", 0),
        "source_need_review_seed_count": len(result.get("source_need_review_seeds", [])),
        "source_candidate_review_seed_count": len(result.get("source_candidate_review_seeds", [])),
        "source_discovery_candidate_review_seed_count": len(result.get("source_discovery_candidate_review_seeds", [])),
        "source_pack_manifest_review_seed_count": len(result.get("source_pack_manifest_review_seeds", [])),
        "connector_pack_manifest_review_seed_count": len(result.get("connector_pack_manifest_review_seeds", [])),
        "coverage_manifest_review_seed_count": len(result.get("coverage_manifest_review_seeds", [])),
        "connector_scorecard_review_seed_count": len(result.get("connector_scorecard_review_seeds", [])),
        "reliability_freshness_review_seed_count": len(result.get("reliability_freshness_review_seeds", [])),
        "dispute_revocation_review_seed_count": len(result.get("dispute_revocation_review_seeds", [])),
        "lineage_provenance_review_seed_count": len(result.get("lineage_provenance_review_seeds", [])),
        "pack_import_export_boundary_review_seed_count": len(result.get("pack_import_export_boundary_review_seeds", [])),
        "blocked_sources": list(result.get("blocked_sources", [])),
        "errors": errors,
    }


def detect_h14_review_truth_boundary_violations(result: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    violations: list[str] = []
    _collect_true_keys(result, FORBIDDEN_TRUTH_TRUE_KEYS, "truth", violations)
    return sorted(dict.fromkeys(violations))


def detect_h14_review_product_boundary_violations(result: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    violations: list[str] = []
    _collect_true_keys(result, FORBIDDEN_PRODUCT_TRUE_KEYS, "product", violations)
    return sorted(dict.fromkeys(violations))


def detect_h14_review_registry_or_pack_mutation_violations(result: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    violations: list[str] = []
    _collect_true_keys(result, {"source_registry_mutated", "connector_registry_mutated", "source_pack_imported", "source_pack_exported", "source_pack_submitted", "source_pack_accepted", "registry_mutation_performed", "pack_export_import_performed", "source_cache_write_performed", "evidence_write_performed", "public_index_write_performed", "master_index_write_performed"}, "mutation", violations)
    return sorted(dict.fromkeys(violations))


def _seed_base(kind: str, source_id: str, source_ref: str, inputs: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "review_seed_id": f"h14.review_seed.{kind}.{source_id}.{_digest(inputs)[:12]}.v0",
        "source_id": source_id,
        "source_record_ref": source_ref,
        "input_schema_version": inputs.get("schema_version", "unknown"),
        "review_status": "preview_only_review_required",
        "accepted_source_truth": False,
        "accepted_evidence_truth": False,
        "accepted_candidate_truth": False,
        "mutates_source_registry": False,
        "mutates_connector_registry": False,
        "mutates_source_cache": False,
        "mutates_evidence_ledger": False,
        "mutates_review_queue": False,
        "mutates_public_index": False,
        "mutates_master_index": False,
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(),
        "notes": ["H14 review seed is a preview and not a review decision."],
    }


def _source_id(inputs: Mapping[str, Any]) -> str:
    source_id = str(inputs.get("source_id") or "")
    if source_id in H14_SOURCE_CONFIGS:
        return source_id
    nested = inputs.get("normalized_rollup_record") or inputs.get("normalized_record")
    if isinstance(nested, Mapping) and nested.get("source_id") in H14_SOURCE_CONFIGS:
        return str(nested.get("source_id"))
    return "unknown"


def _first_ref(inputs: Mapping[str, Any], nested_key: str) -> str:
    nested = inputs.get(nested_key)
    if isinstance(nested, Mapping):
        for key in ("candidate_id", "preview_id", "review_seed_id"):
            value = nested.get(key)
            if value:
                return str(value)
    for key in ("fixture_replay_result_id", "rollup_dry_run_result_id", "normalized_record_ref", "fixture_ref", "rollup_dry_run_request_ref"):
        if inputs.get(key):
            return str(inputs[key])
    return f"h14.{nested_key}.{_source_id(inputs)}.preview"


def _limitations(inputs: Mapping[str, Any]) -> list[str]:
    values = inputs.get("limitations")
    if isinstance(values, list):
        return [str(value) for value in values]
    return ["Input carries no additional limitations beyond H14 no-access/no-truth policy."]


def _best_inputs_by_source(outputs: Sequence[Mapping[str, Any]]) -> dict[str, Mapping[str, Any]]:
    by_source: dict[str, Mapping[str, Any]] = {}
    for item in outputs:
        source_id = _source_id(item)
        if source_id not in H14_SOURCE_CONFIGS:
            continue
        if source_id not in by_source or _score_input(item) > _score_input(by_source[source_id]):
            by_source[source_id] = item
    return by_source


def _score_input(item: Mapping[str, Any]) -> int:
    if _is_rollup_output(item) and item.get("result_status") == "rollup_dry_run_completed":
        return 4
    if _is_rollup_output(item):
        return 3
    if _is_fixture_output(item):
        return 2
    return 1


def _is_fixture_output(item: Mapping[str, Any]) -> bool:
    return item.get("schema_version") == "h14_source_discovery_fixture_replay_result.v0" or item.get("result_status") == "normalized_fixture"


def _is_rollup_output(item: Mapping[str, Any]) -> bool:
    return item.get("schema_version") == "h14_source_discovery_rollup_dry_run_result.v0"


def _blocked_sources(outputs: Sequence[Mapping[str, Any]]) -> list[str]:
    blocked = set()
    for item in outputs:
        status = str(item.get("result_status") or "")
        if status.startswith("blocked_"):
            source_id = _source_id(item)
            if source_id in H14_SOURCE_CONFIGS:
                blocked.add(source_id)
    return sorted(blocked)


def _minimal_source_input(source_id: str) -> dict[str, Any]:
    config = H14_SOURCE_CONFIGS[source_id]
    return {
        "schema_version": "h14_minimal_review_source.v0",
        "source_id": source_id,
        "connector_family": config["connector_family"],
        "limitations": ["Source represented by H14 policy, fixture, or rollup-equivalent review integration only."],
    }


def _public_safe_input_ref(value: Any) -> str:
    text = str(value).replace("\\", "/")
    marker = "examples/connectors/h14_source_discovery/"
    if marker in text:
        return marker + text.split(marker, 1)[1]
    audit_marker = "control/audits/h14-"
    if audit_marker in text:
        return audit_marker + text.split(audit_marker, 1)[1]
    return Path(text).name or "h14_input_ref_redacted"


def _truth_boundary() -> dict[str, bool]:
    return {key: False for key in FORBIDDEN_TRUTH_TRUE_KEYS}


def _product_boundary() -> dict[str, bool]:
    return {key: False for key in FORBIDDEN_PRODUCT_TRUE_KEYS}


def _raise_if_boundaries_fail(value: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> None:
    errors = detect_h14_review_truth_boundary_violations(value, policy) + detect_h14_review_product_boundary_violations(value, policy) + detect_h14_review_registry_or_pack_mutation_violations(value, policy)
    if errors:
        raise ValueError("; ".join(errors))


def _collect_true_keys(value: Any, forbidden: set[str], prefix: str, errors: list[str]) -> None:
    if isinstance(value, Mapping):
        for key, inner in value.items():
            path = f"{prefix}.{key}" if prefix else str(key)
            if key in forbidden and inner is True:
                errors.append(f"{path}=true")
            _collect_true_keys(inner, forbidden, path, errors)
    elif isinstance(value, list):
        for index, inner in enumerate(value):
            _collect_true_keys(inner, forbidden, f"{prefix}[{index}]", errors)


def _digest(value: Any) -> str:
    return hashlib.sha256(json.dumps(value, sort_keys=True, default=str).encode("utf-8")).hexdigest()
