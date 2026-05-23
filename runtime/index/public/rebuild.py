"""Rebuild a local reviewed public index from explicit local stores."""

from __future__ import annotations

import hashlib
import sqlite3
from pathlib import Path
from typing import Any

from runtime.evidence.ledger.queries import row_to_candidate
from runtime.review.queue.queries import row_to_decision, row_to_review_item
from runtime.source.cache.queries import row_to_cache_entry

from .errors import PublicIndexRebuildError
from .records import PublicIndexRebuild, PublicIndexRecord, stable_digest
from .store import PublicIndexStore
from .validation import ensure_valid, validate_public_index_path


def rebuild_reviewed_public_index(
    source_cache_db: str | Path,
    evidence_ledger_db: str | Path,
    review_queue_db: str | Path,
    public_index_db: str | Path,
    *,
    include_statuses: tuple[str, ...] = ("accepted",),
    dry_run: bool = False,
) -> dict[str, Any]:
    ensure_valid(validate_public_index_path(public_index_db))
    if any(str(path) == ":memory:" for path in (source_cache_db, evidence_ledger_db, review_queue_db)):
        raise PublicIndexRebuildError("reviewed public index rebuild requires explicit file-backed input stores")

    cache_connection = _open_readonly(source_cache_db)
    evidence_connection = _open_readonly(evidence_ledger_db)
    review_connection = _open_readonly(review_queue_db)
    try:
        included: list[PublicIndexRecord] = []
        excluded: list[dict[str, str]] = []
        decisions = review_connection.execute(
            "SELECT d.*, i.evidence_id AS item_evidence_id, i.source_cache_entry_id AS item_source_cache_entry_id, "
            "i.queue_status AS item_queue_status, i.subject_kind AS item_subject_kind "
            "FROM review_decisions d JOIN review_items i ON i.review_item_id = d.review_item_id "
            "ORDER BY d.created_at, d.id"
        ).fetchall()
        wanted = {str(item) for item in include_statuses}
        for decision_row in decisions:
            decision_status = str(decision_row["decision_status"])
            item_status = str(decision_row["item_queue_status"])
            review_item_id = str(decision_row["review_item_id"])
            if decision_status not in wanted or item_status not in wanted:
                excluded.append(
                    {
                        "review_item_id": review_item_id,
                        "decision_id": str(decision_row["id"]),
                        "decision_status": decision_status,
                        "reason": "decision or item status is not included",
                    }
                )
                continue
            review_item = row_to_review_item(_select_one(review_connection, "review_items", "review_item_id", review_item_id))
            evidence_id = review_item.evidence_id
            source_cache_entry_id = review_item.source_cache_entry_id
            if not evidence_id or not source_cache_entry_id:
                excluded.append({"review_item_id": review_item_id, "decision_id": str(decision_row["id"]), "reason": "missing links"})
                continue
            evidence_row = _select_one(evidence_connection, "evidence_candidates", "evidence_id", evidence_id)
            cache_row = _select_one(cache_connection, "cache_entries", "id", source_cache_entry_id)
            if evidence_row is None or cache_row is None:
                excluded.append(
                    {
                        "review_item_id": review_item_id,
                        "decision_id": str(decision_row["id"]),
                        "reason": "linked source cache or evidence record was not found",
                    }
                )
                continue
            record = PublicIndexRecord.from_reviewed_inputs(
                row_to_cache_entry(cache_row),
                row_to_candidate(evidence_row),
                review_item,
                row_to_decision(decision_row),
            )
            included.append(record)
        rebuild = PublicIndexRebuild(
            rebuild_id="pireb_" + stable_digest(
                {
                    "source_cache_db": str(source_cache_db),
                    "evidence_ledger_db": str(evidence_ledger_db),
                    "review_queue_db": str(review_queue_db),
                    "public_index_db": str(public_index_db),
                    "included": [record.record_id for record in included],
                    "dry_run": dry_run,
                }
            ),
            status="dry_run" if dry_run else "applied",
            included_count=len(included),
            excluded_count=len(excluded),
            include_statuses=tuple(sorted(wanted)),
            source_cache_db=str(source_cache_db),
            evidence_ledger_db=str(evidence_ledger_db),
            review_queue_db=str(review_queue_db),
            public_index_db=str(public_index_db),
            dry_run=dry_run,
            limitations=("local reviewed projection only", "does not mutate input stores"),
        )
        if not dry_run:
            with PublicIndexStore.open(public_index_db) as public_store:
                public_store.init()
                public_store.write_rebuild(rebuild)
                for record in included:
                    public_store.write_record(record)
        return {
            "schema_version": "public_index_rebuild_report.v0",
            "status": rebuild.status,
            "rebuild": rebuild.to_dict(),
            "included_count": len(included),
            "excluded_count": len(excluded),
            "records": [record.to_dict() for record in included],
            "excluded": excluded,
            "input_stores_mutated": False,
            "site_dist_mutated": False,
            "master_index_mutated": False,
        }
    finally:
        cache_connection.close()
        evidence_connection.close()
        review_connection.close()


def _open_readonly(path: str | Path) -> sqlite3.Connection:
    db_path = Path(path)
    if not db_path.exists():
        raise PublicIndexRebuildError(f"input store does not exist: {db_path}")
    connection = sqlite3.connect(db_path.resolve().as_uri() + "?mode=ro", uri=True)
    connection.row_factory = sqlite3.Row
    return connection


def _select_one(connection: sqlite3.Connection, table: str, column: str, value: str) -> sqlite3.Row | None:
    return connection.execute(f"SELECT * FROM {table} WHERE {column} = ?", (value,)).fetchone()


def file_digest(path: str | Path) -> str:
    db_path = Path(path)
    return hashlib.sha256(db_path.read_bytes()).hexdigest()
