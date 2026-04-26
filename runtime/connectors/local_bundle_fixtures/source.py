from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any

from runtime.engine.interfaces.ingest import LocalBundleSourceRecord


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_LOCAL_BUNDLE_FIXTURE_PATH = (
    REPO_ROOT
    / "runtime"
    / "connectors"
    / "local_bundle_fixtures"
    / "fixtures"
    / "local_bundle_fixtures.json"
)


def load_local_bundle_source_records(
    path: Path | None = None,
) -> tuple[LocalBundleSourceRecord, ...]:
    fixture_path = path or DEFAULT_LOCAL_BUNDLE_FIXTURE_PATH
    with fixture_path.open("r", encoding="utf-8") as handle:
        document = json.load(handle)

    raw_entries = document.get("bundles")
    if not isinstance(raw_entries, list):
        raise ValueError("Local bundle fixture must define a top-level 'bundles' list.")

    return tuple(
        _coerce_source_record(raw_entry, fixture_path, index)
        for index, raw_entry in enumerate(raw_entries)
    )


def local_bundle_target_ref(bundle_id: str, version: str) -> str:
    normalized_bundle_id = _safe_ref_part(bundle_id, "bundle_id")
    normalized_version = version.strip()
    if not normalized_version:
        raise ValueError("version must be a non-empty string.")
    return f"local-bundle-fixture:{normalized_bundle_id}@{normalized_version}"


def _coerce_source_record(
    raw_entry: Any,
    fixture_path: Path,
    index: int,
) -> LocalBundleSourceRecord:
    if not isinstance(raw_entry, dict):
        raise ValueError(f"bundles[{index}] must be an object.")
    bundle_id = raw_entry.get("bundle_id")
    if not isinstance(bundle_id, str) or not bundle_id:
        raise ValueError(f"bundles[{index}].bundle_id must be a non-empty string.")
    version = raw_entry.get("version")
    if not isinstance(version, str) or not version:
        raise ValueError(f"bundles[{index}].version must be a non-empty string.")
    bundle = raw_entry.get("bundle")
    if not isinstance(bundle, dict):
        raise ValueError(f"bundles[{index}].bundle must be an object.")
    payload_fixture = bundle.get("payload_fixture")
    if not isinstance(payload_fixture, dict):
        raise ValueError(f"bundles[{index}].bundle.payload_fixture must be an object.")
    locator = payload_fixture.get("locator")
    if not isinstance(locator, str) or not locator:
        raise ValueError(f"bundles[{index}].bundle.payload_fixture.locator must be a non-empty string.")
    _validate_repo_relative_payload_locator(locator, fixture_path, index)
    return LocalBundleSourceRecord(
        target_ref=local_bundle_target_ref(bundle_id, version),
        source_name="local_bundle_fixture",
        payload=dict(raw_entry),
        source_locator=fixture_path.relative_to(REPO_ROOT).as_posix(),
    )


def _validate_repo_relative_payload_locator(
    locator: str,
    fixture_path: Path,
    index: int,
) -> None:
    candidate = (REPO_ROOT / locator).resolve()
    try:
        candidate.relative_to(REPO_ROOT)
    except ValueError as error:
        raise ValueError(
            f"bundles[{index}].bundle.payload_fixture.locator must stay within the repo root."
        ) from error
    if not candidate.is_file():
        raise ValueError(
            f"bundles[{index}].bundle.payload_fixture.locator points to missing fixture "
            f"'{locator}' from {fixture_path}."
        )


def _safe_ref_part(value: str, field_name: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise ValueError(f"{field_name} must be a non-empty string.")
    if not re.fullmatch(r"[A-Za-z0-9._-]+", normalized):
        raise ValueError(
            f"{field_name} must contain only letters, numbers, dots, underscores, or hyphens."
        )
    return normalized
