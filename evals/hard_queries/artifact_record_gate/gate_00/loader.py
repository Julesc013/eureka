"""Loader and validation helpers for reviewed artifact record gate 00."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from evals.hard_queries import REQUIRED_HARD_QUERY_IDS


ARTIFACT_LEVELS = (
    "artifact_level_0_mention_only",
    "artifact_level_1_metadata_or_source_lead",
    "artifact_level_2_source_observed_artifact_listing",
    "artifact_level_3_artifact_identity_evidence",
    "artifact_level_4_artifact_integrity_evidence",
    "artifact_level_5_verified_acquisition_or_reproducibility_path",
)
PUBLIC_ALLOWED_CLAIMS = {
    "support_fact",
    "metadata_lead",
    "source_lead",
    "artifact_lead",
    "reviewed_artifact_record",
    "verified_artifact",
    "no_public_claim",
}
FORBIDDEN_PUBLIC_ACTIONS = {
    "review_candidate",
    "promote",
    "reject",
    "request_more_evidence",
    "rebuild_index",
    "download",
    "install",
    "launch_emulator",
    "crawl_source",
    "arbitrary_live_lookup",
}
REQUIRED_OUTPUTS = (
    "README.md",
    "artifact_evidence_levels.json",
    "artifact_record_definition.json",
    "existing_seed_record_classification.json",
    "hard_query_artifact_coverage.json",
    "public_alpha_artifact_gate.json",
    "evidence_gap_queue.yml",
    "artifact_review_backlog.yml",
    "blocked_for_user_details.yml",
    "source_reference_index.json",
    "renderer_projection_fixtures.json",
    "truth_boundary_report.md",
)


def gate_root() -> Path:
    return Path(__file__).resolve().parent


def load_artifact_evidence_levels(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or gate_root()) / "artifact_evidence_levels.json")


def load_artifact_record_definition(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or gate_root()) / "artifact_record_definition.json")


def load_existing_seed_record_classification(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or gate_root()) / "existing_seed_record_classification.json")


def load_hard_query_artifact_coverage(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or gate_root()) / "hard_query_artifact_coverage.json")


def load_public_alpha_artifact_gate(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or gate_root()) / "public_alpha_artifact_gate.json")


def load_renderer_projection_fixtures(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or gate_root()) / "renderer_projection_fixtures.json")


def load_source_reference_index(root: Path | None = None) -> dict[str, Any]:
    return _read_json((root or gate_root()) / "source_reference_index.json")


def read_gate_text(name: str, root: Path | None = None) -> str:
    return ((root or gate_root()) / name).read_text(encoding="utf-8")


def classification_records(payload: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
    return tuple(dict(item) for item in payload.get("classifications") or [] if isinstance(item, Mapping))


def coverage_records(payload: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
    return tuple(dict(item) for item in payload.get("hard_query_coverage") or [] if isinstance(item, Mapping))


def source_records(payload: Mapping[str, Any]) -> tuple[dict[str, Any], ...]:
    return tuple(dict(item) for item in payload.get("source_references") or [] if isinstance(item, Mapping))


def validate_required_outputs() -> tuple[str, ...]:
    return tuple(
        f"missing required output: {name}"
        for name in REQUIRED_OUTPUTS
        if not (gate_root() / name).exists()
    )


def validate_artifact_evidence_levels(payload: Mapping[str, Any]) -> tuple[str, ...]:
    errors: list[str] = []
    levels = payload.get("levels")
    if not isinstance(levels, list):
        return ("levels must be a list",)
    level_ids = [str(item.get("level_id")) for item in levels if isinstance(item, Mapping)]
    if tuple(level_ids) != ARTIFACT_LEVELS:
        errors.append("artifact levels must match canonical gate order")
    for index, item in enumerate(levels):
        if not isinstance(item, Mapping):
            errors.append("artifact level must be object")
            continue
        if item.get("rank") != index:
            errors.append(f"{item.get('level_id')} rank must be {index}")
        if item.get("verified_artifact_claim_allowed") is True and item.get("level_id") != ARTIFACT_LEVELS[-1]:
            errors.append(f"{item.get('level_id')} must not allow verified artifact claim")
    return tuple(errors)


def validate_existing_seed_record_classification(payload: Mapping[str, Any]) -> tuple[str, ...]:
    errors: list[str] = []
    records = classification_records(payload)
    level_rank = {level_id: index for index, level_id in enumerate(ARTIFACT_LEVELS)}
    if len(records) != 15:
        errors.append("classification must include 3 reviewed seed records and 12 review-decision-backed outcomes")
    for item in records:
        item_id = str(item.get("record_id") or "<missing>")
        level = str(item.get("artifact_evidence_level") or "")
        if level not in ARTIFACT_LEVELS:
            errors.append(f"{item_id} has unsupported artifact evidence level")
        claims = set(_strings(item.get("public_claim_allowed")))
        if not claims or not claims.issubset(PUBLIC_ALLOWED_CLAIMS):
            errors.append(f"{item_id} has unsupported public claim")
        if item.get("qualifies_as_verified_artifact") is True:
            errors.append(f"{item_id} must not qualify as verified artifact")
        if item.get("qualifies_as_reviewed_artifact_record") is True and level_rank.get(level, -1) < 3:
            errors.append(f"{item_id} cannot be reviewed artifact record below level 3")
    counts = payload.get("counts")
    if not isinstance(counts, Mapping):
        errors.append("classification counts must be present")
    else:
        expected = {
            "reviewed_seed_record_count": 3,
            "review_decision_backed_outcome_count": 12,
            "reviewed_artifact_record_count": 0,
            "verified_artifact_count": 0,
            "reviewed_support_fact_count": 3,
            "need_count": 5,
            "near_miss_count": 3,
            "blocked_for_user_details_count": 1,
        }
        for key, value in expected.items():
            if int(counts.get(key, -1)) != value:
                errors.append(f"{key} must be {value}")
    return tuple(errors)


def validate_hard_query_artifact_coverage(payload: Mapping[str, Any]) -> tuple[str, ...]:
    errors: list[str] = []
    coverage = coverage_records(payload)
    if len(coverage) != len(REQUIRED_HARD_QUERY_IDS):
        errors.append("hard query artifact coverage must cover all required hard queries")
    query_ids = {str(item.get("query_id") or "") for item in coverage}
    for required in REQUIRED_HARD_QUERY_IDS:
        if required not in query_ids:
            errors.append(f"missing hard query coverage for {required}")
    for item in coverage:
        query_id = str(item.get("query_id") or "<missing>")
        if str(item.get("highest_artifact_evidence_level") or "") not in ARTIFACT_LEVELS:
            errors.append(f"{query_id} has unsupported highest level")
        if query_id == "hq_driver_win98" and item.get("blocked_for_user_details") is not True:
            errors.append("Windows 98 driver query must remain blocked for user details")
    if payload.get("artifact_level_2_or_higher_reviewed_outcome_coverage") != "2/6":
        errors.append("level 2+ coverage must be 2/6")
    if payload.get("artifact_level_3_or_higher_reviewed_outcome_coverage") != "0/6":
        errors.append("level 3+ coverage must be 0/6")
    return tuple(errors)


def validate_public_alpha_artifact_gate(payload: Mapping[str, Any]) -> tuple[str, ...]:
    errors: list[str] = []
    if payload.get("status") != "FAIL_INSUFFICIENT_REVIEWED_ARTIFACT_RECORDS":
        errors.append("public alpha artifact gate must fail for insufficient reviewed artifact records")
    if int(payload.get("reviewed_artifact_record_count", -1)) != 0:
        errors.append("reviewed_artifact_record_count must be 0")
    if int(payload.get("verified_artifact_count", -1)) != 0:
        errors.append("verified_artifact_count must be 0")
    if payload.get("next_recommended_task") != "MANUAL-ARTIFACT-OBSERVATION-BATCH-00":
        errors.append("next task must be MANUAL-ARTIFACT-OBSERVATION-BATCH-00")
    if payload.get("source_snapshot_release_gate_after_this_task") != "green_at_prior_head_but_stale_after_this_commit":
        errors.append("gate must record full-discovery evidence as stale after this commit")
    return tuple(errors)


def validate_source_reference_index(payload: Mapping[str, Any]) -> tuple[str, ...]:
    errors: list[str] = []
    refs = source_records(payload)
    if len(refs) != 17:
        errors.append("source reference index must contain 17 references")
    for item in refs:
        source_id = str(item.get("source_ref_id") or "<missing>")
        if item.get("runtime_live_source_call_performed") is not False:
            errors.append(f"{source_id} must record no runtime live source call")
        if item.get("artifact_claim_limit") not in {"support_fact_only", "lead_only", "near_miss_only", "blocked_user_details"}:
            errors.append(f"{source_id} has unsupported artifact claim limit")
    return tuple(errors)


def validate_renderer_projection_fixtures(payload: Mapping[str, Any]) -> tuple[str, ...]:
    errors: list[str] = []
    fixtures = payload.get("fixtures")
    if not isinstance(fixtures, list):
        return ("fixtures must be a list",)
    for item in fixtures:
        if not isinstance(item, Mapping):
            errors.append("fixture must be object")
            continue
        fixture_id = str(item.get("fixture_id") or "<missing>")
        if item.get("qualifies_as_verified_artifact") is True:
            errors.append(f"{fixture_id} must not project verified artifact")
        actions = set(_strings(item.get("public_actions")))
        leaked = actions & FORBIDDEN_PUBLIC_ACTIONS
        if leaked:
            errors.append(f"{fixture_id} leaks operator actions: {sorted(leaked)}")
        if not item.get("public_label") or not item.get("required_disclaimer"):
            errors.append(f"{fixture_id} must include label and disclaimer")
    return tuple(errors)


def _read_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _strings(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if str(item)]
    if isinstance(value, tuple):
        return [str(item) for item in value if str(item)]
    if isinstance(value, str) and value:
        return [value]
    return []
