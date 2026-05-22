#!/usr/bin/env python3
"""Validate IA-01 fixture replay hardening artifacts."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.source_observation.internet_archive_fixture_replay import (
    assert_no_forbidden_side_effects,
    assert_no_network_imports,
    replay_fixture_directory_report,
)
from scripts.validate_ia_metadata_policy import validate_ia_metadata_policy


FIXTURE_DIR = REPO_ROOT / "examples" / "internet_archive_metadata"

REQUIRED_FIXTURES = {
    "metadata_search_small.fixture.json": {
        "fixture_id": "metadata_search_small",
        "observation_kind": "metadata_search_result",
    },
    "item_metadata.fixture.json": {
        "fixture_id": "item_metadata",
        "observation_kind": "item_metadata",
    },
    "item_file_list.fixture.json": {
        "fixture_id": "item_file_list",
        "observation_kind": "item_file_list",
    },
    "missing_item.fixture.json": {
        "fixture_id": "missing_item",
        "observation_kind": "missing_item",
    },
    "malformed_partial.fixture.json": {
        "fixture_id": "malformed_partial",
        "observation_kind": "malformed_partial",
    },
    "retry_after_429.fixture.json": {
        "fixture_id": "retry_after_429",
        "observation_kind": "retry_after",
    },
    "large_file_list.fixture.json": {
        "fixture_id": "large_file_list",
        "observation_kind": "large_file_list",
    },
    "no_download_proof.fixture.json": {
        "fixture_id": "no_download_proof",
        "observation_kind": "no_download_proof",
    },
}

REQUIRED_FILES = [
    "examples/internet_archive_metadata/expected_normalized_records.json",
    "examples/internet_archive_metadata/expected_boundary_reports.json",
    "runtime/source_observation/internet_archive_metadata.py",
    "runtime/source_observation/internet_archive_normalization.py",
    "runtime/source_observation/internet_archive_validation.py",
    "runtime/source_observation/internet_archive_fixture_replay.py",
    "scripts/eureka_ia_fixture_replay.py",
    "tests/runtime/test_ia_metadata_fixture_replay.py",
    "tests/runtime/test_ia_metadata_normalization.py",
    "tests/runtime/test_ia_metadata_boundary.py",
    "tests/operations/test_ia_fixture_replay_scripts.py",
    "docs/reference/IA_METADATA_FIXTURE_REPLAY.md",
    "control/inventory/ia_fixture_inventory.json",
    "control/inventory/ia_fixture_replay_matrix.json",
    "control/inventory/ia_fixture_normalization_matrix.json",
    "control/inventory/ia_fixture_boundary_matrix.json",
    "control/inventory/ia_fixture_no_download_proof.json",
    "control/inventory/ia_01_result.json",
    "control/inventory/ia_01_next_task_decision.json",
    "control/audits/ia-01-fixture-replay-hardening-v0/ia_01_report.json",
]


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    _ = argv
    result = validate_ia_fixture_replay(REPO_ROOT)
    print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    return 0 if result["status"] == "pass" else 1


def validate_ia_fixture_replay(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    policy_result = validate_ia_metadata_policy(repo_root)
    if policy_result.get("status") != "pass":
        errors.append("ia_metadata_policy_validator_failed")

    for rel_path in REQUIRED_FILES:
        if not (repo_root / rel_path).exists():
            errors.append(f"missing_file:{rel_path}")
    for filename in REQUIRED_FIXTURES:
        if not (FIXTURE_DIR / filename).exists():
            errors.append(f"missing_fixture:{filename}")

    try:
        assert_no_network_imports()
    except RuntimeError as exc:
        errors.append(f"forbidden_network_imports:{exc}")

    report: Mapping[str, Any] = {}
    if not errors:
        try:
            report = replay_fixture_directory_report(FIXTURE_DIR)
            assert_no_forbidden_side_effects(report)
        except Exception as exc:  # pragma: no cover - surfaced in validation payload
            errors.append(f"fixture_replay_failed:{exc}")

    if report:
        observed_by_id = {item["fixture_id"]: item for item in report.get("normalized_records", [])}
        for expected in REQUIRED_FIXTURES.values():
            fixture_id = str(expected["fixture_id"])
            observation_kind = str(expected["observation_kind"])
            if fixture_id not in observed_by_id:
                errors.append(f"fixture_id_not_replayed:{fixture_id}")
            elif observed_by_id[fixture_id].get("observation_kind") != observation_kind:
                errors.append(f"fixture_kind_mismatch:{fixture_id}")
        _compare_expected(repo_root, report, errors)
        _validate_case_semantics(report, errors)

    cli_result = _run_cli(repo_root)
    if cli_result.get("returncode") != 0:
        errors.append("fixture_replay_cli_failed")
        warnings.append(str(cli_result.get("stderr", "")).strip())

    _validate_no_forbidden_git_state(repo_root, errors)

    return {
        "schema_version": "ia_fixture_replay_validation.v0",
        "task": "IA-01",
        "status": "pass" if not errors else "fail",
        "errors": errors,
        "warnings": [item for item in warnings if item],
        "fixture_count": int(report.get("fixture_count", 0)) if report else 0,
        "all_fixtures_replay": bool(report.get("all_fixtures_replay", False)) if report else False,
        "expected_records_match": "expected_normalized_records_mismatch" not in errors
        and "expected_boundary_reports_mismatch" not in errors,
        "no_download_proof_passed": _no_download_proof_passed(report),
        "live_source_call_performed": False,
        "source_probe_executed": False,
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


def _compare_expected(repo_root: Path, report: Mapping[str, Any], errors: list[str]) -> None:
    expected_records_path = repo_root / "examples/internet_archive_metadata/expected_normalized_records.json"
    expected_boundaries_path = repo_root / "examples/internet_archive_metadata/expected_boundary_reports.json"
    if not expected_records_path.exists() or not expected_boundaries_path.exists():
        return
    expected_records = json.loads(expected_records_path.read_text(encoding="utf-8"))
    expected_boundaries = json.loads(expected_boundaries_path.read_text(encoding="utf-8"))
    records_by_id = {item["fixture_id"]: item for item in report.get("normalized_records", [])}
    boundaries_by_id = {item["fixture_id"]: item for item in report.get("boundary_reports", [])}
    for expected in expected_records.get("records", []):
        actual = records_by_id.get(expected.get("fixture_id"))
        if not actual:
            errors.append("expected_normalized_records_mismatch")
            continue
        for key in ("observation_id", "observation_kind", "review_required", "accepted_truth", "download_performed"):
            if actual.get(key) != expected.get(key):
                errors.append("expected_normalized_records_mismatch")
        if len(actual.get("file_metadata_candidates", [])) != expected.get("file_metadata_count"):
            errors.append("expected_normalized_records_mismatch")
        for flag in expected.get("risk_flags_include", []):
            if flag not in actual.get("risk_flags", []):
                errors.append("expected_normalized_records_mismatch")
    for expected in expected_boundaries.get("boundary_reports", []):
        actual = boundaries_by_id.get(expected.get("fixture_id"))
        if not actual:
            errors.append("expected_boundary_reports_mismatch")
            continue
        for key in ("observation_id", "observation_kind", "passed", "network_imports_detected"):
            if actual.get(key) != expected.get(key):
                errors.append("expected_boundary_reports_mismatch")
        for flag in (
            "live_source_call_performed",
            "source_probe_executed",
            "source_cache_write_performed",
            "evidence_ledger_write_performed",
            "candidate_index_mutated",
            "reviewed_index_mutated",
            "master_index_mutated",
            "download_performed",
        ):
            if actual.get(flag) is not False:
                errors.append("expected_boundary_reports_mismatch")


def _validate_case_semantics(report: Mapping[str, Any], errors: list[str]) -> None:
    records = {item["fixture_id"]: item for item in report.get("normalized_records", [])}
    if records.get("missing_item", {}).get("observation_kind") != "missing_item":
        errors.append("missing_item_not_source_miss_state")
    if records.get("malformed_partial", {}).get("observation_kind") != "malformed_partial":
        errors.append("malformed_partial_not_handled")
    retry = records.get("retry_after_429", {})
    if retry.get("observation_kind") != "retry_after" or "retry_after_required" not in retry.get("risk_flags", []):
        errors.append("retry_after_not_backoff_state")
    large = records.get("large_file_list", {})
    if len(large.get("file_metadata_candidates", [])) > 5:
        errors.append("large_file_list_cap_not_respected")
    for record in records.values():
        if record.get("review_required") is not True or record.get("accepted_truth") is not False:
            errors.append(f"record_claims_truth:{record.get('fixture_id')}")
        for key in (
            "download_performed",
            "source_cache_write_performed",
            "evidence_ledger_write_performed",
            "index_mutation_performed",
        ):
            if record.get(key) is not False:
                errors.append(f"record_forbidden_side_effect:{record.get('fixture_id')}:{key}")


def _no_download_proof_passed(report: Mapping[str, Any]) -> bool:
    records = {item["fixture_id"]: item for item in report.get("normalized_records", [])}
    record = records.get("no_download_proof", {})
    return bool(record) and record.get("download_performed") is False and bool(record.get("file_metadata_candidates"))


def _run_cli(repo_root: Path) -> dict[str, Any]:
    completed = subprocess.run(
        [
            sys.executable,
            "scripts/eureka_ia_fixture_replay.py",
            "--fixture-dir",
            "examples/internet_archive_metadata",
            "--json",
        ],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    return {
        "returncode": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def _validate_no_forbidden_git_state(repo_root: Path, errors: list[str]) -> None:
    status = subprocess.run(
        [
            "git",
            "status",
            "--short",
            "--",
            "runtime/connectors",
            "runtime/extraction",
            "runtime/search_quality",
            "site/dist/data/public_index",
            "site/dist",
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
    if status.returncode == 0 and status.stdout.strip():
        errors.append("forbidden_path_modified")
    tracked_instances = subprocess.run(
        ["git", "ls-files", "--", "eureka-instance", "instances"],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    if tracked_instances.returncode == 0 and tracked_instances.stdout.strip():
        errors.append("local_instance_state_tracked")


if __name__ == "__main__":
    raise SystemExit(main())
