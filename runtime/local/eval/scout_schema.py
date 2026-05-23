"""Read-only helpers for SCOUT schema examples and console projections."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping, Sequence


REPO_ROOT = Path(__file__).resolve().parents[3]
FIXED_CREATED_AT = "2026-05-21T00:00:00Z"

PROJECTION_PROFILES: tuple[str, ...] = (
    "operator_workbench",
    "public_web",
    "native_desktop_read_only",
)

REQUIRED_DOMAIN_IDS: tuple[str, ...] = (
    "legacy_software",
    "driver_support_media",
    "frontier_resolution_media",
    "manuals_docs_scans",
    "package_source_release",
    "web_archive_trace",
    "games_emulation",
    "hardware_firmware_support",
)

REQUIRED_RELATION_TYPES: tuple[str, ...] = (
    "same_collection",
    "same_uploader",
    "same_creator",
    "same_format_family",
    "same_platform",
    "same_filename_pattern",
    "same_checksum_cluster",
    "same_vendor",
    "same_driver_family",
    "same_media_format",
    "same_archive_collection",
    "same_member_path_pattern",
    "mentions",
    "contains",
    "mirrors",
    "cites",
    "successor_of",
    "predecessor_of",
    "nearby_version",
    "related_tag",
    "related_forum_thread",
    "archived_url_trace",
    "source_catalogue_neighbor",
    "collection_neighbor",
    "package_family_neighbor",
)

REQUIRED_FEEDBACK_EVENT_TYPES: tuple[str, ...] = (
    "useful_lead",
    "accepted_as_evidence",
    "false_positive",
    "duplicate",
    "unsafe",
    "rights_risk",
    "needs_more_work",
    "wrong_domain",
    "source_relevant",
    "source_not_relevant",
    "relation_helpful",
    "relation_misleading",
)

REQUIRED_WORKUNIT_SEED_TYPES: tuple[str, ...] = (
    "inspect_related_collection",
    "search_same_filename_pattern",
    "trace_archived_vendor_url",
    "compare_same_format_examples",
    "verify_candidate_identity",
    "inspect_file_manifest",
    "queue_future_extraction",
    "review_provenance_claim",
)

BLOCKED_ACTIONS: tuple[str, ...] = (
    "live_source_call",
    "source_probe",
    "crawl",
    "download",
    "upload",
    "extract",
    "call_model_provider",
    "public_fanout",
    "mutate_operator_instance",
    "mutate_master_index",
    "write_source_cache",
    "write_evidence",
    "write_candidate_index",
    "write_review_queue",
    "create_reviewed_record",
    "deploy",
)


class ScoutSchemaError(ValueError):
    """Raised when a SCOUT schema example cannot be used."""


def load_scout_seed_manifest(path: str | Path) -> dict[str, Any]:
    """Load the SCOUT seed manifest from disk."""
    return _load_json(_resolve_path(path))


def load_scout_seed_records(manifest_path: str | Path) -> list[dict[str, Any]]:
    """Load every SCOUT seed referenced by the manifest."""
    manifest = load_scout_seed_manifest(manifest_path)
    manifest_root = _resolve_path(manifest_path).parent
    records: list[dict[str, Any]] = []
    for item in _list(manifest.get("seeds")):
        if not isinstance(item, Mapping):
            continue
        record_path = Path(str(item.get("path", "")))
        if not record_path.is_absolute():
            record_path = (manifest_root / record_path).resolve()
        records.append(_load_json(record_path))
    return records


def load_scout_example_records(root: str | Path = REPO_ROOT) -> dict[str, Any]:
    """Load the deterministic SCOUT example packet set."""
    base = _resolve_path(root) / "examples/scout"
    return {
        "manifest": _load_json(base / "scout_seed_manifest.json"),
        "seeds": load_scout_seed_records(base / "scout_seed_manifest.json"),
        "candidate": _load_json(base / "sample_discovery_candidate.json"),
        "trail": _load_json(base / "sample_discovery_trail.json"),
        "related_path": _load_json(base / "sample_related_path.json"),
        "source_trust_record": _load_json(base / "sample_source_trust_record.json"),
        "source_trust_observation": _load_json(base / "sample_source_trust_observation.json"),
        "hunt_feedback_event": _load_json(base / "sample_hunt_feedback_event.json"),
        "workunit_seed_suggestion": _load_json(base / "sample_workunit_seed_suggestion.json"),
    }


def validate_scout_seed(record: Mapping[str, Any]) -> dict[str, Any]:
    """Validate one SCOUT seed example."""
    errors = _validate_common(record, "scout_seed.v0", "scout_seed")
    seed_id = str(record.get("seed_id", ""))
    if not seed_id:
        errors.append("scout_seed: seed_id is required.")
    if not str(record.get("query_text", "")):
        errors.append(f"{seed_id or '<unknown>'}: query_text is required.")
    if record.get("domain_id") not in REQUIRED_DOMAIN_IDS:
        errors.append(f"{seed_id or '<unknown>'}: domain_id must be a required DOMAIN id.")
    if _mapping(record.get("search_need_seed_policy")).get("creates_runtime_search_need") is not False:
        errors.append(f"{seed_id or '<unknown>'}: seed policy must not create runtime SearchNeed records.")
    if _mapping(record.get("workunit_seed_policy")).get("creates_runtime_workunit") is not False:
        errors.append(f"{seed_id or '<unknown>'}: seed policy must not create runtime WorkUnits.")
    return _report("scout_seed_validation_report.v0", seed_id, errors)


def validate_discovery_candidate(record: Mapping[str, Any]) -> dict[str, Any]:
    """Validate one SCOUT DiscoveryCandidate example."""
    errors = _validate_common(record, "discovery_candidate.v0", "discovery_candidate")
    candidate_id = str(record.get("candidate_id", ""))
    for field in (
        "candidate_id",
        "seed_id",
        "candidate_kind",
        "domain_id",
        "source_family",
        "locator",
        "relation_path",
        "evidence_refs",
        "confidence",
        "review_state",
    ):
        if field not in record:
            errors.append(f"{candidate_id or '<unknown>'}: missing required field {field}.")
    if record.get("review_state") not in {"candidate", "needs_review", "rejected"}:
        errors.append(f"{candidate_id or '<unknown>'}: review_state must remain candidate-like.")
    if _list(record.get("evidence_refs")):
        errors.append(f"{candidate_id or '<unknown>'}: evidence_refs must stay empty until review creates evidence.")
    return _report("discovery_candidate_validation_report.v0", candidate_id, errors)


def validate_discovery_trail(record: Mapping[str, Any]) -> dict[str, Any]:
    """Validate one SCOUT DiscoveryTrail example."""
    errors = _validate_common(record, "discovery_trail.v0", "discovery_trail")
    trail_id = str(record.get("trail_id", ""))
    for field in (
        "trail_id",
        "seed_id",
        "domain_id",
        "steps",
        "candidate_ids",
        "workunit_seed_ids",
        "source_trust_observation_ids",
        "explanation",
        "confidence",
    ):
        if field not in record:
            errors.append(f"{trail_id or '<unknown>'}: missing required field {field}.")
    for step in _list(record.get("steps")):
        if isinstance(step, Mapping) and step.get("relation_type") not in REQUIRED_RELATION_TYPES:
            errors.append(f"{trail_id or '<unknown>'}: unknown relation_type {step.get('relation_type')!r}.")
    return _report("discovery_trail_validation_report.v0", trail_id, errors)


def validate_source_trust_record(record: Mapping[str, Any]) -> dict[str, Any]:
    """Validate one SCOUT SourceTrustRecord example."""
    errors = _validate_common(record, "source_trust_record.v0", "source_trust_record")
    source_id = str(record.get("source_id", ""))
    for field in (
        "source_id",
        "source_family",
        "domain_scores",
        "known_strengths",
        "known_failure_modes",
        "accepted_evidence_count",
        "false_positive_count",
        "metadata_quality",
        "provenance_quality",
        "rights_risk",
        "safety_risk",
        "last_verified_at",
    ):
        if field not in record:
            errors.append(f"{source_id or '<unknown>'}: missing required field {field}.")
    if record.get("accepted_evidence_count") != 0:
        errors.append(f"{source_id or '<unknown>'}: example trust record must not claim accepted evidence.")
    if record.get("last_verified_at") is not None:
        errors.append(f"{source_id or '<unknown>'}: example trust record must not claim live verification.")
    return _report("source_trust_record_validation_report.v0", source_id, errors)


def build_scout_console_view(records: Mapping[str, Any], projection_profile: str = "operator_workbench") -> dict[str, Any]:
    """Build a read-only Workbench SCOUT console view model."""
    if projection_profile not in PROJECTION_PROFILES:
        raise ScoutSchemaError(f"unsupported projection profile: {projection_profile}")

    seeds = [dict(seed) for seed in _list(records.get("seeds")) if isinstance(seed, Mapping)]
    candidate = dict(_mapping(records.get("candidate")))
    trail = dict(_mapping(records.get("trail")))
    source_trust = dict(_mapping(records.get("source_trust_record")))
    feedback = dict(_mapping(records.get("hunt_feedback_event")))
    workunit_seed = dict(_mapping(records.get("workunit_seed_suggestion")))
    operator_detail_visible = projection_profile == "operator_workbench"

    if not operator_detail_visible:
        candidate.pop("locator", None)
        source_trust.pop("known_failure_modes", None)
        feedback.pop("operator_notes", None)

    return {
        "schema_version": "scout_console_view.v0",
        "view_id": f"scout:{projection_profile}",
        "routes": [
            "/scout",
            "/scout/trails",
            "/scout/sources",
            "/scout/candidates",
            "/scout/trust",
            "/scout/feedback",
        ],
        "projection_profile": projection_profile,
        "read_only": True,
        "operator_detail_visible": operator_detail_visible,
        "views": {
            "ScoutOverviewView": {
                "seed_count": len(seeds),
                "candidate_count": 1 if candidate else 0,
                "trail_count": 1 if trail else 0,
                "source_trust_record_count": 1 if source_trust else 0,
                "candidate_only": True,
            },
            "DiscoveryTrailView": trail,
            "RelatedPathView": dict(_mapping(records.get("related_path"))),
            "DiscoveryCandidateView": candidate,
            "SourceTrustView": source_trust,
            "SourceTrustObservationView": dict(_mapping(records.get("source_trust_observation"))),
            "HuntFeedbackEventView": feedback,
            "WorkUnitSeedSuggestionView": workunit_seed,
        },
        "blocked_actions": list(BLOCKED_ACTIONS),
        "non_claims": {
            "accepted_truth_created": False,
            "evidence_created": False,
            "reviewed_record_created": False,
            "indexes_mutated": False,
            "live_source_calls_enabled": False,
            "crawling_enabled": False,
        },
        "created_at": FIXED_CREATED_AT,
    }


def map_scout_seed_to_domain(seed: Mapping[str, Any], domain_pack: Mapping[str, Any]) -> dict[str, Any]:
    """Map a SCOUT seed to a DOMAIN pack without mutating runtime state."""
    return {
        "schema_version": "scout_domain_handoff.v0",
        "seed_id": str(seed.get("seed_id", "")),
        "domain_id": str(seed.get("domain_id", "")),
        "domain_pack_id": str(domain_pack.get("domain_id", "")),
        "query_classes": _string_list(domain_pack.get("query_classes")),
        "likely_relation_types": _string_list(seed.get("initial_relation_hints")),
        "creates_evidence": False,
        "creates_runtime_workunit": False,
        "review_required": True,
    }


def map_scout_seed_to_syn_case(seed: Mapping[str, Any], syn_dataset: Mapping[str, Any] | Sequence[Mapping[str, Any]] | None = None) -> dict[str, Any]:
    """Map a SCOUT seed to a SYN query class without creating evidence."""
    del syn_dataset
    return {
        "schema_version": "scout_syn_handoff.v0",
        "seed_id": str(seed.get("seed_id", "")),
        "domain_id": str(seed.get("domain_id", "")),
        "query_text": str(seed.get("query_text", "")),
        "syn_query_class": str(seed.get("syn_query_class", "scout_relation_pressure")),
        "creates_evidence": False,
        "creates_runtime_query": False,
        "review_required": True,
    }


def _validate_common(record: Mapping[str, Any], schema_version: str, record_type: str) -> list[str]:
    errors: list[str] = []
    label = str(record.get("seed_id") or record.get("candidate_id") or record.get("trail_id") or record.get("source_id") or record_type)
    required = (
        "schema_version",
        "record_type",
        "created_at",
        "source_context",
        "domain_id",
        "review_required",
        "accepted_truth",
        "limitations",
        "risk_flags",
        "rights_flags",
        "non_claims",
    )
    for field in required:
        if field not in record:
            errors.append(f"{label}: missing shared field {field}.")
    if record.get("schema_version") != schema_version:
        errors.append(f"{label}: schema_version must be {schema_version}.")
    if record.get("record_type") != record_type:
        errors.append(f"{label}: record_type must be {record_type}.")
    if record.get("review_required") is not True:
        errors.append(f"{label}: review_required must be true.")
    if record.get("accepted_truth") is not False:
        errors.append(f"{label}: accepted_truth must be false.")
    non_claims = _mapping(record.get("non_claims"))
    for flag in (
        "evidence_created",
        "reviewed_record_created",
        "index_mutated",
        "live_source_call_performed",
        "crawling_performed",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    ):
        if non_claims.get(flag) is not False:
            errors.append(f"{label}: non_claims.{flag} must be false.")
    return errors


def _report(schema_version: str, record_id: str, errors: list[str]) -> dict[str, Any]:
    return {
        "schema_version": schema_version,
        "record_id": record_id,
        "status": "valid" if not errors else "invalid",
        "errors": errors,
    }


def _resolve_path(path: str | Path) -> Path:
    resolved = Path(path)
    if not resolved.is_absolute():
        resolved = REPO_ROOT / resolved
    return resolved.resolve()


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value]
