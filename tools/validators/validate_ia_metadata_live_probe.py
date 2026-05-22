#!/usr/bin/env python3
"""Validate IA-BUNDLE-02 live-probe artifacts without performing live calls."""

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

from runtime.connectors.internet_archive.live_metadata_probe import (  # noqa: E402
    detect_live_probe_product_boundary_violations,
    detect_live_probe_truth_boundary_violations,
    load_policy_bundle,
    validate_live_probe_policy,
)


AUDIT_DIR = Path("control/audits/ia-bundle-02-bounded-metadata-live-probe-v0")
LIVE_PROBE_EXAMPLE_DIR = Path("examples/connectors/internet_archive/live_probe")
REQUIRED_JSON = (
    "control/inventory/connectors/internet_archive_live_probe_policy.json",
    "control/inventory/connectors/internet_archive_live_probe_allowed_identifiers.json",
    "control/inventory/connectors/internet_archive_live_probe_output_policy.json",
    "control/inventory/connectors/internet_archive_live_probe_path_policy.json",
    "control/inventory/connectors/internet_archive_live_probe_review_policy.json",
    "control/inventory/connectors/internet_archive_live_probe_truth_policy.json",
    (AUDIT_DIR / "ia_bundle_02_report.json").as_posix(),
)
REQUIRED_EXAMPLES = (
    "blocked_live_probe_request_v0.json",
    "approved_single_identifier_probe_request_v0.json",
    "live_probe_result_example_v0.json",
    "source_cache_candidate_from_live_probe_v0.json",
    "evidence_candidate_preview_from_live_probe_v0.json",
    "review_queue_seed_from_live_probe_v0.json",
)
REQUIRED_AUDIT_FILES = (
    "README.md",
    "ia_bundle_02_report.json",
    "live_probe_policy_review.md",
    "live_probe_execution_report.md",
    "source_cache_write_preview.md",
    "evidence_candidate_preview.md",
    "review_queue_seed_preview.md",
    "validation.md",
    "generated/sample_live_probe_result.json",
    "generated/sample_source_cache_candidate_from_live_probe.json",
    "generated/sample_evidence_candidate_preview_from_live_probe.json",
    "generated/sample_review_queue_seed_from_live_probe.json",
    "generated/sample_live_probe_summary.md",
)
REQUIRED_DOCS = (
    "docs/reference/IA_METADATA_LIVE_PROBE.md",
    "docs/architecture/IA_METADATA_LIVE_PROBE_MODEL.md",
    "docs/operations/IA_METADATA_LIVE_PROBE_REVIEW.md",
)
PYTHON_SCAN_PATHS = (
    "runtime/connectors/internet_archive/live_metadata_probe.py",
    "scripts/run_ia_metadata_live_probe.py",
    "scripts/validate_ia_metadata_live_probe.py",
)
BANNED_IMPORT_RE = re.compile(
    r"^\s*(?:from|import)\s+"
    r"(requests|http|socket|ftplib|smtplib|webbrowser|selenium|playwright|openai|anthropic)\b",
    re.MULTILINE,
)


def validate_repo(root: Path = REPO_ROOT) -> dict[str, Any]:
    root = root.resolve()
    errors: list[str] = []
    payloads = {rel: load_json_object(root / rel, errors) for rel in REQUIRED_JSON}
    for rel in REQUIRED_DOCS:
        if not (root / rel).is_file():
            errors.append(f"missing doc: {rel}")
    validate_policies(payloads, errors)
    validate_audit_files(root, errors)
    validate_examples(root, errors)
    validate_generated_outputs(root, errors)
    validate_python_imports(root, errors)
    validate_dry_preflight(root, errors)
    validate_no_private_roots(root, errors)
    return {
        "schema_version": "ia_metadata_live_probe_validation.v0",
        "status": "valid" if not errors else "invalid",
        "task": "IA-BUNDLE-02",
        "offline_default": True,
        "errors": errors,
    }


def validate_policies(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    live = payloads.get("control/inventory/connectors/internet_archive_live_probe_policy.json", {})
    require_value(live, "source_id", "internet_archive", errors)
    require_value(live, "connector_id", "internet_archive_metadata_connector", errors)
    require_value(live, "live_probe_scope", "single_identifier_metadata_read", errors)
    if live.get("approval_status") != "approved" and live.get("live_probe_enabled") is not False:
        errors.append("live_probe_enabled must be false while approval is pending")
    if live.get("allowed_endpoint_templates") != ["https://archive.org/metadata/{identifier}"]:
        errors.append("live probe policy must allow only the metadata endpoint template")
    if live.get("allowed_http_methods") != ["GET"]:
        errors.append("live probe policy allowed_http_methods must be ['GET']")

    allowed = payloads.get("control/inventory/connectors/internet_archive_live_probe_allowed_identifiers.json", {})
    require_value(allowed, "max_identifiers_current", 1, errors)
    require_value(allowed, "max_identifiers_per_run", 1, errors)
    if allowed.get("approval_status") != "approved" and allowed.get("approved_identifiers") not in ([], None):
        errors.append("approved_identifiers must stay empty while identifier approval is pending")

    output = payloads.get("control/inventory/connectors/internet_archive_live_probe_output_policy.json", {})
    forbidden = output.get("forbidden_output_types", [])
    for key in ("downloaded_file", "item_file_payload", "accepted_public_record", "public_index_mutation", "master_index_mutation", "rights_clearance", "malware_safety", "verified_installability"):
        if key not in forbidden:
            errors.append(f"output policy must forbid {key}")

    review = payloads.get("control/inventory/connectors/internet_archive_live_probe_review_policy.json", {})
    for key in (
        "review_required_before_source_cache_persistence",
        "review_required_before_evidence_acceptance",
        "review_required_before_candidate_acceptance",
        "review_required_before_public_index_use",
        "review_required_before_master_index",
    ):
        require_value(review, key, True, errors)
    for key in (
        "automatic_evidence_acceptance_allowed",
        "automatic_candidate_acceptance_allowed",
        "automatic_public_index_mutation_allowed",
        "automatic_master_index_mutation_allowed",
    ):
        require_value(review, key, False, errors)

    truth = payloads.get("control/inventory/connectors/internet_archive_live_probe_truth_policy.json", {})
    for key in (
        "live_probe_result_is_truth",
        "live_probe_result_is_accepted_evidence",
        "source_cache_candidate_is_accepted_source",
        "evidence_candidate_preview_is_accepted_evidence",
        "review_queue_seed_is_review_decision",
        "live_probe_can_mutate_public_index",
        "live_probe_can_mutate_master_index",
        "live_probe_can_claim_rights_clearance",
        "live_probe_can_claim_malware_safety",
        "live_probe_can_claim_verified_installability",
    ):
        require_value(truth, key, False, errors)

    bundle = load_policy_bundle(REPO_ROOT)
    result = validate_live_probe_policy(bundle)
    if result["approved"]:
        errors.append("committed policy unexpectedly approves live probing; IA-BUNDLE-02 default validator expects blocked policy")


def validate_audit_files(root: Path, errors: list[str]) -> None:
    for rel_name in REQUIRED_AUDIT_FILES:
        path = root / AUDIT_DIR / rel_name
        if not path.is_file():
            errors.append(f"missing audit file: {(AUDIT_DIR / rel_name).as_posix()}")


def validate_examples(root: Path, errors: list[str]) -> None:
    for name in REQUIRED_EXAMPLES:
        payload = load_json_object(root / LIVE_PROBE_EXAMPLE_DIR / name, errors)
        validate_boundaries(payload, name, errors)


def validate_generated_outputs(root: Path, errors: list[str]) -> None:
    result = load_json_object(root / AUDIT_DIR / "generated/sample_live_probe_result.json", errors)
    if result.get("result_status") != "blocked":
        errors.append("generated sample_live_probe_result must be blocked for current committed policy")
    if result.get("request_count") != 0 or result.get("network_used") is not False:
        errors.append("blocked generated live probe result must have request_count 0 and network_used false")
    validate_boundaries(result, "generated sample_live_probe_result", errors)
    for rel_name in (
        "generated/sample_source_cache_candidate_from_live_probe.json",
        "generated/sample_evidence_candidate_preview_from_live_probe.json",
        "generated/sample_review_queue_seed_from_live_probe.json",
    ):
        payload = load_json_object(root / AUDIT_DIR / rel_name, errors)
        if payload.get("status") != "not_created_blocked_by_policy":
            errors.append(f"{rel_name} must be a not-created blocked preview")
        validate_boundaries(payload, rel_name, errors)


def validate_python_imports(root: Path, errors: list[str]) -> None:
    for rel in PYTHON_SCAN_PATHS:
        path = root / rel
        if not path.is_file():
            errors.append(f"missing Python file: {rel}")
            continue
        text = path.read_text(encoding="utf-8")
        for match in BANNED_IMPORT_RE.finditer(text):
            errors.append(f"forbidden import in {rel}: {match.group(1)}")


def validate_dry_preflight(root: Path, errors: list[str]) -> None:
    result = subprocess.run(
        [
            sys.executable,
            "scripts/run_ia_metadata_live_probe.py",
            "--identifier",
            "eureka-software-fixture",
            "--check",
            "--json",
        ],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
        timeout=120,
    )
    if result.returncode != 0:
        errors.append(f"dry preflight failed: {result.stdout} {result.stderr}")
        return
    payload = json.loads(result.stdout)
    live = payload.get("live_probe", {})
    if live.get("result_status") != "blocked":
        errors.append("dry preflight must be blocked by current committed policy")
    if live.get("request_count") != 0 or live.get("network_used") is not False:
        errors.append("dry preflight must not use network")


def validate_no_private_roots(root: Path, errors: list[str]) -> None:
    for rel in (".aide.local", ".local/eureka", ".cache/eureka"):
        if (root / rel).exists():
            errors.append(f"local private root must not be created: {rel}")


def validate_boundaries(payload: Mapping[str, Any], label: str, errors: list[str]) -> None:
    errors.extend(f"{label}: {error}" for error in detect_live_probe_truth_boundary_violations(payload, None))
    errors.extend(f"{label}: {error}" for error in detect_live_probe_product_boundary_violations(payload, None))
    text = json.dumps(payload, sort_keys=True)
    forbidden_terms = ("downloaded_file_payload", "accepted_public_record", "rights_clearance_claimed\": true", "malware_safety_claimed\": true", "verified_installability_claimed\": true")
    for term in forbidden_terms:
        if term in text:
            errors.append(f"{label}: forbidden term present: {term}")


def load_json_object(path: Path, errors: list[str]) -> Mapping[str, Any]:
    if not path.is_file():
        errors.append(f"missing JSON: {rel(path)}")
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001 - deterministic validator surface.
        errors.append(f"invalid JSON: {rel(path)}: {exc}")
        return {}
    if not isinstance(payload, Mapping):
        errors.append(f"JSON must be an object: {rel(path)}")
        return {}
    return payload


def require_value(payload: Mapping[str, Any], key: str, expected: Any, errors: list[str]) -> None:
    if payload.get(key) != expected:
        errors.append(f"{key} must be {expected!r}")


def rel(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    report = validate_repo(REPO_ROOT)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True), file=stdout)
    else:
        print(f"status: {report['status']}", file=stdout)
        for error in report["errors"]:
            print(f"ERROR: {error}", file=stdout)
    return 0 if report["status"] == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
