"""Replay committed Internet Archive metadata fixtures without network access."""

from __future__ import annotations

import ast
import json
from pathlib import Path
from typing import Any, Iterable, Mapping

from runtime.source_observation.ids import canonical_json
from runtime.source_observation.internet_archive_metadata import FORBIDDEN_SIDE_EFFECT_FLAGS
from runtime.source_observation.internet_archive_normalization import normalize_ia_metadata_fixture
from runtime.source_observation.internet_archive_validation import (
    build_boundary_report,
    validate_boundary_report,
    validate_ia_fixture_payload,
    validate_normalized_ia_record,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_FIXTURE_DIR = REPO_ROOT / "examples" / "internet_archive_metadata"
FORBIDDEN_IMPORTS = {
    "requests",
    "httpx",
    "aiohttp",
    "urllib.request",
    "selenium",
    "playwright",
    "openai",
    "anthropic",
    "google.generativeai",
}


def replay_fixture(path: str | Path) -> dict[str, Any]:
    fixture_path = Path(path)
    fixture = json.loads(fixture_path.read_text(encoding="utf-8"))
    payload_errors = validate_ia_fixture_payload(fixture)
    if payload_errors:
        raise ValueError("; ".join(payload_errors))
    record = normalize_ia_metadata_fixture(fixture)
    record_errors = validate_normalized_ia_record(record)
    if record_errors:
        raise ValueError("; ".join(record_errors))
    boundary = build_boundary_report(record, network_imports_detected=False)
    boundary_errors = validate_boundary_report(boundary)
    if boundary_errors:
        raise ValueError("; ".join(boundary_errors))
    return {
        "fixture_path": str(fixture_path.as_posix()),
        "fixture_id": record.fixture_id,
        "normalized_record": record.to_dict(),
        "boundary_report": boundary.to_dict(),
    }


def replay_fixture_directory(path: str | Path = DEFAULT_FIXTURE_DIR) -> list[dict[str, Any]]:
    fixture_dir = Path(path)
    return [replay_fixture(path) for path in sorted(fixture_dir.glob("*.fixture.json"))]


def build_fixture_replay_report(fixtures: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    results = [dict(item) for item in fixtures]
    normalized_records = [dict(item["normalized_record"]) for item in results]
    boundary_reports = [dict(item["boundary_report"]) for item in results]
    aggregate = {key: False for key in FORBIDDEN_SIDE_EFFECT_FLAGS}
    return {
        "schema_version": "ia_fixture_replay_report.v0",
        "task": "IA-01",
        "fixture_count": len(results),
        "fixture_ids": [str(item["fixture_id"]) for item in results],
        "normalized_records": normalized_records,
        "boundary_reports": boundary_reports,
        "all_fixtures_replay": len(results) > 0 and all(report.get("passed") is True for report in boundary_reports),
        "forbidden_network_imports_detected": False,
        "boundaries": aggregate,
    }


def assert_no_network_imports(paths: Iterable[str | Path] | None = None) -> None:
    checked_paths = tuple(Path(path) for path in paths) if paths is not None else _default_code_paths()
    violations: list[str] = []
    for path in checked_paths:
        text = path.read_text(encoding="utf-8")
        tree = ast.parse(text, filename=str(path))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if _forbidden_import(alias.name):
                        violations.append(f"{path.as_posix()} imports {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                module = node.module or ""
                imported_names = {alias.name for alias in node.names}
                if _forbidden_import(module) or (module == "urllib" and "request" in imported_names):
                    violations.append(f"{path.as_posix()} imports {module}")
    if violations:
        raise RuntimeError("; ".join(violations))


def assert_no_forbidden_side_effects(report: Mapping[str, Any]) -> None:
    violations: list[str] = []
    if report.get("forbidden_network_imports_detected") is not False:
        violations.append("forbidden network imports detected")
    for key, value in dict(report.get("boundaries", {}) or {}).items():
        if key in FORBIDDEN_SIDE_EFFECT_FLAGS and value is not False:
            violations.append(f"{key} must be false")
    for record in report.get("normalized_records", []) or []:
        for error in validate_normalized_ia_record(record):
            violations.append(f"{record.get('fixture_id')}: {error}")
    for boundary in report.get("boundary_reports", []) or []:
        for error in validate_boundary_report(boundary):
            violations.append(f"{boundary.get('fixture_id')}: {error}")
    if violations:
        raise RuntimeError("; ".join(violations))


def replay_fixture_directory_report(path: str | Path = DEFAULT_FIXTURE_DIR) -> dict[str, Any]:
    assert_no_network_imports()
    report = build_fixture_replay_report(replay_fixture_directory(path))
    assert_no_forbidden_side_effects(report)
    return report


def report_to_json(report: Mapping[str, Any]) -> str:
    return canonical_json(dict(report))


def _forbidden_import(name: str) -> bool:
    return name in FORBIDDEN_IMPORTS or any(name.startswith(prefix + ".") for prefix in FORBIDDEN_IMPORTS)


def _default_code_paths() -> tuple[Path, ...]:
    root = Path(__file__).resolve().parent
    return (
        root / "internet_archive_metadata.py",
        root / "internet_archive_normalization.py",
        root / "internet_archive_validation.py",
        root / "internet_archive_fixture_replay.py",
        REPO_ROOT / "scripts" / "eureka_ia_fixture_replay.py",
        REPO_ROOT / "scripts" / "validate_ia_fixture_replay.py",
    )
