from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class RankingFactor:
    factor_type: str
    direction: str
    category_value: str
    public_reason: str
    audit_reason: str
    evidence_refs: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "factor_type": self.factor_type,
            "direction": self.direction,
            "category_value": self.category_value,
            "public_reason": self.public_reason,
            "audit_reason": self.audit_reason,
            "evidence_refs": list(self.evidence_refs),
            "limitations": list(self.limitations),
        }


@dataclass(frozen=True)
class RankingResultCandidate:
    result_id: str
    title: str
    current_rank: int
    factors: tuple[RankingFactor, ...]
    policy_status: str = "rankable"
    warnings: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "result_id": self.result_id,
            "title": self.title,
            "current_rank": self.current_rank,
            "policy_status": self.policy_status,
            "warnings": list(self.warnings),
            "factors": [factor.to_dict() for factor in self.factors],
        }


@dataclass(frozen=True)
class RankingExplanationSummary:
    result_id: str
    user_visible_reason: str
    audit_reason: str
    caveats: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "result_id": self.result_id,
            "user_visible_reason": self.user_visible_reason,
            "audit_reason": self.audit_reason,
            "caveats": list(self.caveats),
        }


@dataclass(frozen=True)
class RankingDryRunResultSet:
    result_set_id: str
    current_order: tuple[str, ...]
    proposed_dry_run_order: tuple[str, ...]
    fallback_order: tuple[str, ...]
    fallback_used: bool
    result_summaries: tuple[RankingResultCandidate, ...]
    explanation_summaries: tuple[RankingExplanationSummary, ...]
    warnings: tuple[str, ...] = ()
    errors: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "result_set_id": self.result_set_id,
            "current_order": list(self.current_order),
            "proposed_dry_run_order": list(self.proposed_dry_run_order),
            "fallback_order": list(self.fallback_order),
            "fallback_used": self.fallback_used,
            "result_summaries": [summary.to_dict() for summary in self.result_summaries],
            "explanation_summaries": [summary.to_dict() for summary in self.explanation_summaries],
            "warnings": list(self.warnings),
            "errors": list(self.errors),
        }


@dataclass(frozen=True)
class RankingDryRunReport:
    report_id: str
    mode: str
    input_roots: tuple[str, ...]
    result_sets_seen: int
    result_sets_valid: int
    result_sets_invalid: int
    result_summaries: tuple[dict[str, Any], ...]
    current_order: dict[str, list[str]]
    proposed_dry_run_order: dict[str, list[str]]
    fallback_order: dict[str, list[str]]
    ranking_factors: tuple[dict[str, Any], ...]
    factor_summary: dict[str, int]
    explanation_summaries: tuple[dict[str, Any], ...]
    conflict_gap_visibility_summary: dict[str, int]
    privacy_status_counts: dict[str, int]
    public_safety_status_counts: dict[str, int]
    eval_gate_summary: dict[str, Any]
    warnings: tuple[str, ...] = ()
    errors: tuple[str, ...] = ()
    hard_booleans: dict[str, bool] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "report_id": self.report_id,
            "mode": self.mode,
            "input_roots": list(self.input_roots),
            "result_sets_seen": self.result_sets_seen,
            "result_sets_valid": self.result_sets_valid,
            "result_sets_invalid": self.result_sets_invalid,
            "result_summaries": list(self.result_summaries),
            "current_order": self.current_order,
            "proposed_dry_run_order": self.proposed_dry_run_order,
            "fallback_order": self.fallback_order,
            "ranking_factors": list(self.ranking_factors),
            "factor_summary": self.factor_summary,
            "explanation_summaries": list(self.explanation_summaries),
            "conflict_gap_visibility_summary": self.conflict_gap_visibility_summary,
            "privacy_status_counts": self.privacy_status_counts,
            "public_safety_status_counts": self.public_safety_status_counts,
            "eval_gate_summary": self.eval_gate_summary,
            "warnings": list(self.warnings),
            "errors": list(self.errors),
            "hard_booleans": dict(self.hard_booleans),
        }

