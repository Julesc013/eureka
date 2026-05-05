"""Deterministic report assembly for source cache dry-run."""

from __future__ import annotations

import hashlib
import json
from typing import Iterable

from runtime.source_cache.models import (
    SourceCacheCandidateSummary,
    SourceCacheDryRunError,
    SourceCacheDryRunReport,
)
from runtime.source_cache.policy import HARD_BOOLEANS, MUTATION_SUMMARY


def count_by(items: Iterable[SourceCacheCandidateSummary], attr: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in items:
        value = str(getattr(item, attr))
        counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items()))


def build_report(
    *,
    input_roots: Iterable[str],
    candidates: Iterable[SourceCacheCandidateSummary],
    warnings: Iterable[str] = (),
    errors: Iterable[SourceCacheDryRunError] = (),
) -> SourceCacheDryRunReport:
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
    report_id = f"source-cache-dry-run-{hashlib.sha256(serial_basis.encode('utf-8')).hexdigest()[:16]}"
    valid = sum(1 for item in summaries if item.valid)
    invalid = len(summaries) - valid
    return SourceCacheDryRunReport(
        report_id=report_id,
        input_roots=roots,
        candidates_seen=len(summaries),
        candidates_valid=valid,
        candidates_invalid=invalid,
        candidate_summaries=summaries,
        source_families=count_by(summaries, "source_family"),
        record_kinds=count_by(summaries, "record_kind"),
        privacy_status_counts=count_by(summaries, "privacy_status"),
        public_safety_status_counts=count_by(summaries, "public_safety_status"),
        evidence_readiness_counts=count_by(summaries, "evidence_readiness"),
        policy_status_counts=count_by(summaries, "policy_status"),
        mutation_summary=dict(MUTATION_SUMMARY),
        warnings=tuple(sorted(set(warnings))),
        errors=tuple(errors),
        hard_booleans=dict(HARD_BOOLEANS),
    )


def report_to_json(report: SourceCacheDryRunReport) -> str:
    return json.dumps(report.to_dict(), indent=2, sort_keys=True) + "\n"
