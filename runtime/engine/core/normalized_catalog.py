from __future__ import annotations

from runtime.engine.interfaces.normalize import NormalizedResolutionRecord


class NormalizedCatalog:
    def __init__(self, records: tuple[NormalizedResolutionRecord, ...]) -> None:
        if not records:
            raise ValueError("Normalized catalog requires at least one record.")
        self._records = records

    @property
    def records(self) -> tuple[NormalizedResolutionRecord, ...]:
        return self._records

    @property
    def default_target_ref(self) -> str:
        return self._records[0].target_ref

    def find_by_target_ref(self, target_ref: str) -> NormalizedResolutionRecord | None:
        for record in self._records:
            if record.target_ref == target_ref:
                return record
        return None
