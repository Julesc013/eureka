from __future__ import annotations

from dataclasses import dataclass

from runtime.engine.provenance import EvidenceSummary


@dataclass(frozen=True)
class NormalizedResolutionRecord:
    target_ref: str
    source_name: str
    source_locator: str
    object_id: str
    source_family: str = "synthetic_fixture"
    source_family_label: str | None = None
    object_kind: str | None = None
    object_label: str | None = None
    state_id: str | None = None
    state_kind: str | None = None
    representation_id: str | None = None
    representation_kind: str | None = None
    access_path_id: str | None = None
    access_path_kind: str | None = None
    access_path_locator: str | None = None
    evidence: tuple[EvidenceSummary, ...] = ()
