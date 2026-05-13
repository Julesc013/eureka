#!/usr/bin/env python3
"""Validate H8-BUNDLE-02 manuals/docs/standards fixture runtime offline."""

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

from control.prototypes.legacy_runtime.connectors.h8_manuals_docs_standards.fixture_loader import load_h8_manuals_docs_fixture  # noqa: E402
from control.prototypes.legacy_runtime.connectors.h8_manuals_docs_standards.normalizer_common import (  # noqa: E402
    H8_FIXTURE_KINDS,
    H8_SOURCE_IDS,
    build_h8_fixture_replay_result,
    detect_h8_product_boundary_violations,
    detect_h8_truth_boundary_violations,
)

CONTRACT_FILES = ('control/schemas/fixtures/h8/connectors/manuals_docs_fixture.v0.json', 'control/schemas/previews/h8/connectors/manuals_docs_normalized_record.v0.json', 'control/schemas/previews/h8/connectors/technical_document_identity_candidate.v0.json', 'control/schemas/previews/h8/connectors/manual_artifact_relation_candidate.v0.json', 'control/schemas/previews/h8/connectors/datasheet_device_identity_candidate.v0.json', 'control/schemas/previews/h8/connectors/standards_specification_identity_candidate.v0.json', 'control/schemas/previews/h8/connectors/install_requirement_claim_candidate.v0.json', 'control/schemas/previews/h8/connectors/repair_service_safety_candidate.v0.json', 'control/schemas/previews/h8/connectors/access_rights_candidate.v0.json', 'control/schemas/fixtures/h8/connectors/manuals_docs_fixture_replay_result.v0.json')
POLICY_FILES = ('control/inventory/connectors/h8_manuals_docs_fixture_runtime_policy.json', 'control/inventory/connectors/h8_manuals_docs_normalization_policy.json', 'control/inventory/connectors/h8_technical_document_identity_mapping_policy.json', 'control/inventory/connectors/h8_manual_artifact_relation_mapping_policy.json', 'control/inventory/connectors/h8_datasheet_device_identity_mapping_policy.json', 'control/inventory/connectors/h8_standards_specification_identity_mapping_policy.json', 'control/inventory/connectors/h8_install_requirement_claim_mapping_policy.json', 'control/inventory/connectors/h8_repair_service_safety_mapping_policy.json', 'control/inventory/connectors/h8_access_rights_mapping_policy.json', 'control/inventory/connectors/h8_manuals_docs_fixture_output_policy.json', 'control/inventory/connectors/h8_manuals_docs_fixture_path_policy.json', 'control/inventory/connectors/h8_manuals_docs_fixture_truth_policy.json', 'control/inventory/connectors/h8_manuals_docs_source_cache_mapping_policy.json', 'control/inventory/connectors/h8_manuals_docs_evidence_mapping_policy.json', 'control/inventory/connectors/h8_manuals_docs_no_download_extract_policy.json')
DOC_FILES = ('docs/reference/H8_MANUALS_DOCS_FIXTURE_RUNTIME.md', 'docs/reference/H8_MANUALS_DOCS_NORMALIZED_RECORD.md', 'docs/reference/H8_TECHNICAL_DOCUMENT_IDENTITY_CANDIDATE.md', 'docs/reference/H8_MANUAL_ARTIFACT_RELATION_CANDIDATE.md', 'docs/reference/H8_DATASHEET_DEVICE_IDENTITY_CANDIDATE.md', 'docs/reference/H8_STANDARDS_SPECIFICATION_IDENTITY_CANDIDATE.md', 'docs/reference/H8_INSTALL_REQUIREMENT_CLAIM_CANDIDATE.md', 'docs/reference/H8_REPAIR_SERVICE_SAFETY_CANDIDATE.md', 'docs/reference/H8_ACCESS_RIGHTS_CANDIDATE.md', 'docs/architecture/H8_MANUALS_DOCS_NORMALIZER_MODEL.md', 'docs/architecture/H8_TECHNICAL_DOCUMENT_IDENTITY_MODEL.md', 'docs/architecture/H8_MANUAL_ARTIFACT_RELATION_MODEL.md', 'docs/architecture/H8_DATASHEET_DEVICE_IDENTITY_MODEL.md', 'docs/architecture/H8_STANDARDS_SPECIFICATION_IDENTITY_MODEL.md', 'docs/architecture/H8_INSTALL_REQUIREMENT_CLAIM_MODEL.md', 'docs/architecture/H8_REPAIR_SERVICE_SAFETY_MODEL.md', 'docs/architecture/H8_ACCESS_RIGHTS_MODEL.md', 'docs/operations/H8_MANUALS_DOCS_FIXTURE_REPLAY.md', 'docs/operations/H8_MANUALS_DOCS_FIXTURE_NO_LIVE_CALL_POLICY.md', 'docs/operations/H8_MANUALS_DOCS_FIXTURE_NO_DOWNLOAD_EXTRACT_POLICY.md')
PYTHON_FILES = (
    "scripts/normalize_h8_manuals_docs_fixture.py",
    "scripts/replay_h8_manuals_docs_fixtures.py",
    "scripts/validate_h8_manuals_docs_standards_fixture_runtime.py",
    "scripts/summarize_h8_manuals_docs_fixture_outputs.py",
)
TEST_FILES = (
    "tests/connectors/test_h8_manuals_docs_fixture_runtime.py",
    "tests/connectors/test_h8_technical_document_identity_mapping.py",
    "tests/connectors/test_h8_manual_artifact_datasheet_mapping.py",
    "tests/connectors/test_h8_standards_install_repair_mapping.py",
    "tests/connectors/test_h8_access_rights_mapping.py",
    "tests/operations/test_h8_manuals_docs_fixture_scripts.py",
)
IDENTITY_EXAMPLES = (
    "examples/connectors/h8_manuals_docs_standards/identity/technical_document_identity_candidate_v0.json",
    "examples/connectors/h8_manuals_docs_standards/identity/manual_artifact_relation_candidate_v0.json",
    "examples/connectors/h8_manuals_docs_standards/identity/datasheet_device_identity_candidate_v0.json",
    "examples/connectors/h8_manuals_docs_standards/identity/standards_specification_identity_candidate_v0.json",
    "examples/connectors/h8_manuals_docs_standards/identity/install_requirement_claim_candidate_v0.json",
    "examples/connectors/h8_manuals_docs_standards/identity/repair_service_safety_candidate_v0.json",
    "examples/connectors/h8_manuals_docs_standards/identity/access_rights_candidate_v0.json",
    "examples/connectors/h8_manuals_docs_standards/identity/policy_blocked_identity_candidate_v0.json",
)
AUDIT_FILES = ('control/audits/h8-bundle-02-manuals-docs-fixture-runtime-v0/README.md', 'control/audits/h8-bundle-02-manuals-docs-fixture-runtime-v0/fixture_runtime_summary.md', 'control/audits/h8-bundle-02-manuals-docs-fixture-runtime-v0/normalizer_coverage_summary.md', 'control/audits/h8-bundle-02-manuals-docs-fixture-runtime-v0/technical_document_identity_mapping_summary.md', 'control/audits/h8-bundle-02-manuals-docs-fixture-runtime-v0/manual_artifact_relation_mapping_summary.md', 'control/audits/h8-bundle-02-manuals-docs-fixture-runtime-v0/datasheet_device_identity_mapping_summary.md', 'control/audits/h8-bundle-02-manuals-docs-fixture-runtime-v0/standards_specification_identity_mapping_summary.md', 'control/audits/h8-bundle-02-manuals-docs-fixture-runtime-v0/install_requirement_claim_mapping_summary.md', 'control/audits/h8-bundle-02-manuals-docs-fixture-runtime-v0/repair_service_safety_mapping_summary.md', 'control/audits/h8-bundle-02-manuals-docs-fixture-runtime-v0/access_rights_mapping_summary.md', 'control/audits/h8-bundle-02-manuals-docs-fixture-runtime-v0/source_cache_mapping_preview.md', 'control/audits/h8-bundle-02-manuals-docs-fixture-runtime-v0/evidence_mapping_preview.md', 'control/audits/h8-bundle-02-manuals-docs-fixture-runtime-v0/no_live_call_report.md', 'control/audits/h8-bundle-02-manuals-docs-fixture-runtime-v0/no_download_extract_report.md', 'control/audits/h8-bundle-02-manuals-docs-fixture-runtime-v0/validation.md', 'control/audits/h8-bundle-02-manuals-docs-fixture-runtime-v0/generated/sample_h8_normalized_record.json', 'control/audits/h8-bundle-02-manuals-docs-fixture-runtime-v0/generated/sample_h8_technical_document_identity_candidate.json', 'control/audits/h8-bundle-02-manuals-docs-fixture-runtime-v0/generated/sample_h8_manual_artifact_relation_candidate.json', 'control/audits/h8-bundle-02-manuals-docs-fixture-runtime-v0/generated/sample_h8_datasheet_device_identity_candidate.json', 'control/audits/h8-bundle-02-manuals-docs-fixture-runtime-v0/generated/sample_h8_standards_specification_identity_candidate.json', 'control/audits/h8-bundle-02-manuals-docs-fixture-runtime-v0/generated/sample_h8_install_requirement_claim_candidate.json', 'control/audits/h8-bundle-02-manuals-docs-fixture-runtime-v0/generated/sample_h8_repair_service_safety_candidate.json', 'control/audits/h8-bundle-02-manuals-docs-fixture-runtime-v0/generated/sample_h8_access_rights_candidate.json', 'control/audits/h8-bundle-02-manuals-docs-fixture-runtime-v0/generated/sample_h8_source_cache_candidate.json', 'control/audits/h8-bundle-02-manuals-docs-fixture-runtime-v0/generated/sample_h8_evidence_candidate_preview.json', 'control/audits/h8-bundle-02-manuals-docs-fixture-runtime-v0/generated/sample_h8_fixture_replay_result.json', 'control/audits/h8-bundle-02-manuals-docs-fixture-runtime-v0/generated/sample_h8_fixture_summary.md', 'control/audits/h8-bundle-02-manuals-docs-fixture-runtime-v0/h8_bundle_02_report.json')
FIXTURE_ROOT = Path("examples/connectors/h8_manuals_docs_standards/fixtures")
NORMALIZED_ROOT = Path("examples/connectors/h8_manuals_docs_standards/normalized")
REPLAY_ROOT = Path("examples/connectors/h8_manuals_docs_standards/replay_results")

BANNED_RUNTIME_IMPORT_RE = re.compile(r"^\s*(?:from|import)\s+(requests|urllib|httpx|aiohttp|socket|ftplib|smtplib|webbrowser|selenium|playwright|openai|anthropic)\b", re.MULTILINE)
SECRET_KEY_RE = re.compile(r'"[^"]*(api[_-]?key|api[_-]?token|access[_-]?token|auth[_-]?token|client_secret|password|private_key|cookie)[^"]*"\s*:', re.IGNORECASE)
PAYLOAD_RE = re.compile(r'"[^"]*(document_payload_body|pdf_payload_body|scan_payload_body|datasheet_payload_body|standards_document_payload_body|schematic_payload_body|service_manual_payload_body|full_text_payload_body|ocr_payload_body|iiif_payload_body|media_payload_body|restricted_payload_body|scraping_output_body|crawling_output_body|browser_automation_output_body)[^"]*"\s*:', re.IGNORECASE)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    result = validate_repo(REPO_ROOT)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print("H8 manuals/docs/standards fixture runtime validation", file=stdout)
        print(f"status: {result['status']}", file=stdout)
        print(f"errors: {len(result['errors'])}", file=stdout)
        for error in result["errors"]:
            print(f"- {error}", file=stdout)
    return 0 if result["status"] == "valid" else 1


def validate_repo(root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    required_paths = list(CONTRACT_FILES + POLICY_FILES + DOC_FILES + PYTHON_FILES + TEST_FILES + IDENTITY_EXAMPLES + AUDIT_FILES)
    for source_id in H8_SOURCE_IDS:
        for kind in H8_FIXTURE_KINDS:
            filename = "policy_blocked_record.json" if kind == "policy_blocked" else f"{kind}_record.json"
            required_paths.append(str(FIXTURE_ROOT / source_id / filename))
        required_paths.append(str(NORMALIZED_ROOT / f"{source_id}_normalized.json"))
        required_paths.append(str(REPLAY_ROOT / f"{source_id}_replay_result.json"))
        required_paths.append(f"control/prototypes/legacy_runtime/connectors/h8_manuals_docs_standards/{source_id}.py")
    required_paths.extend([
        "control/prototypes/legacy_runtime/connectors/h8_manuals_docs_standards/__init__.py",
        "control/prototypes/legacy_runtime/connectors/h8_manuals_docs_standards/fixture_loader.py",
        "control/prototypes/legacy_runtime/connectors/h8_manuals_docs_standards/normalizer_common.py",
        "control/prototypes/legacy_runtime/connectors/h8_manuals_docs_standards/technical_document_identity.py",
        "control/prototypes/legacy_runtime/connectors/h8_manuals_docs_standards/manual_artifact_relation.py",
        "control/prototypes/legacy_runtime/connectors/h8_manuals_docs_standards/datasheet_device_identity.py",
        "control/prototypes/legacy_runtime/connectors/h8_manuals_docs_standards/standards_specification_identity.py",
        "control/prototypes/legacy_runtime/connectors/h8_manuals_docs_standards/install_requirement_claim.py",
        "control/prototypes/legacy_runtime/connectors/h8_manuals_docs_standards/repair_service_safety.py",
        "control/prototypes/legacy_runtime/connectors/h8_manuals_docs_standards/access_rights.py",
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
        "schema_version": "h8_manuals_docs_fixture_runtime_validation.v0",
        "status": "valid" if not errors else "invalid",
        "errors": errors,
        "source_count": len(H8_SOURCE_IDS),
        "fixture_kinds": list(H8_FIXTURE_KINDS),
        "network_calls_made": False,
        "query_fetch_download_extract_used": False,
        "restricted_source_access_used": False,
    }


def validate_fixtures(root: Path, errors: list[str]) -> None:
    for source_id in H8_SOURCE_IDS:
        normalizer = importlib.import_module(f"control.prototypes.legacy_runtime.connectors.h8_manuals_docs_standards.{source_id}").normalize
        for kind in H8_FIXTURE_KINDS:
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
                fixture = load_h8_manuals_docs_fixture(path)
                for key in ("live_call_used", "network_used", "external_api_used", "catalog_payload_included", "document_payload_included", "pdf_payload_included", "scan_payload_included", "datasheet_payload_included", "standards_document_payload_included", "schematic_payload_included", "service_manual_payload_included", "full_text_payload_included", "ocr_payload_included", "iiif_payload_included", "media_payload_included", "scraping_output_included", "crawling_output_included", "restricted_source_accessed", "bypass_or_automation_used"):
                    if fixture.get(key) is True:
                        errors.append(f"{rel}: {key} must be false")
                normalized = normalizer(fixture)
                replay = build_h8_fixture_replay_result(fixture, normalized)
                errors.extend(f"{rel} normalized: {item}" for item in validate_normalized_record(normalized))
                errors.extend(f"{rel} replay: {item}" for item in validate_replay_result(replay))
            except Exception as exc:  # noqa: BLE001
                errors.append(f"failed to normalize fixture {rel}: {exc}")


def validate_examples(root: Path, errors: list[str]) -> None:
    for source_id in H8_SOURCE_IDS:
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
    if record.get("schema_version") != "h8_manuals_docs_normalized_record.v0":
        errors.append("normalized schema_version must be h8_manuals_docs_normalized_record.v0")
    for key in ("source_id", "connector_family", "source_record_kind", "source_cache_candidate_preview", "evidence_candidate_preview", "technical_document_identity_candidate", "access_rights_candidate"):
        if key not in record:
            errors.append(f"normalized record missing {key}")
    errors.extend(detect_h8_truth_boundary_violations(record))
    errors.extend(detect_h8_product_boundary_violations(record))
    return errors


def validate_replay_result(result: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if result.get("schema_version") != "h8_manuals_docs_fixture_replay_result.v0":
        errors.append("replay schema_version must be h8_manuals_docs_fixture_replay_result.v0")
    for key in ("no_network_used", "no_live_source_used", "no_api_catalog_query_used", "no_query_fetch_download_extract_used", "no_document_pdf_datasheet_standard_fetch_used", "no_full_text_or_ocr_used", "no_iiif_or_media_fetch_used", "no_scraping_crawling_used", "no_restricted_source_access_used", "no_repair_install_action_authorized"):
        if result.get(key) is not True:
            errors.append(f"{key} must be true")
    errors.extend(detect_h8_truth_boundary_violations(result))
    errors.extend(detect_h8_product_boundary_violations(result))
    return errors


def validate_candidate_boundary(candidate: Mapping[str, Any]) -> list[str]:
    return detect_h8_truth_boundary_violations(candidate) + detect_h8_product_boundary_violations(candidate)


def validate_runtime_imports(errors: list[str]) -> None:
    for source_id in H8_SOURCE_IDS:
        importlib.import_module(f"control.prototypes.legacy_runtime.connectors.h8_manuals_docs_standards.{source_id}")
    for module in ("fixture_loader", "normalizer_common", "technical_document_identity", "manual_artifact_relation", "datasheet_device_identity", "standards_specification_identity", "install_requirement_claim", "repair_service_safety", "access_rights"):
        importlib.import_module(f"control.prototypes.legacy_runtime.connectors.h8_manuals_docs_standards.{module}")


def validate_python_safety(root: Path, errors: list[str]) -> None:
    runtime_dir = root / "control/prototypes/legacy_runtime/connectors/h8_manuals_docs_standards"
    for path in runtime_dir.glob("*.py"):
        text = path.read_text(encoding="utf-8")
        if BANNED_RUNTIME_IMPORT_RE.search(text):
            errors.append(f"{path.relative_to(root)}: imports network/provider/browser library")
        lowered = text.casefold()
        for marker in ("requests.", "httpx.", "aiohttp.", "urlopen", "urlretrieve", "selenium", "playwright", "scrapy", "socket."):
            if marker in lowered:
                errors.append(f"{path.relative_to(root)}: contains forbidden live/fetch/scrape marker {marker}")


def validate_scripts_offline(root: Path, errors: list[str]) -> None:
    commands = [
        [sys.executable, "scripts/normalize_h8_manuals_docs_fixture.py", "--source-id", "bitsavers_docs", "--input", "examples/connectors/h8_manuals_docs_standards/fixtures/bitsavers_docs/document_identity_record.json", "--check"],
        [sys.executable, "scripts/replay_h8_manuals_docs_fixtures.py", "--check"],
        [sys.executable, "scripts/summarize_h8_manuals_docs_fixture_outputs.py", "--input", "examples/connectors/h8_manuals_docs_standards", "--check"],
    ]
    for command in commands:
        result = subprocess.run(command, cwd=root, text=True, capture_output=True, check=False)
        if result.returncode != 0:
            errors.append(f"offline script failed {command}: {result.stdout} {result.stderr}")
    with tempfile.TemporaryDirectory() as tmp:
        ok = subprocess.run([
            sys.executable, "scripts/normalize_h8_manuals_docs_fixture.py",
            "--source-id", "bitsavers_docs",
            "--input", "examples/connectors/h8_manuals_docs_standards/fixtures/bitsavers_docs/document_identity_record.json",
            "--output", str(Path(tmp) / "normalized.json"),
        ], cwd=root, text=True, capture_output=True, check=False)
        if ok.returncode != 0:
            errors.append(f"normalizer temp output failed: {ok.stdout} {ok.stderr}")
    bad = subprocess.run([
        sys.executable, "scripts/normalize_h8_manuals_docs_fixture.py",
        "--source-id", "bitsavers_docs",
        "--input", "examples/connectors/h8_manuals_docs_standards/fixtures/bitsavers_docs/document_identity_record.json",
        "--output", "site/dist/h8.json",
    ], cwd=root, text=True, capture_output=True, check=False)
    if bad.returncode == 0:
        errors.append("normalizer did not reject forbidden site/dist output")


def validate_no_private_roots(root: Path, errors: list[str]) -> None:
    for rel in (".aide.local", ".local/eureka", ".cache/eureka", "harvest_cache", "harvests", "document_downloads", "standards_downloads", "pdf_downloads", "manual_downloads", "datasheet_downloads", "schematic_downloads", "service_manual_downloads", "ocr_cache", "iiif_cache", "media_downloads", "repair_manual_dumps"):
        if (root / rel).exists():
            errors.append(f"forbidden private/download root exists: {rel}")


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
