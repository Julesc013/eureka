"""Deterministic report assembly for evidence-ledger dry-run."""

from __future__ import annotations

import hashlib
import json
from typing import Iterable

from runtime.evidence_ledger.models import (
    EvidenceLedgerCandidateSummary,
    EvidenceLedgerDryRunError,
    EvidenceLedgerDryRunReport,
)
from runtime.evidence_ledger.policy import HARD_BOOLEANS, MUTATION_SUMMARY


def count_by(items: Iterable[EvidenceLedgerCandidateSummary], attr: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in items:
        value = str(getattr(item, attr))
        counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items()))


def build_report(
    *,
    input_roots: Iterable[str],
    candidates: Iterable[EvidenceLedgerCandidateSummary],
    warnings: Iterable[str] = (),
    errors: Iterable[EvidenceLedgerDryRunError] = (),
) -> EvidenceLedgerDryRunReport:
    summaries = tuple(sorted(candidates, key=lambda item: (item.path, item.candidate_id)))
    roots = tuple(sorted(dict.fromkeys(input_roots)))
    serial_basis = json.dumps(
        {
            "input_roots": roots,
            "candidate_summaries": [item.to_dict() for item in summaries],
            "warnings": sorted(set(warnings)),
            "errors": [item.to_dict() for item in errors],
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    report_id = f"evidence-ledger-dry-run-{hashlib.sha256(serial_basis.encode('utf-8')).hexdigest()[:16]}"
    valid = sum(1 for item in summaries if item.valid)
    invalid = len(summaries) - valid
    return EvidenceLedgerDryRunReport(
        report_id=report_id,
        input_roots=roots,
        candidates_seen=len(summaries),
        candidates_valid=valid,
        candidates_invalid=invalid,
        candidate_summaries=summaries,
        evidence_kinds=count_by(summaries, "evidence_kind"),
        claim_kinds=count_by(summaries, "claim_kind"),
        source_families=count_by(summaries, "source_family"),
        provenance_status_counts=count_by(summaries, "provenance_status"),
        review_status_counts=count_by(summaries, "review_status"),
        privacy_status_counts=count_by(summaries, "privacy_status"),
        public_safety_status_counts=count_by(summaries, "public_safety_status"),
        rights_risk_status_counts=count_by(summaries, "rights_risk_status"),
        promotion_readiness_counts=count_by(summaries, "promotion_readiness"),
        mutation_summary=dict(MUTATION_SUMMARY),
        warnings=tuple(sorted(set(warnings))),
        errors=tuple(errors),
        hard_booleans=dict(HARD_BOOLEANS),
    )


def report_to_json(report: EvidenceLedgerDryRunReport) -> str:
    return json.dumps(report.to_dict(), indent=2, sort_keys=True) + "\n"
