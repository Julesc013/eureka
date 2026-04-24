from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from runtime.engine.interfaces.public.resolution_memory import (
    ResolutionMemoryCatalogRequest,
    ResolutionMemoryRecord,
)
from runtime.engine.interfaces.service import ResolutionMemoryNotFoundError
from runtime.engine.memory.resolution_memory import (
    resolution_memory_from_dict,
    resolution_memory_to_dict,
)


class LocalResolutionMemoryStore:
    def __init__(self, root: str | Path) -> None:
        self._root = Path(root)
        self._store_root = self._root / "resolution_memory"
        self._memories_root = self._store_root / "memories"
        self._index_path = self._store_root / "index.json"

    def allocate_memory_id(self, memory_kind: str) -> str:
        index = self._load_index()
        counter = int(index.get("next_counter", 1))
        index["next_counter"] = counter + 1
        self._write_index(index)
        normalized_kind = memory_kind.replace("_", "-")
        return f"memory-{normalized_kind}-{counter:04d}"

    def save_memory(self, memory: ResolutionMemoryRecord) -> ResolutionMemoryRecord:
        self._memories_root.mkdir(parents=True, exist_ok=True)
        memory_path = self._memory_path(memory.memory_id)
        memory_path.write_text(_serialize_json(resolution_memory_to_dict(memory)), encoding="utf-8")
        index = self._load_index()
        memory_ids = [
            entry
            for entry in index.get("memory_ids", [])
            if isinstance(entry, str) and entry != memory.memory_id
        ]
        memory_ids.append(memory.memory_id)
        index["memory_ids"] = memory_ids
        self._write_index(index)
        return memory

    def get_memory(self, memory_id: str) -> ResolutionMemoryRecord:
        memory_path = self._memory_path(memory_id)
        if not memory_path.is_file():
            raise ResolutionMemoryNotFoundError(memory_id)
        with memory_path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        if not isinstance(payload, dict):
            raise ValueError(f"{memory_path}: resolution memory root must be an object.")
        return resolution_memory_from_dict(payload, source_path=memory_path)

    def list_memories(
        self,
        request: ResolutionMemoryCatalogRequest | None = None,
    ) -> tuple[ResolutionMemoryRecord, ...]:
        index = self._load_index()
        memory_ids = [
            entry
            for entry in index.get("memory_ids", [])
            if isinstance(entry, str) and entry
        ]
        memories = tuple(self.get_memory(memory_id) for memory_id in memory_ids)
        if request is None:
            return memories
        return tuple(memory for memory in memories if _matches_request(memory, request))

    def _memory_path(self, memory_id: str) -> Path:
        return self._memories_root / f"{memory_id}.json"

    def _load_index(self) -> dict[str, Any]:
        if not self._index_path.is_file():
            return {
                "record_kind": "eureka.resolution_memory_index",
                "record_version": "0.1.0-draft",
                "next_counter": 1,
                "memory_ids": [],
            }
        with self._index_path.open("r", encoding="utf-8") as handle:
            payload = json.load(handle)
        if not isinstance(payload, dict):
            raise ValueError(f"{self._index_path}: memory index root must be an object.")
        return payload

    def _write_index(self, index: dict[str, Any]) -> None:
        self._store_root.mkdir(parents=True, exist_ok=True)
        self._index_path.write_text(_serialize_json(index), encoding="utf-8")


def _matches_request(memory: ResolutionMemoryRecord, request: ResolutionMemoryCatalogRequest) -> bool:
    if request.memory_kind is not None and memory.memory_kind != request.memory_kind:
        return False
    if request.source_run_id is not None and memory.source_run_id != request.source_run_id:
        return False
    if request.task_kind is not None and memory.task_kind != request.task_kind:
        return False
    if request.checked_source_id is not None and request.checked_source_id not in memory.checked_source_ids:
        return False
    return True


def _serialize_json(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, sort_keys=True) + "\n"
