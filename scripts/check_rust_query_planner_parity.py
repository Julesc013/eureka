from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any, Mapping, Sequence


REPO_ROOT = Path(__file__).resolve().parents[1]
CASE_FILE = REPO_ROOT / "tests" / "parity" / "rust_query_planner_cases.json"
GOLDEN_ROOT = REPO_ROOT / "tests" / "parity" / "golden" / "python_oracle" / "v0" / "query_planner"
RUST_QUERY_PLANNER = REPO_ROOT / "crates" / "eureka-core" / "src" / "query_planner.rs"
RUST_LIB = REPO_ROOT / "crates" / "eureka-core" / "src" / "lib.rs"
CARGO_MANIFEST = REPO_ROOT / "crates" / "Cargo.toml"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check the isolated Rust query-planner parity candidate."
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit a machine-readable summary.",
    )
    parser.add_argument(
        "--require-cargo",
        action="store_true",
        help="Fail if Cargo is unavailable instead of treating Rust execution as skipped.",
    )
    args = parser.parse_args(argv)

    structure = _validate_structure()
    cargo = _run_optional_cargo(require_cargo=args.require_cargo)

    status = "passed"
    if structure["status"] != "passed" or cargo["status"] == "failed":
        status = "failed"
    elif cargo["status"] == "skipped":
        status = "skipped_cargo_unavailable"

    summary: dict[str, Any] = {
        "status": status,
        "check_id": "rust_query_planner_parity_candidate_v0",
        "structure": structure,
        "cargo": cargo,
        "python_remains_oracle": True,
        "runtime_wiring_allowed": False,
    }
    _emit(summary, emit_json=args.json, stderr=status == "failed")
    return 0 if status != "failed" else 1


def _validate_structure() -> dict[str, Any]:
    errors: list[str] = []
    for path in [CASE_FILE, GOLDEN_ROOT, RUST_QUERY_PLANNER, RUST_LIB, CARGO_MANIFEST]:
        if not path.exists():
            errors.append(f"missing: {_rel(path)}")

    cases: list[Mapping[str, Any]] = []
    if CASE_FILE.exists():
        try:
            payload = json.loads(CASE_FILE.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            errors.append(f"{_rel(CASE_FILE)}: invalid JSON: {error}")
            payload = {}
        raw_cases = payload.get("cases") if isinstance(payload, Mapping) else None
        if not isinstance(raw_cases, list) or not raw_cases:
            errors.append(f"{_rel(CASE_FILE)}: cases must be a non-empty list")
        else:
            cases = [case for case in raw_cases if isinstance(case, Mapping)]
            if len(cases) != len(raw_cases):
                errors.append(f"{_rel(CASE_FILE)}: every case must be an object")

    for case in cases:
        case_id = str(case.get("case_id", ""))
        oracle_file = str(case.get("python_oracle_file", ""))
        required_task_kind = str(case.get("required_task_kind", ""))
        query = str(case.get("query", ""))
        if not case_id or not oracle_file or not required_task_kind or not query:
            errors.append(f"{_rel(CASE_FILE)}: malformed case {case!r}")
            continue
        oracle_path = GOLDEN_ROOT / oracle_file
        if not oracle_path.is_file():
            errors.append(f"missing oracle for {case_id}: {_rel(oracle_path)}")
            continue
        try:
            oracle = json.loads(oracle_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as error:
            errors.append(f"{_rel(oracle_path)}: invalid JSON: {error}")
            continue
        observed_task_kind = (
            oracle.get("body", {})
            .get("query_plan", {})
            .get("task_kind")
            if isinstance(oracle, Mapping)
            else None
        )
        if observed_task_kind != required_task_kind:
            errors.append(
                f"{case_id}: expected task_kind {required_task_kind!r}, got {observed_task_kind!r}"
            )

    if RUST_QUERY_PLANNER.exists():
        rust_text = RUST_QUERY_PLANNER.read_text(encoding="utf-8")
        for required in [
            "pub struct ResolutionTask",
            "pub fn plan_query",
            "pub fn query_plan_response",
            "query_planner_candidate_matches_python_oracle_goldens",
        ]:
            if required not in rust_text:
                errors.append(f"{_rel(RUST_QUERY_PLANNER)} missing {required!r}")
    if RUST_LIB.exists():
        lib_text = RUST_LIB.read_text(encoding="utf-8")
        if "pub mod query_planner;" not in lib_text:
            errors.append(f"{_rel(RUST_LIB)} does not export query_planner")

    return {
        "status": "failed" if errors else "passed",
        "case_count": len(cases),
        "errors": errors,
    }


def _run_optional_cargo(*, require_cargo: bool) -> dict[str, Any]:
    cargo_path = shutil.which("cargo")
    if cargo_path is None:
        return {
            "status": "failed" if require_cargo else "skipped",
            "cargo_available": False,
            "reason": "Cargo is not available in PATH.",
        }

    command = [
        cargo_path,
        "test",
        "--manifest-path",
        str(CARGO_MANIFEST),
        "-p",
        "eureka-core",
        "query_planner",
    ]
    result = subprocess.run(
        command,
        cwd=REPO_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    return {
        "status": "passed" if result.returncode == 0 else "failed",
        "cargo_available": True,
        "command": " ".join(command),
        "returncode": result.returncode,
        "stdout": result.stdout[-4000:],
        "stderr": result.stderr[-4000:],
    }


def _emit(summary: Mapping[str, Any], *, emit_json: bool, stderr: bool) -> None:
    output = sys.stderr if stderr else sys.stdout
    if emit_json:
        output.write(json.dumps(summary, indent=2, sort_keys=True) + "\n")
        return
    output.write("Rust query planner parity candidate check\n")
    output.write(f"status: {summary['status']}\n")
    structure = summary["structure"]
    cargo = summary["cargo"]
    output.write(f"case_count: {structure['case_count']}\n")
    output.write(f"structure: {structure['status']}\n")
    output.write(f"cargo: {cargo['status']}\n")
    if structure.get("errors"):
        output.write("errors:\n")
        for error in structure["errors"]:
            output.write(f"- {error}\n")
    if cargo.get("reason"):
        output.write(f"cargo_reason: {cargo['reason']}\n")


def _rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path)


if __name__ == "__main__":
    raise SystemExit(main())
