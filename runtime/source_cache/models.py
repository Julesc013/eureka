"""Data helpers for the P98 source cache dry-run runtime."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class SourceCacheDryRunError:
    """Serializable dry-run error entry."""

    code: str
    message: str
    path: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "code": self.code,
            "message": self.message,
            "path": self.path,
        }


@dataclass(frozen=True)
class SourceCacheCandidateSummary:
    """A conservative summary of one source-cache candidate input."""

    candidate_id: str
    path: str
    source_family: str
    record_kind: str
    privacy_status: str
    public_safety_status: str
    evidence_readiness: str
    policy_status: str
    valid: bool
    source_ref: str | None = None
    summary_text: str | None = None
    warnings: tuple[str, ...] = ()
    errors: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "path": self.path,
            "source_family": self.source_family,
            "record_kind": self.record_kind,
            "privacy_status": self.privacy_status,
            "public_safety_status": self.public_safety_status,
            "evidence_readiness": self.evidence_readiness,
            "policy_status": self.policy_status,
            "valid": self.valid,
            "source_ref": self.source_ref,
            "summary_text": self.summary_text,
            "warnings": list(self.warnings),
            "errors": list(self.errors),
        }


@dataclass(frozen=True)
class SourceCacheDryRunReport:
    """Deterministic dry-run report."""

    report_id: str
    input_roots: tuple[str, ...]
    candidates_seen: int
    candidates_valid: int
    candidates_invalid: int
    candidate_summaries: tuple[SourceCacheCandidateSummary, ...]
    source_families: dict[str, int]
    record_kinds: dict[str, int]
    privacy_status_counts: dict[str, int]
    public_safety_status_counts: dict[str, int]
    evidence_readiness_counts: dict[str, int]
    policy_status_counts: dict[str, int]
    mutation_summary: dict[str, bool]
    warnings: tuple[str, ...] = ()
    errors: tuple[SourceCacheDryRunError, ...] = ()
    hard_booleans: dict[str, bool] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "report_id": self.report_id,
            "mode": "local_dry_run",
            "input_roots": list(self.input_roots),
            "candidates_seen": self.candidates_seen,
            "candidates_valid": self.candidates_valid,
            "candidates_invalid": self.candidates_invalid,
            "candidate_summaries": [item.to_dict() for item in self.candidate_summaries],
            "source_families": dict(self.source_families),
            "record_kinds": dict(self.record_kinds),
            "privacy_status_counts": dict(self.privacy_status_counts),
            "public_safety_status_counts": dict(self.public_safety_status_counts),
            "evidence_readiness_counts": dict(self.evidence_readiness_counts),
            "policy_status_counts": dict(self.policy_status_counts),
            "mutation_summary": dict(self.mutation_summary),
            "warnings": list(self.warnings),
            "errors": [item.to_dict() for item in self.errors],
            "hard_booleans": dict(self.hard_booleans),
        }
