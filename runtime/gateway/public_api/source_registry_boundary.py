from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from runtime.gateway.public_api.resolution_boundary import PublicApiResponse
from runtime.source_registry import SourceRecordNotFoundError, SourceRegistry


@dataclass(frozen=True)
class SourceCatalogRequest:
    status: str | None = None
    source_family: str | None = None
    role: str | None = None
    surface: str | None = None
    coverage_depth: str | None = None
    capability: str | None = None
    connector_mode: str | None = None

    @classmethod
    def from_parts(
        cls,
        *,
        status: str | None = None,
        source_family: str | None = None,
        role: str | None = None,
        surface: str | None = None,
        coverage_depth: str | None = None,
        capability: str | None = None,
        connector_mode: str | None = None,
    ) -> "SourceCatalogRequest":
        return cls(
            status=_normalize_optional_filter(status),
            source_family=_normalize_optional_filter(source_family),
            role=_normalize_optional_filter(role),
            surface=_normalize_optional_filter(surface),
            coverage_depth=_normalize_optional_filter(coverage_depth),
            capability=_normalize_optional_filter(capability),
            connector_mode=_normalize_optional_filter(connector_mode),
        )


@dataclass(frozen=True)
class SourceReadRequest:
    source_id: str

    @classmethod
    def from_parts(cls, source_id: str) -> "SourceReadRequest":
        normalized_source_id = source_id.strip()
        if not normalized_source_id:
            raise ValueError("source_id must be a non-empty string.")
        return cls(source_id=normalized_source_id)


class SourceRegistryPublicApi:
    def __init__(self, registry: SourceRegistry) -> None:
        self._registry = registry

    def list_sources(self, request: SourceCatalogRequest) -> PublicApiResponse:
        records = self._registry.list_records(
            status=request.status,
            source_family=request.source_family,
            role=request.role,
            surface=request.surface,
            coverage_depth=request.coverage_depth,
            capability=request.capability,
            connector_mode=request.connector_mode,
        )
        return PublicApiResponse(
            status_code=200,
            body=source_registry_to_public_envelope(
                records,
                applied_filters={
                    "status": request.status,
                    "family": request.source_family,
                    "role": request.role,
                    "surface": request.surface,
                    "coverage_depth": request.coverage_depth,
                    "capability": request.capability,
                    "connector_mode": request.connector_mode,
                },
            ),
        )

    def get_source(self, request: SourceReadRequest) -> PublicApiResponse:
        try:
            record = self._registry.get_record(request.source_id)
        except SourceRecordNotFoundError:
            return PublicApiResponse(
                status_code=404,
                body=source_registry_not_found_envelope(request.source_id),
            )
        return PublicApiResponse(
            status_code=200,
            body=source_registry_to_public_envelope(
                (record,),
                selected_source_id=record.source_id,
            ),
        )


def source_registry_to_public_envelope(
    records,
    *,
    applied_filters: dict[str, str | None] | None = None,
    selected_source_id: str | None = None,
) -> dict[str, Any]:
    envelope: dict[str, Any] = {
        "status": "available" if selected_source_id is not None else "listed",
        "source_count": len(records),
        "sources": [source_record_to_public_entry(record) for record in records],
    }
    normalized_filters = {
        key: value for key, value in (applied_filters or {}).items() if value is not None
    }
    if normalized_filters:
        envelope["applied_filters"] = normalized_filters
    if selected_source_id is not None:
        envelope["selected_source_id"] = selected_source_id
    return envelope


def source_registry_not_found_envelope(source_id: str) -> dict[str, Any]:
    return {
        "status": "blocked",
        "source_count": 0,
        "selected_source_id": source_id,
        "sources": [],
        "notices": [
            {
                "code": "source_id_not_found",
                "severity": "warning",
                "message": f"Unknown source_id '{source_id}'.",
            }
        ],
    }


def source_record_to_public_entry(record) -> dict[str, Any]:
    return {
        "source_id": record.source_id,
        "name": record.name,
        "source_family": record.source_family,
        "status": record.status,
        "status_summary": _status_summary(record),
        "roles": list(record.roles),
        "surfaces": list(record.surfaces),
        "trust_lane": record.trust_lane,
        "authority_class": record.authority_class,
        "object_types": list(record.object_types),
        "artifact_types": list(record.artifact_types),
        "identifier_types_emitted": list(record.identifier_types_emitted),
        "connector": {
            "label": record.connector.label,
            "status": record.connector.status,
        },
        "capabilities": record.capabilities.to_dict(),
        "capabilities_summary": list(record.capabilities.enabled_capabilities()),
        "coverage": record.coverage.to_dict(),
        "coverage_depth": record.coverage.coverage_depth,
        "coverage_status": record.coverage.coverage_status,
        "connector_mode": record.coverage.connector_mode,
        "indexed_scopes": list(record.coverage.indexed_scopes),
        "current_limitations": list(record.coverage.current_limitations),
        "next_coverage_step": record.coverage.next_coverage_step,
        "placeholder_warning": _placeholder_warning(record),
        "live_access_mode": record.live_access.mode,
        "extraction_mode": record.extraction_policy.mode,
        "legal_posture": record.legal_posture,
        "freshness_model": record.freshness_model,
        "rights_notes": record.rights_notes,
        "notes": record.notes,
    }


def _normalize_optional_filter(value: str | None) -> str | None:
    if value is None:
        return None
    normalized_value = value.strip()
    return normalized_value or None


def _status_summary(record) -> str:
    if record.status == "active_fixture":
        return "Active fixture-backed source record."
    if record.status == "active_recorded_fixture":
        return "Active recorded-fixture source record. Live source access remains separate."
    if record.status == "placeholder":
        return "Placeholder record only. No runtime connector is implemented yet."
    if record.status == "future":
        return "Future source record only. Runtime behavior remains deferred."
    if record.status == "local_private_future":
        return "Future local/private source record only. Runtime behavior remains deferred."
    if record.status == "live_deferred":
        return "Registered source record with live access deferred."
    return "Disabled source record."


def _placeholder_warning(record) -> str:
    if record.status == "placeholder":
        return "Placeholder only; no connector, fixture coverage, or live access is implemented."
    if record.status in {"future", "local_private_future"}:
        return "Future-only source; no runtime connector is implemented."
    if record.connector.status in {"unimplemented", "deferred"}:
        return "Connector is not implemented for current runtime behavior."
    return ""
