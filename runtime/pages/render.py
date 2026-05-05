"""Public-safe local preview renderers for P103 page dry-run summaries."""

from __future__ import annotations

import html
from typing import Any, Mapping

from runtime.pages.models import PageCandidateSummary
from runtime.pages.policy import HARD_BOOLEANS


def render_page_text(summary_or_record: PageCandidateSummary | Mapping[str, Any]) -> str:
    """Render an old-client-safe plain text preview."""

    summary = _summary_dict(summary_or_record)
    lines = [
        f"Title: {summary.get('title') or 'Untitled page'}",
        f"Page kind: {summary.get('page_kind', 'unknown')}",
        f"Status: {summary.get('page_status', 'unknown')}",
        f"Lane: {summary.get('lane', 'unknown')}",
        f"Action posture: {summary.get('action_status', 'unknown')}",
        f"Conflicts/gaps: {summary.get('conflict_gap_status', 'unknown')}",
        "",
        "Summary:",
        str(summary.get("summary_text") or "No public-safe summary provided."),
        "",
        "Safety:",
        "Dry-run preview only. Candidates are provisional; conflicts and gaps remain visible.",
        "Downloads, uploads, installs, execution, package managers, emulators, and VMs are disabled.",
        "No rights clearance, malware safety, installability, source trust, or truth claim is made.",
    ]
    return "\n".join(lines)


def render_page_html(summary_or_record: PageCandidateSummary | Mapping[str, Any]) -> str:
    """Render escaped, no-JS, no-external-asset HTML."""

    summary = _summary_dict(summary_or_record)
    title = html.escape(str(summary.get("title") or "Untitled page"))
    page_kind = html.escape(str(summary.get("page_kind", "unknown")))
    page_status = html.escape(str(summary.get("page_status", "unknown")))
    lane = html.escape(str(summary.get("lane", "unknown")))
    action_status = html.escape(str(summary.get("action_status", "unknown")))
    conflict_gap_status = html.escape(str(summary.get("conflict_gap_status", "unknown")))
    body = html.escape(str(summary.get("summary_text") or "No public-safe summary provided."))
    return (
        "<!doctype html>\n"
        "<html lang=\"en\">\n"
        "<head><meta charset=\"utf-8\"><title>"
        + title
        + "</title></head>\n"
        "<body>\n"
        "<main>\n"
        f"<h1>{title}</h1>\n"
        "<section aria-label=\"page summary\">\n"
        f"<p><strong>Page kind:</strong> {page_kind}</p>\n"
        f"<p><strong>Status:</strong> {page_status}</p>\n"
        f"<p><strong>Lane:</strong> {lane}</p>\n"
        f"<p><strong>Action posture:</strong> {action_status}</p>\n"
        f"<p><strong>Conflicts/gaps:</strong> {conflict_gap_status}</p>\n"
        f"<p>{body}</p>\n"
        "</section>\n"
        "<section aria-label=\"dry-run caveats\">\n"
        "<p>Dry-run preview only. Candidate, provisional, conflict, gap, and limitation labels remain visible.</p>\n"
        "<p>Downloads, uploads, installs, execution, package managers, emulators, and VMs are disabled.</p>\n"
        "<p>No rights clearance, malware safety, installability, source trust, or truth claim is made.</p>\n"
        "</section>\n"
        "</main>\n"
        "</body>\n"
        "</html>\n"
    )


def render_page_json(summary_or_record: PageCandidateSummary | Mapping[str, Any]) -> dict[str, Any]:
    """Render a deterministic public-safe JSON preview object."""

    summary = _summary_dict(summary_or_record)
    return {
        "preview_kind": "page_local_dry_run_preview",
        "page_id": summary.get("page_id", "unknown"),
        "page_kind": summary.get("page_kind", "unknown"),
        "page_status": summary.get("page_status", "unknown"),
        "lane": summary.get("lane", "unknown"),
        "title": summary.get("title"),
        "summary_text": summary.get("summary_text"),
        "privacy_status": summary.get("privacy_status", "unknown"),
        "public_safety_status": summary.get("public_safety_status", "unknown"),
        "action_status": summary.get("action_status", "unknown"),
        "conflict_gap_status": summary.get("conflict_gap_status", "unknown"),
        "candidate_or_provisional_labels_visible": True,
        "conflicts_and_gaps_visible": True,
        "risky_actions_disabled": True,
        "rights_clearance_claimed": False,
        "malware_safety_claimed": False,
        "installability_claimed": False,
        "hard_booleans": dict(HARD_BOOLEANS),
    }


def _summary_dict(summary_or_record: PageCandidateSummary | Mapping[str, Any]) -> dict[str, Any]:
    if isinstance(summary_or_record, PageCandidateSummary):
        return summary_or_record.to_dict()
    return dict(summary_or_record)
