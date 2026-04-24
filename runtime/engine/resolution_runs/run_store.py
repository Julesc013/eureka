from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from runtime.engine.interfaces.public.resolution_run import ResolutionRunRecord
from runtime.engine.resolution_runs.resolution_run import (
    ResolutionRunNotFoundError,
    resolution_run_from_dict,
    resolution_run_to_dict,
)


class LocalResolutionRunStore:
    def __init__(self, root: str | Path) -> None:
        self._root = Path(root)
        self._store_root = self._root / "resolution_runs"
        self._runs_root = self._store_root / "runs"
        self._index_path = self._store_root / "index.json"

    def allocate_run_id(self, run_kind: str) -> str:
        index = self._load_index()
        counter = int(index.get("next_counter", 1))
        index["next_counter"] = counter + 1
        self._write_index(index)
        normalized_kind = run_kind.replace("_", "-")
        return f"run-{normalized_kind}-{counter:04d}"

    def save_run(self, run: ResolutionRunRecord) -> ResolutionRunRecord:
        self._runs_root.mkdir(parents=True, exist_ok=True)
        run_path = self._run_path(run.run_id)
        run_path.write_text(_serialize_json(resolution_run_to_dict(run)), encoding="utf-8")
        index = self._load_index()
        run_ids = [
            entry
            for entry in index.get("run_ids", [])
            if isinstance(entry, str) and entry != run.run_id
        ]
        run_ids.append(run.run_id)
        index["run_ids"] = run_ids
        self._write_index(index)
        return run

    def get_run(self, run_id: str) -> ResolutionRunRecord:
        run_path = self._run_path(run_id)
        if not run_path.is_file():
            raise ResolutionRunNotFoundError(run_id)
        with run_path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        if not isinstance(payload, dict):
            raise ValueError(f"{run_path}: resolution run root must be an object.")
        return resolution_run_from_dict(payload, source_path=run_path)

    def list_runs(self) -> tuple[ResolutionRunRecord, ...]:
        index = self._load_index()
        run_ids = [
            entry
            for entry in index.get("run_ids", [])
            if isinstance(entry, str) and entry
        ]
        return tuple(self.get_run(run_id) for run_id in run_ids)

    def _run_path(self, run_id: str) -> Path:
        return self._runs_root / f"{run_id}.json"

    def _load_index(self) -> dict[str, Any]:
        if not self._index_path.is_file():
            return {
                "record_kind": "eureka.resolution_run_index",
                "record_version": "0.1.0-draft",
                "next_counter": 1,
                "run_ids": [],
            }
        with self._index_path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        if not isinstance(payload, dict):
            raise ValueError(f"{self._index_path}: run index root must be an object.")
        return payload

    def _write_index(self, index: dict[str, Any]) -> None:
        self._store_root.mkdir(parents=True, exist_ok=True)
        self._index_path.write_text(_serialize_json(index), encoding="utf-8")


def _serialize_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"
