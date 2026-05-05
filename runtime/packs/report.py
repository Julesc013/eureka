"""Deterministic report assembly for P104 pack import dry-run."""

from __future__ import annotations

import hashlib
import json
from typing import Iterable

from runtime.packs.models import PackCandidateSummary, PackImportDryRunErrorRecord, PackImportDryRunReport
from runtime.packs.policy import HARD_BOOLEANS, MUTATION_SUMMARY


def count_by(items: Iterable[PackCandidateSummary], attr: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in items:
        value = str(getattr(item, attr))
        counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items()))


def build_dry_run_effects(summaries: tuple[PackCandidateSummary, ...]) -> dict[str, object]:
    return {
        "accepted_records_created": False,
        "promotion_decisions_created": False,
        "authoritative_import_performed": False,
        "candidate_effects_only": True,
        "effect_pack_ids": [summary.pack_id for summary in summaries],
        "mutation_impact_counts": count_by(summaries, "mutation_impact"),
        "notes": [
            "Dry-run effects summarize candidate impact only.",
            "No quarantine, staging, source-cache, evidence-ledger, candidate-index, public-index, local-index, or master-index state was written.",
        ],
    }


def build_report(
    *,
    input_roots: Iterable[str],
    packs: Iterable[PackCandidateSummary],
    warnings: Iterable[str] = (),
    errors: Iterable[PackImportDryRunErrorRecord] = (),
) -> PackImportDryRunReport:
    summaries = tuple(sorted(packs, key=lambda item: (item.path, item.pack_id)))
    roots = tuple(sorted(dict.fromkeys(input_roots)))
    report_errors = tuple(errors)
    serial_basis = json.dumps(
        {
            "input_roots": roots,
            "pack_summaries": [item.to_dict() for item in summaries],
            "warnings": sorted(set(warnings)),
            "errors": [item.to_dict() for item in report_errors],
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    report_id = f"pack-import-dry-run-{hashlib.sha256(serial_basis.encode('utf-8')).hexdigest()[:16]}"
    valid = sum(1 for item in summaries if item.valid)
    invalid = len(summaries) - valid
    return PackImportDryRunReport(
        report_id=report_id,
        input_roots=roots,
        packs_seen=len(summaries),
        packs_valid=valid,
        packs_invalid=invalid,
        pack_summaries=summaries,
        pack_kinds=count_by(summaries, "pack_kind"),
        schema_versions=count_by(summaries, "schema_version"),
        validation_status_counts=count_by(summaries, "validation_status"),
        privacy_status_counts=count_by(summaries, "privacy_status"),
        public_safety_status_counts=count_by(summaries, "public_safety_status"),
        risk_status_counts=count_by(summaries, "risk_status"),
        mutation_impact_counts=count_by(summaries, "mutation_impact"),
        promotion_readiness_counts=count_by(summaries, "promotion_readiness"),
        dry_run_effects=build_dry_run_effects(summaries),
        mutation_summary=dict(MUTATION_SUMMARY),
        warnings=tuple(sorted(set(warnings))),
        errors=report_errors,
        hard_booleans=dict(HARD_BOOLEANS),
    )


def report_to_json(report: PackImportDryRunReport) -> str:
    return json.dumps(report.to_dict(), indent=2, sort_keys=True) + "\n"
