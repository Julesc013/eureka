#!/usr/bin/env python3
"""Validate the PLAY-01 operator play-session boundary."""

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
PLAY_POLICY_PATH = REPO_ROOT / "control" / "policies" / "play_session_policy.json"
PLAY_QUERIES_PATH = REPO_ROOT / "examples" / "play" / "demo_queries.json"

if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

from eureka_play_session import REPORT_SECTIONS  # noqa: E402
from validate_play_seed_pack import (  # noqa: E402
    COMPATIBILITY_QUERY,
    EXTRACTION_QUERY,
    HARD_SOURCE_ROUTING_QUERY,
    KNOWN_ABSENCE_QUERY,
    KNOWN_HIT_QUERY,
    LEGACY_COMPATIBLE_QUERY,
    MEDIA_QUERY,
)


FORBIDDEN_TRUE_FLAGS = (
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
    "instance_state_committed",
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit JSON output.")
    args = parser.parse_args(argv)
    result = validate_play_session()
    print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    return 0 if result["status"] == "pass" else 1


def validate_play_session() -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    policy = _load_json(PLAY_POLICY_PATH, errors)
    queries = _load_json(PLAY_QUERIES_PATH, errors)
    _validate_policy(policy, errors)
    _validate_queries(queries, errors)
    help_result = _run_json("scripts/eureka_play_session.py", "--help")
    if help_result["returncode"] != 0:
        errors.append("play session help failed")
    dry_run = _run_dry_run(errors)
    seed_without_apply = _run_seed_without_apply(errors)
    apply_without_token = _run_json(
        "scripts/eureka_play_session.py",
        "--instance",
        "../instances/default",
        "--apply",
        "--json",
    )
    if apply_without_token["returncode"] == 0:
        errors.append("apply mode succeeded without operator token")
    _validate_report(dry_run["payload"], errors)
    _validate_report(seed_without_apply["payload"], errors)
    _validate_no_instance_state_committed(errors)
    status = "fail" if errors else "pass"
    return {
        "schema_version": "play_session_validation.v0",
        "task": "PLAY-01",
        "status": status,
        "errors": errors,
        "warnings": warnings,
        "policy_exists": PLAY_POLICY_PATH.is_file(),
        "script_help_passed": help_result["returncode"] == 0,
        "dry_run_does_not_mutate_instance": dry_run["did_not_mutate"],
        "apply_requires_explicit_apply": seed_without_apply["payload"].get("seed_state", {}).get("dry_run") is True,
        "apply_requires_operator_token": apply_without_token["returncode"] != 0,
        "known_demo_queries_present": _known_queries_present(queries),
        "report_sections_present": _report_sections_present(dry_run["payload"]),
        "blocked_source_probe_checked": bool(dry_run["payload"].get("blocked_future_actions", {}).get("source_probe_ids")),
        "blocked_extraction_checked": bool(dry_run["payload"].get("blocked_future_actions", {}).get("extraction_ids")),
        "blocked_ai_checked": bool(dry_run["payload"].get("blocked_future_actions", {}).get("ai_ids")),
        "source_probe_executed": False,
        "extraction_executed": False,
        "model_provider_used": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
        "instance_state_committed": False,
        "dry_run_report": _compact_session_report(dry_run["payload"]),
        "seed_without_apply_report": _compact_session_report(seed_without_apply["payload"]),
    }


def _run_dry_run(errors: list[str]) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="eureka-play-session-validator-") as tmp:
        instance = Path(tmp) / "instances" / "default"
        completed = _run_json(
            "scripts/eureka_play_session.py",
            "--instance",
            str(instance),
            "--operator-token",
            "validator-token",
            "--dry-run",
            "--no-server-check",
            "--json",
        )
        did_not_mutate = not instance.exists()
        if completed["returncode"] != 0 or completed["payload"].get("status") != "pass":
            errors.append("dry-run play session failed")
        if not did_not_mutate:
            errors.append("dry-run play session mutated instance path")
        completed["did_not_mutate"] = did_not_mutate
        return completed


def _run_seed_without_apply(errors: list[str]) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="eureka-play-session-validator-") as tmp:
        instance = Path(tmp) / "instances" / "default"
        completed = _run_json(
            "scripts/eureka_play_session.py",
            "--instance",
            str(instance),
            "--operator-token",
            "validator-token",
            "--seed-demo",
            "--json",
        )
        if completed["returncode"] != 0 or completed["payload"].get("status") != "pass":
            errors.append("--seed-demo dry-run play session failed")
        if instance.exists():
            errors.append("--seed-demo without --apply mutated instance path")
        return completed


def _validate_policy(policy: Mapping[str, Any], errors: list[str]) -> None:
    expected = {
        "schema_version": "play_session_policy.v0",
        "task": "PLAY-01",
        "dry_run_default": True,
        "explicit_instance_required_for_apply": True,
        "operator_token_required_for_instance_mutation": True,
        "local_instance_state_commit_forbidden": True,
        "live_source_calls_enabled": False,
        "source_probe_execution_enabled": False,
        "extraction_execution_enabled": False,
        "model_provider_enabled": False,
        "download_install_execute_enabled": False,
        "deployment_enabled": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }
    for key, value in expected.items():
        if policy.get(key) != value:
            errors.append(f"policy {key} mismatch")


def _validate_queries(payload: Mapping[str, Any], errors: list[str]) -> None:
    if not _known_queries_present(payload):
        errors.append("required PLAY demo queries are missing")


def _validate_report(report: Mapping[str, Any], errors: list[str]) -> None:
    if report.get("status") != "pass":
        errors.append("play session report did not pass")
    if not _report_sections_present(report):
        errors.append("play session report missing required sections")
    if report.get("seed_state", {}).get("mutation_performed") is not False:
        errors.append("dry-run report claims mutation")
    for key in FORBIDDEN_TRUE_FLAGS:
        if report.get(key) is True or report.get("boundaries", {}).get(key) is True:
            errors.append(f"forbidden true flag in play session report: {key}")
    blocked = report.get("blocked_future_actions", {})
    if not blocked.get("all_remain_blocked_by_policy"):
        errors.append("blocked future actions are not all policy-blocked")


def _known_queries_present(payload: Mapping[str, Any]) -> bool:
    queries = {str(item.get("query")) for item in payload.get("queries", []) if isinstance(item, Mapping)}
    required = {
        KNOWN_HIT_QUERY,
        KNOWN_ABSENCE_QUERY,
        MEDIA_QUERY,
        EXTRACTION_QUERY,
        HARD_SOURCE_ROUTING_QUERY,
        COMPATIBILITY_QUERY,
        LEGACY_COMPATIBLE_QUERY,
    }
    return required.issubset(queries)


def _report_sections_present(report: Mapping[str, Any]) -> bool:
    return all(section in report for section in REPORT_SECTIONS)


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


def _compact_session_report(payload: Mapping[str, Any]) -> dict[str, Any]:
    seed_state = payload.get("seed_state", {})
    validation = payload.get("validation", {})
    checks = validation.get("checks", {}) if isinstance(validation, Mapping) else {}
    return {
        "schema_version": payload.get("schema_version"),
        "task": payload.get("task"),
        "status": payload.get("status"),
        "mode": payload.get("mode"),
        "seed_mode": seed_state.get("mode") if isinstance(seed_state, Mapping) else None,
        "mutation_performed": seed_state.get("mutation_performed") if isinstance(seed_state, Mapping) else None,
        "known_hit_checked": checks.get("known_hit_checked") if isinstance(checks, Mapping) else None,
        "known_absence_checked": checks.get("known_absence_checked") if isinstance(checks, Mapping) else None,
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
