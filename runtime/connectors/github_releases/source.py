from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from runtime.engine.interfaces.ingest import GitHubReleaseSourceRecord


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_GITHUB_RELEASES_FIXTURE_PATH = (
    REPO_ROOT
    / "runtime"
    / "connectors"
    / "github_releases"
    / "fixtures"
    / "github_releases_fixture.json"
)


def load_github_release_source_records(
    path: Path | None = None,
) -> tuple[GitHubReleaseSourceRecord, ...]:
    fixture_path = path or DEFAULT_GITHUB_RELEASES_FIXTURE_PATH
    with fixture_path.open("r", encoding="utf-8") as handle:
        document = json.load(handle)

    raw_entries = document.get("releases")
    if not isinstance(raw_entries, list):
        raise ValueError("GitHub releases source fixture must define a top-level 'releases' list.")

    return tuple(
        _coerce_source_record(raw_entry, fixture_path, index)
        for index, raw_entry in enumerate(raw_entries)
    )


def github_release_target_ref(repository_full_name: str, tag_name: str) -> str:
    normalized_repo = repository_full_name.strip().casefold()
    normalized_tag = tag_name.strip()
    if not normalized_repo:
        raise ValueError("repository_full_name must be a non-empty string.")
    if not normalized_tag:
        raise ValueError("tag_name must be a non-empty string.")
    return f"github-release:{normalized_repo}@{normalized_tag}"


def _coerce_source_record(
    raw_entry: Any,
    fixture_path: Path,
    index: int,
) -> GitHubReleaseSourceRecord:
    if not isinstance(raw_entry, dict):
        raise ValueError(f"releases[{index}] must be an object.")

    repository = raw_entry.get("repository")
    if not isinstance(repository, dict):
        raise ValueError(f"releases[{index}].repository must be an object.")
    repository_full_name = repository.get("full_name")
    if not isinstance(repository_full_name, str) or not repository_full_name:
        raise ValueError(f"releases[{index}].repository.full_name must be a non-empty string.")

    release = raw_entry.get("release")
    if not isinstance(release, dict):
        raise ValueError(f"releases[{index}].release must be an object.")
    tag_name = release.get("tag_name")
    if not isinstance(tag_name, str) or not tag_name:
        raise ValueError(f"releases[{index}].release.tag_name must be a non-empty string.")

    return GitHubReleaseSourceRecord(
        target_ref=github_release_target_ref(repository_full_name, tag_name),
        source_name="github_releases_fixture",
        payload=dict(raw_entry),
        source_locator=fixture_path.relative_to(REPO_ROOT).as_posix(),
    )
