from __future__ import annotations

import json
from pathlib import Path
import re
from typing import Any

from runtime.engine.interfaces.ingest import ArticleScanRecordedSourceRecord


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_ARTICLE_SCAN_RECORDED_FIXTURE_PATH = (
    REPO_ROOT
    / "runtime"
    / "connectors"
    / "article_scan_recorded"
    / "fixtures"
    / "article_scan_fixture.json"
)


def load_article_scan_recorded_source_records(
    path: Path | None = None,
) -> tuple[ArticleScanRecordedSourceRecord, ...]:
    fixture_path = path or DEFAULT_ARTICLE_SCAN_RECORDED_FIXTURE_PATH
    with fixture_path.open("r", encoding="utf-8") as handle:
        document = json.load(handle)

    raw_entries = document.get("articles")
    if not isinstance(raw_entries, list):
        raise ValueError("Article scan recorded fixture must define a top-level 'articles' list.")

    fixture_notes = document.get("fixture_notes")
    return tuple(
        _coerce_source_record(raw_entry, fixture_path, index, fixture_notes)
        for index, raw_entry in enumerate(raw_entries)
    )


def article_scan_recorded_target_ref(article_id: str) -> str:
    normalized_article_id = _safe_ref_part(article_id, "article_id")
    return f"article-scan-recorded:{normalized_article_id}"


def _coerce_source_record(
    raw_entry: Any,
    fixture_path: Path,
    index: int,
    fixture_notes: Any,
) -> ArticleScanRecordedSourceRecord:
    if not isinstance(raw_entry, dict):
        raise ValueError(f"articles[{index}] must be an object.")
    issue = raw_entry.get("issue")
    if not isinstance(issue, dict):
        raise ValueError(f"articles[{index}].issue must be an object.")
    article = raw_entry.get("article")
    if not isinstance(article, dict):
        raise ValueError(f"articles[{index}].article must be an object.")
    article_id = article.get("id")
    if not isinstance(article_id, str) or not article_id:
        raise ValueError(f"articles[{index}].article.id must be a non-empty string.")
    article_title = article.get("title")
    if not isinstance(article_title, str) or not article_title:
        raise ValueError(f"articles[{index}].article.title must be a non-empty string.")
    member_path = article.get("member_path")
    if not isinstance(member_path, str) or not member_path:
        raise ValueError(f"articles[{index}].article.member_path must be a non-empty string.")
    _validate_payload_fixtures(article, fixture_path, index, "article")
    _validate_payload_fixtures(issue, fixture_path, index, "issue")
    payload = dict(raw_entry)
    if fixture_notes is not None:
        payload["fixture_notes"] = fixture_notes
    return ArticleScanRecordedSourceRecord(
        target_ref=article_scan_recorded_target_ref(article_id),
        source_name="article_scan_recorded_fixture",
        payload=payload,
        source_locator=fixture_path.relative_to(REPO_ROOT).as_posix(),
    )


def _validate_payload_fixtures(
    parent: dict[str, Any],
    fixture_path: Path,
    index: int,
    field_name: str,
) -> None:
    representations = parent.get("representations")
    if representations is None:
        return
    if not isinstance(representations, list):
        raise ValueError(f"articles[{index}].{field_name}.representations must be a list.")
    for rep_index, representation in enumerate(representations):
        if not isinstance(representation, dict):
            raise ValueError(
                f"articles[{index}].{field_name}.representations[{rep_index}] must be an object."
            )
        payload_fixture = representation.get("payload_fixture")
        if payload_fixture is None:
            continue
        if not isinstance(payload_fixture, dict):
            raise ValueError(
                f"articles[{index}].{field_name}.representations[{rep_index}].payload_fixture "
                "must be an object."
            )
        locator = payload_fixture.get("locator")
        if not isinstance(locator, str) or not locator:
            raise ValueError(
                f"articles[{index}].{field_name}.representations[{rep_index}].payload_fixture.locator "
                "must be a non-empty string."
            )
        _validate_repo_relative_payload_locator(locator, fixture_path, index)


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
            f"articles[{index}] payload fixture locator must stay within the repo root."
        ) from error
    if not candidate.is_file():
        raise ValueError(
            f"articles[{index}] payload fixture locator points to missing fixture "
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
