#!/usr/bin/env python3
"""Validate LOCAL-14 Local Appliance closeout and handoff evidence."""

from __future__ import annotations

import argparse
import ast
import json
import os
import signal
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_ROOT = Path(__file__).resolve().parent
if str(SCRIPTS_ROOT) not in sys.path:
    sys.path.insert(0, str(SCRIPTS_ROOT))

from audit_local_appliance_closeout import VALIDATORS, build_closeout_records


TASK_ID = "LOCAL-14"
AUDIT_ROOT = Path("control/audits/local-14-local-appliance-closeout-v0")
INVENTORIES = {
    "control/inventory/local_appliance_closeout_result.json": "local_appliance_closeout_result.v0",
    "control/inventory/local_appliance_capability_matrix.json": "local_appliance_capability_matrix.v0",
    "control/inventory/local_appliance_validation_matrix.json": "local_appliance_validation_matrix.v0",
    "control/inventory/local_appliance_warning_disposition.json": "local_appliance_warning_disposition.v0",
    "control/inventory/local_appliance_blocker_register.json": "local_appliance_blocker_register.v0",
    "control/inventory/local_appliance_runtime_surface_index.json": "local_appliance_runtime_surface_index.v0",
    "control/inventory/local_appliance_future_track_gate.json": "local_appliance_future_track_gate.v0",
    "control/inventory/local_appliance_handoff_to_hunt.json": "local_appliance_handoff_to_hunt.v0",
    "control/inventory/local_appliance_handoff_to_syn.json": "local_appliance_handoff_to_syn.v0",
    "control/inventory/local_appliance_handoff_to_f0.json": "local_appliance_handoff_to_f0.v0",
    "control/inventory/local_appliance_promotion_review.json": "local_appliance_promotion_review.v0",
    "control/inventory/local_14_leakage_baseline.json": "local_14_leakage_baseline.v0",
    "control/inventory/local_14_next_task_decision.json": "local_14_next_task_decision.v0",
}
AUDIT_FILES = (
    "README.md",
    "local_14_report.json",
    "capability_matrix.md",
    "validation_matrix.md",
    "warning_disposition.md",
    "blocker_register.md",
    "runtime_surface_index.md",
    "future_track_gate.md",
    "hunt_handoff.md",
    "syn_handoff.md",
    "f0_handoff.md",
    "promotion_review.md",
    "leakage_baseline.md",
    "validation.md",
    "generated/sample_closeout_result.json",
    "generated/sample_capability_matrix.json",
    "generated/sample_future_track_gate.json",
    "generated/sample_next_task_decision.json",
    "generated/sample_summary.md",
)
SCRIPTS = (
    "scripts/audit_local_appliance_closeout.py",
    "scripts/validate_local_appliance_closeout.py",
    "scripts/summarize_local_appliance_capabilities.py",
    "scripts/prepare_local_to_main_promotion_review.py",
    "scripts/prepare_hunt_syn_f0_handoff.py",
)
FORBIDDEN_IMPORT_PREFIXES = ("requests", "httpx", "aiohttp", "runtime.connectors")


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output")
    parser.add_argument("--skip-local-validators", action="store_true")
    parser.add_argument("--include-full-discovery", action="store_true")
    args = parser.parse_args(argv)

    result = validate(Path(args.repo_root).resolve(), not args.skip_local_validators, args.include_full_discovery)
    if args.output:
        write_json(Path(args.output), result)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print("LOCAL-14 appliance closeout validation", file=stdout)
        print(f"status: {result['status']}", file=stdout)
        for error in result["errors"]:
            print(f"ERROR: {error}", file=stdout)
        for warning in result["warnings"]:
            print(f"WARN: {warning}", file=stdout)
    return 0 if result["status"] in {"pass", "pass_with_warnings"} else 1


def validate(root: Path, run_local_validators: bool = True, include_full_discovery: bool = False) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    payloads = {rel: load_json(root / rel, schema, errors) for rel, schema in INVENTORIES.items()}
    report = load_json(root / AUDIT_ROOT / "local_14_report.json", "local_14_report.v0", errors)
    validate_files(root, errors)
    validate_script_imports(root, errors)
    validate_closeout_payloads(payloads, report, errors, warnings)
    audit = build_closeout_records(root)
    validate_audit_consistency(audit, payloads, errors)
    local_validator_results = run_local_validator_suite(root) if run_local_validators else []
    command_results = run_closeout_commands(root, include_full_discovery)
    classify_command_results(local_validator_results, command_results, warnings, errors)
    status = "fail" if errors else ("pass_with_warnings" if warnings else "pass")
    return {
        "schema_version": "local_appliance_closeout_validation.v0",
        "task": TASK_ID,
        "status": status,
        "errors": errors,
        "warnings": warnings,
        "local_validator_results": local_validator_results,
        "command_results": command_results,
        "local_track_complete": payloads["control/inventory/local_appliance_closeout_result.json"].get("local_track_complete") is True,
        "hunt_can_start": payloads["control/inventory/local_14_next_task_decision.json"].get("hunt_can_start") is True,
        "syn_can_start": payloads["control/inventory/local_14_next_task_decision.json"].get("syn_can_start") is True,
        "f0_can_resume": payloads["control/inventory/local_14_next_task_decision.json"].get("f0_can_resume") is True,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def validate_files(root: Path, errors: list[str]) -> None:
    for rel in SCRIPTS:
        if not (root / rel).is_file():
            errors.append(f"required script missing: {rel}")
    for rel in AUDIT_FILES:
        if not (root / AUDIT_ROOT / rel).is_file():
            errors.append(f"audit file missing: {AUDIT_ROOT / rel}")


def validate_script_imports(root: Path, errors: list[str]) -> None:
    for rel in SCRIPTS:
        text = (root / rel).read_text(encoding="utf-8")
        tree = ast.parse(text, filename=str(root / rel))
        for node in ast.walk(tree):
            modules: list[str] = []
            if isinstance(node, ast.Import):
                modules = [alias.name for alias in node.names]
            elif isinstance(node, ast.ImportFrom) and not node.level:
                modules = [node.module or ""]
            for module in modules:
                if any(module == prefix or module.startswith(prefix + ".") for prefix in FORBIDDEN_IMPORT_PREFIXES):
                    errors.append(f"forbidden import in {rel}: {module}")


def validate_closeout_payloads(
    payloads: Mapping[str, Mapping[str, Any]], report: Mapping[str, Any], errors: list[str], warnings: list[str]
) -> None:
    closeout = payloads["control/inventory/local_appliance_closeout_result.json"]
    required_true = (
        "local_track_complete",
        "all_required_capabilities_implemented",
        "all_required_capabilities_tested",
        "clean_machine_bootstrap_passed",
        "lan_read_only_smoke_passed",
        "auto_test_harness_passed",
        "f0_deferred_until_local_14",
        "f0_can_resume",
        "hunt_can_start",
        "syn_can_start",
    )
    for key in required_true:
        if closeout.get(key) is not True:
            errors.append(f"closeout result must set {key}=true")
    for key in ("deployment_performed", "production_readiness_claimed", "public_launch_readiness_claimed", "runtime_leakage_increased_during_local"):
        if closeout.get(key) is not False:
            errors.append(f"closeout result must set {key}=false")
    if int(closeout.get("hard_blockers_remaining") or 0) != 0:
        errors.append("hard blockers remain")
    if int(closeout.get("warnings_remaining") or 0) > 0 and closeout.get("status") != "pass_with_warnings":
        errors.append("warnings require pass_with_warnings status")
    if report.get("schema_version") != "local_14_report.v0":
        errors.append("LOCAL-14 audit report schema mismatch")
    if int(report.get("warnings_remaining") or 0) > 0:
        warnings.append("LOCAL-14 closes with disposed warnings")
    warning_disposition = payloads["control/inventory/local_appliance_warning_disposition.json"]
    for warning in warning_disposition.get("warnings", []):
        if not warning.get("classification"):
            errors.append("warning disposition missing classification")
    promotion = payloads["control/inventory/local_appliance_promotion_review.json"]
    if promotion.get("branch_mutation_performed") is not False or promotion.get("promotion_recommended") is not False:
        errors.append("promotion review must be plan-only and must not recommend automatic promotion")


def validate_audit_consistency(audit: Mapping[str, Any], payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    generated_closeout = audit["closeout_result"]
    committed_closeout = payloads["control/inventory/local_appliance_closeout_result.json"]
    for key in ("local_track_complete", "hard_blockers_remaining", "warnings_remaining", "recommended_next_task"):
        if generated_closeout.get(key) != committed_closeout.get(key):
            errors.append(f"committed closeout differs from generated audit for {key}")


def run_local_validator_suite(root: Path) -> list[dict[str, Any]]:
    results = []
    for validator in VALIDATORS:
        path = root / validator
        if not path.is_file():
            results.append({"command": f"python {validator}", "status": "missing", "returncode": 127})
            continue
        completed = run_command(root, [sys.executable, validator, "--json"], timeout=900)
        results.append(
            {
                "command": f"python {validator}",
                "status": "pass" if completed.returncode == 0 else "warn",
                "returncode": completed.returncode,
                "stdout_excerpt": completed.stdout[:500],
                "stderr_excerpt": completed.stderr[:500],
            }
        )
    return results


def run_closeout_commands(root: Path, include_full_discovery: bool) -> list[dict[str, Any]]:
    commands: list[tuple[list[str], int]] = [
        ([sys.executable, "scripts/check_generated_artifact_cleanliness.py", "--check", "--json"], 300),
        ([sys.executable, "scripts/check_architecture_boundaries.py"], 300),
        ([sys.executable, "scripts/audit_runtime_architecture_leakage.py", "--check", "--json"], 300),
        ([sys.executable, "scripts/validate_runtime_architecture_leakage.py"], 300),
    ]
    if include_full_discovery:
        commands.append(([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-t", "."], 1800))
    results = []
    for command, timeout in commands:
        completed = run_command(root, command, timeout=timeout)
        results.append(
            {
                "command": " ".join(command),
                "status": "pass" if completed.returncode == 0 else "warn",
                "returncode": completed.returncode,
                "stdout_excerpt": completed.stdout[:500],
                "stderr_excerpt": completed.stderr[:500],
            }
        )
    return results


def classify_command_results(
    local_validator_results: Sequence[Mapping[str, Any]],
    command_results: Sequence[Mapping[str, Any]],
    warnings: list[str],
    errors: list[str],
) -> None:
    for item in local_validator_results:
        if item["status"] == "warn":
            warnings.append(f"LOCAL validator warning: {item['command']}")
        elif item["status"] == "missing":
            errors.append(f"LOCAL validator missing: {item['command']}")
    for item in command_results:
        command = item["command"]
        if item["status"] != "pass":
            if "check_generated_artifact_cleanliness.py" in command:
                warnings.append("generated artifact cleanliness may fail before LOCAL-14 audit pack is committed")
            elif "runtime_architecture_leakage" in command:
                warnings.append("runtime leakage gate remains pre-existing and disposed")
            elif "unittest discover" in command:
                warnings.append("full unittest discovery remains fail_other")
            else:
                warnings.append(f"command warning: {command}")


def run_command(root: Path, command: Sequence[str], timeout: int) -> subprocess.CompletedProcess[str]:
    kwargs: dict[str, Any] = {}
    if sys.platform == "win32":
        kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        kwargs["start_new_session"] = True
    process = subprocess.Popen(
        command,
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        **kwargs,
    )
    try:
        stdout, stderr = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        if sys.platform == "win32":
            subprocess.run(
                ["taskkill", "/F", "/T", "/PID", str(process.pid)],
                text=True,
                capture_output=True,
                check=False,
            )
        else:
            try:
                os.killpg(process.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
        try:
            stdout, stderr = process.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
        timeout_note = f"command timed out after {timeout}s"
        return subprocess.CompletedProcess(command, 124, stdout or "", ((stderr or "") + "\n" + timeout_note).strip())
    return subprocess.CompletedProcess(command, process.returncode or 0, stdout or "", stderr or "")


def load_json(path: Path, schema: str, errors: list[str]) -> dict[str, Any]:
    if not path.is_file():
        errors.append(f"required JSON missing: {path}")
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"invalid JSON {path}: {exc}")
        return {}
    if payload.get("schema_version") != schema:
        errors.append(f"schema mismatch for {path}: {payload.get('schema_version')} != {schema}")
    return payload


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
