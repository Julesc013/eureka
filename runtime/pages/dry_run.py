"""Local dry-run loading, validation, classification, and rendering for page examples."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Iterable, Mapping

from runtime.pages.models import PageCandidateSummary, PageDryRunErrorRecord
from runtime.pages.policy import (
    ACTION_STATUSES,
    CONFLICT_GAP_STATUSES,
    PAGE_DRY_RUN_EXAMPLES_ROOT,
    PAGE_STATUSES,
    ensure_approved_input_root,
    normalize_action_status,
    normalize_lane,
    normalize_page_kind,
    normalize_privacy,
    normalize_public_safety,
    normalize_status,
    repo_relative,
    scan_page_policy,
)
from runtime.pages.report import build_report


PAGE_FILENAMES = ("PAGE_RECORD.json", "OBJECT_PAGE.json", "SOURCE_PAGE.json", "COMPARISON_PAGE.json")


def load_page(path: Path) -> dict[str, Any]:
    """Load one page JSON object from an approved example path."""

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        raise ValueError(f"{path} does not parse as JSON: {exc}") from exc
    if not isinstance(payload, dict):
        raise ValueError(f"{path} must contain a JSON object")
    return payload


def discover_pages(root: Path) -> list[Path]:
    """Find page JSON files under a root deterministically."""

    if root.is_file():
        return [root] if root.name in PAGE_FILENAMES else []
    if not root.exists():
        return []
    found: list[Path] = []
    for filename in PAGE_FILENAMES:
        found.extend(path for path in root.rglob(filename) if path.is_file())
    return sorted(set(found), key=lambda item: item.as_posix())


def validate_page_shape(record: Mapping[str, Any]) -> tuple[list[str], list[str]]:
    """Validate local dry-run shape without accepting page records as truth."""

    errors: list[str] = []
    warnings: list[str] = []
    page_kind = normalize_page_kind(record)
    if page_kind == "unknown":
        errors.append("page kind is unsupported or unknown")
    if not _title(record):
        errors.append("page title is required")
    page_status = _page_status(record)
    if page_status not in PAGE_STATUSES:
        errors.append("page status is unsupported or unknown")
    action_status = _action_status(record)
    if action_status not in ACTION_STATUSES:
        errors.append("action status is unsupported or unknown")
    conflict_gap_status = _conflict_gap_status(record)
    if conflict_gap_status not in CONFLICT_GAP_STATUSES:
        errors.append("conflict/gap status is unsupported or unknown")
    errors.extend(scan_page_policy(record))
    if page_status == "unknown":
        warnings.append("page status was classified unknown")
    return sorted(set(errors)), sorted(set(warnings))


def classify_page(record: Mapping[str, Any], *, path: Path | None = None) -> PageCandidateSummary:
    """Classify a page record conservatively."""

    errors, warnings = validate_page_shape(record)
    page_kind = normalize_page_kind(record)
    page_status = _page_status(record)
    lane = _lane(record)
    privacy_status = _privacy_status(record)
    public_safety_status = _public_safety_status(record)
    action_status = _action_status(record)
    conflict_gap_status = _conflict_gap_status(record)
    page_id = _page_id(record, page_kind)
    return PageCandidateSummary(
        page_id=page_id,
        path=repo_relative(path) if path else "",
        page_kind=page_kind,
        page_status=page_status,
        lane=lane,
        privacy_status=privacy_status,
        public_safety_status=public_safety_status,
        action_status=action_status,
        conflict_gap_status=conflict_gap_status,
        title=_title(record),
        summary_text=_summary(record),
        valid=not errors,
        warnings=tuple(warnings),
        errors=tuple(errors),
    )


def run_page_dry_run(
    roots: Iterable[Path] | None = None,
    strict: bool = False,
    *,
    render: bool = False,
    enforce_approved_roots: bool = False,
    allow_temp_roots: bool = False,
):
    """Run a local dry-run over approved page example roots."""

    input_roots = tuple(Path(root) for root in (roots or (PAGE_DRY_RUN_EXAMPLES_ROOT,)))
    summaries: list[PageCandidateSummary] = []
    report_errors: list[PageDryRunErrorRecord] = []
    warnings: list[str] = []
    for root in input_roots:
        try:
            checked_root = ensure_approved_input_root(root, allow_temp=allow_temp_roots) if enforce_approved_roots else root.resolve()
        except Exception as exc:
            report_errors.append(PageDryRunErrorRecord("input_root_rejected", str(exc), str(root)))
            continue
        page_paths = discover_pages(checked_root)
        if not page_paths:
            warnings.append(f"no page dry-run records found under {repo_relative(checked_root)}")
        for page_path in page_paths:
            try:
                record = load_page(page_path)
                summaries.append(classify_page(record, path=page_path))
            except Exception as exc:
                report_errors.append(PageDryRunErrorRecord("page_load_failed", str(exc), repo_relative(page_path)))
    if strict and not summaries:
        report_errors.append(PageDryRunErrorRecord("strict_no_pages", "strict mode requires at least one page record"))
    return build_report(
        input_roots=(repo_relative(root) for root in input_roots),
        pages=summaries,
        warnings=warnings,
        errors=report_errors,
        render_previews=render,
    )


def _page_id(record: Mapping[str, Any], page_kind: str) -> str:
    for key in ("page_id", "object_page_id", "source_page_id", "comparison_page_id"):
        value = record.get(key)
        if isinstance(value, str) and value:
            return value
    return f"unknown-{page_kind}"


def _page_status(record: Mapping[str, Any]) -> str:
    for key in ("page_status", "status"):
        status = normalize_status(record.get(key))
        if status != "unknown":
            return status
    for key in ("object_status", "source_status", "comparison_type"):
        value = record.get(key)
        if isinstance(value, Mapping):
            for nested_key in ("verification_status", "status_class", "type"):
                status = normalize_status(value.get(nested_key))
                if status != "unknown":
                    return status
    if _conflict_gap_status(record) in {"conflict_present", "conflict_and_gap_present"}:
        return "conflicted"
    return "unknown"


def _lane(record: Mapping[str, Any]) -> str:
    for value in (
        record.get("lane"),
        _nested(record, "object_status", "page_lane"),
        _nested(record, "result_card_projection", "result_lane"),
        _nested(record, "source_identity", "source_family"),
    ):
        lane = normalize_lane(value)
        if lane != "unknown":
            return lane
    return "unknown"


def _privacy_status(record: Mapping[str, Any]) -> str:
    for value in (
        record.get("privacy_status"),
        _nested(record, "privacy", "privacy_classification"),
        _nested(record, "privacy", "publishable"),
    ):
        status = normalize_privacy(value)
        if status != "unknown":
            return status
        if value is True:
            return "public_safe"
    return "unknown"


def _public_safety_status(record: Mapping[str, Any]) -> str:
    for value in (
        record.get("public_safety_status"),
        _nested(record, "privacy", "public_aggregate_allowed"),
        _nested(record, "privacy", "publishable"),
    ):
        status = normalize_public_safety(value)
        if status != "unknown":
            return status
    return "unknown"


def _action_status(record: Mapping[str, Any]) -> str:
    errors = scan_page_policy(record)
    if any("unsafe action" in error for error in errors):
        return "unsafe_action_claim_detected"
    explicit = normalize_action_status(record.get("action_status"))
    if explicit != "unknown":
        return explicit
    if _has_disabled_actions(record):
        return "risky_actions_disabled"
    allowed = list(_allowed_action_strings(record))
    if allowed and all("cite" in item.casefold() for item in allowed):
        return "cite_only"
    if allowed and all("compare" in item.casefold() for item in allowed):
        return "compare_only"
    if allowed:
        return "inspect_only"
    return "unknown"


def _conflict_gap_status(record: Mapping[str, Any]) -> str:
    conflict = _has_conflicts(record)
    gap = _has_gaps(record)
    if conflict and gap:
        return "conflict_and_gap_present"
    if conflict:
        return "conflict_present"
    if gap:
        return "gap_present"
    return "no_known_conflict_or_gap"


def _has_conflicts(record: Mapping[str, Any]) -> bool:
    for value in (
        record.get("conflicts"),
        _nested(record, "conflicts_and_disagreements", "conflicts"),
        _nested(record, "identity_comparison", "identity_conflicts"),
    ):
        if _non_empty(value):
            return True
    status = str(record.get("status", "")).casefold()
    return "conflict" in status


def _has_gaps(record: Mapping[str, Any]) -> bool:
    for value in (
        record.get("gaps"),
        _nested(record, "absence_near_misses_gaps", "gaps"),
        _nested(record, "limitations_and_gaps", "gaps"),
        _nested(record, "absence_near_miss_gap_comparison", "gaps_compared"),
        _nested(record, "coverage", "source_gap_types"),
    ):
        if _non_empty(value):
            return True
    return False


def _has_disabled_actions(record: Mapping[str, Any]) -> bool:
    for key, value in _iter_mapping_items(record):
        if key == "disabled_actions" and _non_empty(value):
            return True
    return False


def _allowed_action_strings(record: Mapping[str, Any]) -> Iterable[str]:
    for key, value in _iter_mapping_items(record):
        if key in {"allowed_actions", "allowed_capabilities"}:
            yield from _iter_strings(value)


def _iter_mapping_items(value: Any) -> Iterable[tuple[str, Any]]:
    if isinstance(value, Mapping):
        for key, nested in value.items():
            yield str(key), nested
            yield from _iter_mapping_items(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from _iter_mapping_items(nested)


def _iter_strings(value: Any) -> Iterable[str]:
    if isinstance(value, str):
        yield value
    elif isinstance(value, Mapping):
        for nested in value.values():
            yield from _iter_strings(nested)
    elif isinstance(value, list):
        for nested in value:
            yield from _iter_strings(nested)


def _nested(record: Mapping[str, Any], *keys: str) -> Any:
    current: Any = record
    for key in keys:
        if not isinstance(current, Mapping):
            return None
        current = current.get(key)
    return current


def _non_empty(value: Any) -> bool:
    return isinstance(value, (list, tuple, set, dict)) and bool(value)


def _text(value: Any) -> str | None:
    return value if isinstance(value, str) and value else None


def _title(record: Mapping[str, Any]) -> str | None:
    for value in (
        record.get("title"),
        _nested(record, "object_identity", "canonical_label"),
        _nested(record, "source_identity", "canonical_label"),
        _nested(record, "comparison_identity", "canonical_label"),
    ):
        text = _text(value)
        if text:
            return text
    return None


def _summary(record: Mapping[str, Any]) -> str | None:
    for value in (
        record.get("summary"),
        _nested(record, "comparison_identity", "comparison_basis"),
        _nested(record, "source_evidence_provenance_comparison", "evidence_strength_summary"),
        _nested(record, "coverage", "coverage_depth"),
    ):
        text = _text(value)
        if text:
            return text
    return None
