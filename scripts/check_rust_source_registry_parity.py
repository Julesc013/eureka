from __future__ import annotations

import argparse
import json
from pathlib import Path
import shutil
import subprocess
import sys
from typing import Any, Mapping, Sequence


REPO_ROOT = Path(__file__).resolve().parents[1]
CASE_FILE = REPO_ROOT / "tests" / "parity" / "rust_source_registry_cases.json"
GOLDEN_ROOT = REPO_ROOT / "tests" / "parity" / "golden" / "python_oracle" / "v0" / "source_registry"
SOURCE_INVENTORY = REPO_ROOT / "control" / "inventory" / "sources"
RUST_SOURCE_REGISTRY = REPO_ROOT / "crates" / "eureka-core" / "src" / "source_registry.rs"
RUST_LIB = REPO_ROOT / "crates" / "eureka-core" / "src" / "lib.rs"
CARGO_MANIFEST = REPO_ROOT / "crates" / "Cargo.toml"


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Check the isolated Rust source-registry parity catch-up candidate."
    )
    parser.add_argument("--json", action="store_true", help="Emit a machine-readable summary.")
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
        "check_id": "rust_source_registry_parity_catch_up_v0",
        "structure": structure,
        "cargo": cargo,
        "python_remains_oracle": True,
        "runtime_wiring_allowed": False,
    }
    _emit(summary, emit_json=args.json, stderr=status == "failed")
    return 0 if status != "failed" else 1


def _validate_structure() -> dict[str, Any]:
    errors: list[str] = []
    for path in [CASE_FILE, GOLDEN_ROOT, SOURCE_INVENTORY, RUST_SOURCE_REGISTRY, RUST_LIB, CARGO_MANIFEST]:
        if not path.exists():
            errors.append(f"missing: {_rel(path)}")

    fixture = _load_json(CASE_FILE, errors)
    cases = _cases_from_fixture(fixture, errors)
    source_paths = sorted(SOURCE_INVENTORY.glob("*.source.json"))
    expected_count = fixture.get("expected_source_count") if isinstance(fixture, Mapping) else None
    if expected_count is not None and len(source_paths) != expected_count:
        errors.append(
            f"{_rel(SOURCE_INVENTORY)}: expected {expected_count} source records, found {len(source_paths)}"
        )

    required_capabilities = _string_list(fixture.get("required_capability_fields"), "required_capability_fields", errors)
    required_coverage = _string_list(fixture.get("required_coverage_fields"), "required_coverage_fields", errors)
    for source_path in source_paths:
        source = _load_json(source_path, errors)
        if not isinstance(source, Mapping):
            continue
        source_id = source.get("source_id")
        if not isinstance(source_id, str) or not source_id:
            errors.append(f"{_rel(source_path)}: source_id must be a non-empty string")
        capabilities = source.get("capabilities")
        if not isinstance(capabilities, Mapping):
            errors.append(f"{_rel(source_path)}: capabilities must be an object")
        else:
            for field in required_capabilities:
                if field not in capabilities:
                    errors.append(f"{_rel(source_path)}: missing capabilities.{field}")
                elif not isinstance(capabilities[field], bool):
                    errors.append(f"{_rel(source_path)}: capabilities.{field} must be boolean")
        coverage = source.get("coverage")
        if not isinstance(coverage, Mapping):
            errors.append(f"{_rel(source_path)}: coverage must be an object")
        else:
            for field in required_coverage:
                if field not in coverage:
                    errors.append(f"{_rel(source_path)}: missing coverage.{field}")

    for case in cases:
        case_id = str(case.get("case_id", ""))
        oracle_file = str(case.get("python_oracle_file", ""))
        if not case_id or not oracle_file:
            errors.append(f"{_rel(CASE_FILE)}: malformed case {case!r}")
            continue
        oracle_path = GOLDEN_ROOT / oracle_file
        oracle = _load_json(oracle_path, errors)
        if not isinstance(oracle, Mapping):
            continue
        if oracle.get("status_code") != case.get("expected_status_code", 200):
            errors.append(f"{case_id}: unexpected status_code in {_rel(oracle_path)}")
        body = oracle.get("body")
        if not isinstance(body, Mapping):
            errors.append(f"{_rel(oracle_path)}: body must be an object")
            continue
        expected_source_count = case.get("expected_source_count")
        if expected_source_count is not None and body.get("source_count") != expected_source_count:
            errors.append(f"{case_id}: expected source_count {expected_source_count}")
        source_id = case.get("source_id")
        sources = body.get("sources")
        if source_id is not None:
            if body.get("selected_source_id") != source_id:
                errors.append(f"{case_id}: selected_source_id must be {source_id!r}")
            if not isinstance(sources, list) or len(sources) != 1 or not isinstance(sources[0], Mapping):
                errors.append(f"{case_id}: expected one source object")
                continue
            source = sources[0]
            if source.get("status") != case.get("expected_status"):
                errors.append(f"{case_id}: status mismatch")
            if source.get("coverage_depth") != case.get("expected_coverage_depth"):
                errors.append(f"{case_id}: coverage_depth mismatch")
            if source.get("connector_mode") != case.get("expected_connector_mode"):
                errors.append(f"{case_id}: connector_mode mismatch")
            for field in required_capabilities:
                if field not in _mapping(source.get("capabilities")):
                    errors.append(f"{case_id}: oracle source missing capabilities.{field}")
            for field in required_coverage:
                if field not in _mapping(source.get("coverage")):
                    errors.append(f"{case_id}: oracle source missing coverage.{field}")

    if RUST_SOURCE_REGISTRY.exists():
        rust_text = RUST_SOURCE_REGISTRY.read_text(encoding="utf-8")
        for required in [
            "pub struct SourceCapabilityRecord",
            "pub struct SourceCoverageRecord",
            "SOURCE_CAPABILITY_FIELDS",
            "COVERAGE_DEPTHS",
            "pub fn source_record_public_entry",
            "pub fn placeholder_warning",
            "current_source_outputs_match_python_oracle_goldens",
        ]:
            if required not in rust_text:
                errors.append(f"{_rel(RUST_SOURCE_REGISTRY)} missing {required!r}")
        for source_id in [
            "article-scan-recorded-fixtures",
            "internet-archive-placeholder",
            "local-files-placeholder",
            "manual-document-recorded-fixtures",
            "package-registry-recorded-fixtures",
            "review-description-recorded-fixtures",
            "software-heritage-recorded-fixtures",
            "sourceforge-recorded-fixtures",
            "wayback-memento-recorded-fixtures",
        ]:
            if source_id not in rust_text:
                errors.append(f"{_rel(RUST_SOURCE_REGISTRY)} missing source case {source_id!r}")
    if RUST_LIB.exists():
        lib_text = RUST_LIB.read_text(encoding="utf-8")
        if "pub mod source_registry;" not in lib_text:
            errors.append(f"{_rel(RUST_LIB)} does not export source_registry")

    return {
        "status": "failed" if errors else "passed",
        "case_count": len(cases),
        "source_count": len(source_paths),
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
        "source_registry",
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


def _load_json(path: Path, errors: list[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"missing: {_rel(path)}")
    except json.JSONDecodeError as error:
        errors.append(f"{_rel(path)}: invalid JSON: {error}")
    return {}


def _cases_from_fixture(fixture: Any, errors: list[str]) -> list[Mapping[str, Any]]:
    raw_cases = fixture.get("cases") if isinstance(fixture, Mapping) else None
    if not isinstance(raw_cases, list) or not raw_cases:
        errors.append(f"{_rel(CASE_FILE)}: cases must be a non-empty list")
        return []
    cases = [case for case in raw_cases if isinstance(case, Mapping)]
    if len(cases) != len(raw_cases):
        errors.append(f"{_rel(CASE_FILE)}: every case must be an object")
    return cases


def _string_list(value: Any, field_name: str, errors: list[str]) -> list[str]:
    if not isinstance(value, list) or not value or not all(isinstance(item, str) and item for item in value):
        errors.append(f"{_rel(CASE_FILE)}: {field_name} must be a non-empty list of strings")
        return []
    return list(value)


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _emit(summary: Mapping[str, Any], *, emit_json: bool, stderr: bool) -> None:
    output = sys.stderr if stderr else sys.stdout
    if emit_json:
        output.write(json.dumps(summary, indent=2, sort_keys=True) + "\n")
        return
    output.write("Rust source registry parity catch-up check\n")
    output.write(f"status: {summary['status']}\n")
    structure = summary["structure"]
    cargo = summary["cargo"]
    output.write(f"source_count: {structure['source_count']}\n")
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
