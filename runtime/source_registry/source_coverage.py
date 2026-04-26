from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


COVERAGE_DEPTHS = (
    "source_known",
    "catalog_indexed",
    "metadata_indexed",
    "representation_indexed",
    "content_or_member_indexed",
    "action_indexed",
)

COVERAGE_DEPTH_RANKS = {
    coverage_depth: index for index, coverage_depth in enumerate(COVERAGE_DEPTHS)
}

SOURCE_COVERAGE_FIELDS = (
    "coverage_depth",
    "coverage_status",
    "indexed_scopes",
    "connector_mode",
    "last_fixture_update",
    "coverage_notes",
    "current_limitations",
    "next_coverage_step",
)


@dataclass(frozen=True)
class SourceCoverageRecord:
    coverage_depth: str
    coverage_status: str
    indexed_scopes: tuple[str, ...]
    connector_mode: str
    last_fixture_update: str
    coverage_notes: str
    current_limitations: tuple[str, ...]
    next_coverage_step: str

    @classmethod
    def from_mapping(
        cls,
        raw_coverage: Mapping[str, Any],
        *,
        field_name: str = "coverage",
    ) -> "SourceCoverageRecord":
        if not isinstance(raw_coverage, Mapping):
            raise ValueError(f"Field '{field_name}' must be an object.")
        unknown_fields = sorted(set(raw_coverage) - set(SOURCE_COVERAGE_FIELDS))
        if unknown_fields:
            joined_fields = ", ".join(unknown_fields)
            raise ValueError(f"Field '{field_name}' has unknown coverage keys: {joined_fields}.")
        coverage_depth = _require_non_empty_string(raw_coverage, field_name, "coverage_depth")
        if coverage_depth not in COVERAGE_DEPTH_RANKS:
            allowed = ", ".join(COVERAGE_DEPTHS)
            raise ValueError(
                f"Field '{field_name}.coverage_depth' must be one of: {allowed}."
            )
        return cls(
            coverage_depth=coverage_depth,
            coverage_status=_require_non_empty_string(
                raw_coverage,
                field_name,
                "coverage_status",
            ),
            indexed_scopes=_require_string_tuple(
                raw_coverage,
                field_name,
                "indexed_scopes",
            ),
            connector_mode=_require_non_empty_string(raw_coverage, field_name, "connector_mode"),
            last_fixture_update=_require_non_empty_string(
                raw_coverage,
                field_name,
                "last_fixture_update",
            ),
            coverage_notes=_require_string(raw_coverage, field_name, "coverage_notes"),
            current_limitations=_require_string_tuple(
                raw_coverage,
                field_name,
                "current_limitations",
            ),
            next_coverage_step=_require_string(raw_coverage, field_name, "next_coverage_step"),
        )

    @property
    def coverage_depth_rank(self) -> int:
        return COVERAGE_DEPTH_RANKS[self.coverage_depth]

    def to_dict(self) -> dict[str, Any]:
        return {
            "coverage_depth": self.coverage_depth,
            "coverage_status": self.coverage_status,
            "indexed_scopes": list(self.indexed_scopes),
            "connector_mode": self.connector_mode,
            "last_fixture_update": self.last_fixture_update,
            "coverage_notes": self.coverage_notes,
            "current_limitations": list(self.current_limitations),
            "next_coverage_step": self.next_coverage_step,
        }


def _require_value(
    raw_mapping: Mapping[str, Any],
    parent_field_name: str,
    field_name: str,
) -> Any:
    if field_name not in raw_mapping:
        raise ValueError(f"Missing required field '{parent_field_name}.{field_name}'.")
    return raw_mapping[field_name]


def _require_string(
    raw_mapping: Mapping[str, Any],
    parent_field_name: str,
    field_name: str,
) -> str:
    value = _require_value(raw_mapping, parent_field_name, field_name)
    if not isinstance(value, str):
        raise ValueError(f"Field '{parent_field_name}.{field_name}' must be a string.")
    return value


def _require_non_empty_string(
    raw_mapping: Mapping[str, Any],
    parent_field_name: str,
    field_name: str,
) -> str:
    value = _require_string(raw_mapping, parent_field_name, field_name)
    if not value:
        raise ValueError(
            f"Field '{parent_field_name}.{field_name}' must be a non-empty string."
        )
    return value


def _require_string_tuple(
    raw_mapping: Mapping[str, Any],
    parent_field_name: str,
    field_name: str,
) -> tuple[str, ...]:
    value = _require_value(raw_mapping, parent_field_name, field_name)
    if not isinstance(value, list):
        raise ValueError(f"Field '{parent_field_name}.{field_name}' must be a list.")
    items: list[str] = []
    for index, entry in enumerate(value):
        if not isinstance(entry, str):
            raise ValueError(
                f"Field '{parent_field_name}.{field_name}[{index}]' must be a string."
            )
        items.append(entry)
    return tuple(items)
