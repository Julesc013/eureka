"""Data helpers for the P99 evidence-ledger dry-run runtime."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class EvidenceLedgerDryRunError:
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
class EvidenceLedgerCandidateSummary:
    """A conservative summary of one evidence-ledger candidate input."""

    candidate_id: str
    path: str
    evidence_kind: str
    claim_kind: str
    source_family: str
    provenance_status: str
    review_status: str
    privacy_status: str
    public_safety_status: str
    rights_risk_status: str
    promotion_readiness: str
    valid: bool
    source_ref: str | None = None
    provenance_ref: str | None = None
    claim_summary: str | None = None
    warnings: tuple[str, ...] = ()
    errors: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "path": self.path,
            "evidence_kind": self.evidence_kind,
            "claim_kind": self.claim_kind,
            "source_family": self.source_family,
            "provenance_status": self.provenance_status,
            "review_status": self.review_status,
            "privacy_status": self.privacy_status,
            "public_safety_status": self.public_safety_status,
            "rights_risk_status": self.rights_risk_status,
            "promotion_readiness": self.promotion_readiness,
            "valid": self.valid,
            "source_ref": self.source_ref,
            "provenance_ref": self.provenance_ref,
            "claim_summary": self.claim_summary,
            "warnings": list(self.warnings),
            "errors": list(self.errors),
        }


@dataclass(frozen=True)
class EvidenceLedgerDryRunReport:
    """Deterministic dry-run report."""

    report_id: str
    input_roots: tuple[str, ...]
    candidates_seen: int
    candidates_valid: int
    candidates_invalid: int
    candidate_summaries: tuple[EvidenceLedgerCandidateSummary, ...]
    evidence_kinds: dict[str, int]
    claim_kinds: dict[str, int]
    source_families: dict[str, int]
    provenance_status_counts: dict[str, int]
    review_status_counts: dict[str, int]
    privacy_status_counts: dict[str, int]
    public_safety_status_counts: dict[str, int]
    rights_risk_status_counts: dict[str, int]
    promotion_readiness_counts: dict[str, int]
    mutation_summary: dict[str, bool]
    warnings: tuple[str, ...] = ()
    errors: tuple[EvidenceLedgerDryRunError, ...] = ()
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
            "evidence_kinds": dict(self.evidence_kinds),
            "claim_kinds": dict(self.claim_kinds),
            "source_families": dict(self.source_families),
            "provenance_status_counts": dict(self.provenance_status_counts),
            "review_status_counts": dict(self.review_status_counts),
            "privacy_status_counts": dict(self.privacy_status_counts),
            "public_safety_status_counts": dict(self.public_safety_status_counts),
            "rights_risk_status_counts": dict(self.rights_risk_status_counts),
            "promotion_readiness_counts": dict(self.promotion_readiness_counts),
            "mutation_summary": dict(self.mutation_summary),
            "warnings": list(self.warnings),
            "errors": [item.to_dict() for item in self.errors],
            "hard_booleans": dict(self.hard_booleans),
        }
