from __future__ import annotations

import argparse
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_REGISTRY = REPO_ROOT / "control" / "inventory" / "packs" / "example_packs.json"
SCHEMA_VERSION = "pack_set_validation.v0"
VALIDATOR_ID = "pack_import_validator_aggregator_v0"

PACK_TYPE_CONFIGS: dict[str, dict[str, str]] = {
    "source_pack": {
        "manifest": "SOURCE_PACK.json",
        "validator": "scripts/validate_source_pack.py",
        "root_arg": "--pack-root",
    },
    "evidence_pack": {
        "manifest": "EVIDENCE_PACK.json",
        "validator": "scripts/validate_evidence_pack.py",
        "root_arg": "--pack-root",
    },
    "index_pack": {
        "manifest": "INDEX_PACK.json",
        "validator": "scripts/validate_index_pack.py",
        "root_arg": "--pack-root",
    },
    "contribution_pack": {
        "manifest": "CONTRIBUTION_PACK.json",
        "validator": "scripts/validate_contribution_pack.py",
        "root_arg": "--pack-root",
    },
    "master_index_review_queue": {
        "manifest": "REVIEW_QUEUE_MANIFEST.json",
        "validator": "scripts/validate_master_index_review_queue.py",
        "root_arg": "--queue-root",
    },
}
PACK_TYPE_CHOICES = sorted(PACK_TYPE_CONFIGS) + ["auto"]
SIDE_EFFECT_FLAGS = {
    "mutation_performed": False,
    "import_performed": False,
    "staging_performed": False,
    "indexing_performed": False,
    "network_performed": False,
}
EXCERPT_MAX_CHARS = 1200


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate known Eureka pack examples or one explicit pack root without importing anything."
    )
    parser.add_argument("--json", action="store_true", help="Emit structured JSON.")
    parser.add_argument("--strict", action="store_true", help="Pass strict mode through to individual validators.")
    parser.add_argument("--all-examples", action="store_true", help="Validate all known repo example packs.")
    parser.add_argument("--pack-root", help="Validate one explicit pack or review-queue root.")
    parser.add_argument(
        "--pack-type",
        default="auto",
        choices=PACK_TYPE_CHOICES,
        help="Pack type for --pack-root; defaults to manifest auto-detection.",
    )
    parser.add_argument("--list-examples", action="store_true", help="List known example packs without validation.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    output = stdout or sys.stdout
    if args.pack_root and args.all_examples:
        report = _base_report("argument_error", strict=args.strict)
        report["ok"] = False
        report["errors"] = ["--pack-root cannot be combined with --all-examples."]
        _write_report(report, json_output=args.json, output=output)
        return 2
    if args.pack_type != "auto" and not args.pack_root:
        report = _base_report("argument_error", strict=args.strict)
        report["ok"] = False
        report["errors"] = ["--pack-type is only valid with --pack-root."]
        _write_report(report, json_output=args.json, output=output)
        return 2

    registry_errors: list[str] = []
    examples = load_example_registry(errors=registry_errors)
    if args.list_examples:
        report = _list_examples_report(examples, registry_errors, strict=args.strict)
        _write_report(report, json_output=args.json, output=output)
        return 0 if report["ok"] else 1

    if args.pack_root:
        root = _resolve_pack_root(args.pack_root)
        result = validate_pack_root(root, args.pack_type, strict=args.strict)
        report = _validation_report("single_pack", [result], strict=args.strict, errors=registry_errors)
    else:
        results = [
            validate_pack_root(REPO_ROOT / example["path"], example["pack_type"], strict=args.strict)
            for example in examples
        ]
        report = _validation_report("all_examples", results, strict=args.strict, errors=registry_errors)

    _write_report(report, json_output=args.json, output=output)
    return 0 if report["ok"] else 1


def load_example_registry(*, errors: list[str] | None = None) -> list[dict[str, str]]:
    error_sink = errors if errors is not None else []
    if not EXAMPLE_REGISTRY.exists():
        error_sink.append(f"{_rel(EXAMPLE_REGISTRY)}: example pack registry is missing.")
        return []
    try:
        payload = json.loads(EXAMPLE_REGISTRY.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        error_sink.append(f"{_rel(EXAMPLE_REGISTRY)}: invalid JSON: {exc}.")
        return []
    examples = payload.get("examples")
    if not isinstance(examples, list):
        error_sink.append(f"{_rel(EXAMPLE_REGISTRY)}: examples must be a list.")
        return []
    normalized: list[dict[str, str]] = []
    for index, item in enumerate(examples):
        if not isinstance(item, Mapping):
            error_sink.append(f"{_rel(EXAMPLE_REGISTRY)}: examples[{index}] must be an object.")
            continue
        normalized_item: dict[str, str] = {}
        for field in ["pack_id", "pack_type", "path", "status", "owning_contract", "validator"]:
            value = item.get(field)
            if not isinstance(value, str) or not value:
                error_sink.append(f"{_rel(EXAMPLE_REGISTRY)}: examples[{index}].{field} must be a string.")
                value = ""
            normalized_item[field] = value
        if normalized_item["pack_type"] not in PACK_TYPE_CONFIGS:
            error_sink.append(
                f"{_rel(EXAMPLE_REGISTRY)}: examples[{index}].pack_type is unknown: "
                f"{normalized_item['pack_type']}."
            )
        normalized.append(normalized_item)
    return normalized


def validate_pack_root(
    pack_root: Path,
    pack_type: str,
    *,
    strict: bool = False,
    configs: Mapping[str, Mapping[str, str]] | None = None,
) -> dict[str, Any]:
    config_map = configs or PACK_TYPE_CONFIGS
    root = pack_root.resolve()
    detected_type = detect_pack_type(root, configs=config_map)
    requested_type = detected_type if pack_type == "auto" else pack_type

    if requested_type is None:
        return _pack_result(root, None, "unknown_type", None, None, None, "No known pack manifest found.")
    if requested_type not in config_map:
        return _pack_result(root, requested_type, "unknown_type", None, None, None, "Unsupported pack type.")
    if detected_type is not None and pack_type != "auto" and detected_type != requested_type:
        return _pack_result(
            root,
            requested_type,
            "unknown_type",
            None,
            None,
            None,
            f"Requested pack_type={requested_type}, but detected {detected_type}.",
        )

    config = config_map[requested_type]
    validator_path = REPO_ROOT / config["validator"]
    root_arg = config["root_arg"]
    command = [sys.executable, str(validator_path), root_arg, str(root)]
    if strict:
        command.append("--strict")

    if not validator_path.exists():
        return _pack_result(
            root,
            requested_type,
            "unavailable",
            command,
            None,
            None,
            f"Validator is missing: {_rel(validator_path)}.",
        )
    if not root.exists() or not root.is_dir():
        return _pack_result(
            root,
            requested_type,
            "failed",
            command,
            None,
            None,
            "Pack root is missing or is not a directory.",
        )

    completed = subprocess.run(command, cwd=REPO_ROOT, capture_output=True, text=True)
    status = "passed" if completed.returncode == 0 else "failed"
    return _pack_result(
        root,
        requested_type,
        status,
        command,
        completed.returncode,
        completed.stdout,
        completed.stderr,
    )


def detect_pack_type(
    pack_root: Path, *, configs: Mapping[str, Mapping[str, str]] | None = None
) -> str | None:
    config_map = configs or PACK_TYPE_CONFIGS
    root = pack_root.resolve()
    for pack_type, config in config_map.items():
        if (root / config["manifest"]).exists():
            return pack_type
    return None


def _pack_result(
    root: Path,
    pack_type: str | None,
    status: str,
    command: Sequence[str] | None,
    exit_code: int | None,
    stdout: str | None,
    stderr: str | None,
) -> dict[str, Any]:
    return {
        "pack_root": _rel_or_abs(root),
        "pack_type": pack_type or "unknown",
        "validator_command": _format_command(command) if command else None,
        "status": status,
        "exit_code": exit_code,
        "stdout_excerpt": _excerpt(stdout),
        "stderr_excerpt": _excerpt(stderr),
    }


def _validation_report(
    mode: str, results: list[dict[str, Any]], *, strict: bool, errors: list[str]
) -> dict[str, Any]:
    summary = _summarize(results)
    report = _base_report(mode, strict=strict)
    report.update(
        {
            "ok": not errors and summary["failed"] == 0 and summary["unavailable"] == 0 and summary["unknown_type"] == 0,
            "pack_results": results,
            "summary": summary,
            "errors": errors,
            "notes": [
                "Aggregate validation delegates to existing validators.",
                "Validation success is not import, staging, indexing, rights clearance, malware safety, canonical truth, or master-index acceptance.",
            ],
        }
    )
    return report


def _list_examples_report(examples: list[dict[str, str]], errors: list[str], *, strict: bool) -> dict[str, Any]:
    report = _base_report("list_examples", strict=strict)
    report.update(
        {
            "ok": not errors,
            "examples": examples,
            "summary": {
                "total": len(examples),
                "passed": 0,
                "failed": 0,
                "unavailable": 0,
                "unknown_type": 0,
            },
            "errors": errors,
            "notes": ["Listing examples does not validate, import, stage, index, upload, or contact a network."],
        }
    )
    return report


def _summarize(results: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    summary = {"total": len(results), "passed": 0, "failed": 0, "unavailable": 0, "unknown_type": 0}
    for result in results:
        status = result.get("status")
        if status in summary and status != "total":
            summary[status] += 1
    return summary


def _base_report(mode: str, *, strict: bool) -> dict[str, Any]:
    report: dict[str, Any] = {
        "ok": False,
        "schema_version": SCHEMA_VERSION,
        "validator_id": VALIDATOR_ID,
        "mode": mode,
        "strict": strict,
        "pack_results": [],
        "summary": {"total": 0, "passed": 0, "failed": 0, "unavailable": 0, "unknown_type": 0},
        "errors": [],
    }
    report.update(SIDE_EFFECT_FLAGS)
    return report


def _write_report(report: Mapping[str, Any], *, json_output: bool, output: TextIO) -> None:
    if json_output:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))


def _format_plain(report: Mapping[str, Any]) -> str:
    if report.get("mode") == "list_examples":
        lines = [
            "Pack Set Examples",
            f"status: {'valid' if report.get('ok') else 'invalid'}",
            f"total: {report.get('summary', {}).get('total', 0)}",
        ]
        for example in report.get("examples", []):
            lines.append(f"- {example['pack_type']}: {example['path']} ({example['pack_id']})")
    else:
        summary = report.get("summary", {})
        lines = [
            "Pack Set Validation",
            f"status: {'passed' if report.get('ok') else 'failed'}",
            f"mode: {report.get('mode')}",
            f"strict: {report.get('strict')}",
            "summary: "
            f"total={summary.get('total', 0)} "
            f"passed={summary.get('passed', 0)} "
            f"failed={summary.get('failed', 0)} "
            f"unavailable={summary.get('unavailable', 0)} "
            f"unknown_type={summary.get('unknown_type', 0)}",
        ]
        for result in report.get("pack_results", []):
            lines.append(
                f"- {result['pack_type']}: {result['pack_root']} -> {result['status']}"
                + (f" (exit {result['exit_code']})" if result.get("exit_code") is not None else "")
            )
    for key in SIDE_EFFECT_FLAGS:
        lines.append(f"{key}: {report.get(key)}")
    for error in report.get("errors", []):
        lines.append(f"error: {error}")
    return "\n".join(lines) + "\n"


def _resolve_pack_root(path_value: str) -> Path:
    path = Path(path_value)
    if path.is_absolute():
        return path
    return REPO_ROOT / path


def _excerpt(value: str | None) -> str:
    if not value:
        return ""
    normalized = value.strip()
    if len(normalized) <= EXCERPT_MAX_CHARS:
        return normalized
    return normalized[:EXCERPT_MAX_CHARS] + "...[truncated]"


def _format_command(command: Sequence[str]) -> str:
    return " ".join(_display_command_part(part) for part in command)


def _display_command_part(part: str) -> str:
    if part == sys.executable:
        return "python"
    path = Path(part)
    if path.is_absolute():
        return _rel_or_abs(path)
    return part


def _rel_or_abs(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.resolve().as_posix()


def _rel(path: Path) -> str:
    return _rel_or_abs(path)


if __name__ == "__main__":
    raise SystemExit(main())
