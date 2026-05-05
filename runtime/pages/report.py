"""Deterministic report assembly for the P103 page dry-run runtime."""

from __future__ import annotations

import hashlib
import json
from typing import Iterable

from runtime.pages.models import (
    PageCandidateSummary,
    PageDryRunErrorRecord,
    PageDryRunReport,
    PagePreviewOutput,
)
from runtime.pages.policy import HARD_BOOLEANS, MUTATION_SUMMARY
from runtime.pages.render import render_page_html, render_page_json, render_page_text


def count_by(items: Iterable[PageCandidateSummary], attr: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for item in items:
        value = str(getattr(item, attr))
        counts[value] = counts.get(value, 0) + 1
    return dict(sorted(counts.items()))


def build_preview(summary: PageCandidateSummary) -> PagePreviewOutput:
    return PagePreviewOutput(
        page_id=summary.page_id,
        page_kind=summary.page_kind,
        text_preview=render_page_text(summary),
        html_preview=render_page_html(summary),
        json_preview=render_page_json(summary),
    )


def build_report(
    *,
    input_roots: Iterable[str],
    pages: Iterable[PageCandidateSummary],
    warnings: Iterable[str] = (),
    errors: Iterable[PageDryRunErrorRecord] = (),
    render_previews: bool = False,
) -> PageDryRunReport:
    summaries = tuple(sorted(pages, key=lambda item: (item.path, item.page_id)))
    roots = tuple(sorted(dict.fromkeys(input_roots)))
    previews = tuple(build_preview(summary) for summary in summaries if render_previews and summary.valid)
    serial_basis = json.dumps(
        {
            "input_roots": roots,
            "page_summaries": [item.to_dict() for item in summaries],
            "preview_outputs": [item.to_dict() for item in previews],
            "warnings": sorted(set(warnings)),
            "errors": [item.to_dict() for item in errors],
        },
        sort_keys=True,
        separators=(",", ":"),
    )
    report_id = f"page-dry-run-{hashlib.sha256(serial_basis.encode('utf-8')).hexdigest()[:16]}"
    valid = sum(1 for item in summaries if item.valid)
    invalid = len(summaries) - valid
    return PageDryRunReport(
        report_id=report_id,
        input_roots=roots,
        pages_seen=len(summaries),
        pages_valid=valid,
        pages_invalid=invalid,
        page_summaries=summaries,
        page_kinds=count_by(summaries, "page_kind"),
        page_statuses=count_by(summaries, "page_status"),
        lane_counts=count_by(summaries, "lane"),
        privacy_status_counts=count_by(summaries, "privacy_status"),
        public_safety_status_counts=count_by(summaries, "public_safety_status"),
        action_status_counts=count_by(summaries, "action_status"),
        conflict_gap_counts=count_by(summaries, "conflict_gap_status"),
        preview_outputs=previews,
        mutation_summary=dict(MUTATION_SUMMARY),
        warnings=tuple(sorted(set(warnings))),
        errors=tuple(errors),
        hard_booleans=dict(HARD_BOOLEANS),
    )


def report_to_json(report: PageDryRunReport) -> str:
    return json.dumps(report.to_dict(), indent=2, sort_keys=True) + "\n"
