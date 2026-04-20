from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from runtime.engine.interfaces.ingest import SyntheticSourceRecord


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_SYNTHETIC_FIXTURE_PATH = (
    REPO_ROOT
    / "contracts"
    / "archive"
    / "fixtures"
    / "software"
    / "synthetic_resolution_fixture.json"
)


def load_synthetic_source_records(path: Path | None = None) -> tuple[SyntheticSourceRecord, ...]:
    fixture_path = path or DEFAULT_SYNTHETIC_FIXTURE_PATH
    with fixture_path.open("r", encoding="utf-8") as handle:
        document = json.load(handle)

    raw_entries = document.get("fixtures")
    if not isinstance(raw_entries, list):
        raise ValueError("Synthetic fixture source must define a top-level 'fixtures' list.")

    return tuple(_coerce_source_record(raw_entry, fixture_path, index) for index, raw_entry in enumerate(raw_entries))


def _coerce_source_record(raw_entry: Any, fixture_path: Path, index: int) -> SyntheticSourceRecord:
    if not isinstance(raw_entry, dict):
        raise ValueError(f"Fixture entry {index} must be an object.")

    target_ref = raw_entry.get("target_ref")
    if not isinstance(target_ref, str) or not target_ref:
        raise ValueError(f"fixtures[{index}].target_ref must be a non-empty string.")

    return SyntheticSourceRecord(
        target_ref=target_ref,
        source_name="synthetic_software_fixture",
        payload=dict(raw_entry),
        source_locator=fixture_path.relative_to(REPO_ROOT).as_posix(),
    )
