#!/usr/bin/env python3
"""Validate H4-BUNDLE-02 code/source/release fixture runtime offline."""

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

from control.prototypes.legacy_runtime.connectors.h4_code_source_release.fixture_loader import load_h4_code_source_fixture  # noqa: E402
from control.prototypes.legacy_runtime.connectors.h4_code_source_release.normalizer_common import (  # noqa: E402
    H4_FIXTURE_KINDS,
    H4_SOURCE_IDS,
    build_h4_fixture_replay_result,
    detect_h4_product_boundary_violations,
    detect_h4_truth_boundary_violations,
)

CONTRACT_FILES = ('control/schemas/fixtures/h4/connectors/code_source_fixture.v0.json', 'control/schemas/previews/h4/connectors/code_source_normalized_record.v0.json', 'control/schemas/previews/h4/connectors/source_identity_candidate.v0.json', 'control/schemas/previews/h4/connectors/release_identity_candidate.v0.json', 'control/schemas/previews/h4/connectors/source_to_binary_relation_candidate.v0.json', 'control/schemas/previews/h4/connectors/release_asset_candidate.v0.json', 'control/schemas/fixtures/h4/connectors/code_source_fixture_replay_result.v0.json')
POLICY_FILES = ('control/inventory/connectors/h4_code_source_fixture_runtime_policy.json', 'control/inventory/connectors/h4_code_source_normalization_policy.json', 'control/inventory/connectors/h4_source_identity_mapping_policy.json', 'control/inventory/connectors/h4_release_identity_mapping_policy.json', 'control/inventory/connectors/h4_source_to_binary_relation_mapping_policy.json', 'control/inventory/connectors/h4_release_asset_metadata_policy.json', 'control/inventory/connectors/h4_code_source_fixture_output_policy.json', 'control/inventory/connectors/h4_code_source_fixture_path_policy.json', 'control/inventory/connectors/h4_code_source_fixture_truth_policy.json', 'control/inventory/connectors/h4_code_source_source_cache_mapping_policy.json', 'control/inventory/connectors/h4_code_source_evidence_mapping_policy.json', 'control/inventory/connectors/h4_code_source_no_clone_download_policy.json')
DOC_FILES = ('docs/reference/H4_CODE_SOURCE_FIXTURE_RUNTIME.md', 'docs/reference/H4_CODE_SOURCE_NORMALIZED_RECORD.md', 'docs/reference/H4_SOURCE_IDENTITY_CANDIDATE.md', 'docs/reference/H4_RELEASE_IDENTITY_CANDIDATE.md', 'docs/reference/H4_SOURCE_TO_BINARY_RELATION_CANDIDATE.md', 'docs/reference/H4_RELEASE_ASSET_CANDIDATE.md', 'docs/architecture/H4_CODE_SOURCE_NORMALIZER_MODEL.md', 'docs/architecture/H4_SOURCE_IDENTITY_MODEL.md', 'docs/architecture/H4_RELEASE_IDENTITY_MODEL.md', 'docs/architecture/H4_SOURCE_TO_BINARY_RELATION_MODEL.md', 'docs/operations/H4_CODE_SOURCE_FIXTURE_REPLAY.md', 'docs/operations/H4_CODE_SOURCE_FIXTURE_NO_LIVE_CALL_POLICY.md', 'docs/operations/H4_CODE_SOURCE_FIXTURE_NO_CLONE_DOWNLOAD_POLICY.md')
AUDIT_FILES = ('control/audits/h4-bundle-02-code-source-fixture-runtime-v0/README.md', 'control/audits/h4-bundle-02-code-source-fixture-runtime-v0/h4_bundle_02_report.json', 'control/audits/h4-bundle-02-code-source-fixture-runtime-v0/fixture_runtime_summary.md', 'control/audits/h4-bundle-02-code-source-fixture-runtime-v0/normalizer_coverage_summary.md', 'control/audits/h4-bundle-02-code-source-fixture-runtime-v0/source_identity_mapping_summary.md', 'control/audits/h4-bundle-02-code-source-fixture-runtime-v0/release_identity_mapping_summary.md', 'control/audits/h4-bundle-02-code-source-fixture-runtime-v0/source_to_binary_relation_mapping_summary.md', 'control/audits/h4-bundle-02-code-source-fixture-runtime-v0/release_asset_metadata_mapping_preview.md', 'control/audits/h4-bundle-02-code-source-fixture-runtime-v0/source_cache_mapping_preview.md', 'control/audits/h4-bundle-02-code-source-fixture-runtime-v0/evidence_mapping_preview.md', 'control/audits/h4-bundle-02-code-source-fixture-runtime-v0/no_live_call_report.md', 'control/audits/h4-bundle-02-code-source-fixture-runtime-v0/no_clone_download_report.md', 'control/audits/h4-bundle-02-code-source-fixture-runtime-v0/validation.md', 'control/audits/h4-bundle-02-code-source-fixture-runtime-v0/generated/sample_h4_normalized_record.json', 'control/audits/h4-bundle-02-code-source-fixture-runtime-v0/generated/sample_h4_source_identity_candidate.json', 'control/audits/h4-bundle-02-code-source-fixture-runtime-v0/generated/sample_h4_release_identity_candidate.json', 'control/audits/h4-bundle-02-code-source-fixture-runtime-v0/generated/sample_h4_source_to_binary_relation_candidate.json', 'control/audits/h4-bundle-02-code-source-fixture-runtime-v0/generated/sample_h4_release_asset_candidate.json', 'control/audits/h4-bundle-02-code-source-fixture-runtime-v0/generated/sample_h4_source_cache_candidate.json', 'control/audits/h4-bundle-02-code-source-fixture-runtime-v0/generated/sample_h4_evidence_candidate_preview.json', 'control/audits/h4-bundle-02-code-source-fixture-runtime-v0/generated/sample_h4_fixture_replay_result.json', 'control/audits/h4-bundle-02-code-source-fixture-runtime-v0/generated/sample_h4_fixture_summary.md')
PYTHON_FILES = ('scripts/normalize_h4_code_source_fixture.py', 'scripts/replay_h4_code_source_fixtures.py', 'scripts/validate_h4_code_source_release_fixture_runtime.py', 'scripts/summarize_h4_code_source_fixture_outputs.py')
TEST_FILES = ('tests/connectors/test_h4_code_source_fixture_runtime.py', 'tests/connectors/test_h4_source_identity_mapping.py', 'tests/connectors/test_h4_release_identity_mapping.py', 'tests/connectors/test_h4_source_to_binary_relation_mapping.py', 'tests/operations/test_h4_code_source_fixture_scripts.py')
IDENTITY_EXAMPLES = (
    "examples/connectors/h4_code_source_release/identity/source_identity_candidate_v0.json",
    "examples/connectors/h4_code_source_release/identity/release_identity_candidate_v0.json",
    "examples/connectors/h4_code_source_release/identity/source_to_binary_relation_candidate_v0.json",
    "examples/connectors/h4_code_source_release/identity/release_asset_candidate_v0.json",
    "examples/connectors/h4_code_source_release/identity/swhid_candidate_v0.json",
    "examples/connectors/h4_code_source_release/identity/git_object_candidate_v0.json",
    "examples/connectors/h4_code_source_release/identity/policy_blocked_identity_candidate_v0.json",
)
FIXTURE_ROOT = Path("examples/connectors/h4_code_source_release/fixtures")
NORMALIZED_ROOT = Path("examples/connectors/h4_code_source_release/normalized")
REPLAY_ROOT = Path("examples/connectors/h4_code_source_release/replay_results")

BANNED_IMPORT_RE = re.compile(
    r"^\s*(?:from|import)\s+"
    r"(requests|urllib|httpx|aiohttp|socket|ftplib|smtplib|webbrowser|selenium|playwright|openai|anthropic)\b",
    re.MULTILINE,
)
TOOL_COMMAND_RE = re.compile(
    r"(subprocess\.|os\.system|Popen\(|run\().*\b(git|make|cmake|ninja|npm|yarn|pnpm|pip|poetry|cargo|go|mvn|gradle|installer)\b",
    re.IGNORECASE | re.DOTALL,
)
SECRET_KEY_RE = re.compile(
    r'"[^"]*(api[_-]?key|api[_-]?token|access[_-]?token|auth[_-]?token|client_secret|password|private_key|cookie)[^"]*"\s*:',
    re.IGNORECASE,
)
PAYLOAD_RE = re.compile(
    r'"[^"]*(repository_payload_bytes|cloned_repository|repo_bytes|git_pack_bytes|source_archive_bytes|release_asset_payload_bytes|release_asset_bytes|binary_payload|installer_bytes|tarball_bytes|zip_bytes|git_command_output|build_tool_output|package_manager_output|executable_payload)[^"]*"\s*:',
    re.IGNORECASE,
)
FORBIDDEN_TEXT_CLAIMS = (
    "rights clearance granted",
    "malware safety established",
    "production readiness claimed",
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print JSON validation result.")
    args = parser.parse_args(argv)
    result = validate_repo(REPO_ROOT)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print("H4 code/source fixture runtime validation", file=stdout)
        print(f"status: {result['status']}", file=stdout)
        print(f"errors: {len(result['errors'])}", file=stdout)
        for error in result["errors"]:
            print(f"- {error}", file=stdout)
    return 0 if result["status"] == "valid" else 1


def validate_repo(root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    required_paths = list(CONTRACT_FILES + POLICY_FILES + DOC_FILES + AUDIT_FILES + PYTHON_FILES + TEST_FILES + IDENTITY_EXAMPLES)
    for source_id in H4_SOURCE_IDS:
        for kind in H4_FIXTURE_KINDS:
            filename = "policy_blocked_record.json" if kind == "policy_blocked" else f"{kind}_record.json"
            required_paths.append(str(FIXTURE_ROOT / source_id / filename))
        required_paths.append(str(NORMALIZED_ROOT / f"{source_id}_normalized.json"))
        required_paths.append(str(REPLAY_ROOT / f"{source_id}_replay_result.json"))
        required_paths.append(f"control/prototypes/legacy_runtime/connectors/h4_code_source_release/{source_id}.py")
    required_paths.extend([
        "control/prototypes/legacy_runtime/connectors/h4_code_source_release/__init__.py",
        "control/prototypes/legacy_runtime/connectors/h4_code_source_release/fixture_loader.py",
        "control/prototypes/legacy_runtime/connectors/h4_code_source_release/normalizer_common.py",
        "control/prototypes/legacy_runtime/connectors/h4_code_source_release/source_identity.py",
        "control/prototypes/legacy_runtime/connectors/h4_code_source_release/release_identity.py",
        "control/prototypes/legacy_runtime/connectors/h4_code_source_release/source_to_binary_relation.py",
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
        "schema_version": "h4_code_source_fixture_runtime_validation.v0",
        "status": "valid" if not errors else "invalid",
        "errors": errors,
        "source_count": len(H4_SOURCE_IDS),
        "fixture_kinds": list(H4_FIXTURE_KINDS),
        "network_calls_made": False,
        "repository_clones_made": False,
        "source_archive_downloads_made": False,
        "release_asset_downloads_made": False,
        "git_command_invocations_made": False,
        "build_tool_invocations_made": False,
    }


def validate_fixtures(root: Path, errors: list[str]) -> None:
    for source_id in H4_SOURCE_IDS:
        normalizer = importlib.import_module(f"control.prototypes.legacy_runtime.connectors.h4_code_source_release.{source_id}").normalize
        for kind in H4_FIXTURE_KINDS:
            filename = "policy_blocked_record.json" if kind == "policy_blocked" else f"{kind}_record.json"
            rel = FIXTURE_ROOT / source_id / filename
            path = root / rel
            if not path.is_file():
                continue
            text = path.read_text(encoding="utf-8")
            if SECRET_KEY_RE.search(text):
                errors.append(f"secret-like key in fixture: {rel}")
            if PAYLOAD_RE.search(text):
                errors.append(f"payload-like field in fixture: {rel}")
            try:
                fixture = load_h4_code_source_fixture(path)
                normalized = normalizer(fixture)
                replay = build_h4_fixture_replay_result(fixture, normalized)
                errors.extend(f"{rel} normalized: {item}" for item in validate_normalized_record(normalized))
                errors.extend(f"{rel} replay: {item}" for item in validate_replay_result(replay))
            except Exception as exc:  # noqa: BLE001
                errors.append(f"failed to normalize fixture {rel}: {exc}")


def validate_examples(root: Path, errors: list[str]) -> None:
    for source_id in H4_SOURCE_IDS:
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
    if record.get("schema_version") != "h4_code_source_normalized_record.v0":
        errors.append("normalized schema_version must be h4_code_source_normalized_record.v0")
    for key in ("source_id", "connector_family", "source_host", "source_native_id", "source_identity_candidate", "release_identity_candidate", "source_to_binary_relation_candidate_preview", "source_cache_candidate_preview", "evidence_candidate_preview"):
        if key not in record:
            errors.append(f"normalized record missing {key}")
    errors.extend(detect_h4_truth_boundary_violations(record))
    errors.extend(detect_h4_product_boundary_violations(record))
    return errors


def validate_replay_result(result: Mapping[str, Any]) -> list[str]:
    errors: list[str] = []
    if result.get("schema_version") != "h4_code_source_fixture_replay_result.v0":
        errors.append("replay schema_version must be h4_code_source_fixture_replay_result.v0")
    for key in ("no_network_used", "no_live_source_used", "no_repository_clone_used", "no_source_archive_download_used", "no_release_asset_download_used", "no_git_command_invoked", "no_build_tool_invoked"):
        if result.get(key) is not True:
            errors.append(f"{key} must be true")
    errors.extend(detect_h4_truth_boundary_violations(result))
    errors.extend(detect_h4_product_boundary_violations(result))
    return errors


def validate_candidate_boundary(candidate: Mapping[str, Any]) -> list[str]:
    return detect_h4_truth_boundary_violations(candidate) + detect_h4_product_boundary_violations(candidate)


def validate_runtime_imports(errors: list[str]) -> None:
    modules = [
        "control.prototypes.legacy_runtime.connectors.h4_code_source_release.fixture_loader",
        "control.prototypes.legacy_runtime.connectors.h4_code_source_release.normalizer_common",
        "control.prototypes.legacy_runtime.connectors.h4_code_source_release.source_identity",
        "control.prototypes.legacy_runtime.connectors.h4_code_source_release.release_identity",
        "control.prototypes.legacy_runtime.connectors.h4_code_source_release.source_to_binary_relation",
    ] + [f"control.prototypes.legacy_runtime.connectors.h4_code_source_release.{source_id}" for source_id in H4_SOURCE_IDS]
    for module_name in modules:
        try:
            importlib.import_module(module_name)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"failed to import {module_name}: {exc}")


def validate_python_safety(root: Path, errors: list[str]) -> None:
    python_paths = [root / rel for rel in PYTHON_FILES]
    python_paths.extend((root / "control/prototypes/legacy_runtime/connectors/h4_code_source_release").glob("*.py"))
    for path in python_paths:
        if not path.is_file():
            continue
        if path.name.startswith("live_probe_"):
            continue
        text = path.read_text(encoding="utf-8")
        if BANNED_IMPORT_RE.search(text):
            errors.append(f"banned network/model/provider import in {path.relative_to(root)}")
        if TOOL_COMMAND_RE.search(text):
            errors.append(f"forbidden git/build/package command invocation in {path.relative_to(root)}")


def validate_scripts_offline(root: Path, errors: list[str]) -> None:
    commands = [
        [sys.executable, "scripts/normalize_h4_code_source_fixture.py", "--source-id", "github_releases", "--input", "examples/connectors/h4_code_source_release/fixtures/github_releases/typical_record.json", "--check"],
        [sys.executable, "scripts/replay_h4_code_source_fixtures.py", "--check"],
        [sys.executable, "scripts/summarize_h4_code_source_fixture_outputs.py", "--input", "examples/connectors/h4_code_source_release", "--check"],
    ]
    for command in commands:
        result = subprocess.run(command, cwd=root, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            errors.append(f"script failed offline: {' '.join(command[1:])} :: {result.stdout}{result.stderr}")
    bad = subprocess.run(
        [sys.executable, "scripts/normalize_h4_code_source_fixture.py", "--source-id", "github_releases", "--input", "examples/connectors/h4_code_source_release/fixtures/github_releases/typical_record.json", "--output", "site/dist/h4.json"],
        cwd=root,
        capture_output=True,
        text=True,
        timeout=120,
    )
    if bad.returncode == 0 or "refusing forbidden output root" not in bad.stdout:
        errors.append("normalizer did not reject site/dist output")


def validate_no_private_roots(root: Path, errors: list[str]) -> None:
    for rel in (".aide.local", ".local/eureka", ".cache/eureka", "repository_clones", "repository_mirrors"):
        if (root / rel).exists():
            errors.append(f"local/private or clone root exists: {rel}")


def load_json_object(path: Path, errors: list[str]) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            errors.append(f"JSON artifact must be object: {path.relative_to(REPO_ROOT)}")
            return None
        lowered = path.read_text(encoding="utf-8").casefold()
        for claim in FORBIDDEN_TEXT_CLAIMS:
            if claim in lowered:
                errors.append(f"forbidden overclaim text in {path.relative_to(REPO_ROOT)}: {claim}")
        if SECRET_KEY_RE.search(path.read_text(encoding="utf-8")):
            errors.append(f"secret-like key in {path.relative_to(REPO_ROOT)}")
        if PAYLOAD_RE.search(path.read_text(encoding="utf-8")):
            errors.append(f"payload-like field in {path.relative_to(REPO_ROOT)}")
        return payload
    except Exception as exc:  # noqa: BLE001
        errors.append(f"invalid JSON {path.relative_to(REPO_ROOT)}: {exc}")
        return None


if __name__ == "__main__":
    raise SystemExit(main())
