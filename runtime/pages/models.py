"""Dataclasses for the P103 local page dry-run runtime."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


@dataclass(frozen=True)
class PageDryRunInput:
    """Approved page dry-run input root."""

    root: str
    approved: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {"root": self.root, "approved": self.approved}


@dataclass(frozen=True)
class PageCandidateSummary:
    """Public-safe classification summary for one page example."""

    page_id: str
    path: str
    page_kind: str
    page_status: str
    lane: str
    privacy_status: str
    public_safety_status: str
    action_status: str
    conflict_gap_status: str
    title: str | None
    summary_text: str | None
    valid: bool
    warnings: tuple[str, ...] = ()
    errors: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "page_id": self.page_id,
            "path": self.path,
            "page_kind": self.page_kind,
            "page_status": self.page_status,
            "lane": self.lane,
            "privacy_status": self.privacy_status,
            "public_safety_status": self.public_safety_status,
            "action_status": self.action_status,
            "conflict_gap_status": self.conflict_gap_status,
            "title": self.title,
            "summary_text": self.summary_text,
            "valid": self.valid,
            "warnings": list(self.warnings),
            "errors": list(self.errors),
        }


@dataclass(frozen=True)
class PagePreviewOutput:
    """Deterministic text, HTML, and JSON previews for one page summary."""

    page_id: str
    page_kind: str
    text_preview: str
    html_preview: str
    json_preview: Mapping[str, Any]

    def to_dict(self) -> dict[str, Any]:
        return {
            "page_id": self.page_id,
            "page_kind": self.page_kind,
            "text_preview": self.text_preview,
            "html_preview": self.html_preview,
            "json_preview": dict(self.json_preview),
        }


@dataclass(frozen=True)
class PageDryRunErrorRecord:
    """Serializable bounded error record."""

    code: str
    message: str
    path: str | None = None

    def to_dict(self) -> dict[str, Any]:
        return {"code": self.code, "message": self.message, "path": self.path}


@dataclass(frozen=True)
class PageDryRunReport:
    """Full dry-run report."""

    report_id: str
    input_roots: tuple[str, ...]
    pages_seen: int
    pages_valid: int
    pages_invalid: int
    page_summaries: tuple[PageCandidateSummary, ...]
    page_kinds: Mapping[str, int]
    page_statuses: Mapping[str, int]
    lane_counts: Mapping[str, int]
    privacy_status_counts: Mapping[str, int]
    public_safety_status_counts: Mapping[str, int]
    action_status_counts: Mapping[str, int]
    conflict_gap_counts: Mapping[str, int]
    preview_outputs: tuple[PagePreviewOutput, ...]
    mutation_summary: Mapping[str, bool]
    warnings: tuple[str, ...]
    errors: tuple[PageDryRunErrorRecord, ...]
    hard_booleans: Mapping[str, bool]

    def to_dict(self) -> dict[str, Any]:
        return {
            "report_id": self.report_id,
            "mode": "local_dry_run",
            "input_roots": list(self.input_roots),
            "pages_seen": self.pages_seen,
            "pages_valid": self.pages_valid,
            "pages_invalid": self.pages_invalid,
            "page_summaries": [item.to_dict() for item in self.page_summaries],
            "page_kinds": dict(self.page_kinds),
            "page_statuses": dict(self.page_statuses),
            "lane_counts": dict(self.lane_counts),
            "privacy_status_counts": dict(self.privacy_status_counts),
            "public_safety_status_counts": dict(self.public_safety_status_counts),
            "action_status_counts": dict(self.action_status_counts),
            "conflict_gap_counts": dict(self.conflict_gap_counts),
            "preview_outputs": [item.to_dict() for item in self.preview_outputs],
            "mutation_summary": dict(self.mutation_summary),
            "warnings": list(self.warnings),
            "errors": [item.to_dict() for item in self.errors],
            "hard_booleans": dict(self.hard_booleans),
        }
