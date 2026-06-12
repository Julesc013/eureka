"""Local review materialization helpers for the local search MVP."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
from typing import Any, Mapping, Sequence

from runtime.local.search_index import document_to_result_card, search_index_path


REVIEW_EVENT_SCHEMA_VERSION = "eureka.local_review_event.v0"
REVIEWED_RECORD_SCHEMA_VERSION = "eureka.local_reviewed_record.v0"
DEFAULT_REVIEW_LEDGER_PATH = ".eureka/local_review_ledger.jsonl"
DEFAULT_REVIEWED_RECORDS_PATH = ".eureka/local_reviewed_records.jsonl"
DEFAULT_REVIEWED_INDEX_PATH = ".eureka/local_search_index.reviewed.json"
SUPPORTED_DECISIONS = ("accept", "reject", "mark_need")


@dataclass(frozen=True)
class LocalReviewSelection:
    query: str
    candidate: Mapping[str, Any]
    search_errors: tuple[str, ...] = ()


def list_candidates(index_path: str | Path, query: str, *, limit: int = 10) -> dict[str, Any]:
    state = search_index_path(index_path, query, limit=max(1, min(int(limit), 25)))
    candidates = [dict(item) for item in state.results]
    return {
        "schema_version": "eureka.local_review_candidates.v0",
        "status": "pass" if state.loaded else "fail",
        "query": query,
        "index_path": state.path,
        "index_loaded": state.loaded,
        "index_document_count": state.document_count,
        "candidate_count": len(candidates),
        "candidates": [_candidate_summary(candidate) for candidate in candidates],
        "index_errors": list(state.errors),
        "artifact_verified": False,
        "review_scope": "local_demo",
    }


def accept_candidate(
    *,
    index_path: str | Path,
    query: str,
    ledger_path: str | Path,
    records_path: str | Path,
    reviewer: str,
    reason: str,
    candidate_id: str | None = None,
    decision: str = "accept",
    reviewed_at: str | None = None,
    dry_run: bool = False,
) -> dict[str, Any]:
    decision = _normalize_decision(decision)
    selection = select_candidate(index_path, query, candidate_id=candidate_id)
    candidate = dict(selection.candidate)
    timestamp = _reviewed_at(reviewed_at)
    event = _review_event(
        candidate,
        query=query,
        reviewer=reviewer,
        reason=reason,
        decision=decision,
        reviewed_at=timestamp,
        index_path=str(index_path),
    )
    record = _reviewed_record(candidate, event) if decision == "accept" else None

    ledger_existing = _load_jsonl(ledger_path)
    records_existing = _load_jsonl(records_path)
    existing_event = _find_by_id(ledger_existing, "review_event_id", str(event["review_event_id"]))
    existing_record = (
        _find_by_id(records_existing, "reviewed_record_id", str(record["reviewed_record_id"]))
        if record is not None
        else None
    )

    event_written = False
    record_written = False
    if not dry_run:
        if existing_event is None:
            _append_jsonl(ledger_path, event)
            event_written = True
        if record is not None and existing_record is None:
            _append_jsonl(records_path, record)
            record_written = True

    materialized = dict(existing_record or record or {})
    return {
        "schema_version": "eureka.local_review_accept_result.v0",
        "status": "pass",
        "decision": decision,
        "query": query,
        "candidate_id": str(candidate.get("id") or ""),
        "review_event_id": str((existing_event or event).get("review_event_id") or ""),
        "reviewed_record_id": str(materialized.get("reviewed_record_id") or ""),
        "review_event": dict(existing_event or event),
        "reviewed_record": materialized or None,
        "ledger_path": str(ledger_path),
        "records_path": str(records_path),
        "event_written": event_written,
        "record_written": record_written,
        "idempotent_existing_event": existing_event is not None,
        "idempotent_existing_record": existing_record is not None,
        "dry_run": bool(dry_run),
        "artifact_verified": False,
        "accepted_truth_created": False,
        "reviewed_index_mutated": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "limitations": [
            "local generated review artifact",
            "reviewed metadata/source lead is not a verified artifact",
            "reviewed index rebuild is a separate explicit command",
        ],
    }


def review_stats(ledger_path: str | Path, records_path: str | Path) -> dict[str, Any]:
    events = _load_jsonl(ledger_path)
    records = _load_jsonl(records_path)
    decision_counts = _counts(str(item.get("decision") or "unknown") for item in events)
    review_state_counts = _counts(str(item.get("review_state") or "unknown") for item in records)
    return {
        "schema_version": "eureka.local_review_stats.v0",
        "status": "pass",
        "ledger_path": str(ledger_path),
        "records_path": str(records_path),
        "review_event_count": len(events),
        "reviewed_record_count": len(records),
        "decision_counts": decision_counts,
        "review_state_counts": review_state_counts,
        "artifact_verified_count": sum(1 for item in records if item.get("artifact_verified") is True),
        "accepted_truth_created": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
    }


def select_candidate(index_path: str | Path, query: str, *, candidate_id: str | None = None) -> LocalReviewSelection:
    state = search_index_path(index_path, query, limit=25)
    if not state.loaded:
        raise ValueError("; ".join(state.errors) or "index could not be loaded")
    candidates = [dict(item) for item in state.results]
    if candidate_id:
        selected = next((item for item in candidates if str(item.get("id") or "") == candidate_id), None)
        if selected is None:
            raise ValueError(f"candidate not found: {candidate_id}")
        return LocalReviewSelection(query=query, candidate=selected, search_errors=state.errors)
    selected = next((item for item in candidates if str(item.get("review_state") or "") != "accepted"), None)
    if selected is None:
        raise ValueError("no reviewable candidate found for query")
    return LocalReviewSelection(query=query, candidate=selected, search_errors=state.errors)


def _candidate_summary(candidate: Mapping[str, Any]) -> dict[str, Any]:
    card = document_to_result_card(candidate)
    return {
        "candidate_id": str(candidate.get("id") or ""),
        "status": str(candidate.get("status") or "unknown"),
        "title": str(candidate.get("title") or ""),
        "source_family": str(candidate.get("source_family") or ""),
        "review_state": str(candidate.get("review_state") or "unreviewed"),
        "artifact_verified": bool(candidate.get("artifact_verified") is True),
        "source_hints": list(card.get("source_hints") or []),
        "evidence_hints": list(card.get("evidence_hints") or []),
        "non_verified_reason": str(card.get("non_verified_reason") or ""),
    }


def _review_event(
    candidate: Mapping[str, Any],
    *,
    query: str,
    reviewer: str,
    reason: str,
    decision: str,
    reviewed_at: str,
    index_path: str,
) -> dict[str, Any]:
    candidate_id = str(candidate.get("id") or "")
    review_event_id = _stable_id("local-review-event", candidate_id, reviewer, decision)
    reviewed_record_id = _stable_id("local-reviewed-record", candidate_id, review_event_id)
    return {
        "schema_version": REVIEW_EVENT_SCHEMA_VERSION,
        "review_event_id": review_event_id,
        "decision": decision,
        "candidate_id": candidate_id,
        "source_query": query,
        "reviewer": str(reviewer or "local_demo"),
        "reason": str(reason or ""),
        "evidence_refs": _string_list(candidate.get("evidence_hints")),
        "source_observation_refs": _string_list(candidate.get("source_hints")),
        "review_scope": "local_demo",
        "reviewed_at": reviewed_at,
        "created_at": reviewed_at,
        "artifact_verified": False,
        "accepted_truth": False,
        "source_index_path": index_path,
        "source_family": str(candidate.get("source_family") or ""),
        "reviewed_record_id": reviewed_record_id if decision == "accept" else "",
        "limitations": [
            "local generated review event",
            "does not establish verified artifact truth",
            "does not mutate public or master indexes",
        ],
    }


def _reviewed_record(candidate: Mapping[str, Any], event: Mapping[str, Any]) -> dict[str, Any]:
    source_candidate_id = str(candidate.get("id") or "")
    reviewed_record_id = str(event.get("reviewed_record_id") or _stable_id("local-reviewed-record", source_candidate_id))
    title = str(candidate.get("title") or "Local reviewed source lead")
    summary = str(candidate.get("summary") or "Accepted local reviewed source lead.")
    evidence_hints = _string_list(candidate.get("evidence_hints"))
    source_hints = _string_list(candidate.get("source_hints"))
    source_query = str(event.get("source_query") or "")
    return {
        "schema_version": REVIEWED_RECORD_SCHEMA_VERSION,
        "reviewed_record_id": reviewed_record_id,
        "source_candidate_id": source_candidate_id,
        "source_review_event_id": str(event.get("review_event_id") or ""),
        "title": title,
        "summary": summary,
        "normalized_searchable_text": str(candidate.get("normalized_search_text") or ""),
        "source_query": source_query,
        "query_hints": [source_query, title, summary, str(candidate.get("source_candidate_id") or "")],
        "matched_queries": [source_query] if source_query else [],
        "status": str(candidate.get("status") or "candidate"),
        "record_state": "reviewed",
        "review_state": "accepted",
        "artifact_verified": False,
        "accepted_truth": False,
        "source_family": str(candidate.get("source_family") or ""),
        "source_hints": source_hints,
        "evidence_hints": evidence_hints,
        "missing_information": _string_list(candidate.get("missing_information")),
        "safe_next_action": "use this local reviewed source lead as search context; artifact verification remains deferred",
        "provenance": {
            "source": "local_review_materialization",
            "source_kind": "local_reviewed_record",
            "source_candidate_id": source_candidate_id,
            "source_review_event_id": str(event.get("review_event_id") or ""),
            "source_candidate_provenance": dict(candidate.get("provenance") or {}),
        },
        "non_verified_reason": "local reviewed metadata/source lead is not a verified artifact",
        "reviewer": str(event.get("reviewer") or ""),
        "review_reason": str(event.get("reason") or ""),
        "reviewed_at": str(event.get("reviewed_at") or ""),
        "review_scope": "local_demo",
        "no_mutation": {
            "reviewed_records_mutated": True,
            "review_ledgers_mutated": True,
            "reviewed_index_mutated": False,
            "public_index_mutated": False,
            "master_index_mutated": False,
            "truth_promotion_performed": False,
        },
    }


def _load_jsonl(path: str | Path) -> list[dict[str, Any]]:
    source = Path(path)
    if not source.is_file():
        return []
    rows: list[dict[str, Any]] = []
    for line_number, line in enumerate(source.read_text(encoding="utf-8").splitlines(), start=1):
        if not line.strip():
            continue
        try:
            value = json.loads(line)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{source}:{line_number}: invalid JSONL row: {exc.msg}") from exc
        if not isinstance(value, Mapping):
            raise ValueError(f"{source}:{line_number}: JSONL row must be an object")
        rows.append(dict(value))
    return rows


def _append_jsonl(path: str | Path, row: Mapping[str, Any]) -> None:
    destination = Path(path)
    destination.parent.mkdir(parents=True, exist_ok=True)
    with destination.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(dict(row), sort_keys=True, separators=(",", ":"), ensure_ascii=True))
        handle.write("\n")


def _find_by_id(rows: Sequence[Mapping[str, Any]], key: str, value: str) -> Mapping[str, Any] | None:
    return next((row for row in rows if str(row.get(key) or "") == value), None)


def _reviewed_at(value: str | None) -> str:
    if value:
        return str(value)
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _normalize_decision(value: str) -> str:
    decision = str(value or "accept").strip()
    if decision not in SUPPORTED_DECISIONS:
        raise ValueError(f"unsupported review decision: {value}")
    return decision


def _stable_id(prefix: str, *parts: Any) -> str:
    encoded = json.dumps(parts, sort_keys=True, separators=(",", ":"), ensure_ascii=True, default=str).encode("utf-8")
    return f"{prefix}:{hashlib.sha256(encoded).hexdigest()[:16]}"


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, (list, tuple, set)):
        return []
    return [str(item) for item in value if item not in (None, "")]


def _counts(values: Any) -> dict[str, int]:
    counter: dict[str, int] = {}
    for value in values:
        key = str(value or "unknown")
        counter[key] = counter.get(key, 0) + 1
    return {key: counter[key] for key in sorted(counter)}
