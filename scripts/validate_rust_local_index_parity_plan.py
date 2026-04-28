from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence


REPO_ROOT = Path(__file__).resolve().parents[1]
PLAN = REPO_ROOT / "tests" / "parity" / "RUST_LOCAL_INDEX_PARITY_PLAN.md"
CASE_FILE = REPO_ROOT / "tests" / "parity" / "rust_local_index_cases.json"
ACCEPTANCE_SCHEMA = REPO_ROOT / "tests" / "parity" / "local_index_acceptance.schema.json"
ALLOWED_DIVERGENCES = REPO_ROOT / "tests" / "parity" / "ALLOWED_DIVERGENCES.md"
GOLDEN_ROOT = REPO_ROOT / "tests" / "parity" / "golden" / "python_oracle" / "v0"
CRATES_ROOT = REPO_ROOT / "crates"

REQUIRED_QUERY_CASES = {
    "synthetic",
    "archive",
    "windows 7",
    "firefox xp",
    "registry repair",
    "blue ftp",
    "thinkpad",
    "driver.inf",
    "ray tracing",
    "pc magazine",
    "creative ct1740",
    "3c905",
    "internet-archive-recorded-fixtures",
    "no-such-local-index-hit",
}
REQUIRED_RECORD_KINDS = {
    "source_record",
    "resolved_object",
    "state_or_release",
    "representation",
    "member",
    "synthetic_member",
    "evidence",
}
REQUIRED_ACCEPTANCE_FIELDS = {
    "parity_id",
    "oracle_version",
    "rust_candidate_version",
    "cargo_status",
    "build_status",
    "query_cases",
    "normalized_outputs",
    "divergences",
    "accepted_divergences",
    "failed_cases",
    "notes",
}


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate Rust Local Index parity planning artifacts."
    )
    parser.add_argument("--json", action="store_true", help="Emit a machine-readable summary.")
    args = parser.parse_args(argv)

    summary = _validate()
    _emit(summary, emit_json=args.json)
    return 0 if summary["status"] == "passed" else 1


def _validate() -> dict[str, Any]:
    errors: list[str] = []
    for path in [PLAN, CASE_FILE, ACCEPTANCE_SCHEMA, ALLOWED_DIVERGENCES]:
        if not path.exists():
            errors.append(f"missing: {_rel(path)}")

    fixture = _load_json(CASE_FILE, errors)
    schema = _load_json(ACCEPTANCE_SCHEMA, errors)
    plan_text = _read_text(PLAN, errors)
    divergences_text = _read_text(ALLOWED_DIVERGENCES, errors)

    _validate_fixture(fixture, errors)
    _validate_acceptance_schema(schema, errors)
    _validate_docs(plan_text, divergences_text, errors)
    _validate_no_implementation_or_wiring(errors)

    query_cases = _query_cases(fixture)
    current_cases = [
        case for case in query_cases if case.get("golden_status") == "current"
    ]
    planned_cases = [
        case
        for case in query_cases
        if case.get("golden_status") == "planned_future_oracle_extension"
    ]

    return {
        "status": "failed" if errors else "passed",
        "check_id": "rust_local_index_parity_planning_v0",
        "plan": _rel(PLAN),
        "case_file": _rel(CASE_FILE),
        "acceptance_schema": _rel(ACCEPTANCE_SCHEMA),
        "case_count": len(query_cases),
        "current_oracle_query_cases": len(current_cases),
        "planned_future_query_cases": len(planned_cases),
        "record_kind_count": len(_string_set(fixture.get("required_record_kinds"))),
        "python_remains_oracle": bool(fixture.get("python_remains_oracle")),
        "rust_local_index_implemented": bool(fixture.get("rust_local_index_implemented")),
        "runtime_wiring_allowed": bool(fixture.get("runtime_wiring_allowed")),
        "errors": errors,
    }


def _validate_fixture(fixture: Any, errors: list[str]) -> None:
    if not isinstance(fixture, Mapping):
        errors.append(f"{_rel(CASE_FILE)}: root must be an object")
        return
    expected_scalars = {
        "status": "planning_only",
        "python_remains_oracle": True,
        "rust_local_index_implemented": False,
        "runtime_wiring_allowed": False,
    }
    for field, expected in expected_scalars.items():
        if fixture.get(field) != expected:
            errors.append(f"{_rel(CASE_FILE)}: {field} must be {expected!r}")

    record_kinds = _string_set(fixture.get("required_record_kinds"))
    missing_record_kinds = sorted(REQUIRED_RECORD_KINDS - record_kinds)
    if missing_record_kinds:
        errors.append(f"{_rel(CASE_FILE)}: missing record kinds {missing_record_kinds}")

    query_cases = _query_cases(fixture)
    if not query_cases:
        errors.append(f"{_rel(CASE_FILE)}: query_cases must be a non-empty list")
    query_strings = {str(case.get("query", "")) for case in query_cases}
    missing_queries = sorted(REQUIRED_QUERY_CASES - query_strings)
    if missing_queries:
        errors.append(f"{_rel(CASE_FILE)}: missing query cases {missing_queries}")

    build_case = fixture.get("build_status_case")
    if not isinstance(build_case, Mapping):
        errors.append(f"{_rel(CASE_FILE)}: build_status_case must be an object")
    else:
        _validate_build_case(build_case, errors)

    for case in query_cases:
        _validate_query_case(case, errors)

    allowed_refs = _string_set(fixture.get("allowed_divergence_refs"))
    if "tests/parity/ALLOWED_DIVERGENCES.md#future-rust-local-index-divergences" not in allowed_refs:
        errors.append(f"{_rel(CASE_FILE)}: local-index allowed divergence reference missing")


def _validate_build_case(build_case: Mapping[str, Any], errors: list[str]) -> None:
    golden_file = build_case.get("golden_file")
    if not isinstance(golden_file, str) or not golden_file:
        errors.append(f"{_rel(CASE_FILE)}: build_status_case.golden_file must be a string")
        return
    golden = _load_json(GOLDEN_ROOT / golden_file, errors)
    if not isinstance(golden, Mapping):
        return
    index = _mapping(_mapping(golden.get("body")).get("index"))
    expected_record_count = build_case.get("expected_record_count")
    if index.get("record_count") != expected_record_count:
        errors.append(f"{golden_file}: record_count does not match case map")
    expected_kinds = build_case.get("expected_record_kind_counts")
    if index.get("record_kind_counts") != expected_kinds:
        errors.append(f"{golden_file}: record_kind_counts do not match case map")


def _validate_query_case(case: Mapping[str, Any], errors: list[str]) -> None:
    case_id = str(case.get("case_id", ""))
    query = str(case.get("query", ""))
    golden_status = case.get("golden_status")
    golden_file = case.get("golden_file")
    if not case_id or not query:
        errors.append(f"{_rel(CASE_FILE)}: malformed query case {case!r}")
        return
    if golden_status == "current":
        if not isinstance(golden_file, str) or not golden_file:
            errors.append(f"{case_id}: current case must reference a golden_file")
            return
        golden = _load_json(GOLDEN_ROOT / golden_file, errors)
        if not isinstance(golden, Mapping):
            return
        body = _mapping(golden.get("body"))
        if golden.get("status_code") != case.get("expected_status_code", 200):
            errors.append(f"{case_id}: status_code mismatch in {golden_file}")
        if body.get("status") != case.get("expected_query_status"):
            errors.append(f"{case_id}: query status mismatch in {golden_file}")
        if body.get("query") != query:
            errors.append(f"{case_id}: query value mismatch in {golden_file}")
        if not isinstance(body.get("results"), list):
            errors.append(f"{case_id}: current golden must expose results list")
    elif golden_status == "planned_future_oracle_extension":
        if golden_file is not None:
            errors.append(f"{case_id}: planned future case must not reference a golden_file yet")
    else:
        errors.append(f"{case_id}: unknown golden_status {golden_status!r}")


def _validate_acceptance_schema(schema: Any, errors: list[str]) -> None:
    if not isinstance(schema, Mapping):
        errors.append(f"{_rel(ACCEPTANCE_SCHEMA)}: root must be an object")
        return
    required = _string_set(schema.get("required_top_level_fields"))
    missing = sorted(REQUIRED_ACCEPTANCE_FIELDS - required)
    if missing:
        errors.append(f"{_rel(ACCEPTANCE_SCHEMA)}: missing required fields {missing}")
    if schema.get("status") != "planning_schema":
        errors.append(f"{_rel(ACCEPTANCE_SCHEMA)}: status must be planning_schema")


def _validate_docs(plan_text: str, divergences_text: str, errors: list[str]) -> None:
    plan_lower = plan_text.lower()
    required_plan_phrases = [
        "python remains the oracle",
        "planning only",
        "rust local index parity implementation is not started",
        "rust remains unwired",
        "no runtime wiring",
    ]
    for phrase in required_plan_phrases:
        if phrase not in plan_lower:
            errors.append(f"{_rel(PLAN)} missing phrase {phrase!r}")

    divergences_lower = divergences_text.lower()
    for phrase in [
        "future rust local index divergences",
        "fts5 availability differences",
        "missing record kinds",
        "missing synthetic members",
        "private path leakage",
        "source placeholder overclaiming",
        "no accepted divergences",
    ]:
        if phrase not in divergences_lower:
            errors.append(f"{_rel(ALLOWED_DIVERGENCES)} missing phrase {phrase!r}")


def _validate_no_implementation_or_wiring(errors: list[str]) -> None:
    implementation_paths = [
        CRATES_ROOT / "eureka-core" / "src" / "local_index.rs",
        CRATES_ROOT / "eureka-index",
    ]
    existing = [_rel(path) for path in implementation_paths if path.exists()]
    if existing:
        errors.append(f"Rust local-index implementation paths must not exist yet: {existing}")

    forbidden = re.compile(
        r"rust_local_index|local_index_parity_candidate|rust_index_candidate|rust_index",
        re.IGNORECASE,
    )
    violations: list[str] = []
    for root in [REPO_ROOT / "runtime", REPO_ROOT / "surfaces"]:
        if not root.exists():
            continue
        for path in root.rglob("*.py"):
            text = path.read_text(encoding="utf-8")
            if forbidden.search(text):
                violations.append(_rel(path))
    if violations:
        errors.append(f"runtime/surfaces must not call Rust local index: {violations}")


def _load_json(path: Path, errors: list[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"missing: {_rel(path)}")
    except json.JSONDecodeError as error:
        errors.append(f"{_rel(path)}: invalid JSON: {error}")
    return {}


def _read_text(path: Path, errors: list[str]) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        errors.append(f"missing: {_rel(path)}")
    return ""


def _query_cases(fixture: Any) -> list[Mapping[str, Any]]:
    raw_cases = fixture.get("query_cases") if isinstance(fixture, Mapping) else None
    if not isinstance(raw_cases, list):
        return []
    return [case for case in raw_cases if isinstance(case, Mapping)]


def _string_set(value: Any) -> set[str]:
    if not isinstance(value, list):
        return set()
    return {item for item in value if isinstance(item, str) and item}


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _emit(summary: Mapping[str, Any], *, emit_json: bool) -> None:
    output = sys.stderr if summary["status"] == "failed" else sys.stdout
    if emit_json:
        output.write(json.dumps(summary, indent=2, sort_keys=True) + "\n")
        return
    output.write("Rust local index parity planning validation\n")
    output.write(f"status: {summary['status']}\n")
    output.write(f"case_count: {summary['case_count']}\n")
    output.write(f"current_oracle_query_cases: {summary['current_oracle_query_cases']}\n")
    output.write(f"planned_future_query_cases: {summary['planned_future_query_cases']}\n")
    output.write(f"record_kind_count: {summary['record_kind_count']}\n")
    if summary.get("errors"):
        output.write("errors:\n")
        for error in summary["errors"]:
            output.write(f"- {error}\n")


def _rel(path: Path) -> str:
    try:
        return str(path.relative_to(REPO_ROOT)).replace("\\", "/")
    except ValueError:
        return str(path).replace("\\", "/")


if __name__ == "__main__":
    raise SystemExit(main())
