"""Absence report helpers for the local reviewed public index."""

from __future__ import annotations

from .records import PublicIndexAbsenceReport


def build_absence_report(
    query: str,
    *,
    result_count: int,
    checked_sources: tuple[str, ...] = (),
) -> PublicIndexAbsenceReport:
    limitations = (
        "local reviewed index only",
        "absence does not prove no matching source exists",
        "absence does not inspect live sources",
    )
    return PublicIndexAbsenceReport(
        query=query,
        result_count=result_count,
        checked_sources=checked_sources,
        limitations=limitations,
    )
