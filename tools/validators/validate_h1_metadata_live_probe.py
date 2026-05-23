#!/usr/bin/env python3
"""Validate H1 metadata live-probe framework without performing live calls."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from archive.prototypes.legacy_runtime.connectors.h1_metadata_wave.live_probe_common import (  # noqa: E402
    H1_SOURCE_IDS,
    detect_h1_live_probe_product_boundary_violations,
    detect_h1_live_probe_truth_boundary_violations,
    load_h1_live_probe_policy_bundle,
    validate_h1_source_approval,
)


CONTRACTS = (
    "contracts/schema/control/previews/h1/connectors/live_probe_request.v0.json",
    "contracts/schema/control/previews/h1/connectors/live_probe_result.v0.json",
    "contracts/schema/control/previews/h1/connectors/live_probe_output_bundle.v0.json",
)
POLICIES = (
    "control/inventory/connectors/h1_metadata_live_probe_policy.json",
    "control/inventory/connectors/h1_metadata_live_probe_allowed_requests.json",
    "control/inventory/connectors/h1_metadata_live_probe_endpoint_policy.json",
    "control/inventory/connectors/h1_metadata_live_probe_rate_limit_policy.json",
    "control/inventory/connectors/h1_metadata_live_probe_cache_policy.json",
    "control/inventory/connectors/h1_metadata_live_probe_kill_switch_policy.json",
    "control/inventory/connectors/h1_metadata_live_probe_output_policy.json",
    "control/inventory/connectors/h1_metadata_live_probe_path_policy.json",
    "control/inventory/connectors/h1_metadata_live_probe_review_policy.json",
    "control/inventory/connectors/h1_metadata_live_probe_truth_policy.json",
)
DOCS = (
    "docs/reference/H1_METADATA_LIVE_PROBE.md",
    "docs/reference/H1_METADATA_LIVE_PROBE_RESULT.md",
    "docs/architecture/H1_METADATA_LIVE_PROBE_MODEL.md",
    "docs/operations/H1_METADATA_LIVE_PROBE_REVIEW.md",
    "docs/operations/H1_METADATA_LIVE_PROBE_APPROVAL_GATES.md",
    "docs/operations/H1_METADATA_LIVE_PROBE_BLOCKED_MODE.md",
)
EXAMPLE_DIRS = (
    "examples/connectors/h1_metadata_wave/live_probe",
    "examples/connectors/h1_metadata_wave/live_probe_results",
    "examples/connectors/h1_metadata_wave/live_probe_outputs",
)
AUDIT_DIR = Path("control/audits/h1-bundle-03-metadata-live-probes-v0")
AUDIT_FILES = (
    "README.md",
    "h1_bundle_03_report.json",
    "live_probe_policy_review.md",
    "live_probe_execution_report.md",
    "source_cache_candidate_preview.md",
    "evidence_candidate_preview.md",
    "review_queue_seed_preview.md",
    "connector_health_summary.md",
    "h1_live_probe_blocked_or_completed_summary.md",
    "validation.md",
    "generated/sample_h1_live_probe_result.json",
    "generated/sample_h1_source_cache_candidate_from_probe.json",
    "generated/sample_h1_evidence_candidate_preview_from_probe.json",
    "generated/sample_h1_review_queue_seed_from_probe.json",
    "generated/sample_h1_connector_health_summary.json",
    "generated/sample_h1_live_probe_summary.md",
)
PYTHON_FILES = tuple(
    ["archive/prototypes/legacy_runtime/connectors/h1_metadata_wave/live_probe_common.py"]
    + [f"archive/prototypes/legacy_runtime/connectors/h1_metadata_wave/live_probe_{source_id}.py" for source_id in H1_SOURCE_IDS]
    + [
        "scripts/run_h1_metadata_live_probe.py",
        "scripts/validate_h1_metadata_live_probe.py",
        "scripts/summarize_h1_live_probe_outputs.py",
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


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    result = validate_repo(REPO_ROOT)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print("H1 metadata live probe validation", file=stdout)
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
    for rel in EXAMPLE_DIRS:
        if not (root / rel).is_dir():
            errors.append(f"missing example directory: {rel}")
    for name in AUDIT_FILES:
        if not (root / AUDIT_DIR / name).is_file():
            errors.append(f"missing audit file: {(AUDIT_DIR / name).as_posix()}")
    validate_policies(payloads, errors)
    validate_examples(root, errors)
    validate_python_imports(root, errors)
    validate_cli_offline(root, errors)
    validate_generated_outputs(root, errors)
    validate_no_private_roots(root, errors)
    return {
        "schema_version": "h1_metadata_live_probe_validation.v0",
        "status": "valid" if not errors else "invalid",
        "task": "H1-BUNDLE-03",
        "offline_default": True,
        "network_calls_made": False,
        "errors": errors,
    }


def validate_policies(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    live = payloads.get("control/inventory/connectors/h1_metadata_live_probe_policy.json", {})
    if live.get("live_probe_default_enabled") is not False:
        errors.append("global live_probe_default_enabled must be false")
    if live.get("source_sync_enabled") is not False or live.get("public_query_fanout_enabled") is not False:
        errors.append("source sync and public query fanout must be false")
    allowed = payloads.get("control/inventory/connectors/h1_metadata_live_probe_allowed_requests.json", {})
    sources = allowed.get("sources", [])
    if sorted(item.get("source_id") for item in sources if isinstance(item, Mapping)) != sorted(H1_SOURCE_IDS):
        errors.append("allowed requests policy must list all H1 sources")
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
            "file_download_approved",
            "package_download_approved",
            "release_asset_download_approved",
            "source_archive_download_approved",
            "scraping_approved",
            "crawling_approved",
            "public_query_fanout_approved",
        ):
            if item.get(key) is not False:
                errors.append(f"{source_id}: {key} must be false")
    truth = payloads.get("control/inventory/connectors/h1_metadata_live_probe_truth_policy.json", {})
    for key in (
        "live_probe_result_is_truth",
        "normalized_record_is_public_truth",
        "source_cache_candidate_is_accepted_source",
        "evidence_candidate_preview_is_accepted_evidence",
        "review_queue_seed_is_review_decision",
        "live_probe_can_mutate_public_index",
        "live_probe_can_mutate_master_index",
        "live_probe_can_claim_rights_clearance",
        "live_probe_can_claim_malware_safety",
        "live_probe_can_claim_verified_installability",
    ):
        if truth.get(key) is not False:
            errors.append(f"truth policy {key} must be false")
    output = payloads.get("control/inventory/connectors/h1_metadata_live_probe_output_policy.json", {})
    for key in (
        "downloaded_file",
        "package_download",
        "release_asset_download",
        "source_archive_download",
        "vulnerability_exploit_payload",
        "accepted_public_record",
        "public_index_mutation",
        "master_index_mutation",
        "rights_clearance",
        "malware_safety",
        "verified_installability",
        "production_readiness_claim",
    ):
        if key not in output.get("forbidden_outputs", []):
            errors.append(f"output policy must forbid {key}")
    bundle = load_h1_live_probe_policy_bundle(REPO_ROOT)
    for item in sources:
        if not isinstance(item, Mapping):
            continue
        source_id = str(item.get("source_id"))
        request_key = str((item.get("planned_request_keys") or [""])[0])
        approval = validate_h1_source_approval(source_id, request_key, bundle)
        if approval["approved"]:
            errors.append(f"{source_id}: live approval unexpectedly passes")


def validate_examples(root: Path, errors: list[str]) -> None:
    expected_requests = ["blocked_live_probe_request_v0.json"] + [f"approved_{source_id}_probe_request_v0.json" for source_id in H1_SOURCE_IDS]
    expected_results = ["blocked_live_probe_result_v0.json"] + [f"{source_id}_live_probe_result_example_v0.json" for source_id in H1_SOURCE_IDS]
    paths = [f"examples/connectors/h1_metadata_wave/live_probe/{name}" for name in expected_requests]
    paths += [f"examples/connectors/h1_metadata_wave/live_probe_results/{name}" for name in expected_results]
    paths += [
        "examples/connectors/h1_metadata_wave/live_probe_outputs/source_cache_candidate_from_h1_probe_v0.json",
        "examples/connectors/h1_metadata_wave/live_probe_outputs/evidence_candidate_preview_from_h1_probe_v0.json",
        "examples/connectors/h1_metadata_wave/live_probe_outputs/review_queue_seed_from_h1_probe_v0.json",
        "examples/connectors/h1_metadata_wave/live_probe_outputs/connector_health_from_h1_probe_v0.json",
    ]
    for rel in paths:
        payload = load_json_object(root / rel, errors)
        validate_boundaries(payload, rel, errors)
        validate_no_secret_text(root / rel, errors)
    result_dir = root / "examples/connectors/h1_metadata_wave/live_probe_results"
    for path in result_dir.glob("*.json"):
        payload = load_json_object(path, errors)
        if payload.get("request_count") != 0 or payload.get("network_used") is not False:
            errors.append(f"{path.relative_to(root)} must be blocked/offline with request_count 0")


def validate_python_imports(root: Path, errors: list[str]) -> None:
    for rel in PYTHON_FILES:
        path = root / rel
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        for match in BANNED_IMPORT_RE.finditer(text):
            errors.append(f"forbidden import in {rel}: {match.group(1)}")


def validate_cli_offline(root: Path, errors: list[str]) -> None:
    commands = [
        [sys.executable, "scripts/run_h1_metadata_live_probe.py", "--source-id", "pypi", "--request-key", "example_project_metadata", "--check", "--json"],
        [sys.executable, "scripts/run_h1_metadata_live_probe.py", "--source-id", "pypi", "--request-key", "example_project_metadata", "--live", "--json"],
        [sys.executable, "scripts/summarize_h1_live_probe_outputs.py", "--input", "examples/connectors/h1_metadata_wave/live_probe_results", "--check", "--json"],
    ]
    for command in commands:
        result = subprocess.run(command, cwd=root, check=False, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            errors.append(f"command failed: {' '.join(command)} :: {result.stdout} {result.stderr}")
            continue
        payload = json.loads(result.stdout)
        if command[1].endswith("run_h1_metadata_live_probe.py"):
            live = payload.get("live_probe", {})
            if live.get("request_count") != 0 or live.get("network_used") is not False:
                errors.append("live probe CLI default/blocked path must not use network")
    bad = subprocess.run([sys.executable, "scripts/run_h1_metadata_live_probe.py", "--source-id", "pypi", "--request-key", "example_project_metadata", "--output", "site/dist/h1.json"], cwd=root, check=False, capture_output=True, text=True, timeout=120)
    if bad.returncode == 0:
        errors.append("live probe CLI must refuse site/dist output")
    bad_public = subprocess.run([sys.executable, "scripts/run_h1_metadata_live_probe.py", "--source-id", "pypi", "--request-key", "example_project_metadata", "--output", "site/dist/data/public_index/h1.json"], cwd=root, check=False, capture_output=True, text=True, timeout=120)
    if bad_public.returncode == 0:
        errors.append("live probe CLI must refuse site/dist/data/public_index output")


def validate_generated_outputs(root: Path, errors: list[str]) -> None:
    result = load_json_object(root / AUDIT_DIR / "generated/sample_h1_live_probe_result.json", errors)
    if not str(result.get("result_status", "")).startswith("blocked"):
        errors.append("generated sample live probe result must be blocked under current policy")
    if result.get("request_count") != 0 or result.get("network_used") is not False:
        errors.append("generated sample live probe must not use network")
    validate_boundaries(result, "generated live probe result", errors)
    report = load_json_object(root / AUDIT_DIR / "h1_bundle_03_report.json", errors)
    if report.get("schema_version") != "h1_bundle_03_report.v0":
        errors.append("h1 bundle 03 report schema mismatch")
    validate_boundaries(report, "h1_bundle_03_report", errors)


def validate_boundaries(payload: Mapping[str, Any], label: str, errors: list[str]) -> None:
    errors.extend(f"{label}: {item}" for item in detect_h1_live_probe_truth_boundary_violations(payload))
    errors.extend(f"{label}: {item}" for item in detect_h1_live_probe_product_boundary_violations(payload))
    text = json.dumps(payload, sort_keys=True)
    for term in (
        "downloaded_binary_payload",
        "package_tarball",
        "release_asset_payload",
        "source_archive_payload",
        "exploit_payload",
        'rights_clearance_claimed": true',
        'malware_safety_claimed": true',
        'verified_installability_claimed": true',
    ):
        if term in text:
            errors.append(f"{label}: forbidden term present: {term}")


def validate_no_secret_text(path: Path, errors: list[str]) -> None:
    if path.is_file() and SECRET_KEY_RE.search(path.read_text(encoding="utf-8")):
        errors.append(f"{path.relative_to(REPO_ROOT)} contains credential/cookie/token-like key")


def validate_no_private_roots(root: Path, errors: list[str]) -> None:
    for rel in (".aide.local", ".local/eureka", ".cache/eureka"):
        if (root / rel).exists():
            errors.append(f"local private root must not be created: {rel}")


def load_json_object(path: Path, errors: list[str]) -> dict[str, Any]:
    if not path.is_file():
        errors.append(f"missing JSON: {path.relative_to(REPO_ROOT)}")
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        errors.append(f"invalid JSON: {path.relative_to(REPO_ROOT)}: {exc}")
        return {}
    if not isinstance(payload, dict):
        errors.append(f"JSON root must be object: {path.relative_to(REPO_ROOT)}")
        return {}
    return payload


if __name__ == "__main__":
    raise SystemExit(main())
