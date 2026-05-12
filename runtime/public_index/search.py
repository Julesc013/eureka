"""Local search helpers for reviewed public index records."""

from __future__ import annotations

import json
import sqlite3
from typing import Any

from .records import PublicIndexRecord, PublicIndexSearchResult


def search_records(connection: sqlite3.Connection, query: str, limit: int = 20) -> list[PublicIndexSearchResult]:
    terms = [item.lower() for item in query.split() if item.strip()]
    if not terms:
        return []
    clauses = " OR ".join("lower(searchable_text) LIKE ?" for _ in terms)
    params: list[Any] = [f"%{term}%" for term in terms]
    params.append(limit)
    rows = connection.execute(
        f"SELECT * FROM public_index_records WHERE {clauses} ORDER BY updated_at DESC, id LIMIT ?",
        params,
    ).fetchall()
    results: list[PublicIndexSearchResult] = []
    for row in rows:
        record = row_to_public_index_record(row)
        matched = tuple(term for term in terms if term in record.searchable_text.lower())
        score = float(len(matched)) / float(max(len(terms), 1))
        results.append(
            PublicIndexSearchResult(
                record_id=record.record_id,
                title=record.title,
                description=record.description,
                source_id=record.source_id,
                score=score,
                matched_terms=matched,
                limitations=record.limitations,
                warnings=record.warnings,
            )
        )
    return results


def row_to_public_index_record(row: sqlite3.Row) -> PublicIndexRecord:
    return PublicIndexRecord(
        record_id=str(row["id"]),
        source_id=str(row["source_id"]),
        source_cache_entry_id=str(row["source_cache_entry_id"]),
        evidence_id=str(row["evidence_id"]),
        review_item_id=str(row["review_item_id"]),
        review_decision_id=str(row["review_decision_id"]),
        title=str(row["title"]),
        description=str(row["description"]),
        normalized_fields=dict(json.loads(str(row["normalized_fields_json"]))),
        searchable_text=str(row["searchable_text"]),
        source_family=str(row["source_family"]),
        trust_lane=str(row["trust_lane"]),
        limitations=tuple(str(item) for item in json.loads(str(row["limitations_json"]))),
        warnings=tuple(str(item) for item in json.loads(str(row["warnings_json"]))),
        created_at=str(row["created_at"]),
        updated_at=str(row["updated_at"]),
    )
