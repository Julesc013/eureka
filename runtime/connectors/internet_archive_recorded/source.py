from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any

from runtime.engine.interfaces.ingest import InternetArchiveRecordedSourceRecord


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_INTERNET_ARCHIVE_RECORDED_FIXTURE_PATH = (
    REPO_ROOT
    / "runtime"
    / "connectors"
    / "internet_archive_recorded"
    / "fixtures"
    / "internet_archive_items_fixture.json"
)


def load_internet_archive_recorded_source_records(
    path: Path | None = None,
) -> tuple[InternetArchiveRecordedSourceRecord, ...]:
    fixture_path = path or DEFAULT_INTERNET_ARCHIVE_RECORDED_FIXTURE_PATH
    with fixture_path.open("r", encoding="utf-8") as handle:
        document = json.load(handle)

    raw_entries = document.get("items")
    if not isinstance(raw_entries, list):
        raise ValueError("Internet Archive recorded fixture must define a top-level 'items' list.")

    return tuple(
        _coerce_source_record(raw_entry, fixture_path, index)
        for index, raw_entry in enumerate(raw_entries)
    )


def internet_archive_recorded_target_ref(identifier: str) -> str:
    normalized_identifier = identifier.strip()
    if not normalized_identifier:
        raise ValueError("identifier must be a non-empty string.")
    if not re.fullmatch(r"[A-Za-z0-9._-]+", normalized_identifier):
        raise ValueError("identifier must contain only letters, numbers, dots, underscores, or hyphens.")
    return f"internet-archive-recorded:{normalized_identifier}"


def _coerce_source_record(
    raw_entry: Any,
    fixture_path: Path,
    index: int,
) -> InternetArchiveRecordedSourceRecord:
    if not isinstance(raw_entry, dict):
        raise ValueError(f"items[{index}] must be an object.")
    item = raw_entry.get("item")
    if not isinstance(item, dict):
        raise ValueError(f"items[{index}].item must be an object.")
    identifier = item.get("identifier")
    if not isinstance(identifier, str) or not identifier:
        raise ValueError(f"items[{index}].item.identifier must be a non-empty string.")
    title = item.get("title")
    if not isinstance(title, str) or not title:
        raise ValueError(f"items[{index}].item.title must be a non-empty string.")
    files = item.get("files")
    if files is not None and not isinstance(files, list):
        raise ValueError(f"items[{index}].item.files must be a list when provided.")
    return InternetArchiveRecordedSourceRecord(
        target_ref=internet_archive_recorded_target_ref(identifier),
        source_name="internet_archive_recorded_fixture",
        payload=dict(raw_entry),
        source_locator=fixture_path.relative_to(REPO_ROOT).as_posix(),
    )
