"""Presentation-safe view models for the local workbench."""

from dataclasses import dataclass
from typing import Any, Mapping, Sequence


LOCAL_ABSENCE_LIMITATION = "This is local current-index absence only, not global proof."


@dataclass(frozen=True)
class HomePageView:
    status: str
    instance_id: str
    instance_schema_version: str
    record_count: int
    warnings: tuple[str, ...]
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class SearchPageView:
    query: str
    result_count: int
    results: tuple[Mapping[str, Any], ...]
    warnings: tuple[str, ...]
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class ObjectPageView:
    record_id: str
    found: bool
    record: Mapping[str, Any]
    warnings: tuple[str, ...]
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class SourcePageView:
    source_id: str
    result_count: int
    records: tuple[Mapping[str, Any], ...]
    warnings: tuple[str, ...]
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class AbsencePageView:
    query: str
    result_count: int
    checked_sources: tuple[str, ...]
    warnings: tuple[str, ...]
    limitations: tuple[str, ...]


@dataclass(frozen=True)
class StatusPageView:
    instance_id: str
    instance_schema_version: str
    stores: tuple[Mapping[str, Any], ...]
    migration_needed: bool
    server_enabled: bool
    lan_enabled: bool
    deployment_performed: bool
    warnings: tuple[str, ...]
    limitations: tuple[str, ...]


def build_home_page_view(status: Mapping[str, Any]) -> HomePageView:
    runtime = _mapping(status.get("runtime"))
    public_index = _mapping(status.get("public_index"))
    return HomePageView(
        status=str(status.get("status", runtime.get("status", ""))),
        instance_id=str(runtime.get("instance_id", "")),
        instance_schema_version=str(runtime.get("instance_schema_version", "")),
        record_count=int(public_index.get("record_count", 0) or 0),
        warnings=_tuple(status.get("warnings")),
        limitations=_tuple(status.get("limitations")),
    )


def build_search_page_view(query: str, search_result: Mapping[str, Any]) -> SearchPageView:
    return SearchPageView(
        query=query,
        result_count=int(search_result.get("result_count", 0) or 0),
        results=tuple(_mapping(item) for item in _sequence(search_result.get("results"))),
        warnings=_tuple(search_result.get("warnings")),
        limitations=_tuple(search_result.get("limitations")),
    )


def build_object_page_view(record_id: str, record: Mapping[str, Any] | None) -> ObjectPageView:
    payload = _mapping(record)
    return ObjectPageView(
        record_id=record_id,
        found=bool(payload),
        record=payload,
        warnings=_tuple(payload.get("warnings")),
        limitations=_tuple(payload.get("limitations")),
    )


def build_source_page_view(source_id: str, records: Mapping[str, Any]) -> SourcePageView:
    return SourcePageView(
        source_id=source_id,
        result_count=int(records.get("result_count", 0) or 0),
        records=tuple(_mapping(item) for item in _sequence(records.get("records"))),
        warnings=_tuple(records.get("warnings")),
        limitations=_tuple(records.get("limitations")),
    )


def build_absence_page_view(query: str, absence_report: Mapping[str, Any]) -> AbsencePageView:
    report = _mapping(absence_report.get("absence", absence_report))
    limitations = _tuple(absence_report.get("limitations")) + _tuple(report.get("limitations")) + (LOCAL_ABSENCE_LIMITATION,)
    return AbsencePageView(
        query=query,
        result_count=int(report.get("result_count", 0) or 0),
        checked_sources=tuple(str(item) for item in _sequence(report.get("checked_sources"))),
        warnings=_tuple(absence_report.get("warnings")) + _tuple(report.get("warnings")),
        limitations=_unique(limitations),
    )


def build_status_page_view(status: Mapping[str, Any]) -> StatusPageView:
    runtime = _mapping(status.get("runtime"))
    stores = _mapping(runtime.get("stores"))
    return StatusPageView(
        instance_id=str(runtime.get("instance_id", "")),
        instance_schema_version=str(runtime.get("instance_schema_version", "")),
        stores=tuple(_store_rows(stores)),
        migration_needed=bool(runtime.get("migration_needed", False)),
        server_enabled=bool(runtime.get("server_enabled", False)),
        lan_enabled=bool(runtime.get("lan_enabled", False)),
        deployment_performed=bool(runtime.get("deployment_performed", False)),
        warnings=_tuple(status.get("warnings")),
        limitations=_tuple(status.get("limitations")),
    )


def _store_rows(stores: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    rows = []
    for store_id, payload in stores.items():
        item = _mapping(payload)
        rows.append(
            {
                "store": store_id,
                "opened": item.get("opened", ""),
                "integrity": item.get("integrity_status", ""),
                "schema": item.get("schema_version", ""),
            }
        )
    return rows


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _sequence(value: Any) -> Sequence[Any]:
    return value if isinstance(value, (list, tuple)) else ()


def _tuple(value: Any) -> tuple[str, ...]:
    return tuple(str(item) for item in _sequence(value))


def _unique(values: Sequence[str]) -> tuple[str, ...]:
    result: list[str] = []
    for value in values:
        if value and value not in result:
            result.append(value)
    return tuple(result)
