#!/usr/bin/env python3
"""Validate H3 OS package archive fixture runtime artifacts offline."""

from __future__ import annotations

import argparse
import importlib
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.connectors.h3_os_package_archives.fixture_loader import load_h3_os_package_fixture, validate_h3_os_package_fixture  # noqa: E402
from runtime.connectors.h3_os_package_archives.normalizer_common import (  # noqa: E402
    H3_SOURCE_IDS,
    build_h3_fixture_replay_result,
    detect_h3_product_boundary_violations,
    detect_h3_truth_boundary_violations,
)


CONTRACTS = (
    "control/schemas/fixtures/h3/connectors/os_package_fixture.v0.json",
    "control/schemas/previews/h3/connectors/os_package_normalized_record.v0.json",
    "control/schemas/previews/h3/connectors/os_package_identity_candidate.v0.json",
    "control/schemas/previews/h3/connectors/os_platform_compatibility_candidate.v0.json",
    "control/schemas/previews/h3/connectors/os_package_dependency_candidate.v0.json",
    "control/schemas/previews/h3/connectors/os_package_file_candidate.v0.json",
    "control/schemas/fixtures/h3/connectors/os_package_fixture_replay_result.v0.json",
)
POLICIES = (
    "control/inventory/connectors/h3_os_package_fixture_runtime_policy.json",
    "control/inventory/connectors/h3_os_package_normalization_policy.json",
    "control/inventory/connectors/h3_os_package_identity_mapping_policy.json",
    "control/inventory/connectors/h3_os_platform_compatibility_mapping_policy.json",
    "control/inventory/connectors/h3_os_package_dependency_mapping_policy.json",
    "control/inventory/connectors/h3_os_package_file_metadata_policy.json",
    "control/inventory/connectors/h3_os_package_fixture_output_policy.json",
    "control/inventory/connectors/h3_os_package_fixture_path_policy.json",
    "control/inventory/connectors/h3_os_package_fixture_truth_policy.json",
    "control/inventory/connectors/h3_os_package_source_cache_mapping_policy.json",
    "control/inventory/connectors/h3_os_package_evidence_mapping_policy.json",
    "control/inventory/connectors/h3_os_package_no_download_policy.json",
)
DOCS = (
    "docs/reference/H3_OS_PACKAGE_FIXTURE_RUNTIME.md",
    "docs/reference/H3_OS_PACKAGE_NORMALIZED_RECORD.md",
    "docs/reference/H3_OS_PACKAGE_IDENTITY_CANDIDATE.md",
    "docs/reference/H3_OS_PLATFORM_COMPATIBILITY_CANDIDATE.md",
    "docs/reference/H3_OS_PACKAGE_DEPENDENCY_CANDIDATE.md",
    "docs/architecture/H3_OS_PACKAGE_NORMALIZER_MODEL.md",
    "docs/architecture/H3_OS_PACKAGE_IDENTITY_MODEL.md",
    "docs/architecture/H3_OS_PLATFORM_COMPATIBILITY_MODEL.md",
    "docs/operations/H3_OS_PACKAGE_FIXTURE_REPLAY.md",
    "docs/operations/H3_OS_PACKAGE_FIXTURE_NO_LIVE_CALL_POLICY.md",
    "docs/operations/H3_OS_PACKAGE_FIXTURE_NO_DOWNLOAD_POLICY.md",
)
AUDIT_FILES = (
    "control/audits/h3-bundle-02-os-package-fixture-runtime-v0/README.md",
    "control/audits/h3-bundle-02-os-package-fixture-runtime-v0/h3_bundle_02_report.json",
    "control/audits/h3-bundle-02-os-package-fixture-runtime-v0/fixture_runtime_summary.md",
    "control/audits/h3-bundle-02-os-package-fixture-runtime-v0/normalizer_coverage_summary.md",
    "control/audits/h3-bundle-02-os-package-fixture-runtime-v0/os_package_identity_mapping_summary.md",
    "control/audits/h3-bundle-02-os-package-fixture-runtime-v0/os_platform_compatibility_mapping_summary.md",
    "control/audits/h3-bundle-02-os-package-fixture-runtime-v0/dependency_conflict_provides_mapping_preview.md",
    "control/audits/h3-bundle-02-os-package-fixture-runtime-v0/source_cache_mapping_preview.md",
    "control/audits/h3-bundle-02-os-package-fixture-runtime-v0/evidence_mapping_preview.md",
    "control/audits/h3-bundle-02-os-package-fixture-runtime-v0/no_live_call_report.md",
    "control/audits/h3-bundle-02-os-package-fixture-runtime-v0/no_download_report.md",
    "control/audits/h3-bundle-02-os-package-fixture-runtime-v0/validation.md",
    "control/audits/h3-bundle-02-os-package-fixture-runtime-v0/generated/sample_h3_normalized_record.json",
    "control/audits/h3-bundle-02-os-package-fixture-runtime-v0/generated/sample_h3_os_package_identity_candidate.json",
    "control/audits/h3-bundle-02-os-package-fixture-runtime-v0/generated/sample_h3_os_platform_compatibility_candidate.json",
    "control/audits/h3-bundle-02-os-package-fixture-runtime-v0/generated/sample_h3_dependency_candidate.json",
    "control/audits/h3-bundle-02-os-package-fixture-runtime-v0/generated/sample_h3_source_cache_candidate.json",
    "control/audits/h3-bundle-02-os-package-fixture-runtime-v0/generated/sample_h3_evidence_candidate_preview.json",
    "control/audits/h3-bundle-02-os-package-fixture-runtime-v0/generated/sample_h3_fixture_replay_result.json",
    "control/audits/h3-bundle-02-os-package-fixture-runtime-v0/generated/sample_h3_fixture_summary.md",
)
PYTHON_FILES = (
    "runtime/connectors/h3_os_package_archives/__init__.py",
    "runtime/connectors/h3_os_package_archives/fixture_loader.py",
    "runtime/connectors/h3_os_package_archives/normalizer_common.py",
    "runtime/connectors/h3_os_package_archives/os_package_identity.py",
    "runtime/connectors/h3_os_package_archives/os_platform_compatibility.py",
    *(f"runtime/connectors/h3_os_package_archives/{source_id}.py" for source_id in H3_SOURCE_IDS),
    "scripts/normalize_h3_os_package_fixture.py",
    "scripts/replay_h3_os_package_fixtures.py",
    "scripts/validate_h3_os_package_archive_fixture_runtime.py",
    "scripts/summarize_h3_os_package_fixture_outputs.py",
)
IDENTITY_EXAMPLES = (
    "examples/connectors/h3_os_package_archives/identity/os_package_identity_candidate_v0.json",
    "examples/connectors/h3_os_package_archives/identity/purl_candidate_v0.json",
    "examples/connectors/h3_os_package_archives/identity/os_platform_compatibility_candidate_v0.json",
    "examples/connectors/h3_os_package_archives/identity/dependency_candidate_v0.json",
    "examples/connectors/h3_os_package_archives/identity/conflict_candidate_v0.json",
    "examples/connectors/h3_os_package_archives/identity/provides_candidate_v0.json",
    "examples/connectors/h3_os_package_archives/identity/package_file_candidate_v0.json",
    "examples/connectors/h3_os_package_archives/identity/policy_blocked_identity_candidate_v0.json",
)
REQUIRED_FIXTURE_KINDS = ("minimal", "typical", "dependency", "architecture", "compatibility", "policy_blocked")
BANNED_IMPORT_RE = re.compile(
    r"^\s*(?:from|import)\s+"
    r"(requests|urllib|httpx|aiohttp|socket|ftplib|smtplib|webbrowser|selenium|playwright|openai|anthropic)\b",
    re.MULTILINE,
)
SECRET_KEY_RE = re.compile(
    r'"[^"]*(api[_-]?key|api[_-]?token|access[_-]?token|auth[_-]?token|client_secret|password|private_key|cookie)[^"]*"\s*:',
    re.IGNORECASE,
)
PACKAGE_BYTES_RE = re.compile(
    r'"[^"]*(payload_bytes|deb_bytes|rpm_bytes|pkg_bytes|nupkg_bytes|flatpak_bytes|snap_bytes|tarball_bytes|layer_bytes|executable_payload|repository_index_bytes|repository_index_dump)[^"]*"\s*:',
    re.IGNORECASE,
)
PACKAGE_MANAGER_CALL_RE = re.compile(
    r"(os\.system|subprocess\.(?:run|call|Popen)).*(apt|dnf|yum|rpm|pacman|pkg|brew|port|nix|winget|choco|flatpak|snap)",
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
        print("H3 OS package fixture runtime validation", file=stdout)
        print(f"status: {result['status']}", file=stdout)
        for error in result["errors"]:
            print(f"ERROR: {error}", file=stdout)
    return 0 if result["status"] == "valid" else 1


def validate_repo(root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    payloads: dict[str, dict[str, Any]] = {}
    for rel in CONTRACTS + POLICIES + DOCS + AUDIT_FILES + PYTHON_FILES + IDENTITY_EXAMPLES:
        path = root / rel
        if not path.is_file():
            errors.append(f"missing required file: {rel}")
        elif path.suffix == ".json":
            payloads[rel] = load_json_object(path, errors)
    validate_policy_payloads(payloads, errors)
    validate_fixture_examples(root, errors)
    validate_normalized_examples(root, errors)
    validate_replay_examples(root, errors)
    validate_identity_examples(payloads, errors)
    validate_runtime_imports(errors)
    validate_python_no_network(root, errors)
    validate_script_offline_behavior(root, errors)
    validate_audit_report(payloads.get("control/audits/h3-bundle-02-os-package-fixture-runtime-v0/h3_bundle_02_report.json", {}), errors)
    validate_no_private_roots(root, errors)
    return {
        "schema_version": "h3_os_package_fixture_runtime_validation.v0",
        "status": "valid" if not errors else "invalid",
        "task": "H3-BUNDLE-02",
        "source_count": len(H3_SOURCE_IDS),
        "offline_default": True,
        "network_calls_made": False,
        "repository_index_fetches_made": False,
        "package_downloads_made": False,
        "package_manager_invocations_made": False,
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
    runtime_policy = payloads.get("control/inventory/connectors/h3_os_package_fixture_runtime_policy.json", {})
    expected_false = (
        "live_access_enabled",
        "source_sync_enabled",
        "connector_runtime_enabled_for_live",
        "repository_index_fetch_enabled",
        "package_download_enabled",
        "package_manager_invocation_enabled",
        "install_execute_enabled",
    )
    for key in expected_false:
        if runtime_policy.get(key) is not False:
            errors.append(f"runtime policy {key} must be false")
    for rel in POLICIES:
        errors.extend(f"{rel}: {item}" for item in detect_h3_truth_boundary_violations(payloads.get(rel, {})))
        errors.extend(f"{rel}: {item}" for item in detect_h3_product_boundary_violations(payloads.get(rel, {})))


def validate_fixture_examples(root: Path, errors: list[str]) -> None:
    for source_id in H3_SOURCE_IDS:
        for fixture_kind in REQUIRED_FIXTURE_KINDS:
            rel = f"examples/connectors/h3_os_package_archives/fixtures/{source_id}/{fixture_kind}_record.json"
            path = root / rel
            if not path.is_file():
                errors.append(f"missing fixture: {rel}")
                continue
            fixture = load_json_object(path, errors)
            errors.extend(f"{rel}: {item}" for item in validate_h3_os_package_fixture(fixture))
            if fixture.get("source_id") != source_id:
                errors.append(f"{rel}: source_id mismatch")
            if fixture.get("fixture_kind") != fixture_kind:
                errors.append(f"{rel}: fixture_kind mismatch")
            validate_no_secret_or_payload_text(path, errors)


def validate_normalized_examples(root: Path, errors: list[str]) -> None:
    for source_id in H3_SOURCE_IDS:
        rel = f"examples/connectors/h3_os_package_archives/normalized/{source_id}_normalized.json"
        path = root / rel
        if not path.is_file():
            errors.append(f"missing normalized example: {rel}")
            continue
        record = load_json_object(path, errors)
        errors.extend(f"{rel}: {item}" for item in validate_normalized_record(record, source_id))


def validate_replay_examples(root: Path, errors: list[str]) -> None:
    for source_id in H3_SOURCE_IDS:
        rel = f"examples/connectors/h3_os_package_archives/replay_results/{source_id}_replay_result.json"
        path = root / rel
        if not path.is_file():
            errors.append(f"missing replay result example: {rel}")
            continue
        result = load_json_object(path, errors)
        errors.extend(f"{rel}: {item}" for item in validate_replay_result(result, source_id))


def validate_identity_examples(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    for rel in IDENTITY_EXAMPLES:
        payload = payloads.get(rel, {})
        errors.extend(f"{rel}: {item}" for item in detect_h3_truth_boundary_violations(payload))
        errors.extend(f"{rel}: {item}" for item in detect_h3_product_boundary_violations(payload))


def validate_normalized_record(record: Mapping[str, Any], expected_source_id: str | None = None) -> list[str]:
    errors: list[str] = []
    if record.get("schema_version") != "h3_os_package_normalized_record.v0":
        errors.append("schema_version must be h3_os_package_normalized_record.v0")
    if expected_source_id and record.get("source_id") != expected_source_id:
        errors.append(f"source_id must be {expected_source_id}")
    for key in ("source_native_id", "package_locator", "ecosystem", "distribution", "package_name", "os_package_identity_candidate", "os_platform_compatibility_candidate", "source_cache_candidate_preview", "evidence_candidate_preview"):
        if record.get(key) in (None, "", [], {}):
            errors.append(f"normalized record missing {key}")
    errors.extend(detect_h3_truth_boundary_violations(record))
    errors.extend(detect_h3_product_boundary_violations(record))
    identity = record.get("os_package_identity_candidate", {})
    compatibility = record.get("os_platform_compatibility_candidate", {})
    source_cache = record.get("source_cache_candidate_preview", {})
    evidence = record.get("evidence_candidate_preview", {})
    if isinstance(identity, Mapping) and identity.get("truth_boundary", {}).get("identity_candidate_is_accepted_identity") is not False:
        errors.append("identity candidate must not be accepted identity")
    if isinstance(compatibility, Mapping) and compatibility.get("truth_boundary", {}).get("compatibility_candidate_is_verified_compatibility") is not False:
        errors.append("compatibility candidate must not be verified compatibility")
    if isinstance(source_cache, Mapping) and source_cache.get("accepted_source_truth") is not False:
        errors.append("source-cache preview must not accept source truth")
    if isinstance(evidence, Mapping) and evidence.get("accepted_evidence") is not False:
        errors.append("evidence preview must not accept evidence")
    return errors


def validate_replay_result(result: Mapping[str, Any], expected_source_id: str | None = None) -> list[str]:
    errors: list[str] = []
    if result.get("schema_version") != "h3_os_package_fixture_replay_result.v0":
        errors.append("schema_version must be h3_os_package_fixture_replay_result.v0")
    if expected_source_id and result.get("source_id") != expected_source_id:
        errors.append(f"source_id must be {expected_source_id}")
    for key in ("no_network_used", "no_live_source_used", "no_repository_index_fetch_used", "no_package_download_used", "no_package_manager_invoked"):
        if result.get(key) is not True:
            errors.append(f"{key} must be true")
    errors.extend(detect_h3_truth_boundary_violations(result))
    errors.extend(detect_h3_product_boundary_violations(result))
    return errors


def validate_runtime_imports(errors: list[str]) -> None:
    for source_id in H3_SOURCE_IDS:
        try:
            module = importlib.import_module(f"runtime.connectors.h3_os_package_archives.{source_id}")
        except Exception as exc:  # noqa: BLE001
            errors.append(f"failed to import normalizer {source_id}: {exc}")
            continue
        fixture_path = REPO_ROOT / f"examples/connectors/h3_os_package_archives/fixtures/{source_id}/typical_record.json"
        if fixture_path.is_file():
            try:
                fixture = load_h3_os_package_fixture(fixture_path)
                record = module.normalize(fixture)
                build_h3_fixture_replay_result(fixture, record)
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
        if rel.startswith("runtime/") and PACKAGE_MANAGER_CALL_RE.search(text):
            errors.append(f"{rel}: forbidden package-manager invocation primitive")


def validate_script_offline_behavior(root: Path, errors: list[str]) -> None:
    commands = (
        [sys.executable, "scripts/normalize_h3_os_package_fixture.py", "--source-id", "debian_snapshot", "--input", "examples/connectors/h3_os_package_archives/fixtures/debian_snapshot/typical_record.json", "--check"],
        [sys.executable, "scripts/replay_h3_os_package_fixtures.py", "--check"],
        [sys.executable, "scripts/summarize_h3_os_package_fixture_outputs.py", "--input", "examples/connectors/h3_os_package_archives", "--check"],
    )
    for command in commands:
        result = subprocess.run(command, cwd=root, check=False, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            errors.append(f"offline script failed: {' '.join(command)}: {result.stdout}{result.stderr}")
    bad = subprocess.run([sys.executable, "scripts/normalize_h3_os_package_fixture.py", "--source-id", "debian_snapshot", "--input", "examples/connectors/h3_os_package_archives/fixtures/debian_snapshot/typical_record.json", "--output", "site/dist/h3.json"], cwd=root, check=False, capture_output=True, text=True, timeout=120)
    if bad.returncode == 0:
        errors.append("normalizer script must refuse site/dist output")
    bad_public = subprocess.run([sys.executable, "scripts/replay_h3_os_package_fixtures.py", "--output-dir", "data/public_index/h3"], cwd=root, check=False, capture_output=True, text=True, timeout=120)
    if bad_public.returncode == 0:
        errors.append("replay script must refuse data/public_index output")


def validate_audit_report(report: Mapping[str, Any], errors: list[str]) -> None:
    if not report:
        return
    if report.get("schema_version") != "h3_bundle_02_report.v0":
        errors.append("h3 bundle 02 report schema_version mismatch")
    if sorted(report.get("sources", [])) != sorted(H3_SOURCE_IDS):
        errors.append("h3 bundle 02 report must list all H3 sources")
    fixture_scope = report.get("fixture_runtime_scope", {})
    if isinstance(fixture_scope, Mapping):
        for key in ("live_access_enabled", "source_sync_enabled", "repository_index_fetch_enabled", "package_download_enabled", "package_manager_invocation_enabled", "install_execute_enabled", "network_calls_made"):
            if fixture_scope.get(key) is not False:
                errors.append(f"h3 bundle 02 report fixture_runtime_scope.{key} must be false")
    errors.extend(f"h3_bundle_02_report: {item}" for item in detect_h3_truth_boundary_violations(report))
    errors.extend(f"h3_bundle_02_report: {item}" for item in detect_h3_product_boundary_violations(report))


def validate_no_secret_or_payload_text(path: Path, errors: list[str]) -> None:
    text = path.read_text(encoding="utf-8")
    if SECRET_KEY_RE.search(text):
        errors.append(f"{path.relative_to(REPO_ROOT)} contains credential/cookie/token-like key")
    if PACKAGE_BYTES_RE.search(text):
        errors.append(f"{path.relative_to(REPO_ROOT)} contains package payload-like key")


def validate_no_private_roots(root: Path, errors: list[str]) -> None:
    for rel in (".aide.local", ".local/eureka", ".cache/eureka"):
        if (root / rel).exists():
            errors.append(f"local private-state root must not exist: {rel}")


if __name__ == "__main__":
    raise SystemExit(main())
