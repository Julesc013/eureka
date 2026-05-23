"""Tiny explicit-instance candidate-index store.

The store persists provisional candidate records as a JSON snapshot inside an
operator-supplied local instance. It is not a reviewed index and does not touch
the master index.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Mapping, Sequence

from runtime.local.foundry import candidate_store


STORE_SCHEMA_VERSION = "candidate_index_store.v0"


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


@dataclass(frozen=True, slots=True)
class CandidateIndexStore:
    path: Path

    @classmethod
    def open(cls, path: str | Path) -> "CandidateIndexStore":
        value = Path(path)
        if not value.name:
            raise ValueError("candidate index path is required")
        if value.name.startswith("."):
            raise ValueError("candidate index file must not be hidden")
        return cls(value)

    def init(self) -> None:
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            self.path.write_text(_encode(_empty_snapshot()), encoding="utf-8")

    def load(self) -> dict[str, Any]:
        if not self.path.exists():
            return _empty_snapshot()
        payload = json.loads(self.path.read_text(encoding="utf-8"))
        return payload if isinstance(payload, dict) else _empty_snapshot()

    def write_candidate_records(self, records: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
        self.init()
        record_list = [dict(item) for item in records]
        normalized = []
        for record in record_list:
            candidate = candidate_store.build_candidate_record(record)
            errors = candidate_store.validate_candidate_record(candidate)
            if errors:
                raise ValueError("; ".join(errors))
            normalized.append(record)
        snapshot = candidate_store.build_candidate_store_snapshot(record_list)
        payload = {
            "schema_version": STORE_SCHEMA_VERSION,
            "updated_at": utc_now(),
            "candidate_count": len(record_list),
            "candidates": normalized,
            "candidate_store_snapshot": snapshot,
            "review_required": True,
            "accepted_truth": False,
            "reviewed_index_mutation_performed": False,
            "master_index_mutation_performed": False,
            "raw_response_committed": False,
            "download_performed": False,
        }
        self.path.write_text(_encode(payload), encoding="utf-8")
        return self.summarize()

    def summarize(self) -> dict[str, Any]:
        payload = self.load()
        candidates = list(payload.get("candidates", []) or [])
        return {
            "schema_version": "candidate_index_store_summary.v0",
            "candidate_count": len(candidates),
            "candidate_ids": [str(item.get("candidate_id", "")) for item in candidates if isinstance(item, Mapping)],
            "review_required_count": sum(1 for item in candidates if isinstance(item, Mapping) and item.get("review_required") is True),
            "accepted_truth_count": sum(1 for item in candidates if isinstance(item, Mapping) and item.get("accepted_truth") is True),
            "reviewed_index_mutation_performed": False,
            "master_index_mutation_performed": False,
            "raw_response_committed": False,
            "download_performed": False,
        }


def _empty_snapshot() -> dict[str, Any]:
    return {
        "schema_version": STORE_SCHEMA_VERSION,
        "updated_at": utc_now(),
        "candidate_count": 0,
        "candidates": [],
        "review_required": True,
        "accepted_truth": False,
        "reviewed_index_mutation_performed": False,
        "master_index_mutation_performed": False,
        "raw_response_committed": False,
        "download_performed": False,
    }


def _encode(payload: Mapping[str, Any]) -> str:
    return json.dumps(dict(payload), indent=2, sort_keys=True) + "\n"
