from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Mapping

from runtime.source_registry.source_capability import SourceCapabilityRecord
from runtime.source_registry.source_coverage import SourceCoverageRecord


class SourceRegistryError(Exception):
    """Base class for bounded source-registry runtime errors."""


class SourceInventoryNotFoundError(SourceRegistryError, FileNotFoundError):
    def __init__(self, inventory_dir: Path) -> None:
        self.inventory_dir = inventory_dir
        super().__init__(f"Source inventory directory '{inventory_dir}' was not found.")


class MalformedSourceRecordError(SourceRegistryError, ValueError):
    def __init__(self, source_path: Path, message: str) -> None:
        self.source_path = source_path
        super().__init__(f"{source_path}: {message}")


class MissingRequiredFieldError(MalformedSourceRecordError):
    def __init__(self, source_path: Path, field_name: str) -> None:
        self.field_name = field_name
        super().__init__(source_path, f"Missing required field '{field_name}'.")


class DuplicateSourceIdError(SourceRegistryError, ValueError):
    def __init__(self, source_id: str, first_path: Path, duplicate_path: Path) -> None:
        self.source_id = source_id
        self.first_path = first_path
        self.duplicate_path = duplicate_path
        super().__init__(
            f"Duplicate source_id '{source_id}' found in '{first_path}' and '{duplicate_path}'."
        )


class SourceRecordNotFoundError(SourceRegistryError, LookupError):
    def __init__(self, source_id: str) -> None:
        self.source_id = source_id
        super().__init__(f"Unknown source_id '{source_id}'.")


@dataclass(frozen=True)
class ConnectorRecord:
    label: str
    status: str
    entrypoint: str | None = None

    def to_dict(self) -> dict[str, str]:
        payload = {
            "label": self.label,
            "status": self.status,
        }
        if self.entrypoint is not None:
            payload["entrypoint"] = self.entrypoint
        return payload


@dataclass(frozen=True)
class LiveAccessRecord:
    mode: str
    notes: str | None = None

    def to_dict(self) -> dict[str, str]:
        payload = {"mode": self.mode}
        if self.notes is not None:
            payload["notes"] = self.notes
        return payload


@dataclass(frozen=True)
class ExtractionPolicyRecord:
    mode: str
    notes: str | None = None

    def to_dict(self) -> dict[str, str]:
        payload = {"mode": self.mode}
        if self.notes is not None:
            payload["notes"] = self.notes
        return payload


@dataclass(frozen=True)
class SourceRecord:
    source_id: str
    name: str
    source_family: str
    status: str
    roles: tuple[str, ...]
    surfaces: tuple[str, ...]
    trust_lane: str
    authority_class: str
    protocols: tuple[str, ...]
    object_types: tuple[str, ...]
    artifact_types: tuple[str, ...]
    identifier_types_emitted: tuple[str, ...]
    connector: ConnectorRecord
    fixture_paths: tuple[str, ...]
    live_access: LiveAccessRecord
    extraction_policy: ExtractionPolicyRecord
    rights_notes: str
    legal_posture: str
    freshness_model: str
    capabilities: SourceCapabilityRecord
    coverage: SourceCoverageRecord
    notes: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "source_id": self.source_id,
            "name": self.name,
            "source_family": self.source_family,
            "status": self.status,
            "roles": list(self.roles),
            "surfaces": list(self.surfaces),
            "trust_lane": self.trust_lane,
            "authority_class": self.authority_class,
            "protocols": list(self.protocols),
            "object_types": list(self.object_types),
            "artifact_types": list(self.artifact_types),
            "identifier_types_emitted": list(self.identifier_types_emitted),
            "connector": self.connector.to_dict(),
            "fixture_paths": list(self.fixture_paths),
            "live_access": self.live_access.to_dict(),
            "extraction_policy": self.extraction_policy.to_dict(),
            "rights_notes": self.rights_notes,
            "legal_posture": self.legal_posture,
            "freshness_model": self.freshness_model,
            "capabilities": self.capabilities.to_dict(),
            "coverage": self.coverage.to_dict(),
            "notes": self.notes,
        }

    @classmethod
    def from_mapping(cls, raw_record: Mapping[str, Any], *, source_path: Path) -> "SourceRecord":
        return cls(
            source_id=_require_non_empty_string(raw_record, "source_id", source_path),
            name=_require_non_empty_string(raw_record, "name", source_path),
            source_family=_require_non_empty_string(raw_record, "source_family", source_path),
            status=_require_non_empty_string(raw_record, "status", source_path),
            roles=_require_non_empty_string_tuple(raw_record, "roles", source_path),
            surfaces=_require_non_empty_string_tuple(raw_record, "surfaces", source_path),
            trust_lane=_require_non_empty_string(raw_record, "trust_lane", source_path),
            authority_class=_require_non_empty_string(raw_record, "authority_class", source_path),
            protocols=_require_non_empty_string_tuple(raw_record, "protocols", source_path),
            object_types=_require_non_empty_string_tuple(raw_record, "object_types", source_path),
            artifact_types=_require_non_empty_string_tuple(raw_record, "artifact_types", source_path),
            identifier_types_emitted=_require_non_empty_string_tuple(
                raw_record,
                "identifier_types_emitted",
                source_path,
            ),
            connector=_require_connector_record(raw_record, "connector", source_path),
            fixture_paths=_require_string_tuple(raw_record, "fixture_paths", source_path),
            live_access=_require_live_access_record(raw_record, "live_access", source_path),
            extraction_policy=_require_extraction_policy_record(
                raw_record,
                "extraction_policy",
                source_path,
            ),
            rights_notes=_require_string(raw_record, "rights_notes", source_path),
            legal_posture=_require_non_empty_string(raw_record, "legal_posture", source_path),
            freshness_model=_require_non_empty_string(raw_record, "freshness_model", source_path),
            capabilities=_require_capability_record(raw_record, "capabilities", source_path),
            coverage=_require_coverage_record(raw_record, "coverage", source_path),
            notes=_require_string(raw_record, "notes", source_path),
        )


def _require_value(raw_record: Mapping[str, Any], field_name: str, source_path: Path) -> Any:
    if field_name not in raw_record:
        raise MissingRequiredFieldError(source_path, field_name)
    return raw_record[field_name]


def _require_string(raw_record: Mapping[str, Any], field_name: str, source_path: Path) -> str:
    value = _require_value(raw_record, field_name, source_path)
    if not isinstance(value, str):
        raise MalformedSourceRecordError(source_path, f"Field '{field_name}' must be a string.")
    return value


def _require_non_empty_string(
    raw_record: Mapping[str, Any],
    field_name: str,
    source_path: Path,
) -> str:
    value = _require_string(raw_record, field_name, source_path)
    if not value:
        raise MalformedSourceRecordError(
            source_path,
            f"Field '{field_name}' must be a non-empty string.",
        )
    return value


def _require_string_tuple(
    raw_record: Mapping[str, Any],
    field_name: str,
    source_path: Path,
) -> tuple[str, ...]:
    value = _require_value(raw_record, field_name, source_path)
    if not isinstance(value, list):
        raise MalformedSourceRecordError(source_path, f"Field '{field_name}' must be a list.")
    items: list[str] = []
    for index, entry in enumerate(value):
        if not isinstance(entry, str):
            raise MalformedSourceRecordError(
                source_path,
                f"Field '{field_name}[{index}]' must be a string.",
            )
        items.append(entry)
    return tuple(items)


def _require_non_empty_string_tuple(
    raw_record: Mapping[str, Any],
    field_name: str,
    source_path: Path,
) -> tuple[str, ...]:
    items = _require_string_tuple(raw_record, field_name, source_path)
    if not items:
        raise MalformedSourceRecordError(source_path, f"Field '{field_name}' must not be empty.")
    for index, entry in enumerate(items):
        if not entry:
            raise MalformedSourceRecordError(
                source_path,
                f"Field '{field_name}[{index}]' must be a non-empty string.",
            )
    return items


def _require_nested_mapping(
    raw_record: Mapping[str, Any],
    field_name: str,
    source_path: Path,
) -> Mapping[str, Any]:
    value = _require_value(raw_record, field_name, source_path)
    if not isinstance(value, Mapping):
        raise MalformedSourceRecordError(source_path, f"Field '{field_name}' must be an object.")
    return value


def _require_nested_optional_string(
    raw_record: Mapping[str, Any],
    field_name: str,
    nested_field_name: str,
    source_path: Path,
) -> str | None:
    nested = _require_nested_mapping(raw_record, field_name, source_path)
    if nested_field_name not in nested:
        return None
    value = nested[nested_field_name]
    if not isinstance(value, str) or not value:
        raise MalformedSourceRecordError(
            source_path,
            f"Field '{field_name}.{nested_field_name}' must be a non-empty string when provided.",
        )
    return value


def _require_nested_non_empty_string(
    raw_record: Mapping[str, Any],
    field_name: str,
    nested_field_name: str,
    source_path: Path,
) -> str:
    nested = _require_nested_mapping(raw_record, field_name, source_path)
    if nested_field_name not in nested:
        raise MissingRequiredFieldError(source_path, f"{field_name}.{nested_field_name}")
    value = nested[nested_field_name]
    if not isinstance(value, str) or not value:
        raise MalformedSourceRecordError(
            source_path,
            f"Field '{field_name}.{nested_field_name}' must be a non-empty string.",
        )
    return value


def _require_connector_record(
    raw_record: Mapping[str, Any],
    field_name: str,
    source_path: Path,
) -> ConnectorRecord:
    return ConnectorRecord(
        label=_require_nested_non_empty_string(raw_record, field_name, "label", source_path),
        status=_require_nested_non_empty_string(raw_record, field_name, "status", source_path),
        entrypoint=_require_nested_optional_string(raw_record, field_name, "entrypoint", source_path),
    )


def _require_live_access_record(
    raw_record: Mapping[str, Any],
    field_name: str,
    source_path: Path,
) -> LiveAccessRecord:
    return LiveAccessRecord(
        mode=_require_nested_non_empty_string(raw_record, field_name, "mode", source_path),
        notes=_require_nested_optional_string(raw_record, field_name, "notes", source_path),
    )


def _require_extraction_policy_record(
    raw_record: Mapping[str, Any],
    field_name: str,
    source_path: Path,
) -> ExtractionPolicyRecord:
    return ExtractionPolicyRecord(
        mode=_require_nested_non_empty_string(raw_record, field_name, "mode", source_path),
        notes=_require_nested_optional_string(raw_record, field_name, "notes", source_path),
    )


def _require_capability_record(
    raw_record: Mapping[str, Any],
    field_name: str,
    source_path: Path,
) -> SourceCapabilityRecord:
    raw_capabilities = _require_nested_mapping(raw_record, field_name, source_path)
    try:
        return SourceCapabilityRecord.from_mapping(raw_capabilities, field_name=field_name)
    except ValueError as error:
        raise MalformedSourceRecordError(source_path, str(error)) from error


def _require_coverage_record(
    raw_record: Mapping[str, Any],
    field_name: str,
    source_path: Path,
) -> SourceCoverageRecord:
    raw_coverage = _require_nested_mapping(raw_record, field_name, source_path)
    try:
        return SourceCoverageRecord.from_mapping(raw_coverage, field_name=field_name)
    except ValueError as error:
        raise MalformedSourceRecordError(source_path, str(error)) from error
