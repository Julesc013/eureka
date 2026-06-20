"""Local durable storage for independently fetched web observations."""

from __future__ import annotations

from pathlib import Path
import json
import tempfile
from typing import Any, Mapping, Protocol

from .http_fetcher import SourceObservation


class SourceObservationStore(Protocol):
    def put(self, observation: SourceObservation | Mapping[str, Any]) -> str:
        """Persist one independently fetched SourceObservation and return its id."""

    def get(self, observation_id: str) -> dict[str, Any] | None:
        """Load one persisted observation by id."""

    def list(self) -> list[dict[str, Any]]:
        """Return persisted observations in deterministic id order."""


class JsonlSourceObservationStore:
    """Small local store for the pre-SQLite fetch milestone.

    The per-id JSON files make idempotent writes simple; the JSONL file is a
    deterministic projection for tests, debugging, and later import.
    """

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.by_id = self.root / "by-id"
        self.jsonl_path = self.root / "source_observations.jsonl"

    def put(self, observation: SourceObservation | Mapping[str, Any]) -> str:
        payload = observation.to_dict() if isinstance(observation, SourceObservation) else dict(observation)
        observation_id = str(payload.get("observation_id") or "").strip()
        if not observation_id:
            raise ValueError("observation_id is required")
        if bool(payload.get("provider_result_payload_persisted", False)):
            raise ValueError("provider result payload cannot be persisted as a SourceObservation")
        payload["provider_result_payload_persisted"] = False
        payload["reviewed_master_mutation"] = False
        payload["public_index_mutation"] = False
        self.by_id.mkdir(parents=True, exist_ok=True)
        _atomic_write_json(self.by_id / f"{_safe_id(observation_id)}.json", payload)
        self._rewrite_jsonl()
        return observation_id

    def get(self, observation_id: str) -> dict[str, Any] | None:
        path = self.by_id / f"{_safe_id(observation_id)}.json"
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    def list(self) -> list[dict[str, Any]]:
        if not self.by_id.exists():
            return []
        records = []
        for path in sorted(self.by_id.glob("*.json")):
            records.append(json.loads(path.read_text(encoding="utf-8")))
        return sorted(records, key=lambda item: str(item.get("observation_id") or ""))

    def _rewrite_jsonl(self) -> None:
        lines = [json.dumps(item, sort_keys=True) for item in self.list()]
        _atomic_write_text(self.jsonl_path, "\n".join(lines) + ("\n" if lines else ""))


def _safe_id(value: str) -> str:
    return "".join(ch if ch.isalnum() or ch in {"-", "_", "."} else "_" for ch in value)


def _atomic_write_json(path: Path, payload: Mapping[str, Any]) -> None:
    _atomic_write_text(path, json.dumps(dict(payload), indent=2, sort_keys=True) + "\n")


def _atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="\n", dir=path.parent, delete=False) as handle:
        handle.write(text)
        temp = Path(handle.name)
    temp.replace(path)
