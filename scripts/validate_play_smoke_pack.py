#!/usr/bin/env python3
"""Validate the PLAY-02 demo query/absence/hunt smoke pack."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_ROOT = REPO_ROOT / "scripts"
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

from eureka_play_smoke import REPORT_SECTIONS  # noqa: E402


POLICY_PATH = REPO_ROOT / "control" / "policies" / "play_smoke_policy.json"
QUERY_MATRIX_PATH = REPO_ROOT / "control" / "inventory" / "play_smoke_query_matrix.json"
ROUTE_MATRIX_PATH = REPO_ROOT / "control" / "inventory" / "play_smoke_route_matrix.json"
RESULT_SCHEMA_PATH = REPO_ROOT / "control" / "inventory" / "play_smoke_result_schema.json"

REQUIRED_QUERY_IDS = {
    "known_hit",
    "known_absence",
    "media_search_need",
    "extraction_search_need",
    "hard_source_routing",
    "compatibility",
}
REQUIRED_ROUTE_IDS = {
    "root_page",
    "status_page",
    "search_known_hit",
    "search_known_absence",
    "hunts_page",
    "hunt_detail_if_available",
    "search_need_detail_if_available",
    "workunit_detail_or_list_if_available",
    "api_search",
    "api_absence",
    "api_hunts_if_available",
    "api_status",
}
FORBIDDEN_TRUE_FLAGS = (
    "operator_instance_mutated",
    "instance_state_committed",
    "fake_evidence_created",
    "fake_verified_records_created",
    "live_source_call_performed",
    "source_probe_executed",
    "extraction_executed",
    "model_provider_used",
    "download_install_execute_performed",
    "deployment_performed",
    "production_readiness_claimed",
    "public_launch_readiness_claimed",
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args(argv)

    result = validate_play_smoke_pack()
    print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    return 0 if result["status"] == "pass" else 1


def validate_play_smoke_pack() -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    policy = _load_json(POLICY_PATH, errors)
    query_matrix = _load_json(QUERY_MATRIX_PATH, errors)
    route_matrix = _load_json(ROUTE_MATRIX_PATH, errors)
    result_schema = _load_json(RESULT_SCHEMA_PATH, errors)
    _validate_policy(policy, errors)
    _validate_query_matrix(query_matrix, errors)
    _validate_route_matrix(route_matrix, errors)
    _validate_result_schema(result_schema, errors)
    help_result = _run_json("scripts/eureka_play_smoke.py", "--help")
    if help_result["returncode"] != 0:
        errors.append("play smoke help failed")
    dry_run = _run_dry_run(errors)
    temp_apply = _run_temp_apply(errors)
    _validate_smoke_report(dry_run["payload"], errors, expected_temp=False)
    _validate_smoke_report(temp_apply["payload"], errors, expected_temp=True)
    _validate_no_instance_state_committed(errors)
    status = "fail" if errors else "pass"
    return {
        "schema_version": "play_smoke_pack_validation.v0",
        "task": "PLAY-02",
        "status": status,
        "errors": errors,
        "warnings": warnings,
        "policy_exists": POLICY_PATH.is_file(),
        "query_matrix_exists": QUERY_MATRIX_PATH.is_file(),
        "route_matrix_exists": ROUTE_MATRIX_PATH.is_file(),
        "result_schema_exists": RESULT_SCHEMA_PATH.is_file(),
        "script_help_passed": help_result["returncode"] == 0,
        "dry_run_smoke_passed": dry_run["payload"].get("status") == "pass",
        "dry_run_does_not_mutate_operator_instance": dry_run.get("operator_instance_untouched") is True,
        "temp_instance_apply_passed": temp_apply["payload"].get("status") == "pass",
        "known_hit_assertion_exists": _query_present(query_matrix, "known_hit"),
        "known_absence_assertion_exists": _query_present(query_matrix, "known_absence"),
        "media_search_need_assertion_exists": _query_present(query_matrix, "media_search_need"),
        "extraction_search_need_assertion_exists": _query_present(query_matrix, "extraction_search_need"),
        "blocked_source_probe_assertion_exists": _blocked_path_present(query_matrix, "source_probe"),
        "blocked_extraction_assertion_exists": _blocked_path_present(query_matrix, "extraction"),
        "blocked_ai_assertion_exists": _blocked_path_present(query_matrix, "AI_model"),
        "source_probe_executed": False,
        "extraction_executed": False,
        "model_provider_used": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
        "instance_state_committed": False,
        "dry_run_report": _compact_smoke_report(dry_run["payload"]),
        "temp_apply_report": _compact_smoke_report(temp_apply["payload"]),
    }


def _validate_policy(policy: Mapping[str, Any], errors: list[str]) -> None:
    expected = {
        "schema_version": "play_smoke_policy.v0",
        "task": "PLAY-02",
        "temp_instance_allowed": True,
        "operator_instance_mutation_default": False,
        "dry_run_default": True,
        "explicit_apply_required": True,
        "source_probe_execution_enabled": False,
        "extraction_execution_enabled": False,
        "model_provider_enabled": False,
        "download_install_execute_enabled": False,
        "deployment_enabled": False,
        "fake_evidence_forbidden": True,
        "fake_verified_records_forbidden": True,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }
    for key, value in expected.items():
        if policy.get(key) != value:
            errors.append(f"policy {key} mismatch")


def _validate_query_matrix(payload: Mapping[str, Any], errors: list[str]) -> None:
    rows = payload.get("queries", [])
    if not isinstance(rows, list):
        errors.append("query matrix queries must be a list")
        return
    ids = {str(item.get("query_id")) for item in rows if isinstance(item, Mapping)}
    missing = sorted(REQUIRED_QUERY_IDS - ids)
    if missing:
        errors.append("missing query matrix rows: " + ", ".join(missing))
    required_fields = {
        "query_id",
        "query",
        "expected_state",
        "expected_artifacts",
        "must_not_create",
        "blocked_paths_expected",
        "smoke_assertions",
    }
    for item in rows:
        if not isinstance(item, Mapping):
            errors.append("query matrix row must be object")
            continue
        missing_fields = sorted(required_fields - set(item))
        if missing_fields:
            errors.append(f"query matrix row {item.get('query_id')} missing fields: {', '.join(missing_fields)}")


def _validate_route_matrix(payload: Mapping[str, Any], errors: list[str]) -> None:
    rows = payload.get("routes", [])
    if not isinstance(rows, list):
        errors.append("route matrix routes must be a list")
        return
    ids = {str(item.get("route_id")) for item in rows if isinstance(item, Mapping)}
    missing = sorted(REQUIRED_ROUTE_IDS - ids)
    if missing:
        errors.append("missing route matrix rows: " + ", ".join(missing))
    required_fields = {
        "route_id",
        "route",
        "method",
        "requires_server",
        "requires_operator_token",
        "expected_status",
        "expected_content_markers",
        "forbidden_content_markers",
    }
    for item in rows:
        if not isinstance(item, Mapping):
            errors.append("route matrix row must be object")
            continue
        missing_fields = sorted(required_fields - set(item))
        if missing_fields:
            errors.append(f"route matrix row {item.get('route_id')} missing fields: {', '.join(missing_fields)}")


def _validate_result_schema(payload: Mapping[str, Any], errors: list[str]) -> None:
    sections = payload.get("sections", [])
    if not isinstance(sections, list):
        errors.append("result schema sections must be a list")
        return
    names = {str(item.get("section")) for item in sections if isinstance(item, Mapping)}
    missing = [section for section in REPORT_SECTIONS if section not in names]
    if missing:
        errors.append("result schema missing sections: " + ", ".join(missing))


def _run_dry_run(errors: list[str]) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="eureka-play-smoke-validator-") as tmp:
        instance = Path(tmp) / "instances" / "default"
        completed = _run_json(
            "scripts/eureka_play_smoke.py",
            "--instance",
            str(instance),
            "--operator-token",
            "validator-token",
            "--dry-run",
            "--json",
        )
        untouched = not instance.exists()
        if completed["returncode"] != 0 or completed["payload"].get("status") != "pass":
            errors.append("dry-run play smoke failed")
        if not untouched:
            errors.append("dry-run play smoke mutated instance path")
        completed["operator_instance_untouched"] = untouched
        return completed


def _run_temp_apply(errors: list[str]) -> dict[str, Any]:
    completed = _run_json(
        "scripts/eureka_play_smoke.py",
        "--use-temp-instance",
        "--apply-demo-to-temp",
        "--operator-token",
        "validator-token",
        "--json",
    )
    if completed["returncode"] != 0 or completed["payload"].get("status") != "pass":
        errors.append("temp-instance apply play smoke failed")
    return completed


def _validate_smoke_report(payload: Mapping[str, Any], errors: list[str], *, expected_temp: bool) -> None:
    if payload.get("status") != "pass":
        errors.append("play smoke report did not pass")
    for section in REPORT_SECTIONS:
        if section not in payload:
            errors.append(f"play smoke report missing section: {section}")
    instance = payload.get("instance", {})
    if isinstance(instance, Mapping) and bool(instance.get("temporary")) != expected_temp:
        errors.append("play smoke temporary-instance flag mismatch")
    checks = payload.get("validation", {}).get("checks", {}) if isinstance(payload.get("validation"), Mapping) else {}
    for key in (
        "known_hit_checked",
        "known_absence_checked",
        "media_search_need_checked",
        "extraction_search_need_checked",
        "hard_source_routing_checked",
        "compatibility_query_checked",
        "blocked_source_probe_checked",
        "blocked_extraction_checked",
        "blocked_ai_checked",
    ):
        if not isinstance(checks, Mapping) or checks.get(key) is not True:
            errors.append(f"play smoke check missing or false: {key}")
    for key in FORBIDDEN_TRUE_FLAGS:
        if payload.get(key) is True or payload.get("boundaries", {}).get(key) is True:
            errors.append(f"forbidden true flag in play smoke report: {key}")


def _validate_no_instance_state_committed(errors: list[str]) -> None:
    completed = subprocess.run(
        ["git", "ls-files", "--", "eureka-instance", "instances"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode == 0 and completed.stdout.strip():
        errors.append("local instance state is tracked: " + completed.stdout.strip().replace("\n", ", "))


def _query_present(payload: Mapping[str, Any], query_id: str) -> bool:
    return any(isinstance(item, Mapping) and item.get("query_id") == query_id for item in payload.get("queries", []))


def _blocked_path_present(payload: Mapping[str, Any], marker: str) -> bool:
    for item in payload.get("queries", []):
        if not isinstance(item, Mapping):
            continue
        paths = item.get("blocked_paths_expected", [])
        if any(str(path) == marker for path in paths if isinstance(path, str)):
            return True
    return False


def _compact_smoke_report(payload: Mapping[str, Any]) -> dict[str, Any]:
    checks = payload.get("validation", {}).get("checks", {}) if isinstance(payload.get("validation"), Mapping) else {}
    return {
        "schema_version": payload.get("schema_version"),
        "task": payload.get("task"),
        "status": payload.get("status"),
        "mode": payload.get("mode"),
        "known_hit_checked": checks.get("known_hit_checked") if isinstance(checks, Mapping) else None,
        "known_absence_checked": checks.get("known_absence_checked") if isinstance(checks, Mapping) else None,
        "media_search_need_checked": checks.get("media_search_need_checked") if isinstance(checks, Mapping) else None,
        "extraction_search_need_checked": checks.get("extraction_search_need_checked") if isinstance(checks, Mapping) else None,
        "blocked_source_probe_checked": checks.get("blocked_source_probe_checked") if isinstance(checks, Mapping) else None,
        "blocked_extraction_checked": checks.get("blocked_extraction_checked") if isinstance(checks, Mapping) else None,
        "blocked_ai_checked": checks.get("blocked_ai_checked") if isinstance(checks, Mapping) else None,
        "source_probe_executed": payload.get("source_probe_executed"),
        "extraction_executed": payload.get("extraction_executed"),
        "model_provider_used": payload.get("model_provider_used"),
        "deployment_performed": payload.get("deployment_performed"),
    }


def _load_json(path: Path, errors: list[str]) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"missing file: {path.relative_to(REPO_ROOT).as_posix()}")
        return {}
    except json.JSONDecodeError as exc:
        errors.append(f"invalid JSON {path.relative_to(REPO_ROOT).as_posix()}: {exc}")
        return {}
    if not isinstance(payload, dict):
        errors.append(f"JSON root must be object: {path.relative_to(REPO_ROOT).as_posix()}")
        return {}
    return payload


def _run_json(*args: str) -> dict[str, Any]:
    completed = subprocess.run([sys.executable, *args], cwd=REPO_ROOT, text=True, capture_output=True, check=False)
    try:
        payload = json.loads(completed.stdout)
    except json.JSONDecodeError:
        payload = {"status": "fail", "stdout": completed.stdout, "stderr": completed.stderr}
    return {"returncode": completed.returncode, "payload": payload, "stderr": completed.stderr}


if __name__ == "__main__":
    raise SystemExit(main())
