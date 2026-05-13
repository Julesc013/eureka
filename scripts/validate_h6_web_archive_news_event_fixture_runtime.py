#!/usr/bin/env python3
"""Validate H6-BUNDLE-02 web archive/news/event fixture runtime offline."""

from __future__ import annotations

import argparse
import importlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from typing import Any, Mapping, Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from control.prototypes.legacy_runtime.connectors.h6_web_archive_news_event.fixture_loader import load_h6_web_archive_fixture  # noqa: E402
from control.prototypes.legacy_runtime.connectors.h6_web_archive_news_event.normalizer_common import (  # noqa: E402
    H6_FIXTURE_KINDS,
    H6_SOURCE_IDS,
    build_h6_fixture_replay_result,
    detect_h6_product_boundary_violations,
    detect_h6_truth_boundary_violations,
)

CONTRACT_FILES = ('control/schemas/fixtures/h6/connectors/web_archive_fixture.v0.json', 'control/schemas/previews/h6/connectors/web_archive_normalized_record.v0.json', 'control/schemas/previews/h6/connectors/web_capture_identity_candidate.v0.json', 'control/schemas/previews/h6/connectors/archived_url_time_state_candidate.v0.json', 'control/schemas/previews/h6/connectors/news_event_mention_candidate.v0.json', 'control/schemas/previews/h6/connectors/dead_link_trace_candidate.v0.json', 'control/schemas/previews/h6/connectors/public_document_trace_candidate.v0.json', 'control/schemas/previews/h6/connectors/media_transcript_metadata_candidate.v0.json', 'control/schemas/fixtures/h6/connectors/web_archive_fixture_replay_result.v0.json')
POLICY_FILES = ('control/inventory/connectors/h6_web_archive_fixture_runtime_policy.json', 'control/inventory/connectors/h6_web_archive_normalization_policy.json', 'control/inventory/connectors/h6_web_capture_identity_mapping_policy.json', 'control/inventory/connectors/h6_archived_url_time_state_mapping_policy.json', 'control/inventory/connectors/h6_news_event_mention_mapping_policy.json', 'control/inventory/connectors/h6_dead_link_trace_mapping_policy.json', 'control/inventory/connectors/h6_public_document_trace_mapping_policy.json', 'control/inventory/connectors/h6_media_transcript_metadata_mapping_policy.json', 'control/inventory/connectors/h6_web_archive_fixture_output_policy.json', 'control/inventory/connectors/h6_web_archive_fixture_path_policy.json', 'control/inventory/connectors/h6_web_archive_fixture_truth_policy.json', 'control/inventory/connectors/h6_web_archive_source_cache_mapping_policy.json', 'control/inventory/connectors/h6_web_archive_evidence_mapping_policy.json', 'control/inventory/connectors/h6_web_archive_no_fetch_crawl_policy.json')
DOC_FILES = ('docs/reference/H6_WEB_ARCHIVE_FIXTURE_RUNTIME.md', 'docs/reference/H6_WEB_ARCHIVE_NORMALIZED_RECORD.md', 'docs/reference/H6_WEB_CAPTURE_IDENTITY_CANDIDATE.md', 'docs/reference/H6_ARCHIVED_URL_TIME_STATE_CANDIDATE.md', 'docs/reference/H6_NEWS_EVENT_MENTION_CANDIDATE.md', 'docs/reference/H6_DEAD_LINK_TRACE_CANDIDATE.md', 'docs/reference/H6_PUBLIC_DOCUMENT_TRACE_CANDIDATE.md', 'docs/reference/H6_MEDIA_TRANSCRIPT_METADATA_CANDIDATE.md', 'docs/architecture/H6_WEB_ARCHIVE_NORMALIZER_MODEL.md', 'docs/architecture/H6_WEB_CAPTURE_IDENTITY_MODEL.md', 'docs/architecture/H6_ARCHIVED_TIME_STATE_MODEL.md', 'docs/architecture/H6_NEWS_EVENT_MENTION_MODEL.md', 'docs/architecture/H6_DEAD_LINK_TRACE_MODEL.md', 'docs/architecture/H6_PUBLIC_DOCUMENT_TRACE_MODEL.md', 'docs/operations/H6_WEB_ARCHIVE_FIXTURE_REPLAY.md', 'docs/operations/H6_WEB_ARCHIVE_FIXTURE_NO_LIVE_CALL_POLICY.md', 'docs/operations/H6_WEB_ARCHIVE_FIXTURE_NO_FETCH_CRAWL_POLICY.md')
PYTHON_FILES = ('scripts/normalize_h6_web_archive_fixture.py', 'scripts/replay_h6_web_archive_fixtures.py', 'scripts/validate_h6_web_archive_news_event_fixture_runtime.py', 'scripts/summarize_h6_web_archive_fixture_outputs.py')
TEST_FILES = ('tests/connectors/test_h6_web_archive_fixture_runtime.py', 'tests/connectors/test_h6_web_capture_identity_mapping.py', 'tests/connectors/test_h6_archived_url_time_state_mapping.py', 'tests/connectors/test_h6_news_event_dead_link_mapping.py', 'tests/connectors/test_h6_public_document_trace_mapping.py', 'tests/operations/test_h6_web_archive_fixture_scripts.py')
IDENTITY_EXAMPLES = ('examples/connectors/h6_web_archive_news_event/identity/web_capture_identity_candidate_v0.json', 'examples/connectors/h6_web_archive_news_event/identity/archived_url_time_state_candidate_v0.json', 'examples/connectors/h6_web_archive_news_event/identity/news_event_mention_candidate_v0.json', 'examples/connectors/h6_web_archive_news_event/identity/dead_link_trace_candidate_v0.json', 'examples/connectors/h6_web_archive_news_event/identity/public_document_trace_candidate_v0.json', 'examples/connectors/h6_web_archive_news_event/identity/media_transcript_metadata_candidate_v0.json', 'examples/connectors/h6_web_archive_news_event/identity/policy_blocked_trace_candidate_v0.json')
AUDIT_FILES = ('control/audits/h6-bundle-02-web-archive-fixture-runtime-v0/README.md', 'control/audits/h6-bundle-02-web-archive-fixture-runtime-v0/h6_bundle_02_report.json', 'control/audits/h6-bundle-02-web-archive-fixture-runtime-v0/fixture_runtime_summary.md', 'control/audits/h6-bundle-02-web-archive-fixture-runtime-v0/normalizer_coverage_summary.md', 'control/audits/h6-bundle-02-web-archive-fixture-runtime-v0/web_capture_identity_mapping_summary.md', 'control/audits/h6-bundle-02-web-archive-fixture-runtime-v0/archived_url_time_state_mapping_summary.md', 'control/audits/h6-bundle-02-web-archive-fixture-runtime-v0/news_event_mention_mapping_summary.md', 'control/audits/h6-bundle-02-web-archive-fixture-runtime-v0/dead_link_trace_mapping_summary.md', 'control/audits/h6-bundle-02-web-archive-fixture-runtime-v0/public_document_trace_mapping_summary.md', 'control/audits/h6-bundle-02-web-archive-fixture-runtime-v0/media_transcript_metadata_mapping_summary.md', 'control/audits/h6-bundle-02-web-archive-fixture-runtime-v0/source_cache_mapping_preview.md', 'control/audits/h6-bundle-02-web-archive-fixture-runtime-v0/evidence_mapping_preview.md', 'control/audits/h6-bundle-02-web-archive-fixture-runtime-v0/no_live_call_report.md', 'control/audits/h6-bundle-02-web-archive-fixture-runtime-v0/no_fetch_crawl_report.md', 'control/audits/h6-bundle-02-web-archive-fixture-runtime-v0/validation.md', 'control/audits/h6-bundle-02-web-archive-fixture-runtime-v0/generated/sample_h6_normalized_record.json', 'control/audits/h6-bundle-02-web-archive-fixture-runtime-v0/generated/sample_h6_web_capture_identity_candidate.json', 'control/audits/h6-bundle-02-web-archive-fixture-runtime-v0/generated/sample_h6_archived_url_time_state_candidate.json', 'control/audits/h6-bundle-02-web-archive-fixture-runtime-v0/generated/sample_h6_news_event_mention_candidate.json', 'control/audits/h6-bundle-02-web-archive-fixture-runtime-v0/generated/sample_h6_dead_link_trace_candidate.json', 'control/audits/h6-bundle-02-web-archive-fixture-runtime-v0/generated/sample_h6_public_document_trace_candidate.json', 'control/audits/h6-bundle-02-web-archive-fixture-runtime-v0/generated/sample_h6_media_transcript_metadata_candidate.json', 'control/audits/h6-bundle-02-web-archive-fixture-runtime-v0/generated/sample_h6_source_cache_candidate.json', 'control/audits/h6-bundle-02-web-archive-fixture-runtime-v0/generated/sample_h6_evidence_candidate_preview.json', 'control/audits/h6-bundle-02-web-archive-fixture-runtime-v0/generated/sample_h6_fixture_replay_result.json', 'control/audits/h6-bundle-02-web-archive-fixture-runtime-v0/generated/sample_h6_fixture_summary.md')
FIXTURE_ROOT = Path("examples/connectors/h6_web_archive_news_event/fixtures")
NORMALIZED_ROOT = Path("examples/connectors/h6_web_archive_news_event/normalized")
REPLAY_ROOT = Path("examples/connectors/h6_web_archive_news_event/replay_results")

BANNED_RUNTIME_IMPORT_RE = re.compile(r"^\s*(?:from|import)\s+(requests|urllib|httpx|aiohttp|socket|ftplib|smtplib|webbrowser|selenium|playwright|openai|anthropic)\b", re.MULTILINE)
SECRET_KEY_RE = re.compile(r'"[^"]*(api[_-]?key|api[_-]?token|access[_-]?token|auth[_-]?token|client_secret|password|private_key|cookie)[^"]*"\s*:', re.IGNORECASE)
PAYLOAD_RE = re.compile(r'"[^"]*(archived_page_payload_body|live_page_payload_body|warc_payload_body|wacz_payload_body|media_payload_bytes|video_payload|audio_payload|transcript_payload_text|newspaper_page_payload_body|public_document_payload_body|sensitive_document_body|scraping_output_body|crawling_output_body|browser_automation_output)[^"]*"\s*:', re.IGNORECASE)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    result = validate_repo(REPO_ROOT)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print("H6 web archive/news/event fixture runtime validation", file=stdout)
        print(f"status: {result['status']}", file=stdout)
        print(f"errors: {len(result['errors'])}", file=stdout)
        for error in result["errors"]:
            print(f"- {error}", file=stdout)
    return 0 if result["status"] == "valid" else 1


def validate_repo(root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    required_paths = list(CONTRACT_FILES + POLICY_FILES + DOC_FILES + PYTHON_FILES + TEST_FILES + IDENTITY_EXAMPLES + AUDIT_FILES)
    for source_id in H6_SOURCE_IDS:
        for kind in H6_FIXTURE_KINDS:
            filename = "policy_blocked_record.json" if kind == "policy_blocked" else f"{kind}_record.json"
            required_paths.append(str(FIXTURE_ROOT / source_id / filename))
        required_paths.append(str(NORMALIZED_ROOT / f"{source_id}_normalized.json"))
        required_paths.append(str(REPLAY_ROOT / f"{source_id}_replay_result.json"))
        required_paths.append(f"control/prototypes/legacy_runtime/connectors/h6_web_archive_news_event/{source_id}.py")
    required_paths.extend([
        "control/prototypes/legacy_runtime/connectors/h6_web_archive_news_event/__init__.py",
        "control/prototypes/legacy_runtime/connectors/h6_web_archive_news_event/fixture_loader.py",
        "control/prototypes/legacy_runtime/connectors/h6_web_archive_news_event/normalizer_common.py",
        "control/prototypes/legacy_runtime/connectors/h6_web_archive_news_event/web_capture_identity.py",
        "control/prototypes/legacy_runtime/connectors/h6_web_archive_news_event/archived_url_time_state.py",
        "control/prototypes/legacy_runtime/connectors/h6_web_archive_news_event/news_event_mention.py",
        "control/prototypes/legacy_runtime/connectors/h6_web_archive_news_event/dead_link_trace.py",
        "control/prototypes/legacy_runtime/connectors/h6_web_archive_news_event/public_document_trace.py",
        "control/prototypes/legacy_runtime/connectors/h6_web_archive_news_event/media_transcript_metadata.py",
    ])
    for rel in required_paths:
        path = root / rel
        if not path.is_file():
            errors.append(f"missing required artifact: {rel}")
            continue
        if path.suffix == ".json":
            load_json_object(path, errors)
    validate_fixtures(root, errors)
    validate_examples(root, errors)
    validate_runtime_imports(errors)
    validate_python_safety(root, errors)
    validate_scripts_offline(root, errors)
    validate_no_private_roots(root, errors)
    return {
        "schema_version": "h6_web_archive_fixture_runtime_validation.v0",
        "status": "valid" if not errors else "invalid",
        "errors": errors,
        "source_count": len(H6_SOURCE_IDS),
        "fixture_kinds": list(H6_FIXTURE_KINDS),
        "network_calls_made": False,
        "fetch_crawl_used": False,
        "restricted_source_access_used": False,
    }


def validate_fixtures(root: Path, errors: list[str]) -> None:
    for source_id in H6_SOURCE_IDS:
        normalizer = importlib.import_module(f"control.prototypes.legacy_runtime.connectors.h6_web_archive_news_event.{source_id}").normalize
        for kind in H6_FIXTURE_KINDS:
            filename = "policy_blocked_record.json" if kind == "policy_blocked" else f"{kind}_record.json"
            rel = FIXTURE_ROOT / source_id / filename
            path = root / rel
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8")
            if SECRET_KEY_RE.search(text):
                errors.append(f"secret-like key in fixture: {rel}")
            if PAYLOAD_RE.search(text):
                errors.append(f"payload/fetch-output-like field in fixture: {rel}")
            try:
                fixture = load_h6_web_archive_fixture(path)
                normalized = normalizer(fixture)
                replay = build_h6_fixture_replay_result(fixture, normalized)
                errors.extend(f"{rel} normalized: {item}" for item in validate_normalized_record(normalized))
                errors.extend(f"{rel} replay: {item}" for item in validate_replay_result(replay))
            except Exception as exc:  # noqa: BLE001
                errors.append(f"failed to normalize fixture {rel}: {exc}")


def validate_examples(root: Path, errors: list[str]) -> None:
    for source_id in H6_SOURCE_IDS:
        normalized_path = root / NORMALIZED_ROOT / f"{source_id}_normalized.json"
        replay_path = root / REPLAY_ROOT / f"{source_id}_replay_result.json"
        if normalized_path.is_file():
            payload = load_json_object(normalized_path, errors)
            if payload is not None:
                errors.extend(f"{normalized_path.relative_to(root)}: {item}" for item in validate_normalized_record(payload))
        if replay_path.is_file():
            payload = load_json_object(replay_path, errors)
            if payload is not None:
                errors.extend(f"{replay_path.relative_to(root)}: {item}" for item in validate_replay_result(payload))
    for rel in IDENTITY_EXAMPLES:
        payload = load_json_object(root / rel, errors)
        if payload is not None:
            errors.extend(f"{rel}: {item}" for item in validate_candidate_boundary(payload))


def validate_normalized_record(record: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if record.get("schema_version") != "h6_web_archive_normalized_record.v0":
        errors.append("normalized schema_version must be h6_web_archive_normalized_record.v0")
    for key in ("source_id", "connector_family", "source_record_kind", "source_cache_candidate_preview", "evidence_candidate_preview"):
        if key not in record:
            errors.append(f"normalized record missing {key}")
    errors.extend(detect_h6_truth_boundary_violations(record))
    errors.extend(detect_h6_product_boundary_violations(record))
    return errors


def validate_replay_result(result: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if result.get("schema_version") != "h6_web_archive_fixture_replay_result.v0":
        errors.append("replay schema_version must be h6_web_archive_fixture_replay_result.v0")
    for key in ("no_network_used", "no_live_source_used", "no_cdx_query_used", "no_memento_lookup_used", "no_warc_wacz_fetch_used", "no_archived_page_fetch_used", "no_media_download_used", "no_scraping_crawling_used", "no_sensitive_source_access_used"):
        if result.get(key) is not True:
            errors.append(f"{key} must be true")
    errors.extend(detect_h6_truth_boundary_violations(result))
    errors.extend(detect_h6_product_boundary_violations(result))
    return errors


def validate_candidate_boundary(candidate: Mapping[str, Any]) -> list[str]:
    return detect_h6_truth_boundary_violations(candidate) + detect_h6_product_boundary_violations(candidate)


def validate_runtime_imports(errors: list[str]) -> None:
    for source_id in H6_SOURCE_IDS:
        importlib.import_module(f"control.prototypes.legacy_runtime.connectors.h6_web_archive_news_event.{source_id}")
    for module in ("fixture_loader", "normalizer_common", "web_capture_identity", "archived_url_time_state", "news_event_mention", "dead_link_trace", "public_document_trace", "media_transcript_metadata"):
        importlib.import_module(f"control.prototypes.legacy_runtime.connectors.h6_web_archive_news_event.{module}")


def validate_python_safety(root: Path, errors: list[str]) -> None:
    runtime_dir = root / "control/prototypes/legacy_runtime/connectors/h6_web_archive_news_event"
    for path in runtime_dir.glob("*.py"):
        if path.name.startswith("live_probe_"):
            continue
        text = path.read_text(encoding="utf-8")
        if BANNED_RUNTIME_IMPORT_RE.search(text):
            errors.append(f"{path.relative_to(root)}: imports network/provider/browser library")
        lowered = text.casefold()
        for marker in ("requests.", "httpx.", "aiohttp.", "urlopen", "urlretrieve", "selenium", "playwright", "scrapy"):
            if marker in lowered:
                errors.append(f"{path.relative_to(root)}: contains forbidden live/fetch/scrape marker {marker}")


def validate_scripts_offline(root: Path, errors: list[str]) -> None:
    commands = [
        [sys.executable, "scripts/normalize_h6_web_archive_fixture.py", "--source-id", "wayback_cdx_memento", "--input", "examples/connectors/h6_web_archive_news_event/fixtures/wayback_cdx_memento/capture_record.json", "--check"],
        [sys.executable, "scripts/replay_h6_web_archive_fixtures.py", "--check"],
        [sys.executable, "scripts/summarize_h6_web_archive_fixture_outputs.py", "--input", "examples/connectors/h6_web_archive_news_event", "--check"],
    ]
    for command in commands:
        result = subprocess.run(command, cwd=root, text=True, capture_output=True, check=False)
        if result.returncode != 0:
            errors.append(f"offline script failed {command}: {result.stdout} {result.stderr}")
    with tempfile.TemporaryDirectory() as tmp:
        ok = subprocess.run([
            sys.executable, "scripts/normalize_h6_web_archive_fixture.py",
            "--source-id", "wayback_cdx_memento",
            "--input", "examples/connectors/h6_web_archive_news_event/fixtures/wayback_cdx_memento/capture_record.json",
            "--output", str(Path(tmp) / "normalized.json"),
        ], cwd=root, text=True, capture_output=True, check=False)
        if ok.returncode != 0:
            errors.append(f"normalizer temp output failed: {ok.stdout} {ok.stderr}")
    bad = subprocess.run([
        sys.executable, "scripts/normalize_h6_web_archive_fixture.py",
        "--source-id", "wayback_cdx_memento",
        "--input", "examples/connectors/h6_web_archive_news_event/fixtures/wayback_cdx_memento/capture_record.json",
        "--output", "site/dist/h6.json",
    ], cwd=root, text=True, capture_output=True, check=False)
    if bad.returncode == 0:
        errors.append("normalizer did not reject forbidden site/dist output")


def validate_no_private_roots(root: Path, errors: list[str]) -> None:
    for rel in (".aide.local", ".local/eureka", ".cache/eureka", "crawl_cache", "warc_wacz_cache", "media_downloads", "document_dumps"):
        if (root / rel).exists():
            errors.append(f"forbidden private/fetch root exists: {rel}")


def load_json_object(path: Path, errors: list[str]) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"{path.relative_to(REPO_ROOT)}: invalid JSON: {exc}")
        return None
    if not isinstance(payload, dict):
        errors.append(f"{path.relative_to(REPO_ROOT)}: expected JSON object")
        return None
    return payload


if __name__ == "__main__":
    raise SystemExit(main())
