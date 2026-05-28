#!/usr/bin/env python3
"""Unified Eureka test gate command with compact AI handoff support."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import zipfile
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools.testing.check_full_discovery import (  # noqa: E402
    DEFAULT_WATCH_INTERVAL_SECONDS,
    git_status_short,
    is_terminal,
    load_status,
    status_exit_code,
    watch_status,
)
from tools.testing.run_full_unittest_discovery import (  # noqa: E402
    DEFAULT_HEARTBEAT_SECONDS,
    DEFAULT_TIMEOUT_SECONDS,
    discovery_artifact_paths,
    format_duration,
    normalize_output_dir,
    output_dir_for_run_id,
    run_discovery,
)
from tools.testing.start_full_discovery import (  # noqa: E402
    pid_is_running,
    read_json,
    start_discovery,
)
from tools.testing.eureka_test_gate import (  # noqa: E402
    assert_safe_clean_dir,
    copy_to_clipboard,
    open_path,
    terminate_pid,
)


AI_HANDOFF_SCHEMA_VERSION = "eureka_ai_handoff.v0"
GATE_STATUS_SCHEMA_VERSION = "eureka_gate_status.v0"
GATE_START_SCHEMA_VERSION = "eureka_gate_start.v0"
TERMINAL_STATUSES = {"pass", "fail", "error", "cancelled", "timeout"}


@dataclass(frozen=True)
class GateDefinition:
    name: str
    legacy_gate: str
    run_id: str
    task: str
    description: str
    recommended_next_task_pass: str
    recommended_next_task_fail: str
    audit_dir: Path
    inventory_result: Path | None


GATES: dict[str, GateDefinition] = {
    "public-alpha-closeout": GateDefinition(
        name="public-alpha-closeout",
        legacy_gate="public_alpha_readonly_closeout",
        run_id="public_alpha_readonly_closeout",
        task="PUBLIC-ALPHA-READONLY-CLOSEOUT-01",
        description="External full discovery for the public read-only alpha closeout.",
        recommended_next_task_pass="DEV-TO-MAIN-PROMOTION-REVIEW-04",
        recommended_next_task_fail="CLASSIFY_PUBLIC_ALPHA_CLOSEOUT_FAILURE_FAMILIES",
        audit_dir=Path("control/audits/public-alpha-readonly-closeout-01-v0"),
        inventory_result=Path("control/inventory/public_alpha_readonly_closeout_full_discovery_result.json"),
    ),
    "source-snapshot-closeout": GateDefinition(
        name="source-snapshot-closeout",
        legacy_gate="source_snapshot_closeout",
        run_id="source_snapshot_closeout",
        task="SOURCE-SNAPSHOT-BASELINE-CLOSEOUT-01",
        description="External full discovery for source snapshot closeout.",
        recommended_next_task_pass="DEV-TO-MAIN-PROMOTION-REVIEW",
        recommended_next_task_fail="CLASSIFY_SOURCE_SNAPSHOT_CLOSEOUT_FAILURE_FAMILIES",
        audit_dir=Path("control/audits/source-snapshot-baseline-closeout-01-v0"),
        inventory_result=Path("control/inventory/source_snapshot_closeout_full_discovery_result.json"),
    ),
    "promotion-gate": GateDefinition(
        name="promotion-gate",
        legacy_gate="promotion_gate",
        run_id="promotion_gate",
        task="PROMOTION-GATE",
        description="External full discovery for promotion gate evidence.",
        recommended_next_task_pass="CONTINUE_PROMOTION_REVIEW",
        recommended_next_task_fail="BLOCK_PROMOTION_AND_CLASSIFY_FAILURE_FAMILIES",
        audit_dir=Path("control/audits/promotion-gate-v0"),
        inventory_result=Path("control/inventory/promotion_gate_full_discovery_result.json"),
    ),
}

GATE_ALIASES = {
    **{name: name for name in GATES},
    "public_alpha_readonly_closeout": "public-alpha-closeout",
    "source_snapshot_closeout": "source-snapshot-closeout",
    "promotion_gate": "promotion-gate",
}


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("gate", nargs="?", help="Gate name: public-alpha-closeout, source-snapshot-closeout, promotion-gate.")
    parser.add_argument("--watch", action="store_true", help="Run or attach to a gate and wait for terminal status.")
    parser.add_argument("--background", action="store_true", help="Start the gate detached and return immediately.")
    parser.add_argument("--status", action="store_true", help="Print concise gate status.")
    parser.add_argument("--handoff", action="store_true", help="Print compact AI handoff when the gate is complete.")
    parser.add_argument("--commit-handoff", action="store_true", help="Copy compact handoff into repo audit/inventory paths.")
    parser.add_argument("--git-commit", action="store_true", help="With --commit-handoff, commit the copied compact handoff paths.")
    parser.add_argument("--clean", action="store_true", help="Stop stale active run if needed and remove prior output.")
    parser.add_argument("--notify", action="store_true", help="Emit a terminal bell when a watched gate finishes.")
    parser.add_argument("--copy", action="store_true", help="Copy ai_handoff.md to clipboard where supported.")
    parser.add_argument("--open", action="store_true", help="Open ai_handoff.md with the OS default handler.")
    parser.add_argument("--github", action="store_true", help="Trigger the Full Discovery GitHub Actions workflow for pushed branch state.")
    parser.add_argument("--github-status", action="store_true", help="Show recent Full Discovery GitHub Actions runs.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable output for status/start/handoff.")
    parser.add_argument("--out", help="Explicit output directory; defaults to ../eureka-test-runs/<gate-run-id>.")
    parser.add_argument("--allow-repo-local-output", action="store_true")
    parser.add_argument("--start-dir", default="tests")
    parser.add_argument("--top-level-dir", default=".")
    parser.add_argument("--pattern", default="test*.py")
    parser.add_argument("--timeout-seconds", type=int, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument("--heartbeat-seconds", type=int, default=DEFAULT_HEARTBEAT_SECONDS)
    parser.add_argument("--interval-seconds", type=float, default=DEFAULT_WATCH_INTERVAL_SECONDS)
    args = parser.parse_args(argv)
    if not args.gate:
        parser.error("gate is required")
    if args.heartbeat_seconds < 1:
        parser.error("--heartbeat-seconds must be at least 1")
    if args.interval_seconds <= 0:
        parser.error("--interval-seconds must be greater than 0")

    try:
        gate = resolve_gate(args.gate)
        out_dir = resolve_output_dir(args=args, gate=gate)
    except ValueError as exc:
        parser.error(str(exc))

    if args.github:
        return trigger_github_workflow(gate=gate, stdout=stdout, stderr=stderr, json_output=args.json)
    if args.github_status:
        return show_github_status(stdout=stdout, stderr=stderr)
    if args.clean:
        try:
            clean_gate_output(out_dir=out_dir, stdout=stdout)
        except ValueError as exc:
            parser.error(str(exc))

    if args.background:
        return run_background(args=args, gate=gate, out_dir=out_dir, stdout=stdout, stderr=stderr)
    if args.watch:
        return run_watch(args=args, gate=gate, out_dir=out_dir, stdout=stdout, stderr=stderr)
    if args.commit_handoff:
        return run_commit_handoff(args=args, gate=gate, out_dir=out_dir, stdout=stdout, stderr=stderr)
    if args.handoff:
        return run_handoff(args=args, gate=gate, out_dir=out_dir, stdout=stdout, stderr=stderr)
    return run_status(args=args, gate=gate, out_dir=out_dir, stdout=stdout)


def resolve_gate(value: str) -> GateDefinition:
    key = GATE_ALIASES.get(value.strip())
    if not key:
        supported = ", ".join(sorted(GATES))
        raise ValueError(f"unknown gate {value!r}; supported gates: {supported}")
    return GATES[key]


def resolve_output_dir(*, args: argparse.Namespace, gate: GateDefinition) -> Path:
    return normalize_output_dir(
        Path(args.out) if args.out else output_dir_for_run_id(gate.run_id),
        args.allow_repo_local_output,
    )


def run_background(
    *,
    args: argparse.Namespace,
    gate: GateDefinition,
    out_dir: Path,
    stdout: TextIO,
    stderr: TextIO,
) -> int:
    namespace = argparse.Namespace(
        run_id=gate.run_id,
        out=str(out_dir),
        allow_repo_local_output=args.allow_repo_local_output,
        start_dir=args.start_dir,
        top_level_dir=args.top_level_dir,
        pattern=args.pattern,
        timeout_seconds=args.timeout_seconds,
        heartbeat_seconds=args.heartbeat_seconds,
        quiet=False,
        json=args.json,
    )
    try:
        metadata = start_discovery(args=namespace, out_dir=out_dir)
    except (RuntimeError, subprocess.CalledProcessError) as exc:
        print(f"eureka_gate: {exc}", file=stderr)
        return 2
    response = {
        "schema_version": GATE_START_SCHEMA_VERSION,
        "gate": gate.name,
        "run_id": gate.run_id,
        **metadata,
        "status_command": status_command(gate),
        "watch_command": watch_command(gate),
        "handoff_command": handoff_command(gate),
    }
    if args.json:
        print(json.dumps(response, indent=2, sort_keys=True), file=stdout)
    else:
        print(f"Eureka Gate: {gate.name}", file=stdout)
        print("", file=stdout)
        print("Started", file=stdout)
        print(f"PID: {metadata['pid']}", file=stdout)
        print(f"Output: {metadata['out_dir']}", file=stdout)
        print("", file=stdout)
        print("Next:", file=stdout)
        print(f"  {response['status_command']}", file=stdout)
        print(f"  {response['watch_command']}", file=stdout)
        print(f"  {response['handoff_command']}", file=stdout)
    return 0


def run_watch(
    *,
    args: argparse.Namespace,
    gate: GateDefinition,
    out_dir: Path,
    stdout: TextIO,
    stderr: TextIO,
) -> int:
    existing = read_json(discovery_artifact_paths(out_dir)["status_path"])
    if existing and is_terminal(existing):
        paths = write_ai_handoff_bundle(gate=gate, out_dir=out_dir, status_payload=existing)
        print_final_status(gate=gate, payload=existing, handoff_paths=paths, stdout=stdout)
        maybe_finish_actions(args=args, handoff_md=paths["md"], stdout=stdout, stderr=stderr)
        return status_exit_code(existing)

    if active_run_exists(out_dir):
        payload = watch_status(out_dir=out_dir, interval_seconds=args.interval_seconds, stdout=stdout, stderr=stderr)
    else:
        result = run_discovery(
            out_dir=out_dir,
            start_dir=args.start_dir,
            top_level_dir=args.top_level_dir,
            pattern=args.pattern,
            timeout_seconds=args.timeout_seconds,
            heartbeat_seconds=args.heartbeat_seconds,
            run_id=gate.run_id,
            allow_repo_local_output=args.allow_repo_local_output,
            progress_stream=stdout,
        )
        payload = load_status(out_dir)
        payload["exit_code"] = result["exit_code"]
    if is_terminal(payload):
        paths = write_ai_handoff_bundle(gate=gate, out_dir=out_dir, status_payload=payload)
        print_final_status(gate=gate, payload=payload, handoff_paths=paths, stdout=stdout)
        maybe_finish_actions(args=args, handoff_md=paths["md"], stdout=stdout, stderr=stderr)
    return status_exit_code(payload)


def run_status(*, args: argparse.Namespace, gate: GateDefinition, out_dir: Path, stdout: TextIO) -> int:
    try:
        payload = load_status(out_dir)
    except FileNotFoundError:
        payload = missing_status(gate=gate, out_dir=out_dir)
    response = gate_status_payload(gate=gate, out_dir=out_dir, payload=payload)
    if args.json:
        print(json.dumps(response, indent=2, sort_keys=True), file=stdout)
        return 0
    print_status_card(response=response, stdout=stdout)
    return 0


def run_handoff(
    *,
    args: argparse.Namespace,
    gate: GateDefinition,
    out_dir: Path,
    stdout: TextIO,
    stderr: TextIO,
) -> int:
    try:
        payload = load_status(out_dir)
    except FileNotFoundError:
        print_status_card(response=gate_status_payload(gate=gate, out_dir=out_dir, payload=missing_status(gate=gate, out_dir=out_dir)), stdout=stdout)
        return 2
    if not is_terminal(payload):
        print_status_card(response=gate_status_payload(gate=gate, out_dir=out_dir, payload=payload), stdout=stdout)
        return 1
    paths = write_ai_handoff_bundle(gate=gate, out_dir=out_dir, status_payload=payload)
    maybe_finish_actions(args=args, handoff_md=paths["md"], stdout=stdout, stderr=stderr)
    if args.json:
        print(paths["json"].read_text(encoding="utf-8").rstrip(), file=stdout)
    else:
        print(paths["md"].read_text(encoding="utf-8").rstrip(), file=stdout)
    return status_exit_code(payload)


def run_commit_handoff(
    *,
    args: argparse.Namespace,
    gate: GateDefinition,
    out_dir: Path,
    stdout: TextIO,
    stderr: TextIO,
) -> int:
    try:
        payload = load_status(out_dir)
    except FileNotFoundError:
        print(f"eureka_gate: no completed gate artifacts found under {out_dir}", file=stderr)
        return 2
    if not is_terminal(payload):
        print(f"eureka_gate: gate is not complete yet; status={payload.get('status')}", file=stderr)
        print(f"watch: {watch_command(gate)}", file=stderr)
        return 1
    handoff_paths = write_ai_handoff_bundle(gate=gate, out_dir=out_dir, status_payload=payload)
    try:
        changed = commit_handoff_bundle(
            gate=gate,
            out_dir=out_dir,
            handoff_paths=handoff_paths,
            repo_root=REPO_ROOT,
            git_commit=args.git_commit,
            stdout=stdout,
            stderr=stderr,
        )
    except RuntimeError as exc:
        print(f"eureka_gate: {exc}", file=stderr)
        return 2
    response = {
        "schema_version": "eureka_gate_commit_handoff.v0",
        "gate": gate.name,
        "status": "written",
        "git_commit_performed": args.git_commit,
        "paths": changed,
    }
    if args.json:
        print(json.dumps(response, indent=2, sort_keys=True), file=stdout)
    else:
        print("Compact handoff paths:", file=stdout)
        for path in changed:
            print(f"- {path}", file=stdout)
        if not args.git_commit:
            print("", file=stdout)
            print("No git commit was created. Add/commit these paths explicitly, or rerun with --git-commit.", file=stdout)
    return 0


def write_ai_handoff_bundle(*, gate: GateDefinition, out_dir: Path, status_payload: dict[str, Any]) -> dict[str, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    payload = build_ai_handoff(gate=gate, out_dir=out_dir, status_payload=status_payload)
    json_path = out_dir / "ai_handoff.json"
    md_path = out_dir / "ai_handoff.md"
    zip_path = out_dir / "ai_handoff.zip"
    json_path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(format_ai_handoff_markdown(payload) + "\n", encoding="utf-8")
    write_handoff_zip(zip_path=zip_path, json_path=json_path, md_path=md_path)
    return {"json": json_path, "md": md_path, "zip": zip_path}


def build_ai_handoff(*, gate: GateDefinition, out_dir: Path, status_payload: dict[str, Any]) -> dict[str, Any]:
    artifacts = discovery_artifact_paths(out_dir)
    summary_path = Path(str(status_payload.get("summary_path") or artifacts["summary_path"]))
    failure_families_path = Path(str(status_payload.get("failure_families_path") or artifacts["failure_families_path"]))
    failed_tests_path = Path(str(status_payload.get("failed_tests_path") or artifacts["failed_tests_path"]))
    status_path = Path(str(status_payload.get("status_path") or artifacts["status_path"]))
    summary = read_json(summary_path) or {}
    families_payload = read_json(failure_families_path) or {}
    failed_tests = read_lines(failed_tests_path)
    counts = summary.get("counts") or {}
    status = str(summary.get("status") or status_payload.get("status") or "unknown")
    exit_code = summary.get("exit_code", status_payload.get("exit_code"))
    git = normalized_git(summary.get("git") or {})
    failure_families_top = compact_failure_families(families_payload)
    safe_to_continue = (
        status == "pass"
        and exit_code == 0
        and counts.get("failures") == 0
        and counts.get("errors") == 0
        and git.get("working_tree_clean") is True
    )
    recommended_next = gate.recommended_next_task_pass if safe_to_continue else gate.recommended_next_task_fail
    paste_to_ai = paste_to_ai_text(
        gate=gate,
        status=status,
        tests_run=counts.get("tests_run"),
        failures=counts.get("failures"),
        errors=counts.get("errors"),
        exit_code=exit_code,
        safe_to_continue=safe_to_continue,
        recommended_next_task=recommended_next,
    )
    return {
        "schema_version": AI_HANDOFF_SCHEMA_VERSION,
        "gate": gate.name,
        "run_id": gate.run_id,
        "task": gate.task,
        "status": status,
        "git": git,
        "current_git_status_short": git_status_short(),
        "full_discovery": {
            "status": status,
            "tests_run": counts.get("tests_run"),
            "failures": counts.get("failures"),
            "errors": counts.get("errors"),
            "skipped": counts.get("skipped"),
            "exit_code": exit_code,
            "duration_seconds": summary.get("duration_seconds", status_payload.get("elapsed_seconds")),
        },
        "failure_families_top": failure_families_top,
        "failed_tests_count": len(failed_tests),
        "recommended_next_task": recommended_next,
        "safe_to_continue": safe_to_continue,
        "paste_to_ai": paste_to_ai,
        "artifact_paths": {
            "output_dir": str(out_dir),
            "status": str(status_path),
            "summary": str(summary_path),
            "failure_families": str(failure_families_path),
            "failed_tests": str(failed_tests_path),
            "ai_handoff_json": str(out_dir / "ai_handoff.json"),
            "ai_handoff_md": str(out_dir / "ai_handoff.md"),
            "ai_handoff_zip": str(out_dir / "ai_handoff.zip"),
        },
        "raw_logs_included": False,
        "raw_stdout_stderr_included": False,
    }


def normalized_git(git: dict[str, Any]) -> dict[str, Any]:
    return {
        "branch": git.get("branch") or git_value("branch", "--show-current"),
        "head": git.get("head") or git_value("rev-parse", "HEAD"),
        "working_tree_clean": git.get("working_tree_clean") if "working_tree_clean" in git else current_tree_clean(),
    }


def compact_failure_families(payload: dict[str, Any], limit: int = 5) -> list[dict[str, Any]]:
    families = payload.get("failure_families") or []
    compact: list[dict[str, Any]] = []
    for family in families[:limit]:
        compact.append(
            {
                "family_id": family.get("family_id"),
                "exception_type": family.get("exception_type"),
                "representative_test": family.get("representative_test"),
                "normalized_message": family.get("normalized_message"),
                "failed_test_count": len(family.get("failed_tests") or []),
            }
        )
    return compact


def paste_to_ai_text(
    *,
    gate: GateDefinition,
    status: str,
    tests_run: object,
    failures: object,
    errors: object,
    exit_code: object,
    safe_to_continue: bool,
    recommended_next_task: str,
) -> str:
    if safe_to_continue:
        return (
            f"{gate.name} external full discovery passed: tests_run={tests_run}, "
            f"failures={failures}, errors={errors}, exit_code={exit_code}. "
            f"Continue with {recommended_next_task}."
        )
    return (
        f"{gate.name} gate status is {status}: tests_run={tests_run}, "
        f"failures={failures}, errors={errors}, exit_code={exit_code}. "
        "Classify compact failure families before continuing."
    )


def format_ai_handoff_markdown(payload: dict[str, Any]) -> str:
    full = payload["full_discovery"]
    git = payload["git"]
    lines = [
        f"# AI Handoff - {payload['gate']}",
        "",
        f"STATUS: {str(payload['status']).upper()}",
        "",
        "SUMMARY:",
        f"- gate: {payload['gate']}",
        f"- task: {payload['task']}",
        f"- tests_run: {full.get('tests_run')}",
        f"- failures: {full.get('failures')}",
        f"- errors: {full.get('errors')}",
        f"- exit_code: {full.get('exit_code')}",
        f"- duration_seconds: {full.get('duration_seconds')}",
        f"- git_branch: {git.get('branch')}",
        f"- git_head: {git.get('head')}",
        f"- git_working_tree_clean: {git.get('working_tree_clean')}",
        f"- failed_tests_count: {payload['failed_tests_count']}",
        f"- safe_to_continue: {payload['safe_to_continue']}",
        "",
        "NEXT:",
        f"- {payload['recommended_next_task']}",
        "",
        "PASTE_TO_AI:",
        payload["paste_to_ai"],
        "",
        "FILES:",
        f"- ai_handoff.json: {payload['artifact_paths']['ai_handoff_json']}",
        f"- full_unittest_summary.json: {payload['artifact_paths']['summary']}",
        f"- failure_families.json: {payload['artifact_paths']['failure_families']}",
        f"- failed_tests.txt: {payload['artifact_paths']['failed_tests']}",
        "",
        "COMPACT_HANDOFF_JSON:",
        "```json",
        json.dumps(payload, indent=2, sort_keys=True),
        "```",
    ]
    return "\n".join(lines).rstrip()


def write_handoff_zip(*, zip_path: Path, json_path: Path, md_path: Path) -> None:
    with zipfile.ZipFile(zip_path, "w", compression=zipfile.ZIP_DEFLATED) as archive:
        archive.write(json_path, arcname="ai_handoff.json")
        archive.write(md_path, arcname="ai_handoff.md")


def commit_handoff_bundle(
    *,
    gate: GateDefinition,
    out_dir: Path,
    handoff_paths: dict[str, Path],
    repo_root: Path,
    git_commit: bool,
    stdout: TextIO,
    stderr: TextIO,
) -> list[str]:
    audit_dir = repo_root / gate.audit_dir
    audit_dir.mkdir(parents=True, exist_ok=True)
    target_json = audit_dir / "external_gate_result.json"
    target_md = audit_dir / "external_gate_handoff.md"
    shutil.copyfile(handoff_paths["json"], target_json)
    shutil.copyfile(handoff_paths["md"], target_md)
    changed_paths = [relative_repo_path(repo_root, target_json), relative_repo_path(repo_root, target_md)]
    if gate.inventory_result is not None:
        inventory_path = repo_root / gate.inventory_result
        inventory_path.parent.mkdir(parents=True, exist_ok=True)
        inventory_payload = build_inventory_full_discovery_result(
            gate=gate,
            out_dir=out_dir,
            handoff=json.loads(handoff_paths["json"].read_text(encoding="utf-8")),
            existing=read_json(inventory_path) or {},
        )
        inventory_path.write_text(json.dumps(inventory_payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        changed_paths.append(relative_repo_path(repo_root, inventory_path))
    if git_commit:
        commit_compact_paths(paths=changed_paths, repo_root=repo_root, stdout=stdout, stderr=stderr)
    return changed_paths


def build_inventory_full_discovery_result(
    *,
    gate: GateDefinition,
    out_dir: Path,
    handoff: dict[str, Any],
    existing: dict[str, Any],
) -> dict[str, Any]:
    full = handoff.get("full_discovery") or {}
    git = handoff.get("git") or {}
    payload = dict(existing)
    payload.update(
        {
            "schema_version": existing.get("schema_version") or f"{gate.run_id}_full_discovery_result.v0",
            "task": gate.task,
            "gate": gate.name,
            "status": handoff.get("status"),
            "external_summary_received": True,
            "full_unittest_discovery_passed": handoff.get("status") == "pass",
            "full_unittest_discovery_count": full.get("tests_run"),
            "full_discovery_failures_remaining": full.get("failures"),
            "full_discovery_errors_remaining": full.get("errors"),
            "full_discovery_exit_code": full.get("exit_code"),
            "full_discovery_git_working_tree_clean": git.get("working_tree_clean"),
            "summary_path": artifact_relpath(out_dir / "full_unittest_summary.json"),
            "failure_families_path": artifact_relpath(out_dir / "failure_families.json"),
            "failed_tests_path": artifact_relpath(out_dir / "failed_tests.txt"),
            "ai_handoff_json_path": artifact_relpath(out_dir / "ai_handoff.json"),
            "ai_handoff_md_path": artifact_relpath(out_dir / "ai_handoff.md"),
            "raw_logs_committed": False,
            "full_discovery_run_inside_ai": False,
            "safe_to_continue": handoff.get("safe_to_continue"),
            "recommended_next_task": handoff.get("recommended_next_task"),
        }
    )
    return payload


def commit_compact_paths(*, paths: list[str], repo_root: Path, stdout: TextIO, stderr: TextIO) -> None:
    subprocess.run(["git", "add", *paths], cwd=repo_root, text=True, check=True)
    completed = subprocess.run(
        ["git", "commit", "-m", "test(gate): record compact handoff"],
        cwd=repo_root,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.stdout.strip():
        print(completed.stdout.rstrip(), file=stdout)
    if completed.stderr.strip():
        print(completed.stderr.rstrip(), file=stderr)
    if completed.returncode != 0:
        raise RuntimeError(f"git commit failed with exit code {completed.returncode}")


def gate_status_payload(*, gate: GateDefinition, out_dir: Path, payload: dict[str, Any]) -> dict[str, Any]:
    artifacts = discovery_artifact_paths(out_dir)
    return {
        "schema_version": GATE_STATUS_SCHEMA_VERSION,
        "gate": gate.name,
        "run_id": gate.run_id,
        "status": payload.get("status") or "unknown",
        "pid": payload.get("pid"),
        "elapsed_seconds": payload.get("elapsed_seconds"),
        "stdout_bytes": payload.get("stdout_bytes"),
        "stderr_bytes": payload.get("stderr_bytes"),
        "exit_code": payload.get("exit_code"),
        "updated_at": payload.get("updated_at"),
        "out_dir": str(out_dir),
        "status_path": str(payload.get("status_path") or artifacts["status_path"]),
        "summary_path": str(payload.get("summary_path") or artifacts["summary_path"]),
        "failure_families_path": str(payload.get("failure_families_path") or artifacts["failure_families_path"]),
        "failed_tests_path": str(payload.get("failed_tests_path") or artifacts["failed_tests_path"]),
        "ai_handoff_json_path": str(out_dir / "ai_handoff.json"),
        "ai_handoff_md_path": str(out_dir / "ai_handoff.md"),
        "ai_handoff_zip_path": str(out_dir / "ai_handoff.zip"),
        "tests_run": payload.get("tests_run"),
        "failures": payload.get("failures"),
        "errors": payload.get("errors"),
        "status_command": status_command(gate),
        "watch_command": watch_command(gate),
        "handoff_command": handoff_command(gate),
    }


def print_status_card(*, response: dict[str, Any], stdout: TextIO) -> None:
    print(f"Eureka Gate: {response['gate']}", file=stdout)
    print("", file=stdout)
    print(f"Status: {str(response['status']).upper()}", file=stdout)
    print(f"PID: {response.get('pid')}", file=stdout)
    print(f"Elapsed: {format_duration(float(response.get('elapsed_seconds') or 0))}", file=stdout)
    print(f"Output: {response['out_dir']}", file=stdout)
    print(f"Stdout: {format_optional_size(response.get('stdout_bytes'))}", file=stdout)
    print(f"Stderr: {format_optional_size(response.get('stderr_bytes'))}", file=stdout)
    print(f"Last update: {response.get('updated_at')}", file=stdout)
    if response.get("tests_run") is not None:
        print("", file=stdout)
        print(f"Tests: {response.get('tests_run')}", file=stdout)
        print(f"Failures: {response.get('failures')}", file=stdout)
        print(f"Errors: {response.get('errors')}", file=stdout)
        print(f"Exit code: {response.get('exit_code')}", file=stdout)
    print("", file=stdout)
    print("Handoff:", file=stdout)
    print(f"  {response['ai_handoff_md_path']}", file=stdout)
    print("", file=stdout)
    print("Next:", file=stdout)
    if response["status"] in TERMINAL_STATUSES:
        print(f"  {response['handoff_command']}", file=stdout)
    else:
        print(f"  {response['status_command']}", file=stdout)
        print(f"  {response['watch_command']}", file=stdout)


def print_final_status(*, gate: GateDefinition, payload: dict[str, Any], handoff_paths: dict[str, Path], stdout: TextIO) -> None:
    handoff = json.loads(handoff_paths["json"].read_text(encoding="utf-8"))
    full = handoff.get("full_discovery") or {}
    print(f"[eureka-gate] status={handoff.get('status')}", file=stdout)
    print(
        "[eureka-gate] "
        f"tests={full.get('tests_run')} failures={full.get('failures')} errors={full.get('errors')} "
        f"duration={full.get('duration_seconds')}",
        file=stdout,
    )
    print(f"[eureka-gate] ai_handoff_json={handoff_paths['json']}", file=stdout)
    print(f"[eureka-gate] ai_handoff_md={handoff_paths['md']}", file=stdout)
    print(f"[eureka-gate] ai_handoff_zip={handoff_paths['zip']}", file=stdout)


def missing_status(*, gate: GateDefinition, out_dir: Path) -> dict[str, Any]:
    artifacts = discovery_artifact_paths(out_dir)
    return {
        "status": "missing",
        "run_id": gate.run_id,
        "pid": None,
        "elapsed_seconds": None,
        "stdout_bytes": None,
        "stderr_bytes": None,
        "exit_code": None,
        "summary_path": str(artifacts["summary_path"]),
        "failure_families_path": str(artifacts["failure_families_path"]),
        "failed_tests_path": str(artifacts["failed_tests_path"]),
        "status_path": str(artifacts["status_path"]),
    }


def active_run_exists(out_dir: Path) -> bool:
    status = read_json(discovery_artifact_paths(out_dir)["status_path"])
    if not status or status.get("status") not in {"starting", "running"}:
        return False
    return pid_is_running(status.get("pid"))


def clean_gate_output(*, out_dir: Path, stdout: TextIO) -> None:
    stop_active_run(out_dir=out_dir, stdout=stdout)
    if out_dir.exists():
        assert_safe_clean_dir(out_dir)
        shutil.rmtree(out_dir)
        print(f"[eureka-gate] cleaned={out_dir}", file=stdout)


def stop_active_run(*, out_dir: Path, stdout: TextIO) -> None:
    status = read_json(discovery_artifact_paths(out_dir)["status_path"])
    if not status or status.get("status") not in {"starting", "running"}:
        return
    pid = status.get("pid")
    if not pid_is_running(pid):
        return
    terminate_pid(int(pid))
    print(f"[eureka-gate] stopped stale run pid={pid}", file=stdout)


def maybe_finish_actions(*, args: argparse.Namespace, handoff_md: Path, stdout: TextIO, stderr: TextIO) -> None:
    if args.notify:
        print("\a", end="", file=stdout, flush=True)
    if args.copy:
        copy_to_clipboard(handoff_md, stdout=stdout, stderr=stderr)
    if args.open:
        open_path(handoff_md, stderr=stderr)


def trigger_github_workflow(*, gate: GateDefinition, stdout: TextIO, stderr: TextIO, json_output: bool) -> int:
    if shutil.which("gh") is None:
        print("eureka_gate: gh CLI is not available", file=stderr)
        return 2
    completed = subprocess.run(
        ["gh", "workflow", "run", "Full Discovery", "--ref", "dev"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    payload = {
        "schema_version": "eureka_gate_github_dispatch.v0",
        "gate": gate.name,
        "command": "gh workflow run \"Full Discovery\" --ref dev",
        "exit_code": completed.returncode,
        "stdout": completed.stdout.strip(),
        "stderr": completed.stderr.strip(),
    }
    if json_output:
        print(json.dumps(payload, indent=2, sort_keys=True), file=stdout)
    else:
        print(payload["command"], file=stdout)
        if completed.stdout.strip():
            print(completed.stdout.strip(), file=stdout)
        if completed.stderr.strip():
            print(completed.stderr.strip(), file=stderr)
    return completed.returncode


def show_github_status(*, stdout: TextIO, stderr: TextIO) -> int:
    if shutil.which("gh") is None:
        print("eureka_gate: gh CLI is not available", file=stderr)
        return 2
    completed = subprocess.run(
        ["gh", "run", "list", "--workflow", "Full Discovery", "--limit", "5"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.stdout.strip():
        print(completed.stdout.rstrip(), file=stdout)
    if completed.stderr.strip():
        print(completed.stderr.rstrip(), file=stderr)
    return completed.returncode


def status_command(gate: GateDefinition) -> str:
    return f"python scripts/eureka_gate.py {gate.name} --status"


def watch_command(gate: GateDefinition) -> str:
    return f"python scripts/eureka_gate.py {gate.name} --watch"


def handoff_command(gate: GateDefinition) -> str:
    return f"python scripts/eureka_gate.py {gate.name} --handoff"


def artifact_relpath(path: Path) -> str:
    resolved = path.resolve()
    try:
        return resolved.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        try:
            return "../" + resolved.relative_to(REPO_ROOT.parent).as_posix()
        except ValueError:
            return str(path)


def relative_repo_path(repo_root: Path, path: Path) -> str:
    return path.resolve().relative_to(repo_root.resolve()).as_posix()


def read_lines(path: Path) -> list[str]:
    try:
        return [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    except FileNotFoundError:
        return []


def git_value(*args: str) -> str | None:
    completed = subprocess.run(["git", *args], cwd=REPO_ROOT, text=True, capture_output=True, check=False)
    if completed.returncode != 0:
        return None
    return completed.stdout.strip()


def current_tree_clean() -> bool:
    completed = subprocess.run(["git", "status", "--short"], cwd=REPO_ROOT, text=True, capture_output=True, check=False)
    return completed.returncode == 0 and completed.stdout.strip() == ""


def format_optional_size(value: object) -> str:
    try:
        size = int(value)  # type: ignore[arg-type]
    except (TypeError, ValueError):
        return "unknown"
    units = ("B", "KiB", "MiB", "GiB")
    display = float(size)
    for unit in units:
        if display < 1024 or unit == units[-1]:
            if unit == "B":
                return f"{int(display)} {unit}"
            return f"{display:.1f} {unit}"
        display /= 1024
    return f"{size} B"


if __name__ == "__main__":
    raise SystemExit(main())
