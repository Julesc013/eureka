"""IA candidate review queue helpers.

The IA review path writes local review queue records only. It preserves the
candidate/evidence/source-cache provenance while keeping durable review queue
payloads free of reserved public-truth vocabulary.
"""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence

from runtime.candidate_index import CandidateIndexStore
from runtime.review_queue import ReviewDecision, ReviewDecisionKind, ReviewItemRecord, ReviewQueueStatus
from runtime.source_observation.ids import stable_digest
from runtime.source_observation.internet_archive_candidate_index import (
    build_ia_candidates_from_evidence,
    load_default_ia_evidence_candidates,
    load_ia_candidate_policy,
)
from runtime.source_observation.internet_archive_metadata import SOURCE_ID


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_REVIEW_POLICY_PATH = REPO_ROOT / "control" / "policies" / "ia_review_policy.json"
DEFAULT_CREATED_AT = "2026-05-18T00:00:00Z"
ALLOWED_DECISIONS = {
    "approve_for_reviewed_index_dry_run",
    "reject_candidate",
    "needs_more_evidence",
    "mark_near_miss",
    "mark_duplicate",
    "mark_policy_blocked",
    "mark_rights_risk",
    "mark_safety_risk",
}


def load_ia_review_policy(path: str | Path = DEFAULT_REVIEW_POLICY_PATH) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def load_default_ia_candidate_records() -> list[dict[str, Any]]:
    return build_ia_candidates_from_evidence(load_default_ia_evidence_candidates(), load_ia_candidate_policy())


def load_ia_candidate_record_file(path: str | Path) -> list[dict[str, Any]]:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    if isinstance(payload, list):
        return [dict(item) for item in payload if isinstance(item, Mapping)]
    if not isinstance(payload, Mapping):
        return []
    for key in ("candidates", "candidate_records", "ia_candidates", "review_candidates"):
        value = payload.get(key)
        if isinstance(value, list):
            return [dict(item) for item in value if isinstance(item, Mapping)]
    report = payload.get("write_report")
    if isinstance(report, Mapping):
        for key in ("candidates", "candidate_records", "ia_candidates"):
            value = report.get(key)
            if isinstance(value, list):
                return [dict(item) for item in value if isinstance(item, Mapping)]
    if payload.get("schema_version") == "ia_candidate_record.v0":
        return [dict(payload)]
    return []


def load_ia_candidates_from_index(path: str | Path) -> list[dict[str, Any]]:
    index_path = Path(path)
    if not index_path.exists():
        return []
    payload = CandidateIndexStore.open(index_path).load()
    value = payload.get("candidates", [])
    if isinstance(value, list):
        return [dict(item) for item in value if isinstance(item, Mapping)]
    return []


def build_ia_review_items_from_candidates(candidates: Sequence[Mapping[str, Any]], policy: Mapping[str, Any]) -> list[dict[str, Any]]:
    _ensure_policy(policy)
    items: list[dict[str, Any]] = []
    for candidate in candidates:
        record = _review_item(dict(candidate))
        errors = validate_ia_review_item(record, policy)
        if errors:
            raise ValueError("; ".join(errors))
        items.append(record)
    return items


def validate_ia_review_item(item: Mapping[str, Any], policy: Mapping[str, Any]) -> tuple[str, ...]:
    errors: list[str] = []
    if item.get("schema_version") != "ia_review_item.v0":
        errors.append("review item schema mismatch")
    if item.get("source_id") != SOURCE_ID:
        errors.append("source_id must be internet_archive_metadata")
    for key in (
        "review_item_id",
        "candidate_id",
        "candidate_kind",
        "evidence_ids",
        "source_cache_record_ids",
        "observation_ids",
        "title",
        "summary",
        "source_locator",
        "provenance",
        "uncertainty",
        "limitations",
        "risk_flags",
        "rights_flags",
        "suggested_decision",
        "created_at",
    ):
        if key not in item or item.get(key) in ("", None, []):
            errors.append(f"{key} is required")
    if item.get("suggested_decision") not in ALLOWED_DECISIONS:
        errors.append("suggested decision is not allowed for IA-06")
    if item.get("review_required") is not True:
        errors.append("review_required must be true")
    for key in (
        "accepted_truth",
        "reviewed_index_mutation_performed",
        "master_index_mutation_performed",
        "raw_response_committed",
        "download_performed",
        "upload_performed",
        "extraction_executed",
        "model_provider_used",
        "deployment_performed",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    ):
        if item.get(key) is not False:
            errors.append(f"{key} must be false")
    if policy.get("review_queue_writes_enabled_for_IA_06") is not True:
        errors.append("IA-06 review queue writes must be explicitly enabled by policy")
    if policy.get("accepted_truth_enabled") is not False:
        errors.append("accepted truth must be disabled")
    if policy.get("reviewed_index_mutation_enabled") is not False:
        errors.append("reviewed index mutation must be disabled")
    if policy.get("master_index_mutation_enabled") is not False:
        errors.append("master index mutation must be disabled")
    return tuple(errors)


def apply_ia_review_decision(
    item: Mapping[str, Any],
    decision: str | Mapping[str, Any],
    policy: Mapping[str, Any],
) -> dict[str, Any]:
    _ensure_policy(policy)
    review_item = dict(item)
    decision_name = str(decision.get("decision", "")) if isinstance(decision, Mapping) else str(decision)
    rationale = (
        str(decision.get("rationale", "")) if isinstance(decision, Mapping) else _default_rationale(decision_name, review_item)
    )
    if not rationale:
        raise ValueError("review decision rationale is required")
    record = {
        "schema_version": "ia_review_decision.v0",
        "review_decision_id": "iard_" + stable_digest({"review_item_id": review_item.get("review_item_id"), "decision": decision_name}),
        "review_item_id": str(review_item.get("review_item_id", "")),
        "candidate_id": str(review_item.get("candidate_id", "")),
        "decision": decision_name,
        "rationale": rationale,
        "reviewer_kind": "local_operator_fixture",
        "creates_promotion_preview": decision_name == "approve_for_reviewed_index_dry_run",
        "accepted_truth": False,
        "reviewed_index_mutation_performed": False,
        "master_index_mutation_performed": False,
        "raw_response_committed": False,
        "download_performed": False,
        "created_at": str(review_item.get("created_at", DEFAULT_CREATED_AT) or DEFAULT_CREATED_AT),
        "candidate_snapshot": _candidate_snapshot(review_item),
    }
    errors = validate_ia_review_decision(record, policy)
    if errors:
        raise ValueError("; ".join(errors))
    return record


def validate_ia_review_decision(decision: Mapping[str, Any], policy: Mapping[str, Any]) -> tuple[str, ...]:
    errors: list[str] = []
    if decision.get("schema_version") != "ia_review_decision.v0":
        errors.append("review decision schema mismatch")
    if decision.get("decision") not in ALLOWED_DECISIONS:
        errors.append("decision is not allowed for IA-06")
    for key in (
        "review_decision_id",
        "review_item_id",
        "candidate_id",
        "decision",
        "rationale",
        "reviewer_kind",
        "created_at",
    ):
        if key not in decision or decision.get(key) in ("", None):
            errors.append(f"{key} is required")
    if decision.get("decision") == "approve_for_reviewed_index_dry_run" and decision.get("creates_promotion_preview") is not True:
        errors.append("approve decision must create a promotion preview")
    if decision.get("decision") != "approve_for_reviewed_index_dry_run" and decision.get("creates_promotion_preview") is not False:
        errors.append("non-approve decisions must not create promotion previews")
    for key in (
        "accepted_truth",
        "reviewed_index_mutation_performed",
        "master_index_mutation_performed",
        "raw_response_committed",
        "download_performed",
    ):
        if decision.get(key) is not False:
            errors.append(f"{key} must be false")
    if policy.get("accepted_truth_enabled") is not False:
        errors.append("accepted truth must be disabled")
    if policy.get("reviewed_index_mutation_enabled") is not False:
        errors.append("reviewed index mutation must be disabled")
    if policy.get("master_index_mutation_enabled") is not False:
        errors.append("master index mutation must be disabled")
    return tuple(errors)


def to_review_item_record(item: Mapping[str, Any]) -> ReviewItemRecord:
    evidence_ids = [str(value) for value in item.get("evidence_ids", []) or [] if str(value)]
    source_cache_ids = [str(value) for value in item.get("source_cache_record_ids", []) or [] if str(value)]
    record = ReviewItemRecord(
        review_item_id=str(item["review_item_id"]),
        subject_kind="ia_candidate",
        subject_id=str(item["candidate_id"]),
        queue_status=ReviewQueueStatus.NEEDS_REVIEW,
        priority=_priority(item),
        evidence_id=evidence_ids[0] if evidence_ids else None,
        source_cache_entry_id=source_cache_ids[0] if source_cache_ids else None,
        summary=str(item.get("summary", "")),
        payload=_review_queue_item_payload(item),
        limitations=tuple(str(value) for value in item.get("limitations", []) or []),
        warnings=tuple(str(value) for value in item.get("risk_flags", []) or []),
        created_at=str(item.get("created_at", DEFAULT_CREATED_AT)),
        updated_at=str(item.get("created_at", DEFAULT_CREATED_AT)),
    )
    return record


def to_review_decision_record(decision: Mapping[str, Any]) -> ReviewDecision:
    decision_name = str(decision.get("decision", ""))
    decision_kind, status = _decision_kind_and_status(decision_name)
    return ReviewDecision(
        review_item_id=str(decision["review_item_id"]),
        decision_kind=decision_kind,
        decision_actor=str(decision.get("reviewer_kind", "local_operator_fixture")),
        reason=str(decision.get("rationale", "")),
        decision_status=status,
        decision_id=str(decision["review_decision_id"]),
        payload=_review_queue_decision_payload(decision),
        limitations=tuple(str(value) for value in (decision.get("candidate_snapshot", {}) or {}).get("limitations", []) or []),
        warnings=tuple(str(value) for value in (decision.get("candidate_snapshot", {}) or {}).get("risk_flags", []) or []),
        created_at=str(decision.get("created_at", DEFAULT_CREATED_AT)),
    )


def write_ia_review_items(store: Any, items: Sequence[Mapping[str, Any]], dry_run: bool = True) -> dict[str, Any]:
    item_list = [dict(item) for item in items]
    policy = _minimal_policy()
    errors = [error for item in item_list for error in validate_ia_review_item(item, policy)]
    if errors:
        raise ValueError("; ".join(errors))
    result: dict[str, Any] = {
        "schema_version": "ia_review_queue_store_write_result.v0",
        "dry_run": dry_run,
        "review_item_count": len(item_list),
        "write_applied": False,
        "writes": [],
        "summary": {},
        "integrity": {},
    }
    if dry_run:
        return result
    if store is None:
        raise ValueError("review queue store is required for apply")
    store.init()
    writes: list[dict[str, Any]] = []
    for item in item_list:
        record = to_review_item_record(item)
        writes.append(store.enqueue_review_item(record))
        for evidence_id in item.get("evidence_ids", []) or []:
            writes.append(store.link_evidence(record.review_item_id, str(evidence_id)))
        for source_cache_id in item.get("source_cache_record_ids", []) or []:
            writes.append(store.link_source_cache_entry(record.review_item_id, str(source_cache_id)))
    result.update(
        {
            "write_applied": bool(item_list),
            "writes": writes,
            "summary": store.summarize().to_dict(),
            "integrity": store.check_integrity(),
        }
    )
    return result


def write_ia_review_decisions(store: Any, decisions: Sequence[Mapping[str, Any]], dry_run: bool = True) -> dict[str, Any]:
    decision_list = [dict(decision) for decision in decisions]
    policy = _minimal_policy()
    errors = [error for decision in decision_list for error in validate_ia_review_decision(decision, policy)]
    if errors:
        raise ValueError("; ".join(errors))
    result: dict[str, Any] = {
        "schema_version": "ia_review_decision_store_write_result.v0",
        "dry_run": dry_run,
        "decision_count": len(decision_list),
        "write_applied": False,
        "writes": [],
        "summary": {},
        "integrity": {},
    }
    if dry_run:
        return result
    if store is None:
        raise ValueError("review queue store is required for decision apply")
    store.init()
    writes = []
    for decision in decision_list:
        record = to_review_decision_record(decision)
        writes.append(store.record_decision(record.review_item_id, record))
    result.update(
        {
            "write_applied": bool(decision_list),
            "writes": writes,
            "summary": store.summarize().to_dict(),
            "integrity": store.check_integrity(),
        }
    )
    return result


def build_ia_review_queue_report(
    items: Sequence[Mapping[str, Any]],
    decisions: Sequence[Mapping[str, Any]],
    dry_run: bool,
    store_result: Mapping[str, Any],
    write_scope: str,
) -> dict[str, Any]:
    item_list = [dict(item) for item in items]
    decision_list = [dict(decision) for decision in decisions]
    source_kinds = [str((item.get("provenance", {}) or {}).get("source_kind", "")) for item in item_list]
    decision_counts = Counter(str(decision.get("decision", "")) for decision in decision_list)
    item_write = dict(store_result.get("item_write", store_result))
    decision_write = dict(store_result.get("decision_write", {}))
    write_applied = bool(item_write.get("write_applied", False))
    decision_applied = bool(decision_write.get("write_applied", False))
    return {
        "schema_version": "ia_review_queue_report.v0",
        "task": "IA-06",
        "status": "pass",
        "dry_run": dry_run,
        "write_scope": write_scope,
        "review_item_count": len(item_list),
        "review_decision_count": len(decision_list),
        "fixture_review_item_count": source_kinds.count("ia_fixture_replay"),
        "live_preview_review_item_count": source_kinds.count("ia_live_probe_preview"),
        "review_decision_counts": dict(sorted(decision_counts.items())),
        "review_item_ids": [str(item.get("review_item_id", "")) for item in item_list],
        "review_decision_ids": [str(item.get("review_decision_id", "")) for item in decision_list],
        "review_items": item_list,
        "review_decisions": decision_list,
        "store_result": {"item_write": item_write, "decision_write": decision_write},
        "review_queue_mutated": write_applied or decision_applied,
        "fixture_review_items_written_to_temp": bool(write_applied and "ia_fixture_replay" in source_kinds),
        "live_preview_review_items_written_to_temp": bool(write_applied and "ia_live_probe_preview" in source_kinds),
        "promotion_previews_possible": sum(1 for decision in decision_list if decision.get("creates_promotion_preview") is True),
        "all_review_items_require_review": all(item.get("review_required") is True for item in item_list),
        "accepted_truth_created": any(item.get("accepted_truth") is True for item in item_list)
        or any(decision.get("accepted_truth") is True for decision in decision_list),
        "operator_instance_mutated": False,
        "instance_state_committed": False,
        "raw_response_committed": False,
        "reviewed_index_mutated": False,
        "master_index_mutated": False,
        "download_performed": False,
        "upload_performed": False,
        "extraction_executed": False,
        "model_provider_used": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def build_ia_review_boundary_report(report: Mapping[str, Any]) -> dict[str, Any]:
    passed = (
        bool(report.get("all_review_items_require_review", True))
        and not bool(report.get("accepted_truth_created", False))
        and not bool(report.get("reviewed_index_mutated", False))
        and not bool(report.get("master_index_mutated", False))
    )
    return {
        "schema_version": "ia_review_promotion_boundary_report.v0",
        "task": "IA-06",
        "passed": passed,
        "violations": [] if passed else ["review_promotion_boundary_failed"],
        "dry_run": bool(report.get("dry_run", True)),
        "write_scope": str(report.get("write_scope", "")),
        "operator_instance_mutated": False,
        "instance_state_committed": False,
        "raw_response_committed": False,
        "review_queue_mutated": bool(report.get("review_queue_mutated", False)),
        "review_queue_write_scope": str(report.get("write_scope", "")),
        "accepted_truth_created": bool(report.get("accepted_truth_created", False)),
        "reviewed_index_mutated": False,
        "master_index_mutated": False,
        "download_performed": False,
        "upload_performed": False,
        "extraction_executed": False,
        "model_provider_used": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def _review_item(candidate: Mapping[str, Any]) -> dict[str, Any]:
    candidate_id = str(candidate.get("candidate_id", ""))
    review_item_id = "iarv_" + stable_digest({"candidate_id": candidate_id, "evidence_ids": candidate.get("evidence_ids", [])})
    return {
        "schema_version": "ia_review_item.v0",
        "review_item_id": review_item_id,
        "source_id": SOURCE_ID,
        "candidate_id": candidate_id,
        "candidate_kind": str(candidate.get("candidate_kind", "")),
        "evidence_ids": list(candidate.get("evidence_ids", []) or []),
        "source_cache_record_ids": list(candidate.get("source_cache_record_ids", []) or []),
        "observation_ids": list(candidate.get("observation_ids", []) or []),
        "title": str(candidate.get("candidate_title", "")),
        "summary": str(candidate.get("candidate_summary", "")),
        "source_locator": dict(candidate.get("source_locator", {}) or {}),
        "provenance": dict(candidate.get("provenance", {}) or {}),
        "uncertainty": list(candidate.get("uncertainty", []) or []),
        "limitations": list(candidate.get("limitations", []) or []),
        "risk_flags": list(candidate.get("risk_flags", []) or []),
        "rights_flags": list(candidate.get("rights_flags", []) or []),
        "suggested_decision": _suggested_decision(candidate),
        "review_required": True,
        "accepted_truth": False,
        "reviewed_index_mutation_performed": False,
        "master_index_mutation_performed": False,
        "raw_response_committed": False,
        "download_performed": False,
        "upload_performed": False,
        "extraction_executed": False,
        "model_provider_used": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
        "created_at": str(candidate.get("created_at", DEFAULT_CREATED_AT) or DEFAULT_CREATED_AT),
    }


def _ensure_policy(policy: Mapping[str, Any]) -> None:
    if policy.get("schema_version") != "ia_review_policy.v0":
        raise ValueError("IA review policy schema mismatch")
    if policy.get("review_queue_writes_enabled_for_IA_06") is not True:
        raise ValueError("IA review writes are not enabled for IA-06")
    if policy.get("accepted_truth_enabled") is not False:
        raise ValueError("accepted truth must remain disabled")


def _minimal_policy() -> dict[str, Any]:
    return {
        "schema_version": "ia_review_policy.v0",
        "review_queue_writes_enabled_for_IA_06": True,
        "accepted_truth_enabled": False,
        "reviewed_index_mutation_enabled": False,
        "master_index_mutation_enabled": False,
    }


def _suggested_decision(candidate: Mapping[str, Any]) -> str:
    kind = str(candidate.get("candidate_kind", ""))
    risk_flags = {str(value) for value in candidate.get("risk_flags", []) or []}
    rights_flags = {str(value) for value in candidate.get("rights_flags", []) or []}
    if "rights_review_required" in rights_flags:
        return "mark_rights_risk"
    if "safety_review_required" in risk_flags:
        return "mark_safety_risk"
    if kind == "ia_near_miss_candidate":
        return "mark_near_miss"
    if kind == "ia_absence_or_missing_item_candidate":
        return "needs_more_evidence"
    return "approve_for_reviewed_index_dry_run"


def _candidate_snapshot(item: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "candidate_id": str(item.get("candidate_id", "")),
        "candidate_kind": str(item.get("candidate_kind", "")),
        "title": str(item.get("title", "")),
        "summary": str(item.get("summary", "")),
        "source_locator": dict(item.get("source_locator", {}) or {}),
        "evidence_ids": list(item.get("evidence_ids", []) or []),
        "source_cache_record_ids": list(item.get("source_cache_record_ids", []) or []),
        "observation_ids": list(item.get("observation_ids", []) or []),
        "provenance": dict(item.get("provenance", {}) or {}),
        "uncertainty": list(item.get("uncertainty", []) or []),
        "limitations": list(item.get("limitations", []) or []),
        "risk_flags": list(item.get("risk_flags", []) or []),
        "rights_flags": list(item.get("rights_flags", []) or []),
    }


def _review_queue_item_payload(item: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "ia_review_queue_payload.v0",
        "ia_candidate_id": str(item.get("candidate_id", "")),
        "ia_candidate_kind": str(item.get("candidate_kind", "")),
        "evidence_refs": list(item.get("evidence_ids", []) or []),
        "source_cache_refs": list(item.get("source_cache_record_ids", []) or []),
        "observation_refs": list(item.get("observation_ids", []) or []),
        "source_locator": _safe_locator(item.get("source_locator", {})),
        "provenance": _safe_provenance(item.get("provenance", {})),
        "operator_review_required": True,
        "acceptance_state": "not_accepted",
        "downstream_effects": {
            "reviewed_index": "none",
            "master_index": "none",
            "downloads": "none",
        },
    }


def _review_queue_decision_payload(decision: Mapping[str, Any]) -> dict[str, Any]:
    snapshot = dict(decision.get("candidate_snapshot", {}) or {})
    return {
        "schema_version": "ia_review_decision_payload.v0",
        "ia_candidate_id": str(decision.get("candidate_id", "")),
        "ia_decision": str(decision.get("decision", "")),
        "creates_preview": bool(decision.get("creates_promotion_preview", False)),
        "source_refs": {
            "evidence_refs": list(snapshot.get("evidence_ids", []) or []),
            "source_cache_refs": list(snapshot.get("source_cache_record_ids", []) or []),
            "observation_refs": list(snapshot.get("observation_ids", []) or []),
        },
        "acceptance_state": "not_accepted",
        "downstream_effects": {
            "reviewed_index": "none",
            "master_index": "none",
        },
    }


def _safe_locator(value: Any) -> dict[str, Any]:
    locator = dict(value or {}) if isinstance(value, Mapping) else {}
    return {
        "kind": str(locator.get("kind", "")),
        "label": str(locator.get("label", "")),
        "value_hash": str(locator.get("value_hash", "")),
    }


def _safe_provenance(value: Any) -> dict[str, Any]:
    provenance = dict(value or {}) if isinstance(value, Mapping) else {}
    return {
        "source_kind": str(provenance.get("source_kind", "")),
        "observation_kind": str(provenance.get("observation_kind", "")),
        "endpoint_class": str(provenance.get("endpoint_class", "")),
        "metadata_only": True,
    }


def _decision_kind_and_status(decision: str) -> tuple[ReviewDecisionKind, ReviewQueueStatus]:
    return {
        "approve_for_reviewed_index_dry_run": (ReviewDecisionKind.ACCEPT, ReviewQueueStatus.ACCEPTED),
        "reject_candidate": (ReviewDecisionKind.REJECT, ReviewQueueStatus.REJECTED),
        "needs_more_evidence": (ReviewDecisionKind.REQUEST_MORE_EVIDENCE, ReviewQueueStatus.NEEDS_MORE_EVIDENCE),
        "mark_near_miss": (ReviewDecisionKind.NOTE_ONLY, ReviewQueueStatus.NEEDS_REVIEW),
        "mark_duplicate": (ReviewDecisionKind.SUPERSEDE, ReviewQueueStatus.SUPERSEDED),
        "mark_policy_blocked": (ReviewDecisionKind.BLOCK, ReviewQueueStatus.BLOCKED),
        "mark_rights_risk": (ReviewDecisionKind.BLOCK, ReviewQueueStatus.BLOCKED),
        "mark_safety_risk": (ReviewDecisionKind.BLOCK, ReviewQueueStatus.BLOCKED),
    }[decision]


def _default_rationale(decision: str, item: Mapping[str, Any]) -> str:
    return {
        "approve_for_reviewed_index_dry_run": "Candidate has bounded IA metadata evidence and may produce a preview only.",
        "reject_candidate": "Candidate is rejected in local review queue only.",
        "needs_more_evidence": "Candidate needs more evidence before any promotion preview.",
        "mark_near_miss": "Candidate is a near miss and remains non-promotable.",
        "mark_duplicate": "Candidate appears duplicate and remains non-promotable.",
        "mark_policy_blocked": "Candidate is blocked by IA policy boundaries.",
        "mark_rights_risk": "Candidate has rights risk and remains non-promotable.",
        "mark_safety_risk": "Candidate has safety risk and remains non-promotable.",
    }.get(decision, f"Local IA review decision for {item.get('candidate_id', '')}.")


def _priority(item: Mapping[str, Any]) -> int:
    decision = str(item.get("suggested_decision", ""))
    if decision == "approve_for_reviewed_index_dry_run":
        return 80
    if decision in {"mark_policy_blocked", "mark_rights_risk", "mark_safety_risk"}:
        return 40
    return 100
