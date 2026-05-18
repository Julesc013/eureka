#!/usr/bin/env python3
"""Validate IA-02 live metadata probe policy, dry-run, and evidence."""

from __future__ import annotations

import ast
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.validate_ia_fixture_replay import validate_ia_fixture_replay  # noqa: E402
from scripts.validate_ia_metadata_policy import validate_ia_metadata_policy  # noqa: E402


REQUIRED_FILES = [
    "control/policies/ia_live_probe_policy.json",
    "control/inventory/ia_live_probe_policy_matrix.json",
    "control/inventory/ia_live_probe_request_plan.json",
    "control/inventory/ia_live_probe_redaction_policy.json",
    "control/inventory/ia_live_probe_result_summary.json",
    "control/inventory/ia_live_probe_normalized_preview.json",
    "control/inventory/ia_live_probe_boundary_report.json",
    "runtime/source_observation/internet_archive_live_transport.py",
    "runtime/source_observation/internet_archive_live_probe.py",
    "scripts/eureka_ia_live_metadata_probe.py",
]

ALLOWED_NETWORK_IMPORT_FILES = {
    "runtime/source_observation/internet_archive_live_transport.py",
    "runtime/source_observation/internet_archive_live_probe.py",
    "scripts/eureka_ia_live_metadata_probe.py",
}

FORBIDDEN_NETWORK_IMPORTS = {
    "requests",
    "httpx",
    "aiohttp",
    "selenium",
    "playwright",
    "openai",
    "anthropic",
    "google.generativeai",
}


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    _ = argv
    result = validate_ia_live_metadata_probe(REPO_ROOT)
    print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    return 0 if result["status"] == "pass" else 1


def validate_ia_live_metadata_probe(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    policy_result = validate_ia_metadata_policy(repo_root)
    fixture_result = validate_ia_fixture_replay(repo_root)
    if policy_result.get("status") != "pass":
        errors.append("ia_00_policy_validator_failed")
    if fixture_result.get("status") != "pass":
        errors.append("ia_01_fixture_replay_validator_failed")

    for rel_path in REQUIRED_FILES:
        if not (repo_root / rel_path).exists():
            errors.append(f"missing_file:{rel_path}")

    policy = _load_json(repo_root / "control/policies/ia_live_probe_policy.json", errors)
    summary = _load_json(repo_root / "control/inventory/ia_live_probe_result_summary.json", errors)
    preview = _load_json(repo_root / "control/inventory/ia_live_probe_normalized_preview.json", errors)
    boundary = _load_json(repo_root / "control/inventory/ia_live_probe_boundary_report.json", errors)
    _validate_policy(policy, errors)
    _validate_summary(policy, summary, errors)
    _validate_preview(preview, errors)
    _validate_boundary(boundary, errors)
    _validate_no_raw_body_commit(repo_root, errors)
    _validate_network_imports(repo_root, errors)
    _validate_no_forbidden_git_state(repo_root, errors, warnings)

    dry_run = _run_dry_run(repo_root)
    if dry_run.get("returncode") != 0:
        errors.append("live_probe_cli_dry_run_failed")
        warnings.append(str(dry_run.get("stderr", "")).strip())
    else:
        try:
            dry_run_payload = json.loads(str(dry_run.get("stdout", "")))
            if dry_run_payload.get("redacted_summary", {}).get("total_http_requests") != 0:
                errors.append("dry_run_performed_network")
        except json.JSONDecodeError as exc:
            errors.append(f"live_probe_cli_dry_run_invalid_json:{exc}")

    live_status = str(summary.get("probe_status", "not_run_yet"))
    live_attempted = live_status not in {"not_run_yet", "dry_run", ""}
    return {
        "schema_version": "ia_live_probe_validation.v0",
        "task": "IA-02",
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "warnings": [item for item in warnings if item],
        "ia_00_policy_validated": policy_result.get("status") == "pass",
        "ia_01_fixture_replay_validated": fixture_result.get("status") == "pass",
        "dry_run_passed": dry_run.get("returncode") == 0,
        "live_probe_evidence_present": live_attempted,
        "total_http_requests": int(summary.get("total_http_requests", 0) or 0),
        "raw_response_committed": False,
        "live_source_call_performed": bool(boundary.get("live_source_call_performed", False)),
        "source_probe_executed": bool(boundary.get("source_probe_executed", False)),
        "source_cache_write_performed": False,
        "evidence_ledger_write_performed": False,
        "candidate_index_mutated": False,
        "reviewed_index_mutated": False,
        "master_index_mutated": False,
        "download_performed": False,
        "upload_performed": False,
        "model_provider_used": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def _load_json(path: Path, errors: list[str]) -> Mapping[str, Any]:
    if not path.exists():
        errors.append(f"missing_json:{path.relative_to(REPO_ROOT).as_posix()}")
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"invalid_json:{path.relative_to(REPO_ROOT).as_posix()}:{exc}")
        return {}
    return payload if isinstance(payload, Mapping) else {}


def _validate_policy(policy: Mapping[str, Any], errors: list[str]) -> None:
    if policy.get("schema_version") != "ia_live_probe_policy.v0":
        errors.append("bad_ia_live_probe_policy_schema")
    if policy.get("live_calls_require_approve_live_flag") is not True:
        errors.append("approve_live_not_required")
    if policy.get("allowed_domains") != ["archive.org"]:
        errors.append("allowed_domains_not_archive_org_only")
    if int(policy.get("metadata_search_rows_max", 0)) > 1:
        errors.append("metadata_search_rows_cap_too_high")
    if int(policy.get("total_http_requests_max", 0)) > 2:
        errors.append("total_http_requests_cap_too_high")
    for key in (
        "downloads_enabled",
        "uploads_enabled",
        "write_apis_enabled",
        "public_search_fanout_enabled",
        "source_cache_writes_enabled",
        "evidence_ledger_writes_enabled",
        "candidate_index_mutation_enabled",
        "reviewed_index_mutation_enabled",
        "master_index_mutation_enabled",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    ):
        if policy.get(key) is not False:
            errors.append(f"policy_expected_false:{key}")
    for key in (
        "user_agent_required",
        "contact_required",
        "kill_switch_required",
        "redacted_summary_required",
        "raw_response_commit_forbidden",
        "honor_retry_after",
        "cache_before_repeat",
    ):
        if policy.get(key) is not True:
            errors.append(f"policy_expected_true:{key}")


def _validate_summary(policy: Mapping[str, Any], summary: Mapping[str, Any], errors: list[str]) -> None:
    if summary.get("schema_version") != "ia_live_probe_redacted_summary.v0":
        errors.append("bad_live_probe_summary_schema")
    if int(summary.get("total_http_requests", 0) or 0) > int(policy.get("total_http_requests_max", 2) or 2):
        errors.append("summary_request_count_exceeds_policy")
    if int(summary.get("metadata_search_rows_requested", 0) or 0) > int(policy.get("metadata_search_rows_max", 1) or 1):
        errors.append("summary_row_count_exceeds_policy")
    if summary.get("raw_response_committed") is not False:
        errors.append("summary_raw_response_committed")
    status = str(summary.get("probe_status", ""))
    if status not in {"not_run_yet", "dry_run", "succeeded", "zero_results", "rate_limited", "failed"}:
        errors.append(f"summary_bad_probe_status:{status}")
    if status in {"succeeded", "zero_results", "rate_limited", "failed"}:
        if summary.get("user_agent_present") is not True:
            errors.append("summary_user_agent_missing")
        if summary.get("contact_present") is not True:
            errors.append("summary_contact_missing")
        if not summary.get("http_responses"):
            errors.append("summary_missing_http_response_metadata")


def _validate_preview(preview: Mapping[str, Any], errors: list[str]) -> None:
    records = preview.get("preview_records", [])
    if not isinstance(records, list):
        errors.append("preview_records_not_list")
        return
    for record in records:
        if not isinstance(record, Mapping):
            errors.append("preview_record_not_object")
            continue
        if record.get("review_required") is not True:
            errors.append("preview_record_review_not_required")
        if record.get("accepted_truth") is not False:
            errors.append("preview_record_claims_truth")
        for key in (
            "download_performed",
            "source_cache_write_performed",
            "evidence_ledger_write_performed",
            "index_mutation_performed",
            "candidate_index_mutated",
            "reviewed_index_mutated",
            "master_index_mutated",
        ):
            if record.get(key) is not False:
                errors.append(f"preview_record_forbidden_flag:{key}")


def _validate_boundary(boundary: Mapping[str, Any], errors: list[str]) -> None:
    if boundary.get("schema_version") != "ia_live_probe_boundary_report.v0":
        errors.append("bad_live_probe_boundary_schema")
    if boundary.get("passed") is not True:
        errors.append("boundary_not_passed")
    if boundary.get("raw_response_committed") is not False:
        errors.append("boundary_raw_response_committed")
    for key in (
        "source_cache_write_performed",
        "evidence_ledger_write_performed",
        "candidate_index_mutated",
        "reviewed_index_mutated",
        "master_index_mutated",
        "download_performed",
        "upload_performed",
        "model_provider_used",
        "deployment_performed",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    ):
        if boundary.get(key) is not False:
            errors.append(f"boundary_forbidden_flag:{key}")


def _validate_no_raw_body_commit(repo_root: Path, errors: list[str]) -> None:
    for rel_path in (
        "control/inventory/ia_live_probe_result_summary.json",
        "control/inventory/ia_live_probe_normalized_preview.json",
        "control/audits/ia-02-local-live-metadata-probe-v0/generated/live_probe_redacted_summary.json",
        "control/audits/ia-02-local-live-metadata-probe-v0/generated/live_probe_boundary_report.json",
    ):
        path = repo_root / rel_path
        if not path.exists():
            continue
        payload = json.loads(path.read_text(encoding="utf-8"))
        if _contains_raw_body(payload):
            errors.append(f"raw_live_response_body_committed:{rel_path}")


def _contains_raw_body(value: Any) -> bool:
    if isinstance(value, Mapping):
        for key, item in value.items():
            if str(key) in {"body_text", "raw_body", "response_body", "raw_response_body"}:
                return True
            if _contains_raw_body(item):
                return True
    if isinstance(value, list):
        return any(_contains_raw_body(item) for item in value)
    return False


def _validate_network_imports(repo_root: Path, errors: list[str]) -> None:
    for path in (repo_root / "runtime/source_observation").glob("internet_archive*.py"):
        relative = path.relative_to(repo_root).as_posix()
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            imported = _import_name(node)
            if not imported:
                continue
            if imported == "urllib.request" and relative not in ALLOWED_NETWORK_IMPORT_FILES:
                errors.append(f"forbidden_urllib_request_import:{relative}")
            if imported in FORBIDDEN_NETWORK_IMPORTS or any(imported.startswith(name + ".") for name in FORBIDDEN_NETWORK_IMPORTS):
                errors.append(f"forbidden_network_import:{relative}:{imported}")


def _import_name(node: ast.AST) -> str:
    if isinstance(node, ast.Import):
        return node.names[0].name if node.names else ""
    if isinstance(node, ast.ImportFrom):
        module = node.module or ""
        if module == "urllib" and any(alias.name == "request" for alias in node.names):
            return "urllib.request"
        return module
    return ""


def _run_dry_run(repo_root: Path) -> dict[str, Any]:
    completed = subprocess.run(
        [sys.executable, "scripts/eureka_ia_live_metadata_probe.py", "--dry-run", "--json"],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    return {"returncode": completed.returncode, "stdout": completed.stdout, "stderr": completed.stderr}


def _validate_no_forbidden_git_state(repo_root: Path, errors: list[str], warnings: list[str]) -> None:
    status = subprocess.run(
        [
            "git",
            "status",
            "--short",
            "--",
            "runtime/connectors",
            "runtime/extraction",
            "runtime/search_quality",
            "data/public_index",
            "site/dist",
            "native",
            "crates",
            "eureka-instance",
            "instances",
            ".aide.local",
            "secrets",
            ".env",
        ],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    if status.returncode != 0:
        warnings.append("git_status_forbidden_paths_failed")
    elif status.stdout.strip():
        errors.append("forbidden_path_modified:" + status.stdout.strip().replace("\n", ";"))


if __name__ == "__main__":
    raise SystemExit(main())
