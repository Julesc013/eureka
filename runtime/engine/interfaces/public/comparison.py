from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Sequence

from runtime.engine.interfaces.public.resolution import Notice, ObjectSummary, SourceSummary
from runtime.engine.provenance import EvidenceSummary


@dataclass(frozen=True)
class ComparisonRequest:
    left_target_ref: str
    right_target_ref: str

    @classmethod
    def from_parts(cls, left_target_ref: str, right_target_ref: str) -> "ComparisonRequest":
        left = left_target_ref.strip()
        right = right_target_ref.strip()
        if not left:
            raise ValueError("left_target_ref must be a non-empty string.")
        if not right:
            raise ValueError("right_target_ref must be a non-empty string.")
        return cls(left_target_ref=left, right_target_ref=right)


@dataclass(frozen=True)
class ComparisonSide:
    target_ref: str
    status: str
    resolved_resource_id: str | None = None
    primary_object: ObjectSummary | None = None
    source: SourceSummary | None = None
    version_or_state: str | None = None
    evidence: tuple[EvidenceSummary, ...] = ()
    notices: tuple[Notice, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "target_ref": self.target_ref,
            "status": self.status,
            "notices": [notice.to_dict() for notice in self.notices],
        }
        if self.resolved_resource_id is not None:
            payload["resolved_resource_id"] = self.resolved_resource_id
        if self.primary_object is not None:
            payload["object"] = self.primary_object.to_dict()
        if self.source is not None:
            payload["source"] = self.source.to_dict()
        if self.version_or_state is not None:
            payload["version_or_state"] = self.version_or_state
        if self.evidence:
            payload["evidence"] = [summary.to_dict() for summary in self.evidence]
        return payload


@dataclass(frozen=True)
class ComparisonAgreement:
    category: str
    value: str

    def to_dict(self) -> dict[str, str]:
        return {
            "category": self.category,
            "value": self.value,
        }


@dataclass(frozen=True)
class ComparisonDisagreement:
    category: str
    left_value: str
    right_value: str

    def to_dict(self) -> dict[str, str]:
        return {
            "category": self.category,
            "left_value": self.left_value,
            "right_value": self.right_value,
        }


@dataclass(frozen=True)
class ComparisonResult:
    status: str
    left: ComparisonSide
    right: ComparisonSide
    agreements: tuple[ComparisonAgreement, ...] = ()
    disagreements: tuple[ComparisonDisagreement, ...] = ()
    notices: tuple[Notice, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "left": self.left.to_dict(),
            "right": self.right.to_dict(),
            "agreements": [agreement.to_dict() for agreement in self.agreements],
            "disagreements": [disagreement.to_dict() for disagreement in self.disagreements],
            "notices": [notice.to_dict() for notice in self.notices],
        }
