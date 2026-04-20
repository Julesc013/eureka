from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
import json
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SOFTWARE_FIXTURE_PATH = (
    REPO_ROOT
    / "contracts"
    / "archive"
    / "fixtures"
    / "software"
    / "synthetic_resolution_fixture.json"
)


@dataclass(frozen=True)
class FixtureEntry:
    target_ref: str
    object_record: dict[str, Any]
    state_record: dict[str, Any]
    representation_record: dict[str, Any]
    access_path_record: dict[str, Any]


class FixtureCatalog:
    def __init__(self, entries: tuple[FixtureEntry, ...], source_path: Path) -> None:
        if not entries:
            raise ValueError("Fixture catalog requires at least one entry.")
        self._entries = entries
        self.source_path = source_path

    @property
    def entries(self) -> tuple[FixtureEntry, ...]:
        return self._entries

    @property
    def default_target_ref(self) -> str:
        return self._entries[0].target_ref

    def find_by_target_ref(self, target_ref: str) -> FixtureEntry | None:
        for entry in self._entries:
            if entry.target_ref == target_ref:
                return entry
        return None


def load_fixture_catalog(path: Path | None = None) -> FixtureCatalog:
    fixture_path = path or DEFAULT_SOFTWARE_FIXTURE_PATH
    with fixture_path.open("r", encoding="utf-8") as handle:
        document = json.load(handle)

    raw_entries = document.get("fixtures")
    if not isinstance(raw_entries, list):
        raise ValueError("Fixture catalog must define a top-level 'fixtures' list.")

    entries = tuple(_coerce_fixture_entry(raw_entry, index) for index, raw_entry in enumerate(raw_entries))
    return FixtureCatalog(entries=entries, source_path=fixture_path)


@lru_cache(maxsize=1)
def load_default_fixture_catalog() -> FixtureCatalog:
    return load_fixture_catalog(DEFAULT_SOFTWARE_FIXTURE_PATH)


def _coerce_fixture_entry(raw_entry: Any, index: int) -> FixtureEntry:
    if not isinstance(raw_entry, dict):
        raise ValueError(f"Fixture entry {index} must be an object.")

    return FixtureEntry(
        target_ref=_require_string(raw_entry.get("target_ref"), f"fixtures[{index}].target_ref"),
        object_record=_require_mapping(raw_entry.get("object"), f"fixtures[{index}].object"),
        state_record=_require_mapping(raw_entry.get("state"), f"fixtures[{index}].state"),
        representation_record=_require_mapping(
            raw_entry.get("representation"),
            f"fixtures[{index}].representation",
        ),
        access_path_record=_require_mapping(
            raw_entry.get("access_path"),
            f"fixtures[{index}].access_path",
        ),
    )


def _require_string(value: Any, field_name: str) -> str:
    if not isinstance(value, str) or not value:
        raise ValueError(f"{field_name} must be a non-empty string.")
    return value


def _require_mapping(value: Any, field_name: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise ValueError(f"{field_name} must be an object.")
    return dict(value)
