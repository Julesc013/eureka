#!/usr/bin/env python3
"""One-command external test gate runner with status and AI handoff."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
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
    print_status,
    status_exit_code,
    watch_status,
)
from tools.testing.run_full_unittest_discovery import (  # noqa: E402
    DEFAULT_HEARTBEAT_SECONDS,
    DEFAULT_TIMEOUT_SECONDS,
    discovery_artifact_paths,
    normalize_output_dir,
    output_dir_for_run_id,
    run_discovery,
)
from tools.testing.start_full_discovery import (  # noqa: E402
    pid_is_running,
    read_json,
    start_discovery,
)


TERMINAL_GATE_STATUSES = {"pass", "fail", "error", "cancelled", "timeout"}


@dataclass(frozen=True)
class GateDefinition:
    gate: str
    run_id: str
    description: str
    next_on_pass: tuple[str, ...]
    next_on_fail: tuple[str, ...]


GATES: dict[str, GateDefinition] = {
    "public_alpha_readonly_closeout": GateDefinition(
        gate="public_alpha_readonly_closeout",
        run_id="public_alpha_readonly_closeout",
        description="External full discovery for PUBLIC-ALPHA-READONLY-CLOSEOUT-01.",
        next_on_pass=(
            "Finish PUBLIC-ALPHA-READONLY-CLOSEOUT-01.",
            "Proceed to DEV-TO-MAIN-PROMOTION-REVIEW-04.",
        ),
        next_on_fail=(
            "Classify compact failure families.",
            "Repair only in-scope failures and rerun focused tests before another external gate.",
        ),
    ),
    "source_snapshot_closeout": GateDefinition(
        gate="source_snapshot_closeout",
        run_id="source_snapshot_closeout",
        description="External full discovery for source snapshot closeout.",
        next_on_pass=(
            "Finish source snapshot baseline closeout.",
            "Proceed to the matching dev-to-main promotion review.",
        ),
        next_on_fail=(
            "Classify compact failure families.",
            "Repair only the closeout failure families.",
        ),
    ),
    "promotion_gate": GateDefinition(
        gate="promotion_gate",
        run_id="promotion_gate",
        description="External full discovery for promotion gate validation.",
        next_on_pass=(
            "Use the passing full discovery as promotion evidence.",
            "Proceed only if branch and boundary validators also pass.",
        ),
        next_on_fail=(
            "Do not promote.",
            "Classify compact failure families and repair before retry.",
        ),
    ),
}


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--gate", required=True, choices=sorted(GATES), help="Named external test gate.")
    parser.add_argument("--watch", action="store_true", help="Run or watch the gate until terminal status.")
    parser.add_argument("--background", action="store_true", help="Start the gate detached and return immediately.")
    parser.add_argument("--status", action="store_true", help="Print compact gate status.")
    parser.add_argument("--handoff", action="store_true", help="Print ai_handoff.md if complete.")
    parser.add_argument("--clean", action="store_true", help="Stop active run if needed and remove prior gate output.")
    parser.add_argument("--notify", action="store_true", help="Emit a terminal bell when the gate reaches terminal status.")
    parser.add_argument("--copy-handoff", action="store_true", help="Copy ai_handoff.md to clipboard when available.")
    parser.add_argument("--open-handoff", action="store_true", help="Open ai_handoff.md with the OS default handler when available.")
    parser.add_argument("--github", action="store_true", help="Trigger the Full Discovery GitHub Actions workflow for pushed branch state.")
    parser.add_argument("--github-status", action="store_true", help="Show recent Full Discovery GitHub Actions runs.")
    parser.add_argument("--json", action="store_true", help="Print machine-readable output for status/start operations.")
    parser.add_argument("--out", help="Explicit output directory; defaults to ../eureka-test-runs/<gate>.")
    parser.add_argument("--allow-repo-local-output", action="store_true")
    parser.add_argument("--start-dir", default="tests")
    parser.add_argument("--top-level-dir", default=".")
    parser.add_argument("--pattern", default="test*.py")
    parser.add_argument("--timeout-seconds", type=int, default=DEFAULT_TIMEOUT_SECONDS)
    parser.add_argument("--heartbeat-seconds", type=int, default=DEFAULT_HEARTBEAT_SECONDS)
    parser.add_argument("--interval-seconds", type=float, default=DEFAULT_WATCH_INTERVAL_SECONDS)
    args = parser.parse_args(argv)
    if args.heartbeat_seconds < 1:
        parser.error("--heartbeat-seconds must be at least 1")
    if args.interval_seconds <= 0:
        parser.error("--interval-seconds must be greater than 0")

    gate = GATES[args.gate]
    try:
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
    if args.handoff:
        return run_handoff(args=args, gate=gate, out_dir=out_dir, stdout=stdout, stderr=stderr)
    return run_status(args=args, gate=gate, out_dir=out_dir, stdout=stdout, stderr=stderr)


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
    except RuntimeError as exc:
        print(f"eureka_test_gate: {exc}", file=stderr)
        return 2
    response = {
        "schema_version": "test_gate_start.v0",
        "gate": gate.gate,
        "run_id": gate.run_id,
        **metadata,
        "status_command": status_command(gate),
        "watch_command": watch_command(gate),
        "handoff_command": handoff_command(gate),
    }
    if args.json:
        print(json.dumps(response, indent=2, sort_keys=True), file=stdout)
    else:
        print(f"Started gate {gate.gate}", file=stdout)
        print(f"PID: {metadata['pid']}", file=stdout)
        print(f"Output: {metadata['out_dir']}", file=stdout)
        print("Status:", file=stdout)
        print(f"  {response['status_command']}", file=stdout)
        print("Watch:", file=stdout)
        print(f"  {response['watch_command']}", file=stdout)
        print("Handoff:", file=stdout)
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
        handoff = write_ai_handoff(gate=gate, out_dir=out_dir, payload=existing)
        print_final_gate_status(gate=gate, payload=existing, handoff_path=handoff, stdout=stdout)
        maybe_notify(args=args, handoff_path=handoff, stdout=stdout, stderr=stderr)
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
        handoff = write_ai_handoff(gate=gate, out_dir=out_dir, payload=payload)
        print_final_gate_status(gate=gate, payload=payload, handoff_path=handoff, stdout=stdout)
        maybe_notify(args=args, handoff_path=handoff, stdout=stdout, stderr=stderr)
    return status_exit_code(payload)


def run_status(
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
        payload = missing_status(gate=gate, out_dir=out_dir)
    response = gate_status_payload(gate=gate, out_dir=out_dir, payload=payload)
    if args.json:
        print(json.dumps(response, indent=2, sort_keys=True), file=stdout)
    else:
        print(f"gate: {gate.gate}", file=stdout)
        if response["status"] == "missing":
            print("status: missing", file=stdout)
            print(f"start: python scripts/eureka_test_gate.py --gate {gate.gate} --watch --clean", file=stdout)
        else:
            print_status(payload, stdout=stdout)
            print(f"ai_handoff: {response['ai_handoff_path']}", file=stdout)
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
        print(f"gate: {gate.gate}", file=stdout)
        print("status: missing", file=stdout)
        print(f"watch: {watch_command(gate)}", file=stdout)
        return 2
    if not is_terminal(payload):
        print(f"gate: {gate.gate}", file=stdout)
        print_status(payload, stdout=stdout)
        print(f"watch: {watch_command(gate)}", file=stdout)
        return 1
    handoff = write_ai_handoff(gate=gate, out_dir=out_dir, payload=payload)
    maybe_notify(args=args, handoff_path=handoff, stdout=stdout, stderr=stderr)
    if args.json:
        response = handoff_payload(gate=gate, out_dir=out_dir, payload=payload, handoff_path=handoff)
        print(json.dumps(response, indent=2, sort_keys=True), file=stdout)
    else:
        print(handoff.read_text(encoding="utf-8").rstrip(), file=stdout)
    return status_exit_code(payload)


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


def gate_status_payload(*, gate: GateDefinition, out_dir: Path, payload: dict[str, Any]) -> dict[str, Any]:
    artifacts = discovery_artifact_paths(out_dir)
    return {
        "schema_version": "test_gate_status.v0",
        "gate": gate.gate,
        "run_id": gate.run_id,
        "status": payload.get("status") or "unknown",
        "pid": payload.get("pid"),
        "elapsed_seconds": payload.get("elapsed_seconds"),
        "stdout_bytes": payload.get("stdout_bytes"),
        "stderr_bytes": payload.get("stderr_bytes"),
        "exit_code": payload.get("exit_code"),
        "out_dir": str(out_dir),
        "status_path": str(payload.get("status_path") or artifacts["status_path"]),
        "summary_path": str(payload.get("summary_path") or artifacts["summary_path"]),
        "failure_families_path": str(payload.get("failure_families_path") or artifacts["failure_families_path"]),
        "failed_tests_path": str(payload.get("failed_tests_path") or artifacts["failed_tests_path"]),
        "ai_handoff_path": str(ai_handoff_path(out_dir)),
    }


def write_ai_handoff(*, gate: GateDefinition, out_dir: Path, payload: dict[str, Any]) -> Path:
    summary = read_json(Path(str(payload.get("summary_path") or discovery_artifact_paths(out_dir)["summary_path"]))) or {}
    counts = summary.get("counts") or {}
    status = str(summary.get("status") or payload.get("status") or "unknown")
    next_items = gate.next_on_pass if status == "pass" else gate.next_on_fail
    families_path = Path(str(payload.get("failure_families_path") or discovery_artifact_paths(out_dir)["failure_families_path"]))
    failed_tests_path = Path(str(payload.get("failed_tests_path") or discovery_artifact_paths(out_dir)["failed_tests_path"]))
    summary_path = Path(str(payload.get("summary_path") or discovery_artifact_paths(out_dir)["summary_path"]))
    git_status = git_status_short()

    lines = [
        f"# AI Handoff - {gate.gate}",
        "",
        f"STATUS: {status.upper()}",
        "",
        "SUMMARY:",
        f"- Full discovery status: {status}",
        f"- tests_run: {counts.get('tests_run')}",
        f"- failures: {counts.get('failures')}",
        f"- errors: {counts.get('errors')}",
        f"- exit_code: {summary.get('exit_code', payload.get('exit_code'))}",
        f"- git status: {git_status}",
        "",
        "NEXT:",
        *[f"- {item}" for item in next_items],
        "",
        "FILES:",
        f"- full_unittest_summary.json: {summary_path}",
        f"- failure_families.json: {families_path}",
        f"- failed_tests.txt: {failed_tests_path}",
        "",
        "COMPACT_SUMMARY_JSON:",
        "```json",
        json.dumps(summary, indent=2, sort_keys=True),
        "```",
    ]
    if status != "pass":
        lines.extend(
            [
                "",
                "FAILURE_FAMILIES_JSON:",
                "```json",
                read_text(families_path),
                "```",
                "",
                "FAILED_TESTS:",
                "```text",
                read_text(failed_tests_path),
                "```",
            ]
        )
    path = ai_handoff_path(out_dir)
    path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return path


def handoff_payload(*, gate: GateDefinition, out_dir: Path, payload: dict[str, Any], handoff_path: Path) -> dict[str, Any]:
    summary = read_json(Path(str(payload.get("summary_path") or ""))) or {}
    counts = summary.get("counts") or {}
    status = str(summary.get("status") or payload.get("status") or "unknown")
    return {
        "schema_version": "test_gate_handoff.v0",
        "gate": gate.gate,
        "run_id": gate.run_id,
        "status": status,
        "tests_run": counts.get("tests_run"),
        "failures": counts.get("failures"),
        "errors": counts.get("errors"),
        "exit_code": summary.get("exit_code", payload.get("exit_code")),
        "ai_handoff_path": str(handoff_path),
        "summary_path": str(payload.get("summary_path") or discovery_artifact_paths(out_dir)["summary_path"]),
        "failure_families_path": str(payload.get("failure_families_path") or discovery_artifact_paths(out_dir)["failure_families_path"]),
        "failed_tests_path": str(payload.get("failed_tests_path") or discovery_artifact_paths(out_dir)["failed_tests_path"]),
        "git_status_short": git_status_short(),
        "next": list(gate.next_on_pass if status == "pass" else gate.next_on_fail),
    }


def print_final_gate_status(*, gate: GateDefinition, payload: dict[str, Any], handoff_path: Path, stdout: TextIO) -> None:
    summary = read_json(Path(str(payload.get("summary_path") or ""))) or {}
    counts = summary.get("counts") or {}
    print(f"[eureka-test-gate] status={summary.get('status', payload.get('status'))}", file=stdout)
    print(
        "[eureka-test-gate] "
        f"tests={counts.get('tests_run')} failures={counts.get('failures')} errors={counts.get('errors')} "
        f"duration={summary.get('duration_seconds')}",
        file=stdout,
    )
    print(f"[eureka-test-gate] handoff={handoff_path}", file=stdout)


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
        print(f"[eureka-test-gate] cleaned={out_dir}", file=stdout)


def stop_active_run(*, out_dir: Path, stdout: TextIO) -> None:
    status = read_json(discovery_artifact_paths(out_dir)["status_path"])
    if not status or status.get("status") not in {"starting", "running"}:
        return
    pid = status.get("pid")
    if not pid_is_running(pid):
        return
    terminate_pid(int(pid))
    print(f"[eureka-test-gate] stopped stale run pid={pid}", file=stdout)


def terminate_pid(pid: int) -> None:
    if os.name == "nt":
        subprocess.run(["taskkill", "/PID", str(pid), "/T", "/F"], text=True, capture_output=True, check=False)
        return
    try:
        os.kill(pid, 15)
    except OSError:
        return


def assert_safe_clean_dir(out_dir: Path) -> None:
    resolved = out_dir.resolve()
    repo = REPO_ROOT.resolve()
    if resolved == repo or repo in resolved.parents:
        raise ValueError(f"refusing to clean repo-local output directory: {resolved}")
    if resolved.name in {"", ".", ".."}:
        raise ValueError(f"refusing to clean unsafe output directory: {resolved}")
    if not (
        resolved.parent.name == "eureka-test-runs"
        or (resolved / "status.json").exists()
        or (resolved / "full_unittest_summary.json").exists()
    ):
        raise ValueError(f"refusing to clean unrecognized output directory: {resolved}")


def maybe_notify(*, args: argparse.Namespace, handoff_path: Path, stdout: TextIO, stderr: TextIO) -> None:
    if args.notify:
        print("\a", end="", file=stdout, flush=True)
    if args.copy_handoff:
        copy_to_clipboard(handoff_path, stdout=stdout, stderr=stderr)
    if args.open_handoff:
        open_path(handoff_path, stderr=stderr)


def copy_to_clipboard(path: Path, *, stdout: TextIO, stderr: TextIO) -> None:
    text = path.read_text(encoding="utf-8")
    if os.name == "nt":
        completed = subprocess.run(["clip"], input=text, text=True, capture_output=True, check=False)
    elif sys.platform == "darwin":
        completed = subprocess.run(["pbcopy"], input=text, text=True, capture_output=True, check=False)
    else:
        completed = subprocess.run(["xclip", "-selection", "clipboard"], input=text, text=True, capture_output=True, check=False)
    if completed.returncode == 0:
        print(f"[eureka-test-gate] copied_handoff={path}", file=stdout)
    else:
        print(f"[eureka-test-gate] copy_handoff_failed={completed.stderr.strip()}", file=stderr)


def open_path(path: Path, *, stderr: TextIO) -> None:
    try:
        if os.name == "nt":
            os.startfile(str(path))  # type: ignore[attr-defined]
        elif sys.platform == "darwin":
            subprocess.Popen(["open", str(path)])
        else:
            subprocess.Popen(["xdg-open", str(path)])
    except OSError as exc:
        print(f"[eureka-test-gate] open_handoff_failed={exc}", file=stderr)


def trigger_github_workflow(*, gate: GateDefinition, stdout: TextIO, stderr: TextIO, json_output: bool) -> int:
    if shutil.which("gh") is None:
        print("eureka_test_gate: gh CLI is not available", file=stderr)
        return 2
    completed = subprocess.run(
        ["gh", "workflow", "run", "Full Discovery", "--ref", "dev"],
        cwd=REPO_ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    payload = {
        "schema_version": "test_gate_github_dispatch.v0",
        "gate": gate.gate,
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
        print("eureka_test_gate: gh CLI is not available", file=stderr)
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
    return f"python scripts/eureka_test_gate.py --gate {gate.gate} --status"


def watch_command(gate: GateDefinition) -> str:
    return f"python scripts/eureka_test_gate.py --gate {gate.gate} --watch"


def handoff_command(gate: GateDefinition) -> str:
    return f"python scripts/eureka_test_gate.py --gate {gate.gate} --handoff"


def ai_handoff_path(out_dir: Path) -> Path:
    return out_dir / "ai_handoff.md"


def read_json(path: Path) -> dict[str, Any] | None:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        return None


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8").rstrip()
    except OSError:
        return f"<missing: {path}>"


if __name__ == "__main__":
    raise SystemExit(main())
