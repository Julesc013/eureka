#!/usr/bin/env python3
"""Update active schema references for the R0-03B-2 contract cleanup."""

from __future__ import annotations

import argparse
import json
import shutil
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
TASK_ID = "R0-03B-2"
DEFAULT_MIGRATION_RESULT = Path("control/inventory/r0_03b_1_migration_result.json")
DEFAULT_REFERENCE_GRAPH = Path("control/inventory/contract_reference_graph.json")
DEFAULT_MIGRATION_PLAN = Path("control/inventory/contract_migration_plan.json")
DEFAULT_SHIM_REPORT = Path("control/inventory/r0_03b_1_compatibility_shim_report.json")
AUDIT_DIR = Path("control/audits/r0-03b-2-contract-reference-product-cleanup-v0")
REFERENCE_RESULT_PATH = Path("control/inventory/r0_03b_2_reference_update_result.json")

B2_MOVE_CLASSES = {
    "control_schema",
    "task_queue_schema",
    "validator_schema",
    "generated_scaffold_schema",
    "deprecated_schema",
}
CONTROL_SCHEMA_TARGETS = (
    "control/schemas/policies/",
    "control/schemas/tasks/",
    "control/schemas/validators/",
    "control/schemas/deprecated/",
)
FORBIDDEN_UPDATE_PREFIXES = ("runtime/", "surfaces/", "site/", "native/", "crates/")
FORBIDDEN_OUTPUT_ROOTS = (
    ".git",
    ".env",
    "runtime",
    "surfaces",
    "site",
    "native",
    "crates",
    "secrets",
    ".aide.local",
    ".local",
    ".cache",
)
APPROVED_OUTPUT_PREFIXES = (
    "control/inventory/",
    f"{AUDIT_DIR.as_posix()}/",
)
TEXT_SUFFIXES = {
    "",
    ".cfg",
    ".csv",
    ".html",
    ".ini",
    ".json",
    ".jsonl",
    ".md",
    ".ps1",
    ".py",
    ".rs",
    ".schema",
    ".sh",
    ".toml",
    ".ts",
    ".tsx",
    ".txt",
    ".yaml",
    ".yml",
}
IMMUTABLE_HISTORICAL_INVENTORY_PREFIXES = (
    "control/inventory/r0_03b_1_",
)
TEST_FIXTURE_REFERENCE_PATHS = {
    "tests/operations/test_contract_taxonomy_migration.py",
}


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--migration-result", default=str(DEFAULT_MIGRATION_RESULT))
    parser.add_argument("--reference-graph", default=str(DEFAULT_REFERENCE_GRAPH))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--output")
    parser.add_argument("--summary-output")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--write-standard-outputs", action="store_true")
    args = parser.parse_args(argv)

    root = Path(args.repo_root).resolve()
    errors: list[str] = []
    if args.dry_run and args.apply:
        errors.append("--dry-run and --apply cannot both be set")
    for output in (args.output, args.summary_output):
        if output:
            check_output_path(root, Path(output), errors)

    if errors:
        result = blocked_result(errors)
    else:
        try:
            migration_result = load_json(resolve_repo_path(root, Path(args.migration_result)))
            reference_graph = load_json(resolve_repo_path(root, Path(args.reference_graph)))
            migration_plan = load_json(root / DEFAULT_MIGRATION_PLAN)
            shim_report = load_json(root / DEFAULT_SHIM_REPORT)
        except FileNotFoundError as exc:
            result = blocked_result([f"missing required migration inventory: {exc.filename}"])
        except json.JSONDecodeError as exc:
            result = blocked_result([f"malformed required migration inventory: {exc}"])
        else:
            result = update_references(
                root,
                migration_result,
                reference_graph,
                migration_plan,
                shim_report,
                apply_changes=bool(args.apply),
            )

    if args.output and not result["errors"]:
        write_json(resolve_repo_path(root, Path(args.output)), result["reference_update_result"])
    if args.summary_output and not result["errors"]:
        write_text(resolve_repo_path(root, Path(args.summary_output)), render_summary(result))
    if args.write_standard_outputs and not result["errors"]:
        write_json(root / REFERENCE_RESULT_PATH, result["reference_update_result"])

    if args.json:
        print(json.dumps(result["reference_update_result"], indent=2, sort_keys=True), file=stdout)
    else:
        print(render_console(result), file=stdout)
    for error in result["errors"]:
        print(f"ERROR: {error}", file=stderr)
    return 1 if result["reference_update_result"]["status"] in {"blocked", "fail"} else 0


def update_references(
    root: Path,
    migration_result: Mapping[str, Any],
    reference_graph: Mapping[str, Any],
    migration_plan: Mapping[str, Any],
    shim_report: Mapping[str, Any],
    *,
    apply_changes: bool,
) -> dict[str, Any]:
    errors: list[str] = []
    if migration_result.get("task") != "R0-03B-1":
        errors.append("migration result must come from R0-03B-1")
    if reference_graph.get("schema_version") != "contract_reference_graph.v0":
        errors.append("reference graph schema_version must be contract_reference_graph.v0")
    if errors:
        return blocked_result(errors)

    selected, blocked = select_b2_moves(root, migration_plan)
    moved = move_selected(root, selected, apply_changes=apply_changes)
    b1_mapping = mapping_from_shims(root, shim_report)
    b2_mapping = {item["source_path"]: item["target_path"] for item in moved}
    replacements = {**b1_mapping, **b2_mapping}
    updates, unresolved, historical = find_reference_updates(root, replacements, selected, blocked)

    if apply_changes:
        apply_replacements(root, replacements, updates)
        for item in moved:
            item["references_updated"] = sorted(
                update["path"] for update in updates if update["old_reference"] == item["source_path"]
            )

    status = "pass"
    if blocked or unresolved:
        status = "pass_with_warnings"

    reference_result = {
        "schema_version": "r0_03b_2_reference_update_result.v0",
        "task": TASK_ID,
        "status": status,
        "mode": "apply" if apply_changes else "dry_run",
        "updates_attempted": len(updates) + len(unresolved),
        "updates_completed": len(updates) if apply_changes else 0,
        "updates_blocked": len(unresolved),
        "moved_in_this_task": moved,
        "blocked_moves": blocked,
        "historical_references_left_intact": historical,
        "unresolved_references": unresolved,
        "runtime_files_modified": 0,
        "product_behavior_changed": False,
        "f0_should_remain_blocked": True,
        "dev_to_main_should_remain_blocked": True,
    }
    return {"reference_update_result": reference_result, "errors": []}


def select_b2_moves(root: Path, migration_plan: Mapping[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    selected: list[dict[str, Any]] = []
    blocked: list[dict[str, Any]] = []
    for move in migration_plan.get("moves", []) or []:
        if not isinstance(move, Mapping):
            continue
        source_path = str(move.get("source_path", ""))
        target_path = str(move.get("target_path", ""))
        contract_class = str(move.get("contract_class_before", ""))
        if contract_class not in B2_MOVE_CLASSES:
            continue
        if not source_path.startswith("contracts/") or not target_path.startswith(CONTROL_SCHEMA_TARGETS):
            continue
        source = root / source_path
        target = root / target_path
        if not source.exists() and target.exists():
            selected.append(dict(move))
            continue
        if not source.exists() and not target.exists():
            blocked.append(blocked_move(move, "Source schema is missing and target schema does not exist."))
            continue
        if source.exists() and target.exists():
            blocked.append(blocked_move(move, "Target schema already exists while source still exists; refusing overwrite."))
            continue
        bad_refs, historical_refs = partition_bad_and_historical_refs(move)
        if bad_refs:
            item = blocked_move(move, "References require forbidden or unsupported path updates in R0-03B-2.")
            item["references"] = bad_refs
            item["historical_references"] = historical_refs
            blocked.append(item)
            continue
        selected.append(dict(move))
    return selected, blocked


def move_selected(root: Path, selected: Sequence[Mapping[str, Any]], *, apply_changes: bool) -> list[dict[str, Any]]:
    moved: list[dict[str, Any]] = []
    for move in selected:
        source = root / str(move["source_path"])
        target = root / str(move["target_path"])
        mode = "dry_run"
        if target.is_file() and not source.exists():
            mode = "already_moved"
        elif apply_changes:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(source), str(target))
            mode = "apply"
        moved.append(
            {
                "source_path": str(move["source_path"]),
                "target_path": str(move["target_path"]),
                "contract_class": str(move["contract_class_before"]),
                "reason": str(move.get("rationale", "R0-03B-2 control/task schema cleanup.")),
                "references_updated": [],
                "mode": mode,
            }
        )
    return moved


def mapping_from_shims(root: Path, shim_report: Mapping[str, Any]) -> dict[str, str]:
    mapping: dict[str, str] = {}
    for shim in shim_report.get("shims", []) or []:
        old = str(shim.get("old_path", ""))
        new = str(shim.get("new_path", ""))
        if not old or not new:
            continue
        if (root / new).exists():
            mapping[old] = new
    return mapping


def find_reference_updates(
    root: Path,
    replacements: Mapping[str, str],
    selected: Sequence[Mapping[str, Any]],
    blocked_moves: Sequence[Mapping[str, Any]],
) -> tuple[list[dict[str, str]], list[dict[str, str]], list[dict[str, str]]]:
    updates: list[dict[str, str]] = []
    unresolved: list[dict[str, str]] = []
    historical: list[dict[str, str]] = []
    selected_sources = {str(item["source_path"]) for item in selected}
    paths = iter_candidate_text_files(root)
    for path in paths:
        rel = path.relative_to(root).as_posix()
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = path.read_text(encoding="utf-8", errors="ignore")
        for old, new in replacements.items():
            if old not in text and old.replace("/", "\\") not in text:
                continue
            entry = {
                "path": rel,
                "old_reference": old,
                "new_reference": new,
                "reason": "Active schema reference updated for R0-03B-2.",
            }
            if is_historical_reference_path(rel):
                historical.append({**entry, "reason": "Historical audit evidence left intact."})
            elif is_allowed_active_update_path(rel):
                updates.append(entry)
            else:
                unresolved.append({**entry, "reason": "Reference path is outside the R0-03B-2 update boundary."})
    for move in blocked_moves:
        for ref in move.get("references", []) or []:
            unresolved.append(
                {
                    "path": str(ref),
                    "old_reference": str(move.get("source_path", "")),
                    "new_reference": str(move.get("target_path", "")),
                    "reason": str(move.get("reason", "Move remains blocked.")),
                }
            )
        for ref in move.get("historical_references", []) or []:
            historical.append(
                {
                    "path": str(ref),
                    "old_reference": str(move.get("source_path", "")),
                    "new_reference": str(move.get("target_path", "")),
                    "reason": "Historical audit evidence left intact.",
                }
            )
    return dedupe_dicts(updates), dedupe_dicts(unresolved), dedupe_dicts(historical)


def apply_replacements(root: Path, replacements: Mapping[str, str], updates: Sequence[Mapping[str, str]]) -> None:
    for rel in sorted({item["path"] for item in updates}):
        path = root / rel
        if not path.exists() or not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            text = path.read_text(encoding="utf-8", errors="ignore")
        original = text
        for old, new in replacements.items():
            text = text.replace(old, new)
            text = text.replace(old.replace("/", "\\"), new.replace("/", "\\"))
        if text != original:
            path.write_text(text, encoding="utf-8")


def iter_candidate_text_files(root: Path) -> list[Path]:
    roots = [
        "contracts",
        "control/inventory",
        "control/policies",
        "control/schemas",
        "docs/architecture",
        "docs/operations",
        "docs/reference",
        "examples",
        "scripts",
        "tests",
        "control/audits",
    ]
    files: list[Path] = []
    for rel in roots:
        base = root / rel
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if path.is_file() and path.suffix.lower() in TEXT_SUFFIXES:
                files.append(path)
    return files


def partition_bad_and_historical_refs(move: Mapping[str, Any]) -> tuple[list[str], list[str]]:
    bad: list[str] = []
    historical: list[str] = []
    for ref in move.get("references_to_update", []) or []:
        ref_path = str(ref).replace("\\", "/")
        if is_historical_reference_path(ref_path):
            historical.append(ref_path)
        elif not is_allowed_active_update_path(ref_path):
            bad.append(ref_path)
    return sorted(set(bad)), sorted(set(historical))


def is_allowed_active_update_path(path: str) -> bool:
    return (
        path.startswith("contracts/")
        or path.startswith("control/schemas/")
        or path.startswith("control/inventory/")
        or path.startswith("control/policies/contract_")
        or path.startswith("docs/operations/")
        or path.startswith("docs/reference/")
        or path.startswith("docs/architecture/")
        or path.startswith("examples/")
        or path.startswith("tests/")
        or path.startswith("scripts/audit_")
        or path.startswith("scripts/validate_")
        or path == "scripts/update_contract_schema_references.py"
        or path == "scripts/validate_product_contract_tree.py"
        or (path.startswith("control/audits/") and (path.endswith("/README.md") or path.endswith("/validation.md")))
    )


def is_historical_reference_path(path: str) -> bool:
    return (
        path.startswith(IMMUTABLE_HISTORICAL_INVENTORY_PREFIXES)
        or path in TEST_FIXTURE_REFERENCE_PATHS
        or (path.startswith("control/audits/") and not (path.endswith("/README.md") or path.endswith("/validation.md")))
    )


def blocked_move(move: Mapping[str, Any], reason: str) -> dict[str, Any]:
    return {
        "source_path": str(move.get("source_path", "")),
        "target_path": str(move.get("target_path", "")),
        "contract_class": str(move.get("contract_class_before", "")),
        "reason": reason,
        "blocks": ["R0-03B-2"],
    }


def blocked_result(errors: Sequence[str]) -> dict[str, Any]:
    return {
        "reference_update_result": {
            "schema_version": "r0_03b_2_reference_update_result.v0",
            "task": TASK_ID,
            "status": "blocked",
            "updates_attempted": 0,
            "updates_completed": 0,
            "updates_blocked": len(errors),
            "historical_references_left_intact": [],
            "unresolved_references": [{"reason": error} for error in errors],
            "runtime_files_modified": 0,
            "product_behavior_changed": False,
            "f0_should_remain_blocked": True,
            "dev_to_main_should_remain_blocked": True,
        },
        "errors": list(errors),
    }


def resolve_repo_path(root: Path, path: Path) -> Path:
    return path if path.is_absolute() else root / path


def check_output_path(root: Path, path: Path, errors: list[str]) -> None:
    full = resolve_repo_path(root, path).resolve()
    rel = full.relative_to(root).as_posix() if is_relative_to(full, root) else full.as_posix()
    if not is_relative_to(full, root):
        errors.append(f"refusing output outside repo: {path}")
        return
    first = rel.split("/", 1)[0]
    if first in FORBIDDEN_OUTPUT_ROOTS or rel in FORBIDDEN_OUTPUT_ROOTS:
        errors.append(f"refusing forbidden output root: {rel}")
        return
    if not rel.startswith(APPROVED_OUTPUT_PREFIXES):
        errors.append(f"refusing output outside approved R0-03B-2 roots: {rel}")


def is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def dedupe_dicts(items: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    result: list[dict[str, Any]] = []
    for item in items:
        key = json.dumps(item, sort_keys=True)
        if key in seen:
            continue
        seen.add(key)
        result.append(dict(item))
    return result


def render_console(result: Mapping[str, Any]) -> str:
    payload = result["reference_update_result"]
    return "\n".join(
        [
            "R0-03B-2 contract schema reference update",
            f"status: {payload['status']}",
            f"mode: {payload.get('mode', 'blocked')}",
            f"updates_completed: {payload['updates_completed']}",
            f"updates_blocked: {payload['updates_blocked']}",
            f"runtime_files_modified: {payload['runtime_files_modified']}",
            "f0_should_remain_blocked: true",
            "dev_to_main_should_remain_blocked: true",
        ]
    )


def render_summary(result: Mapping[str, Any]) -> str:
    payload = result["reference_update_result"]
    return "\n".join(
        [
            "# R0-03B-2 Reference Update Summary",
            "",
            f"- status: {payload['status']}",
            f"- updates attempted: {payload['updates_attempted']}",
            f"- updates completed: {payload['updates_completed']}",
            f"- updates blocked: {payload['updates_blocked']}",
            f"- moved in this task: {len(payload.get('moved_in_this_task', []))}",
            f"- blocked moves: {len(payload.get('blocked_moves', []))}",
            f"- historical references left intact: {len(payload['historical_references_left_intact'])}",
            "- runtime files modified: 0",
            "- product behavior changed: false",
            "- F0 remains blocked: true",
            "- dev-to-main remains blocked: true",
            "",
        ]
    )


if __name__ == "__main__":
    raise SystemExit(main())
