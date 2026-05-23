#!/usr/bin/env python3
"""Validate H4 code/source/release metadata live-probe framework without live calls."""

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

from archive.prototypes.legacy_runtime.connectors.h4_code_source_release.live_probe_common import (  # noqa: E402
    H4_SOURCE_IDS,
    detect_h4_code_source_live_probe_product_boundary_violations,
    detect_h4_code_source_live_probe_truth_boundary_violations,
    load_h4_code_source_live_probe_policy_bundle,
    validate_h4_source_approval,
)

CONTRACTS = (
    "contracts/schema/control/previews/h4/connectors/code_source_live_probe_request.v0.json",
    "contracts/schema/control/previews/h4/connectors/code_source_live_probe_result.v0.json",
    "contracts/schema/control/previews/h4/connectors/code_source_live_probe_output_bundle.v0.json",
    "contracts/schema/control/previews/h4/connectors/code_source_connector_health_summary.v0.json",
)
POLICIES = (
    "control/inventory/connectors/h4_code_source_live_probe_policy.json",
    "control/inventory/connectors/h4_code_source_live_probe_allowed_requests.json",
    "control/inventory/connectors/h4_code_source_live_probe_endpoint_policy.json",
    "control/inventory/connectors/h4_code_source_live_probe_rate_limit_policy.json",
    "control/inventory/connectors/h4_code_source_live_probe_cache_policy.json",
    "control/inventory/connectors/h4_code_source_live_probe_kill_switch_policy.json",
    "control/inventory/connectors/h4_code_source_live_probe_output_policy.json",
    "control/inventory/connectors/h4_code_source_live_probe_path_policy.json",
    "control/inventory/connectors/h4_code_source_live_probe_review_policy.json",
    "control/inventory/connectors/h4_code_source_live_probe_truth_policy.json",
    "control/inventory/connectors/h4_code_source_live_probe_no_clone_download_policy.json",
)
DOCS = (
    "docs/reference/H4_CODE_SOURCE_LIVE_PROBE.md",
    "docs/reference/H4_CODE_SOURCE_LIVE_PROBE_RESULT.md",
    "docs/reference/H4_CODE_SOURCE_CONNECTOR_HEALTH_SUMMARY.md",
    "docs/architecture/H4_CODE_SOURCE_LIVE_PROBE_MODEL.md",
    "docs/operations/H4_CODE_SOURCE_LIVE_PROBE_APPROVAL_GATES.md",
    "docs/operations/H4_CODE_SOURCE_LIVE_PROBE_REVIEW.md",
    "docs/operations/H4_CODE_SOURCE_LIVE_PROBE_BLOCKED_MODE.md",
    "docs/operations/H4_CODE_SOURCE_LIVE_PROBE_NO_CLONE_DOWNLOAD_POLICY.md",
)
AUDIT_DIR = Path("control/audits/h4-bundle-03-code-source-live-probes-v0")
AUDIT_FILES = (
    "README.md",
    "h4_bundle_03_report.json",
    "live_probe_policy_review.md",
    "live_probe_execution_report.md",
    "source_identity_candidate_preview.md",
    "release_identity_candidate_preview.md",
    "source_to_binary_relation_candidate_preview.md",
    "release_asset_candidate_preview.md",
    "source_cache_candidate_preview.md",
    "evidence_candidate_preview.md",
    "review_queue_seed_preview.md",
    "connector_health_summary.md",
    "no_clone_download_report.md",
    "h4_live_probe_blocked_or_completed_summary.md",
    "validation.md",
    "generated/sample_h4_live_probe_result.json",
    "generated/sample_h4_source_identity_candidate_from_probe.json",
    "generated/sample_h4_release_identity_candidate_from_probe.json",
    "generated/sample_h4_source_to_binary_relation_candidate_from_probe.json",
    "generated/sample_h4_release_asset_candidate_from_probe.json",
    "generated/sample_h4_source_cache_candidate_from_probe.json",
    "generated/sample_h4_evidence_candidate_preview_from_probe.json",
    "generated/sample_h4_review_queue_seed_from_probe.json",
    "generated/sample_h4_connector_health_summary.json",
    "generated/sample_h4_live_probe_summary.md",
)
PYTHON_FILES = tuple(
    ["archive/prototypes/legacy_runtime/connectors/h4_code_source_release/live_probe_common.py"]
    + [f"archive/prototypes/legacy_runtime/connectors/h4_code_source_release/live_probe_{source_id}.py" for source_id in H4_SOURCE_IDS]
    + [
        "scripts/run_h4_code_source_live_probe.py",
        "scripts/validate_h4_code_source_live_probe.py",
        "scripts/summarize_h4_code_source_live_probe_outputs.py",
    ]
)
BANNED_IMPORT_RE = re.compile(
    r"^\s*(?:from|import)\s+"
    r"(requests|httpx|aiohttp|socket|ftplib|smtplib|webbrowser|selenium|playwright|openai|anthropic)\b",
    re.MULTILINE,
)
SECRET_KEY_RE = re.compile(
    r'"[^"]*(api[_-]?key|api[_-]?token|access[_-]?token|auth[_-]?token|client_secret|password|private_key|cookie)[^"]*"\s*:',
    re.IGNORECASE,
)
TOOL_CALL_RE = re.compile(
    r"(os\.system|subprocess\.(?:call|Popen)).*\b(git|make|cmake|ninja|npm|yarn|pnpm|pip|poetry|cargo|go|mvn|gradle|installer|apt|dnf|brew|winget|choco)\b",
    re.IGNORECASE,
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    result = validate_repo(REPO_ROOT)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print("H4 code/source live probe validation", file=stdout)
        print(f"status: {result['status']}", file=stdout)
        for error in result["errors"]:
            print(f"ERROR: {error}", file=stdout)
    return 0 if result["status"] == "valid" else 1


def validate_repo(root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    payloads: dict[str, dict[str, Any]] = {}
    for rel in CONTRACTS + POLICIES:
        payloads[rel] = load_json_object(root / rel, errors)
    for rel in DOCS + PYTHON_FILES:
        if not (root / rel).is_file():
            errors.append(f"missing required file: {rel}")
    for name in AUDIT_FILES:
        if not (root / AUDIT_DIR / name).is_file():
            errors.append(f"missing audit file: {(AUDIT_DIR / name).as_posix()}")
    validate_policies(payloads, errors)
    validate_examples(root, errors)
    validate_runtime_imports(errors)
    validate_python_safety(root, errors)
    validate_cli_offline(root, errors)
    validate_generated_outputs(root, errors)
    validate_no_private_roots(root, errors)
    return {
        "schema_version": "h4_code_source_live_probe_validation.v0",
        "status": "valid" if not errors else "invalid",
        "task": "H4-BUNDLE-03",
        "offline_default": True,
        "network_calls_made": False,
        "repository_clone_used": False,
        "source_archive_download_used": False,
        "release_asset_download_used": False,
        "git_command_invoked": False,
        "build_tool_invoked": False,
        "errors": errors,
    }


def validate_policies(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    live = payloads.get("control/inventory/connectors/h4_code_source_live_probe_policy.json", {})
    for key in ("live_probe_default_enabled", "source_sync_enabled", "public_query_fanout_enabled", "repository_clone_enabled", "source_archive_download_enabled", "release_asset_download_enabled", "git_command_invocation_enabled", "build_tool_invocation_enabled", "install_execute_enabled"):
        if live.get(key) is not False:
            errors.append(f"global policy {key} must be false")
    allowed = payloads.get("control/inventory/connectors/h4_code_source_live_probe_allowed_requests.json", {})
    sources = allowed.get("sources", [])
    if sorted(item.get("source_id") for item in sources if isinstance(item, Mapping)) != sorted(H4_SOURCE_IDS):
        errors.append("allowed requests policy must list all H4 sources")
    bundle = load_h4_code_source_live_probe_policy_bundle(REPO_ROOT)
    for item in sources:
        if not isinstance(item, Mapping):
            errors.append("allowed request source entry must be object")
            continue
        source_id = item.get("source_id")
        if item.get("approval_status") != "not_approved_for_live_access":
            errors.append(f"{source_id}: approval_status must remain not_approved_for_live_access")
        if item.get("allowed_request_keys") not in ([], None):
            errors.append(f"{source_id}: allowed_request_keys must stay empty without approval")
        for key in ("live_access_approved", "metadata_probe_approved"):
            if item.get(key) is not False:
                errors.append(f"{source_id}: {key} must be false")
        for key in (
            "source_sync_approved",
            "repository_clone_approved",
            "source_archive_download_approved",
            "release_asset_download_approved",
            "binary_download_approved",
            "package_download_approved",
            "git_command_invocation_approved",
            "build_tool_invocation_approved",
            "install_execute_approved",
            "scraping_approved",
            "crawling_approved",
            "public_query_fanout_approved",
        ):
            if item.get(key) is not False:
                errors.append(f"{source_id}: {key} must be false")
        request_key = str((item.get("planned_request_keys") or [""])[0])
        approval = validate_h4_source_approval(str(source_id), request_key, bundle)
        if approval["approved"]:
            errors.append(f"{source_id}: live approval unexpectedly passes")
    truth = payloads.get("control/inventory/connectors/h4_code_source_live_probe_truth_policy.json", {})
    for key in (
        "live_probe_result_is_public_truth",
        "normalized_record_is_public_truth",
        "source_identity_candidate_is_truth",
        "release_identity_candidate_is_truth",
        "source_to_binary_relation_candidate_is_provenance_truth",
        "git_object_candidate_is_provenance_truth",
        "swhid_candidate_is_object_truth",
        "release_asset_hash_candidate_is_malware_safety",
        "signature_metadata_is_authenticity",
        "sbom_metadata_is_provenance",
        "source_cache_candidate_is_accepted_source",
        "evidence_candidate_preview_is_accepted_evidence",
        "review_seed_is_review_decision",
        "public_index_mutated",
        "master_index_mutated",
    ):
        if truth.get(key) is not False:
            errors.append(f"truth policy {key} must be false")
    output = payloads.get("control/inventory/connectors/h4_code_source_live_probe_output_policy.json", {})
    for key in (
        "repository_clone",
        "source_archive_download",
        "release_asset_download",
        "git_command_output",
        "build_tool_output",
        "accepted_source_identity_truth",
        "accepted_release_identity_truth",
        "accepted_source_to_binary_relation_truth",
        "accepted_public_record",
        "public_index_mutation",
        "master_index_mutation",
        "rights_clearance",
        "malware_safety",
        "verified_installability",
        "verified_authenticity",
        "verified_build_reproducibility",
        "production_readiness_claim",
    ):
        if key not in output.get("forbidden_outputs", []):
            errors.append(f"output policy must forbid {key}")


def validate_examples(root: Path, errors: list[str]) -> None:
    expected_requests = ["blocked_live_probe_request_v0.json"] + [f"approved_{source_id}_probe_request_v0.json" for source_id in H4_SOURCE_IDS]
    expected_results = ["blocked_live_probe_result_v0.json"] + [f"{source_id}_live_probe_result_example_v0.json" for source_id in H4_SOURCE_IDS]
    paths = [f"examples/connectors/h4_code_source_release/live_probe/{name}" for name in expected_requests]
    paths += [f"examples/connectors/h4_code_source_release/live_probe_results/{name}" for name in expected_results]
    paths += [
        "examples/connectors/h4_code_source_release/live_probe_outputs/source_cache_candidate_from_h4_probe_v0.json",
        "examples/connectors/h4_code_source_release/live_probe_outputs/evidence_candidate_preview_from_h4_probe_v0.json",
        "examples/connectors/h4_code_source_release/live_probe_outputs/review_queue_seed_from_h4_probe_v0.json",
        "examples/connectors/h4_code_source_release/live_probe_outputs/connector_health_from_h4_probe_v0.json",
        "examples/connectors/h4_code_source_release/live_probe_outputs/source_identity_candidate_from_h4_probe_v0.json",
        "examples/connectors/h4_code_source_release/live_probe_outputs/release_identity_candidate_from_h4_probe_v0.json",
        "examples/connectors/h4_code_source_release/live_probe_outputs/source_to_binary_relation_candidate_from_h4_probe_v0.json",
        "examples/connectors/h4_code_source_release/live_probe_outputs/release_asset_candidate_from_h4_probe_v0.json",
    ]
    for rel in paths:
        payload = load_json_object(root / rel, errors)
        validate_boundaries(payload, rel, errors)
        validate_no_secret_text(root / rel, errors)
    result_dir = root / "examples/connectors/h4_code_source_release/live_probe_results"
    for path in result_dir.glob("*.json"):
        payload = load_json_object(path, errors)
        if payload.get("request_count") != 0 or payload.get("network_used") is not False:
            errors.append(f"{path.relative_to(root)} must be blocked/offline with request_count 0")


def validate_runtime_imports(errors: list[str]) -> None:
    modules = ["archive.prototypes.legacy_runtime.connectors.h4_code_source_release.live_probe_common"] + [
        f"archive.prototypes.legacy_runtime.connectors.h4_code_source_release.live_probe_{source_id}" for source_id in H4_SOURCE_IDS
    ]
    for module_name in modules:
        try:
            importlib.import_module(module_name)
        except Exception as exc:  # noqa: BLE001
            errors.append(f"failed to import {module_name}: {exc}")


def validate_python_safety(root: Path, errors: list[str]) -> None:
    for rel in PYTHON_FILES:
        path = root / rel
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for match in BANNED_IMPORT_RE.finditer(text):
            errors.append(f"forbidden import in {rel}: {match.group(1)}")
        if TOOL_CALL_RE.search(text):
            errors.append(f"forbidden git/build/package command invocation primitive in {rel}")


def validate_cli_offline(root: Path, errors: list[str]) -> None:
    commands = [
        [sys.executable, "scripts/run_h4_code_source_live_probe.py", "--source-id", "github_releases", "--request-key", "example_release_metadata", "--check", "--json"],
        [sys.executable, "scripts/run_h4_code_source_live_probe.py", "--source-id", "github_releases", "--request-key", "example_release_metadata", "--live", "--json"],
        [sys.executable, "scripts/summarize_h4_code_source_live_probe_outputs.py", "--input", "examples/connectors/h4_code_source_release/live_probe_results", "--check", "--json"],
    ]
    for command in commands:
        result = subprocess.run(command, cwd=root, check=False, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            errors.append(f"command failed: {' '.join(command)} :: {result.stdout} {result.stderr}")
            continue
        payload = json.loads(result.stdout)
        if command[1].endswith("run_h4_code_source_live_probe.py"):
            live = payload.get("live_probe", {})
            if live.get("request_count") != 0 or live.get("network_used") is not False:
                errors.append("live probe CLI default/blocked path must not use network")
    for bad_path in ("site/dist/h4.json", "site/dist/data/public_index/h4.json", "repository_clones/h4.json"):
        bad = subprocess.run([sys.executable, "scripts/run_h4_code_source_live_probe.py", "--source-id", "github_releases", "--request-key", "example_release_metadata", "--output", bad_path], cwd=root, check=False, capture_output=True, text=True, timeout=120)
        if bad.returncode == 0:
            errors.append(f"live probe CLI must refuse {bad_path} output")


def validate_generated_outputs(root: Path, errors: list[str]) -> None:
    result = load_json_object(root / AUDIT_DIR / "generated/sample_h4_live_probe_result.json", errors)
    if not str(result.get("result_status", "")).startswith("blocked"):
        errors.append("generated sample live probe result must be blocked under current policy")
    if result.get("request_count") != 0 or result.get("network_used") is not False:
        errors.append("generated sample live probe must not use network")
    validate_boundaries(result, "generated live probe result", errors)
    report = load_json_object(root / AUDIT_DIR / "h4_bundle_03_report.json", errors)
    if report.get("schema_version") != "h4_bundle_03_report.v0":
        errors.append("h4 bundle 03 report schema mismatch")
    validate_boundaries(report, "h4_bundle_03_report", errors)


def validate_boundaries(payload: Mapping[str, Any], label: str, errors: list[str]) -> None:
    errors.extend(f"{label}: {item}" for item in detect_h4_code_source_live_probe_truth_boundary_violations(payload))
    errors.extend(f"{label}: {item}" for item in detect_h4_code_source_live_probe_product_boundary_violations(payload))


def validate_no_secret_text(path: Path, errors: list[str]) -> None:
    if path.is_file() and SECRET_KEY_RE.search(path.read_text(encoding="utf-8")):
        errors.append(f"secret-like key in example: {path.relative_to(REPO_ROOT)}")


def validate_no_private_roots(root: Path, errors: list[str]) -> None:
    for rel in (".aide.local", ".local/eureka", ".cache/eureka", "repository_clones", "repository_mirrors"):
        if (root / rel).exists():
            errors.append(f"local/private or clone root exists: {rel}")


def load_json_object(path: Path, errors: list[str]) -> dict[str, Any]:
    if not path.is_file():
        errors.append(f"missing JSON file: {path.relative_to(REPO_ROOT)}")
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"invalid JSON {path.relative_to(REPO_ROOT)}: {exc}")
        return {}
    if not isinstance(payload, dict):
        errors.append(f"JSON file must contain object: {path.relative_to(REPO_ROOT)}")
        return {}
    return payload


if __name__ == "__main__":
    raise SystemExit(main())
