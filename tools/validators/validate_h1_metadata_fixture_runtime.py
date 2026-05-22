#!/usr/bin/env python3
"""Validate H1 metadata fixture runtime artifacts offline."""

from __future__ import annotations

import argparse
import importlib
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from archive.prototypes.legacy_runtime.connectors.h1_metadata_wave.fixture_loader import load_h1_fixture, validate_h1_fixture  # noqa: E402
from archive.prototypes.legacy_runtime.connectors.h1_metadata_wave.normalizer_common import (  # noqa: E402
    H1_SOURCE_IDS,
    build_h1_fixture_replay_result,
    detect_h1_product_boundary_violations,
    detect_h1_truth_boundary_violations,
)


CONTRACTS = (
    "contracts/control_schemas/fixtures/h1/connectors/metadata_fixture.v0.json",
    "contracts/control_schemas/previews/h1/connectors/metadata_normalized_record.v0.json",
    "contracts/control_schemas/fixtures/h1/connectors/metadata_fixture_replay_result.v0.json",
)
POLICIES = (
    "control/inventory/connectors/h1_metadata_fixture_runtime_policy.json",
    "control/inventory/connectors/h1_metadata_normalization_policy.json",
    "control/inventory/connectors/h1_metadata_fixture_output_policy.json",
    "control/inventory/connectors/h1_metadata_fixture_path_policy.json",
    "control/inventory/connectors/h1_metadata_fixture_truth_policy.json",
    "control/inventory/connectors/h1_metadata_source_cache_mapping_policy.json",
    "control/inventory/connectors/h1_metadata_evidence_mapping_policy.json",
)
DOCS = (
    "docs/reference/H1_METADATA_FIXTURE_RUNTIME.md",
    "docs/reference/H1_METADATA_NORMALIZED_RECORD.md",
    "docs/architecture/H1_METADATA_NORMALIZER_MODEL.md",
    "docs/operations/H1_METADATA_FIXTURE_REPLAY.md",
    "docs/operations/H1_METADATA_FIXTURE_NO_LIVE_CALL_POLICY.md",
)
AUDIT_FILES = (
    "control/audits/h1-bundle-02-metadata-fixture-runtime-v0/README.md",
    "control/audits/h1-bundle-02-metadata-fixture-runtime-v0/h1_bundle_02_report.json",
    "control/audits/h1-bundle-02-metadata-fixture-runtime-v0/fixture_runtime_summary.md",
    "control/audits/h1-bundle-02-metadata-fixture-runtime-v0/normalizer_coverage_summary.md",
    "control/audits/h1-bundle-02-metadata-fixture-runtime-v0/source_cache_mapping_preview.md",
    "control/audits/h1-bundle-02-metadata-fixture-runtime-v0/evidence_mapping_preview.md",
    "control/audits/h1-bundle-02-metadata-fixture-runtime-v0/no_live_call_report.md",
    "control/audits/h1-bundle-02-metadata-fixture-runtime-v0/validation.md",
    "control/audits/h1-bundle-02-metadata-fixture-runtime-v0/generated/sample_h1_normalized_record.json",
    "control/audits/h1-bundle-02-metadata-fixture-runtime-v0/generated/sample_h1_fixture_replay_result.json",
    "control/audits/h1-bundle-02-metadata-fixture-runtime-v0/generated/sample_h1_source_cache_candidate.json",
    "control/audits/h1-bundle-02-metadata-fixture-runtime-v0/generated/sample_h1_evidence_candidate_preview.json",
    "control/audits/h1-bundle-02-metadata-fixture-runtime-v0/generated/sample_h1_fixture_summary.md",
)
PYTHON_FILES = (
    "archive/prototypes/legacy_runtime/connectors/h1_metadata_wave/__init__.py",
    "archive/prototypes/legacy_runtime/connectors/h1_metadata_wave/fixture_loader.py",
    "archive/prototypes/legacy_runtime/connectors/h1_metadata_wave/normalizer_common.py",
    "archive/prototypes/legacy_runtime/connectors/h1_metadata_wave/wayback_cdx_memento.py",
    "archive/prototypes/legacy_runtime/connectors/h1_metadata_wave/github_releases.py",
    "archive/prototypes/legacy_runtime/connectors/h1_metadata_wave/pypi.py",
    "archive/prototypes/legacy_runtime/connectors/h1_metadata_wave/npm_registry.py",
    "archive/prototypes/legacy_runtime/connectors/h1_metadata_wave/software_heritage.py",
    "archive/prototypes/legacy_runtime/connectors/h1_metadata_wave/repology.py",
    "archive/prototypes/legacy_runtime/connectors/h1_metadata_wave/osv.py",
    "scripts/normalize_h1_metadata_fixture.py",
    "scripts/replay_h1_metadata_fixtures.py",
    "scripts/validate_h1_metadata_fixture_runtime.py",
)
BANNED_IMPORT_RE = re.compile(
    r"^\s*(?:from|import)\s+"
    r"(requests|urllib|httpx|aiohttp|socket|ftplib|smtplib|webbrowser|selenium|playwright|openai|anthropic)\b",
    re.MULTILINE,
)
SECRET_KEY_RE = re.compile(
    r'"[^"]*(api[_-]?key|api[_-]?token|access[_-]?token|auth[_-]?token|client_secret|password|private_key|cookie)[^"]*"\s*:',
    re.IGNORECASE,
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print JSON validation result.")
    args = parser.parse_args(argv)
    result = validate_repo(REPO_ROOT)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print("H1 metadata fixture runtime validation", file=stdout)
        print(f"status: {result['status']}", file=stdout)
        for error in result["errors"]:
            print(f"ERROR: {error}", file=stdout)
    return 0 if result["status"] == "valid" else 1


def validate_repo(root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    payloads: dict[str, dict[str, Any]] = {}
    for rel in CONTRACTS + POLICIES + DOCS + AUDIT_FILES + PYTHON_FILES:
        path = root / rel
        if not path.is_file():
            errors.append(f"missing required file: {rel}")
        elif path.suffix == ".json":
            payloads[rel] = load_json_object(path, errors)
    validate_policy_payloads(payloads, errors)
    validate_fixture_examples(root, errors)
    validate_normalized_examples(root, errors)
    validate_replay_examples(root, errors)
    validate_runtime_imports(errors)
    validate_python_no_network(root, errors)
    validate_script_offline_behavior(root, errors)
    validate_audit_report(payloads.get("control/audits/h1-bundle-02-metadata-fixture-runtime-v0/h1_bundle_02_report.json", {}), errors)
    validate_no_private_roots(root, errors)
    return {
        "schema_version": "h1_metadata_fixture_runtime_validation.v0",
        "status": "valid" if not errors else "invalid",
        "task": "H1-BUNDLE-02",
        "source_count": len(H1_SOURCE_IDS),
        "offline_default": True,
        "network_calls_made": False,
        "errors": errors,
    }


def load_json_object(path: Path, errors: list[str]) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        errors.append(f"invalid JSON: {path.relative_to(REPO_ROOT)}: {exc}")
        return {}
    if not isinstance(payload, dict):
        errors.append(f"JSON root must be object: {path.relative_to(REPO_ROOT)}")
        return {}
    return payload


def validate_policy_payloads(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    runtime_policy = payloads.get("control/inventory/connectors/h1_metadata_fixture_runtime_policy.json", {})
    for key in ("live_access_enabled", "source_sync_enabled", "connector_runtime_enabled_for_live"):
        if runtime_policy.get(key) is not False:
            errors.append(f"runtime policy {key} must be false")
    truth_policy = payloads.get("control/inventory/connectors/h1_metadata_fixture_truth_policy.json", {})
    for key in (
        "normalized_record_is_public_truth",
        "source_cache_preview_is_accepted_source",
        "evidence_preview_is_accepted_evidence",
        "fixture_replay_result_is_source_truth",
        "fixture_replay_can_mutate_public_index",
        "fixture_replay_can_mutate_master_index",
        "fixture_replay_can_claim_rights_clearance",
        "fixture_replay_can_claim_malware_safety",
        "fixture_replay_can_claim_verified_installability",
    ):
        if truth_policy.get(key) is not False:
            errors.append(f"truth policy {key} must be false")
    for rel in POLICIES:
        errors.extend(f"{rel}: {item}" for item in detect_h1_truth_boundary_violations(payloads.get(rel, {})))
        errors.extend(f"{rel}: {item}" for item in detect_h1_product_boundary_violations(payloads.get(rel, {})))


def validate_fixture_examples(root: Path, errors: list[str]) -> None:
    for source_id in H1_SOURCE_IDS:
        for fixture_kind in ("minimal", "typical", "policy_blocked"):
            rel = f"examples/connectors/h1_metadata_wave/fixtures/{source_id}/{fixture_kind}_record.json"
            path = root / rel
            if not path.is_file():
                errors.append(f"missing fixture: {rel}")
                continue
            fixture = load_json_object(path, errors)
            errors.extend(f"{rel}: {item}" for item in validate_h1_fixture(fixture))
            if fixture.get("source_id") != source_id:
                errors.append(f"{rel}: source_id mismatch")
            if fixture.get("fixture_kind") != fixture_kind:
                errors.append(f"{rel}: fixture_kind mismatch")
            validate_no_secret_text(path, errors)


def validate_normalized_examples(root: Path, errors: list[str]) -> None:
    for source_id in H1_SOURCE_IDS:
        rel = f"examples/connectors/h1_metadata_wave/normalized/{source_id}_normalized.json"
        path = root / rel
        if not path.is_file():
            errors.append(f"missing normalized example: {rel}")
            continue
        record = load_json_object(path, errors)
        errors.extend(f"{rel}: {item}" for item in validate_normalized_record(record, source_id))


def validate_replay_examples(root: Path, errors: list[str]) -> None:
    for source_id in H1_SOURCE_IDS:
        rel = f"examples/connectors/h1_metadata_wave/replay_results/{source_id}_replay_result.json"
        path = root / rel
        if not path.is_file():
            errors.append(f"missing replay result example: {rel}")
            continue
        result = load_json_object(path, errors)
        errors.extend(f"{rel}: {item}" for item in validate_replay_result(result, source_id))


def validate_normalized_record(record: Mapping[str, Any], expected_source_id: str | None = None) -> list[str]:
    errors: list[str] = []
    if record.get("schema_version") != "h1_metadata_normalized_record.v0":
        errors.append("schema_version must be h1_metadata_normalized_record.v0")
    if expected_source_id and record.get("source_id") != expected_source_id:
        errors.append(f"source_id must be {expected_source_id}")
    for key in ("source_native_id", "source_locator", "title", "artifact_type", "source_cache_candidate_preview", "evidence_candidate_preview"):
        if record.get(key) in (None, "", [], {}):
            errors.append(f"normalized record missing {key}")
    errors.extend(detect_h1_truth_boundary_violations(record))
    errors.extend(detect_h1_product_boundary_violations(record))
    source_cache = record.get("source_cache_candidate_preview", {})
    evidence = record.get("evidence_candidate_preview", {})
    if isinstance(source_cache, Mapping) and source_cache.get("accepted_source_truth") is not False:
        errors.append("source-cache preview must not accept source truth")
    if isinstance(evidence, Mapping) and evidence.get("accepted_evidence") is not False:
        errors.append("evidence preview must not accept evidence")
    return errors


def validate_replay_result(result: Mapping[str, Any], expected_source_id: str | None = None) -> list[str]:
    errors: list[str] = []
    if result.get("schema_version") != "h1_metadata_fixture_replay_result.v0":
        errors.append("schema_version must be h1_metadata_fixture_replay_result.v0")
    if expected_source_id and result.get("source_id") != expected_source_id:
        errors.append(f"source_id must be {expected_source_id}")
    if result.get("no_network_used") is not True:
        errors.append("no_network_used must be true")
    if result.get("no_live_source_used") is not True:
        errors.append("no_live_source_used must be true")
    errors.extend(detect_h1_truth_boundary_violations(result))
    errors.extend(detect_h1_product_boundary_violations(result))
    return errors


def validate_runtime_imports(errors: list[str]) -> None:
    for source_id in H1_SOURCE_IDS:
        try:
            module = importlib.import_module(f"archive.prototypes.legacy_runtime.connectors.h1_metadata_wave.{source_id}")
        except Exception as exc:  # noqa: BLE001
            errors.append(f"failed to import normalizer {source_id}: {exc}")
            continue
        fixture_path = REPO_ROOT / f"examples/connectors/h1_metadata_wave/fixtures/{source_id}/typical_record.json"
        if fixture_path.is_file():
            try:
                fixture = load_h1_fixture(fixture_path)
                record = module.normalize(fixture)
                build_h1_fixture_replay_result(fixture, record)
            except Exception as exc:  # noqa: BLE001
                errors.append(f"normalizer failed for {source_id}: {exc}")


def validate_python_no_network(root: Path, errors: list[str]) -> None:
    for rel in PYTHON_FILES:
        path = root / rel
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        match = BANNED_IMPORT_RE.search(text)
        if match:
            errors.append(f"{rel}: forbidden network/model/browser import {match.group(1)}")
        if ("url" + "open(") in text or (".Re" + "quest(") in text:
            errors.append(f"{rel}: forbidden live-call primitive")


def validate_script_offline_behavior(root: Path, errors: list[str]) -> None:
    commands = (
        [sys.executable, "scripts/normalize_h1_metadata_fixture.py", "--source-id", "pypi", "--input", "examples/connectors/h1_metadata_wave/fixtures/pypi/typical_record.json", "--check"],
        [sys.executable, "scripts/replay_h1_metadata_fixtures.py", "--check"],
    )
    for command in commands:
        result = subprocess.run(command, cwd=root, check=False, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            errors.append(f"offline script failed: {' '.join(command)}: {result.stdout}{result.stderr}")
    bad = subprocess.run([sys.executable, "scripts/normalize_h1_metadata_fixture.py", "--source-id", "pypi", "--input", "examples/connectors/h1_metadata_wave/fixtures/pypi/typical_record.json", "--output", "site/dist/h1.json"], cwd=root, check=False, capture_output=True, text=True, timeout=120)
    if bad.returncode == 0:
        errors.append("normalizer script must refuse site/dist output")
    bad_public = subprocess.run([sys.executable, "scripts/replay_h1_metadata_fixtures.py", "--output-dir", "site/dist/data/public_index/h1"], cwd=root, check=False, capture_output=True, text=True, timeout=120)
    if bad_public.returncode == 0:
        errors.append("replay script must refuse site/dist/data/public_index output")


def validate_audit_report(report: Mapping[str, Any], errors: list[str]) -> None:
    if not report:
        return
    if report.get("schema_version") != "h1_bundle_02_report.v0":
        errors.append("h1 bundle 02 report schema_version mismatch")
    if sorted(report.get("sources", [])) != sorted(H1_SOURCE_IDS):
        errors.append("h1 bundle 02 report must list all H1 sources")
    fixture_scope = report.get("fixture_runtime_scope", {})
    if isinstance(fixture_scope, Mapping):
        for key in ("live_access_enabled", "source_sync_enabled", "network_calls_made"):
            if fixture_scope.get(key) is not False:
                errors.append(f"h1 bundle 02 report fixture_runtime_scope.{key} must be false")
    errors.extend(f"h1_bundle_02_report: {item}" for item in detect_h1_truth_boundary_violations(report))
    errors.extend(f"h1_bundle_02_report: {item}" for item in detect_h1_product_boundary_violations(report))


def validate_no_secret_text(path: Path, errors: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    if SECRET_KEY_RE.search(text):
        errors.append(f"{path.relative_to(REPO_ROOT)} contains credential/cookie/token-like key")


def validate_no_private_roots(root: Path, errors: list[str]) -> None:
    for rel in (".aide.local", ".local/eureka", ".cache/eureka"):
        if (root / rel).exists():
            errors.append(f"local private-state root must not exist: {rel}")


if __name__ == "__main__":
    raise SystemExit(main())
