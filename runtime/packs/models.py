"""Dataclasses for the P104 local pack import dry-run runtime."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping


@dataclass(frozen=True)
class PackDryRunInput:
    """Approved pack dry-run input root."""

    root: str
    approved: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {"root": self.root, "approved": self.approved}


@dataclass(frozen=True)
class PackImportDryRunErrorRecord:
    """Serializable bounded error record."""

    code: str
    message: str
    path: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {"code": self.code, "message": self.message, "path": self.path}


@dataclass(frozen=True)
class PackCandidateSummary:
    """Conservative classification summary for one pack candidate."""

    pack_id: str
    path: str
    pack_kind: str
    schema_version: str
    validation_status: str
    privacy_status: str
    public_safety_status: str
    risk_status: str
    mutation_impact: str
    promotion_readiness: str
    valid: bool
    pack_version: str | None = None
    title: str | None = None
    validator_command: str | None = None
    validator_exit_code: int | None = None
    summary_text: str | None = None
    warnings: tuple[str, ...] = ()
    errors: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "pack_id": self.pack_id,
            "path": self.path,
            "pack_kind": self.pack_kind,
            "schema_version": self.schema_version,
            "validation_status": self.validation_status,
            "privacy_status": self.privacy_status,
            "public_safety_status": self.public_safety_status,
            "risk_status": self.risk_status,
            "mutation_impact": self.mutation_impact,
            "promotion_readiness": self.promotion_readiness,
            "valid": self.valid,
            "pack_version": self.pack_version,
            "title": self.title,
            "validator_command": self.validator_command,
            "validator_exit_code": self.validator_exit_code,
            "summary_text": self.summary_text,
            "warnings": list(self.warnings),
            "errors": list(self.errors),
        }


@dataclass(frozen=True)
class PackImportDryRunReport:
    """Deterministic local dry-run import report."""

    report_id: str
    input_roots: tuple[str, ...]
    packs_seen: int
    packs_valid: int
    packs_invalid: int
    pack_summaries: tuple[PackCandidateSummary, ...]
    pack_kinds: Mapping[str, int]
    schema_versions: Mapping[str, int]
    validation_status_counts: Mapping[str, int]
    privacy_status_counts: Mapping[str, int]
    public_safety_status_counts: Mapping[str, int]
    risk_status_counts: Mapping[str, int]
    mutation_impact_counts: Mapping[str, int]
    promotion_readiness_counts: Mapping[str, int]
    dry_run_effects: Mapping[str, Any]
    mutation_summary: Mapping[str, bool]
    warnings: tuple[str, ...] = ()
    errors: tuple[PackImportDryRunErrorRecord, ...] = ()
    hard_booleans: Mapping[str, bool] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "report_id": self.report_id,
            "mode": "local_dry_run",
            "input_roots": list(self.input_roots),
            "packs_seen": self.packs_seen,
            "packs_valid": self.packs_valid,
            "packs_invalid": self.packs_invalid,
            "pack_summaries": [item.to_dict() for item in self.pack_summaries],
            "pack_kinds": dict(self.pack_kinds),
            "schema_versions": dict(self.schema_versions),
            "validation_status_counts": dict(self.validation_status_counts),
            "privacy_status_counts": dict(self.privacy_status_counts),
            "public_safety_status_counts": dict(self.public_safety_status_counts),
            "risk_status_counts": dict(self.risk_status_counts),
            "mutation_impact_counts": dict(self.mutation_impact_counts),
            "promotion_readiness_counts": dict(self.promotion_readiness_counts),
            "dry_run_effects": dict(self.dry_run_effects),
            "mutation_summary": dict(self.mutation_summary),
            "warnings": list(self.warnings),
            "errors": [item.to_dict() for item in self.errors],
            "hard_booleans": dict(self.hard_booleans),
        }
