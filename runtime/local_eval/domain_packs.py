"""Read-only helpers for DOMAIN seed packs and console projections."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping, Sequence


REPO_ROOT = Path(__file__).resolve().parents[2]
FIXED_CREATED_AT = "2026-05-21T00:00:00Z"

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

PROJECTION_PROFILES: tuple[str, ...] = (
    "operator_workbench",
    "public_web",
    "native_desktop_read_only",
)

EXPECTED_LANES: tuple[str, ...] = (
    "reviewed_local_results",
    "local_candidate_results",
    "source_cache_hits",
    "ia_metadata_candidates",
    "review_queue_items",
    "known_absence",
    "near_misses",
    "blocked_actions",
    "running_workunits",
    "deferred_deepening",
    "future_extraction_work",
)

BLOCKED_ACTIONS: tuple[str, ...] = (
    "download",
    "upload",
    "extract",
    "execute",
    "install",
    "call_model_provider",
    "run_source_probe",
    "public_fanout",
    "mutate_master_index",
    "mutate_operator_instance",
    "deploy",
)

READ_ONLY_ACTIONS: tuple[str, ...] = (
    "inspect",
    "cite",
    "export_metadata",
    "request_review",
)


class DomainPackError(ValueError):
    """Raised when a DOMAIN pack cannot be used as a governed seed pack."""


def load_domain_pack(path: str | Path) -> dict[str, Any]:
    """Load one DOMAIN pack from disk."""
    resolved = _resolve_path(path)
    return json.loads(resolved.read_text(encoding="utf-8"))


def validate_domain_pack(record: Mapping[str, Any]) -> dict[str, Any]:
    """Validate one DOMAIN pack and return a concise report."""
    errors: list[str] = []
    domain_id = str(record.get("domain_id", ""))

    for field in _required_fields():
        if field not in record:
            errors.append(f"{domain_id or '<unknown>'}: missing required field {field}.")

    if record.get("schema_version") != "domain_pack.v0":
        errors.append(f"{domain_id or '<unknown>'}: schema_version must be domain_pack.v0.")
    if domain_id and domain_id not in REQUIRED_DOMAIN_IDS:
        errors.append(f"{domain_id}: not in required DOMAIN seed set.")
    if record.get("seed_pack_status") != "example_only":
        errors.append(f"{domain_id}: seed_pack_status must be example_only.")

    no_claims = _mapping(record.get("non_claims"))
    for flag in (
        "canonical_truth",
        "evidence_created",
        "reviewed_record_created",
        "runtime_source_behavior_enabled",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    ):
        if no_claims.get(flag) is not False:
            errors.append(f"{domain_id}: non_claims.{flag} must be false.")

    action_posture = _mapping(record.get("action_posture_defaults"))
    blocked_actions = set(_string_list(action_posture.get("blocked_actions")))
    missing_blocked = set(BLOCKED_ACTIONS) - blocked_actions
    if missing_blocked:
        errors.append(f"{domain_id}: blocked_actions missing {sorted(missing_blocked)}.")

    allowed_actions = set(_string_list(action_posture.get("allowed_read_only_actions")))
    if not set(READ_ONLY_ACTIONS).issubset(allowed_actions):
        errors.append(f"{domain_id}: allowed_read_only_actions must include {sorted(READ_ONLY_ACTIONS)}.")

    lanes = {str(item.get("lane_kind")) for item in _list(record.get("result_lane_expectations")) if isinstance(item, Mapping)}
    missing_lanes = set(EXPECTED_LANES) - lanes
    if missing_lanes:
        errors.append(f"{domain_id}: result_lane_expectations missing {sorted(missing_lanes)}.")

    if not _list(record.get("query_hints")):
        errors.append(f"{domain_id}: query_hints must not be empty.")
    if not _list(record.get("source_preferences")):
        errors.append(f"{domain_id}: source_preferences must not be empty.")
    if not _list(record.get("syn_case_refs")):
        errors.append(f"{domain_id}: syn_case_refs must not be empty.")
    if _mapping(record.get("search_need_seed_policy")).get("creates_runtime_search_need") is not False:
        errors.append(f"{domain_id}: search_need_seed_policy.creates_runtime_search_need must be false.")
    if _mapping(record.get("workunit_seed_policy")).get("creates_runtime_workunit") is not False:
        errors.append(f"{domain_id}: workunit_seed_policy.creates_runtime_workunit must be false.")

    return {
        "schema_version": "domain_pack_validation_report.v0",
        "domain_id": domain_id,
        "status": "valid" if not errors else "invalid",
        "errors": errors,
    }


def load_domain_seed_manifest(path: str | Path) -> dict[str, Any]:
    """Load and normalize the DOMAIN seed manifest."""
    manifest = json.loads(_resolve_path(path).read_text(encoding="utf-8"))
    return manifest


def load_domain_packs_from_manifest(manifest_path: str | Path) -> list[dict[str, Any]]:
    """Load every pack referenced by the seed manifest."""
    manifest = load_domain_seed_manifest(manifest_path)
    manifest_root = _resolve_path(manifest_path).parent
    packs: list[dict[str, Any]] = []
    for item in _list(manifest.get("domain_packs")):
        if not isinstance(item, Mapping):
            continue
        pack_path = Path(str(item.get("path", "")))
        if not pack_path.is_absolute():
            pack_path = (manifest_root / pack_path).resolve()
        packs.append(load_domain_pack(pack_path))
    return packs


def compile_domain_query_hints(domain_pack: Mapping[str, Any]) -> dict[str, Any]:
    """Compile the query-hint subset used by SYN and future search routing."""
    hints = [dict(item) for item in _list(domain_pack.get("query_hints")) if isinstance(item, Mapping)]
    promote_terms = sorted({term for hint in hints for term in _string_list(hint.get("promote_terms"))})
    suppress_terms = sorted({term for hint in hints for term in _string_list(hint.get("suppress_terms"))})
    source_families = sorted(
        {
            family
            for hint in hints
            for family in _string_list(hint.get("source_family_preferences"))
        }
    )
    return {
        "schema_version": "domain_compiled_query_hints.v0",
        "domain_id": str(domain_pack.get("domain_id", "")),
        "query_classes": _string_list(domain_pack.get("query_classes")),
        "promote_terms": promote_terms,
        "suppress_terms": suppress_terms,
        "source_family_preferences": source_families,
        "review_required": True,
        "creates_runtime_behavior": False,
    }


def map_domain_to_syn_cases(domain_pack: Mapping[str, Any], syn_dataset: Mapping[str, Any] | Sequence[Mapping[str, Any]] | None = None) -> dict[str, Any]:
    """Map DOMAIN query classes to deterministic SYN case references."""
    del syn_dataset
    refs = [dict(item) for item in _list(domain_pack.get("syn_case_refs")) if isinstance(item, Mapping)]
    return {
        "schema_version": "domain_syn_case_mapping.v0",
        "domain_id": str(domain_pack.get("domain_id", "")),
        "syn_case_refs": refs,
        "syn_case_count": len(refs),
        "creates_runtime_query_logs": False,
        "creates_evidence": False,
    }


def build_domain_console_view(domain_pack: Mapping[str, Any], projection_profile: str = "operator_workbench") -> dict[str, Any]:
    """Build a read-only Workbench DOMAIN console view model."""
    if projection_profile not in PROJECTION_PROFILES:
        raise DomainPackError(f"unsupported projection profile: {projection_profile}")

    hints = compile_domain_query_hints(domain_pack)
    source_preferences = [dict(item) for item in _list(domain_pack.get("source_preferences")) if isinstance(item, Mapping)]
    result_expectations = [dict(item) for item in _list(domain_pack.get("result_lane_expectations")) if isinstance(item, Mapping)]
    action_posture = dict(_mapping(domain_pack.get("action_posture_defaults")))
    syn_mapping = map_domain_to_syn_cases(domain_pack)

    operator_detail_visible = projection_profile == "operator_workbench"
    pack_summary: dict[str, Any] = {
        "domain_id": str(domain_pack.get("domain_id", "")),
        "display_name": str(domain_pack.get("display_name", "")),
        "domain_version": str(domain_pack.get("domain_version", "")),
        "object_families": _string_list(domain_pack.get("object_families")),
        "query_classes": _string_list(domain_pack.get("query_classes")),
        "seed_pack_status": str(domain_pack.get("seed_pack_status", "")),
    }
    if operator_detail_visible:
        pack_summary["identity_rules"] = [dict(item) for item in _list(domain_pack.get("identity_rules")) if isinstance(item, Mapping)]
        pack_summary["suppression_rules"] = [dict(item) for item in _list(domain_pack.get("suppression_rules")) if isinstance(item, Mapping)]
        pack_summary["promote_rules"] = [dict(item) for item in _list(domain_pack.get("promote_rules")) if isinstance(item, Mapping)]

    return {
        "schema_version": "domain_console_view.v0",
        "view_id": f"domain:{domain_pack.get('domain_id', '')}:{projection_profile}",
        "route": f"/domain/{domain_pack.get('domain_id', '')}",
        "projection_profile": projection_profile,
        "read_only": True,
        "operator_detail_visible": operator_detail_visible,
        "domain_id": str(domain_pack.get("domain_id", "")),
        "display_name": str(domain_pack.get("display_name", "")),
        "views": {
            "DomainListView": {
                "selected_domain_id": str(domain_pack.get("domain_id", "")),
                "available_domain_ids": list(REQUIRED_DOMAIN_IDS),
            },
            "DomainPackView": pack_summary,
            "DomainQueryHintView": hints,
            "DomainSourcePreferenceView": {
                "source_preferences": source_preferences,
                "live_source_calls_enabled": False,
            },
            "DomainResultExpectationView": {
                "result_lane_expectations": result_expectations,
                "truth_level": "hint_only_requires_review",
            },
            "DomainActionPostureView": {
                "action_posture_defaults": action_posture,
                "operator_gated": True,
            },
            "DomainSynCoverageView": syn_mapping,
        },
        "blocked_actions": list(BLOCKED_ACTIONS),
        "non_claims": dict(_mapping(domain_pack.get("non_claims"))),
        "created_at": FIXED_CREATED_AT,
    }


def _required_fields() -> tuple[str, ...]:
    return (
        "domain_id",
        "display_name",
        "domain_version",
        "object_families",
        "query_classes",
        "identity_rules",
        "query_hints",
        "source_preferences",
        "result_lane_expectations",
        "suppression_rules",
        "promote_rules",
        "action_posture_defaults",
        "risk_posture_defaults",
        "rights_posture_defaults",
        "safety_posture_defaults",
        "syn_case_refs",
        "search_need_seed_policy",
        "workunit_seed_policy",
        "non_claims",
        "created_at",
    )


def _resolve_path(path: str | Path) -> Path:
    resolved = Path(path)
    if not resolved.is_absolute():
        resolved = REPO_ROOT / resolved
    return resolved.resolve()


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _list(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value]
