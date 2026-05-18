"""Local Internet Archive metadata observation candidate records."""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import Any, Mapping

from runtime.source_observation.ids import canonical_json


SOURCE_ID = "internet_archive_metadata"
SOURCE_FAMILY = "preservation_metadata"
FILE_METADATA_CAP = 5

OBSERVATION_KINDS = (
    "metadata_search_result",
    "item_metadata",
    "item_file_list",
    "missing_item",
    "malformed_partial",
    "retry_after",
    "large_file_list",
    "no_download_proof",
)

FORBIDDEN_SIDE_EFFECT_FLAGS = (
    "live_source_call_performed",
    "source_probe_executed",
    "source_cache_write_performed",
    "evidence_ledger_write_performed",
    "candidate_index_mutated",
    "reviewed_index_mutated",
    "master_index_mutated",
    "download_performed",
    "upload_performed",
    "model_provider_used",
    "deployment_performed",
    "production_readiness_claimed",
    "public_launch_readiness_claimed",
)


def default_boundary_flags() -> dict[str, bool]:
    return {key: False for key in FORBIDDEN_SIDE_EFFECT_FLAGS}


@dataclass(frozen=True, slots=True)
class IAMetadataSourceLocator:
    kind: str
    value: str
    label: str
    metadata: Mapping[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "value": self.value,
            "label": self.label,
            "metadata": dict(self.metadata),
        }


@dataclass(frozen=True, slots=True)
class IAMetadataCandidateRecord:
    observation_id: str
    fixture_id: str
    observation_kind: str
    item_identifier: str
    title_candidate: str
    mediatype_candidate: str
    collection_candidates: tuple[str, ...]
    creator_candidate: str
    date_candidate: str
    description_candidate: str
    file_metadata_candidates: tuple[Mapping[str, Any], ...]
    checksum_candidates: tuple[Mapping[str, Any], ...]
    source_locator: IAMetadataSourceLocator
    limitations: tuple[str, ...]
    risk_flags: tuple[str, ...]
    rights_flags: tuple[str, ...]
    confidence: float
    review_required: bool = True
    accepted_truth: bool = False
    download_performed: bool = False
    source_cache_write_performed: bool = False
    evidence_ledger_write_performed: bool = False
    index_mutation_performed: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "ia_normalized_source_observation_candidate.v0",
            "source_id": SOURCE_ID,
            "observation_id": self.observation_id,
            "fixture_id": self.fixture_id,
            "observation_kind": self.observation_kind,
            "item_identifier": self.item_identifier,
            "title_candidate": self.title_candidate,
            "mediatype_candidate": self.mediatype_candidate,
            "collection_candidates": list(self.collection_candidates),
            "creator_candidate": self.creator_candidate,
            "date_candidate": self.date_candidate,
            "description_candidate": self.description_candidate,
            "file_metadata_candidates": [dict(item) for item in self.file_metadata_candidates],
            "checksum_candidates": [dict(item) for item in self.checksum_candidates],
            "source_locator": self.source_locator.to_dict(),
            "limitations": list(self.limitations),
            "risk_flags": list(self.risk_flags),
            "rights_flags": list(self.rights_flags),
            "confidence": self.confidence,
            "review_required": self.review_required,
            "accepted_truth": self.accepted_truth,
            "download_performed": self.download_performed,
            "source_cache_write_performed": self.source_cache_write_performed,
            "evidence_ledger_write_performed": self.evidence_ledger_write_performed,
            "index_mutation_performed": self.index_mutation_performed,
        }

    def to_json(self) -> str:
        return canonical_json(self.to_dict())

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> "IAMetadataCandidateRecord":
        locator = data.get("source_locator", {}) or {}
        return cls(
            observation_id=str(data.get("observation_id", "")),
            fixture_id=str(data.get("fixture_id", "")),
            observation_kind=str(data.get("observation_kind", "")),
            item_identifier=str(data.get("item_identifier", "")),
            title_candidate=str(data.get("title_candidate", "")),
            mediatype_candidate=str(data.get("mediatype_candidate", "")),
            collection_candidates=tuple(str(item) for item in data.get("collection_candidates", []) or []),
            creator_candidate=str(data.get("creator_candidate", "")),
            date_candidate=str(data.get("date_candidate", "")),
            description_candidate=str(data.get("description_candidate", "")),
            file_metadata_candidates=tuple(dict(item) for item in data.get("file_metadata_candidates", []) or []),
            checksum_candidates=tuple(dict(item) for item in data.get("checksum_candidates", []) or []),
            source_locator=IAMetadataSourceLocator(
                kind=str(locator.get("kind", "")),
                value=str(locator.get("value", "")),
                label=str(locator.get("label", "")),
                metadata=dict(locator.get("metadata", {}) or {}),
            ),
            limitations=tuple(str(item) for item in data.get("limitations", []) or []),
            risk_flags=tuple(str(item) for item in data.get("risk_flags", []) or []),
            rights_flags=tuple(str(item) for item in data.get("rights_flags", []) or []),
            confidence=float(data.get("confidence", 0.0)),
            review_required=bool(data.get("review_required", True)),
            accepted_truth=bool(data.get("accepted_truth", False)),
            download_performed=bool(data.get("download_performed", False)),
            source_cache_write_performed=bool(data.get("source_cache_write_performed", False)),
            evidence_ledger_write_performed=bool(data.get("evidence_ledger_write_performed", False)),
            index_mutation_performed=bool(data.get("index_mutation_performed", False)),
        )

    @classmethod
    def from_json(cls, text: str) -> "IAMetadataCandidateRecord":
        return cls.from_dict(json.loads(text))


@dataclass(frozen=True, slots=True)
class IABoundaryReport:
    fixture_id: str
    observation_id: str
    observation_kind: str
    passed: bool
    violations: tuple[str, ...]
    network_imports_detected: bool = False
    live_source_call_performed: bool = False
    source_probe_executed: bool = False
    source_cache_write_performed: bool = False
    evidence_ledger_write_performed: bool = False
    candidate_index_mutated: bool = False
    reviewed_index_mutated: bool = False
    master_index_mutated: bool = False
    download_performed: bool = False
    upload_performed: bool = False
    model_provider_used: bool = False
    deployment_performed: bool = False
    production_readiness_claimed: bool = False
    public_launch_readiness_claimed: bool = False

    def to_dict(self) -> dict[str, Any]:
        payload = {
            "schema_version": "ia_fixture_boundary_report.v0",
            "fixture_id": self.fixture_id,
            "observation_id": self.observation_id,
            "observation_kind": self.observation_kind,
            "passed": self.passed,
            "violations": list(self.violations),
            "network_imports_detected": self.network_imports_detected,
        }
        for key in FORBIDDEN_SIDE_EFFECT_FLAGS:
            payload[key] = bool(getattr(self, key))
        return payload
