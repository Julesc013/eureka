from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from runtime.engine.compatibility import CompatibilityRequirements
from runtime.engine.provenance import EvidenceSummary
from runtime.engine.representations import RepresentationSummary


@dataclass(frozen=True)
class NormalizedResolutionRecord:
    target_ref: str
    source_name: str
    source_locator: str
    object_id: str
    record_kind: str = "resolved_object"
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
    representations: tuple[RepresentationSummary, ...] = ()
    compatibility_requirements: CompatibilityRequirements | None = None
    evidence: tuple[EvidenceSummary, ...] = ()
    parent_target_ref: str | None = None
    parent_resolved_resource_id: str | None = None
    parent_representation_id: str | None = None
    parent_object_label: str | None = None
    member_path: str | None = None
    member_label: str | None = None
    member_kind: str | None = None
    media_type: str | None = None
    size_bytes: int | None = None
    content_hash: str | None = None
    parent_lineage: dict[str, Any] | None = None
    action_hints: tuple[str, ...] = ()
