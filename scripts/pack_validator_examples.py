from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Callable, Mapping, Sequence


REPO_ROOT = Path(__file__).resolve().parents[1]
EXAMPLE_REGISTRY = REPO_ROOT / "control" / "inventory" / "packs" / "example_packs.json"


def load_examples_for_type(pack_type: str, errors: list[str]) -> list[dict[str, str]]:
    if not EXAMPLE_REGISTRY.exists():
        errors.append(f"{_rel(EXAMPLE_REGISTRY)}: example pack registry is missing.")
        return []
    try:
        payload = json.loads(EXAMPLE_REGISTRY.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"{_rel(EXAMPLE_REGISTRY)}: invalid JSON: {exc.msg}.")
        return []
    examples = payload.get("examples")
    if not isinstance(examples, list):
        errors.append(f"{_rel(EXAMPLE_REGISTRY)}: examples must be a list.")
        return []

    matched: list[dict[str, str]] = []
    for index, item in enumerate(examples):
        if not isinstance(item, Mapping):
            errors.append(f"{_rel(EXAMPLE_REGISTRY)}: examples[{index}] must be an object.")
            continue
        if item.get("pack_type") != pack_type:
            continue
        normalized: dict[str, str] = {}
        for field in ("pack_id", "pack_type", "path", "status", "validator"):
            value = item.get(field)
            if not isinstance(value, str) or not value:
                errors.append(f"{_rel(EXAMPLE_REGISTRY)}: examples[{index}].{field} must be a non-empty string.")
                value = ""
            normalized[field] = value
        if normalized["path"]:
            matched.append(normalized)
    if not matched and not errors:
        errors.append(f"{_rel(EXAMPLE_REGISTRY)}: no examples registered for {pack_type}.")
    return matched


def validate_all_examples(
    *,
    pack_type: str,
    created_by: str,
    root_field: str,
    strict: bool,
    validate_one: Callable[[Path], Mapping[str, Any]],
) -> dict[str, Any]:
    errors: list[str] = []
    examples = load_examples_for_type(pack_type, errors)
    results: list[dict[str, Any]] = []
    for example in examples:
        root = REPO_ROOT / example["path"]
        report = dict(validate_one(root))
        results.append(
            {
                "pack_id": example["pack_id"],
                "pack_type": pack_type,
                root_field: example["path"],
                "status": report.get("status", "invalid"),
                "errors": list(report.get("errors", [])),
                "warnings": list(report.get("warnings", [])),
            }
        )

    failed = sum(1 for result in results if result["status"] != "valid")
    return {
        "status": "valid" if not errors and failed == 0 else "invalid",
        "created_by": created_by,
        "mode": "all_examples",
        "pack_type": pack_type,
        "strict": strict,
        "example_count": len(results),
        "passed": len(results) - failed,
        "failed": failed,
        "results": results,
        "errors": errors,
        "warnings": [],
        "notes": [
            "All-examples validation reads the governed example pack registry only.",
            "Validation does not import, stage, index, upload, mutate runtime state, or accept master-index records.",
        ],
    }


def argument_error(created_by: str, message: str) -> dict[str, Any]:
    return {
        "status": "invalid",
        "created_by": created_by,
        "mode": "argument_error",
        "errors": [message],
        "warnings": [],
    }


def format_all_examples(report: Mapping[str, Any], *, title: str, root_field: str) -> str:
    if report.get("mode") == "argument_error":
        lines = [title, "status: invalid"]
        lines.extend(f"error: {error}" for error in report.get("errors", []))
        return "\n".join(lines) + "\n"
    lines = [
        title,
        f"status: {report['status']}",
        f"mode: {report.get('mode')}",
        f"example_count: {report.get('example_count', 0)}",
        f"passed: {report.get('passed', 0)}",
        f"failed: {report.get('failed', 0)}",
    ]
    for result in report.get("results", []):
        lines.append(f"- {result.get(root_field)} -> {result.get('status')}")
        for error in result.get("errors", []):
            lines.append(f"  error: {error}")
    for error in report.get("errors", []):
        lines.append(f"error: {error}")
    for note in report.get("notes", []):
        lines.append(f"note: {note}")
    return "\n".join(lines) + "\n"


def _rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return str(path)
