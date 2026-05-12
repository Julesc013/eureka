#!/usr/bin/env python3
"""Execute the R0-03B-1 contract taxonomy migration batch."""

from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Iterable, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
TASK_ID = "R0-03B-1"
BATCH_ID = "R0-03B-1"
DEFAULT_PLAN = Path("control/inventory/contract_migration_plan.json")
AUDIT_DIR = Path("control/audits/r0-03b-1-contract-taxonomy-migration-v0")
RESULT_PATH = Path("control/inventory/r0_03b_1_migration_result.json")
REFERENCE_REPORT_PATH = Path("control/inventory/r0_03b_1_reference_update_report.json")
SHIM_REPORT_PATH = Path("control/inventory/r0_03b_1_compatibility_shim_report.json")
AUDIT_REPORT_PATH = AUDIT_DIR / "r0_03b_1_report.json"

TARGET_SCHEMA_ROOTS = (
    "control/schemas/audits/",
    "control/schemas/fixtures/",
    "control/schemas/previews/",
    "control/schemas/policies/",
    "control/schemas/validators/",
    "control/schemas/tasks/",
    "control/schemas/deprecated/",
)

BATCH_CLASSES = {"audit_schema", "fixture_schema", "preview_schema"}
KEEP_IN_CONTRACTS_FOR_BATCH_1 = {
    "contracts/api/absence_report.v0.json",
    "contracts/api/examples/search_result_card_firefox_xp_candidate.v0.json",
    "contracts/views/candidate_page.v0.json",
    "contracts/ui/ui_contracts/absence_report.ui_contract.yaml",
    "contracts/ui/view_models/absence_report.view_model.yaml",
}
DEFERRED_CLASSES = {"control_schema", "validator_schema", "task_queue_schema", "generated_scaffold_schema", "deprecated_schema"}
PRODUCT_CLASSES = {
    "product_domain_contract",
    "product_runtime_contract",
    "public_api_contract",
    "snapshot_contract",
    "native_contract",
    "durable_store_contract",
    "connector_interface_contract",
    "source_policy_contract",
}
FORBIDDEN_PRODUCT_PREFIXES = ("runtime/", "surfaces/", "site/", "native/", "crates/")
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
APPROVED_REPO_OUTPUT_ROOTS = (
    "control/inventory",
    AUDIT_DIR.as_posix(),
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


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--plan", default=str(DEFAULT_PLAN))
    parser.add_argument("--batch-id", default=BATCH_ID)
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--update-references", action="store_true")
    parser.add_argument("--output")
    parser.add_argument("--summary-output")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--write-standard-outputs", action="store_true")
    args = parser.parse_args(argv)

    root = Path(args.repo_root).resolve()
    errors: list[str] = []
    plan_path = resolve_repo_path(root, Path(args.plan))
    if args.batch_id != BATCH_ID:
        errors.append(f"unsupported batch id for this executor: {args.batch_id}")
    for output in (args.output, args.summary_output):
        if output:
            check_output_path(root, Path(output), errors)

    apply_changes = bool(args.apply)
    if args.dry_run and args.apply:
        errors.append("--dry-run and --apply cannot both be set")
    mode = "apply" if apply_changes else "dry_run"

    if errors:
        result = blocked_result(errors)
    else:
        try:
            plan = load_json(plan_path)
        except FileNotFoundError:
            result = blocked_result([f"missing R0-03A migration plan: {plan_path.as_posix()}"])
        except json.JSONDecodeError as exc:
            result = blocked_result([f"malformed R0-03A migration plan: {exc}"])
        else:
            result = execute_migration(root, plan, mode=mode, update_references=args.update_references)

    if args.output and not errors:
        write_json(resolve_repo_path(root, Path(args.output)), result["migration_result"])
    if args.summary_output and not errors:
        write_text(resolve_repo_path(root, Path(args.summary_output)), render_summary(result))
    if args.write_standard_outputs and not errors:
        write_standard_outputs(root, result)

    if args.json:
        print(json.dumps(result["migration_result"], indent=2, sort_keys=True), file=stdout)
    else:
        print(render_console_summary(result), file=stdout)

    if result["migration_result"]["status"] in {"blocked", "fail"}:
        for item in result["migration_result"].get("blocked", []):
            print(f"BLOCKED: {item.get('source_path') or item.get('reason')}: {item.get('reason')}", file=stderr)
        return 1
    return 0 if result["migration_result"]["status"] != "fail" else 1


def execute_migration(root: Path, plan: Mapping[str, Any], *, mode: str, update_references: bool) -> dict[str, Any]:
    create_target_roots(root, apply_changes=(mode == "apply"))
    selected, blocked, deferred = select_batch_moves(root, plan)
    moved: list[dict[str, Any]] = []
    warnings: list[str] = []
    for move in selected:
        source = root / move["source_path"]
        target = root / move["target_path"]
        already_moved = target.is_file() and not source.exists()
        if mode == "apply" and not already_moved:
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(source), str(target))
        moved.append(
            {
                "source_path": move["source_path"],
                "target_path": move["target_path"],
                "contract_class": move["contract_class_before"],
                "reason": move["rationale"],
                "references_updated": [],
                "compatibility_shim": False,
                "mode": "already_moved" if already_moved else mode,
            }
        )

    reference_report = build_reference_report(plan, moved, blocked, update_references)
    shim_report = build_shim_report(moved, blocked, reference_report)
    if mode == "apply" and update_references:
        apply_reference_updates(root, moved, reference_report)
        for item in moved:
            item["references_updated"] = sorted(
                update["path"]
                for update in reference_report["updates"]
                if update["old_reference"] == item["source_path"]
            )
            item["compatibility_shim"] = any(shim["old_path"] == item["source_path"] for shim in shim_report["shims"])

    if deferred:
        warnings.append(f"{len(deferred)} non-batch or product/unknown schema moves were deferred to later R0 tasks.")
    if blocked:
        warnings.append(f"{len(blocked)} audit/fixture/preview moves were blocked by forbidden or unresolved references.")

    status = "pass"
    if blocked or deferred:
        status = "pass_with_warnings"
    if any(str(item.get("reason", "")).startswith("ambiguous migration plan") for item in blocked):
        status = "blocked"

    result = {
        "schema_version": "r0_03b_1_migration_result.v0",
        "task": TASK_ID,
        "status": status,
        "batch_id": BATCH_ID,
        "mode": mode,
        "reference_updates_enabled": update_references,
        "moves_attempted": len(selected) + len(blocked),
        "moves_completed": len(moved),
        "moves_blocked": len(blocked),
        "schemas_deleted": 0,
        "product_contracts_moved": sum(1 for item in moved if item["contract_class"] in PRODUCT_CLASSES),
        "unknown_contracts_moved": sum(1 for item in moved if item["contract_class"] == "unknown"),
        "runtime_files_modified": 0,
        "moved": moved,
        "blocked": blocked,
        "deferred": deferred,
        "warnings": warnings,
        "f0_should_remain_blocked": True,
        "dev_to_main_should_remain_blocked": True,
    }
    audit_report = build_audit_report(result, reference_report, shim_report)
    return {
        "migration_result": result,
        "reference_update_report": reference_report,
        "compatibility_shim_report": shim_report,
        "audit_report": audit_report,
    }


def select_batch_moves(root: Path, plan: Mapping[str, Any]) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    selected: list[dict[str, Any]] = []
    blocked: list[dict[str, Any]] = []
    deferred: list[dict[str, Any]] = []
    moves = plan.get("moves", [])
    if not isinstance(moves, list) or not moves:
        blocked.append({"reason": "ambiguous migration plan: no move records available", "blocks": ["R0-03B-1"]})
        return selected, blocked, deferred
    for move in moves:
        if not isinstance(move, Mapping):
            continue
        source_path = str(move.get("source_path", ""))
        target_path = str(move.get("target_path", ""))
        contract_class = str(move.get("contract_class_before", ""))
        if source_path in KEEP_IN_CONTRACTS_FOR_BATCH_1:
            deferred.append(deferred_item(move, "Active public API/UI contract was kept in contracts/ for product-contract cleanup review."))
            continue
        if contract_class in PRODUCT_CLASSES or contract_class == "unknown":
            deferred.append(deferred_item(move, "Product and unknown contracts are out of scope for R0-03B-1."))
            continue
        if contract_class in DEFERRED_CLASSES:
            deferred.append(deferred_item(move, "Control/task/validator/deprecated/generated schemas are deferred to R0-03B-2."))
            continue
        if contract_class not in BATCH_CLASSES:
            deferred.append(deferred_item(move, "Schema class is not part of the R0-03B-1 audit/fixture/preview batch."))
            continue
        if not target_path.startswith(("control/schemas/audits/", "control/schemas/fixtures/", "control/schemas/previews/")):
            blocked.append(blocked_item(move, "Batch target is not an approved R0-03B-1 control schema root."))
            continue
        source = root / source_path
        target = root / target_path
        if not source.exists() and not target.exists():
            blocked.append(blocked_item(move, "Source schema is missing and target schema does not exist."))
            continue
        if source.exists() and target.exists():
            blocked.append(blocked_item(move, "Target schema already exists while source still exists; refusing overwrite."))
            continue
        bad_refs, historical_refs = unsafe_references(move)
        if bad_refs:
            item = blocked_item(move, "References require forbidden or unsupported path updates in this batch.")
            item["references"] = bad_refs
            item["historical_references"] = historical_refs
            blocked.append(item)
            continue
        selected.append(dict(move))
    return selected, blocked, deferred


def unsafe_references(move: Mapping[str, Any]) -> tuple[list[str], list[str]]:
    bad: list[str] = []
    historical: list[str] = []
    for ref in move.get("references_to_update", []) or []:
        ref_path = str(ref).replace("\\", "/")
        if any(ref_path.startswith(prefix) for prefix in FORBIDDEN_PRODUCT_PREFIXES):
            bad.append(ref_path)
            continue
        if ref_path.startswith("control/audits/") and not (ref_path.endswith("/README.md") or ref_path.endswith("/validation.md")):
            historical.append(ref_path)
            continue
        if not is_allowed_reference_update_path(ref_path):
            bad.append(ref_path)
    return sorted(set(bad)), sorted(set(historical))


def is_allowed_reference_update_path(path: str) -> bool:
    return (
        path.startswith("contracts/")
        or path.startswith("control/schemas/")
        or path.startswith("control/inventory/")
        or path.startswith("control/policies/")
        or path.startswith("docs/operations/")
        or path.startswith("docs/reference/")
        or path.startswith("examples/")
        or path.startswith("tests/")
        or path.startswith("scripts/audit_")
        or path.startswith("scripts/validate_")
        or (path.startswith("control/audits/") and (path.endswith("/README.md") or path.endswith("/validation.md")))
    )


def build_reference_report(
    plan: Mapping[str, Any],
    moved: Sequence[Mapping[str, Any]],
    blocked: Sequence[Mapping[str, Any]],
    update_references: bool,
) -> dict[str, Any]:
    updates: list[dict[str, str]] = []
    unresolved: list[dict[str, Any]] = []
    historical: list[dict[str, Any]] = []
    moved_by_source = {item["source_path"]: item for item in moved}
    moved_path_map = {str(item["source_path"]): str(item["target_path"]) for item in moved}
    for move in plan.get("moves", []) or []:
        if not isinstance(move, Mapping):
            continue
        source_path = str(move.get("source_path", ""))
        if source_path not in moved_by_source:
            continue
        target_path = str(move.get("target_path", ""))
        _, historical_refs = unsafe_references(move)
        for ref in move.get("references_to_update", []) or []:
            ref_path = str(ref).replace("\\", "/")
            update_path = moved_path_map.get(ref_path, ref_path)
            if ref_path in historical_refs:
                historical.append(
                    {
                        "path": ref_path,
                        "old_reference": source_path,
                        "new_reference": target_path,
                        "reason": "Historical audit evidence was left intact by R0-03B-1.",
                    }
                )
                continue
            if is_allowed_reference_update_path(update_path):
                updates.append(
                    {
                        "path": update_path,
                        "old_reference": source_path,
                        "new_reference": target_path,
                        "reason": "Moved schema path updated for R0-03B-1." if update_references else "Eligible for update when --update-references is used.",
                    }
                )
            else:
                unresolved.append(
                    {
                        "path": ref_path,
                        "old_reference": source_path,
                        "new_reference": target_path,
                        "reason": "Reference path is outside the R0-03B-1 update boundary.",
                    }
                )
    for item in blocked:
        for ref_path in item.get("references", []):
            unresolved.append(
                {
                    "path": ref_path,
                    "old_reference": item.get("source_path", ""),
                    "new_reference": item.get("target_path", ""),
                    "reason": item.get("reason", "Blocked move keeps old reference intact."),
                }
            )
        for ref_path in item.get("historical_references", []):
            historical.append(
                {
                    "path": ref_path,
                    "old_reference": item.get("source_path", ""),
                    "new_reference": item.get("target_path", ""),
                    "reason": "Historical audit evidence was left intact.",
                }
            )
    return {
        "schema_version": "r0_03b_1_reference_update_report.v0",
        "task": TASK_ID,
        "updates": dedupe_dicts(updates),
        "unresolved_references": dedupe_dicts(unresolved),
        "historical_references_left_intact": dedupe_dicts(historical),
    }


def apply_reference_updates(root: Path, moved: Sequence[Mapping[str, Any]], report: Mapping[str, Any]) -> None:
    replacements = {item["source_path"]: item["target_path"] for item in moved}
    paths = sorted({str(update["path"]) for update in report.get("updates", [])})
    for rel in paths:
        if not is_allowed_reference_update_path(rel):
            continue
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


def build_shim_report(
    moved: Sequence[Mapping[str, Any]],
    blocked: Sequence[Mapping[str, Any]],
    reference_report: Mapping[str, Any],
) -> dict[str, Any]:
    unresolved_by_old = Counter(str(item.get("old_reference", "")) for item in reference_report.get("unresolved_references", []))
    shims: list[dict[str, str]] = []
    for item in moved:
        old_path = str(item["source_path"])
        new_path = str(item["target_path"])
        shim_kind = "validator_mapping" if unresolved_by_old.get(old_path, 0) else "none"
        shims.append(
            {
                "old_path": old_path,
                "new_path": new_path,
                "shim_kind": shim_kind,
                "expires_after_task": "R0-03B-2" if shim_kind != "none" else "never",
                "reason": "Path mapping is recorded for validators and audit readers; no compatibility schema file was left under contracts/.",
            }
        )
    for item in blocked:
        shims.append(
            {
                "old_path": str(item.get("source_path", "")),
                "new_path": str(item.get("target_path", "")),
                "shim_kind": "none",
                "expires_after_task": "R0-03B-2",
                "reason": "Move was blocked, so the original contract path remains in place.",
            }
        )
    return {
        "schema_version": "r0_03b_1_compatibility_shim_report.v0",
        "task": TASK_ID,
        "shims": shims,
    }


def build_audit_report(
    result: Mapping[str, Any],
    reference_report: Mapping[str, Any],
    shim_report: Mapping[str, Any],
) -> dict[str, Any]:
    return {
        "schema_version": "r0_03b_1_report.v0",
        "status": result["status"],
        "task": TASK_ID,
        "purpose": "contract_taxonomy_migration_batch_1",
        "moves_completed": result["moves_completed"],
        "moves_blocked": result["moves_blocked"],
        "schemas_deleted": 0,
        "product_contracts_moved": result["product_contracts_moved"],
        "unknown_contracts_moved": result["unknown_contracts_moved"],
        "runtime_modified": False,
        "product_behavior_changed": False,
        "reference_updates_completed": len(reference_report.get("updates", [])),
        "compatibility_shims_added": sum(1 for item in shim_report.get("shims", []) if item.get("shim_kind") != "none"),
        "f0_should_remain_blocked": True,
        "dev_to_main_should_remain_blocked": True,
        "recommended_next_task": "R0-03B-2 — Contract reference update and product contract cleanup",
        "validation": {},
    }


def create_target_roots(root: Path, *, apply_changes: bool) -> None:
    if not apply_changes:
        return
    schemas_root = root / "control/schemas"
    schemas_root.mkdir(parents=True, exist_ok=True)
    readme = schemas_root / "README.md"
    if not readme.exists():
        readme.write_text(
            "# Control Schemas\n\n"
            "Control schemas hold audit, fixture, preview, policy, validator, task, and deprecated schemas that are not stable product contracts.\n",
            encoding="utf-8",
        )
    for rel in TARGET_SCHEMA_ROOTS:
        directory = root / rel
        directory.mkdir(parents=True, exist_ok=True)
        marker = directory / ".gitkeep"
        if not marker.exists() and not any(directory.iterdir()):
            marker.write_text("", encoding="utf-8")


def write_standard_outputs(root: Path, result: Mapping[str, Any]) -> None:
    write_json(root / RESULT_PATH, result["migration_result"])
    write_json(root / REFERENCE_REPORT_PATH, result["reference_update_report"])
    write_json(root / SHIM_REPORT_PATH, result["compatibility_shim_report"])
    write_json(root / AUDIT_REPORT_PATH, result["audit_report"])
    write_json(root / (AUDIT_DIR / "generated/sample_migration_result.json"), result["migration_result"])
    write_json(root / (AUDIT_DIR / "generated/sample_reference_update_report.json"), result["reference_update_report"])
    write_text(root / (AUDIT_DIR / "generated/sample_summary.md"), render_summary(result))
    write_audit_markdown(root, result)
    refresh_taxonomy_inventory(root)


def write_audit_markdown(root: Path, result: Mapping[str, Any]) -> None:
    result_payload = result["migration_result"]
    reference_report = result["reference_update_report"]
    shim_report = result["compatibility_shim_report"]
    moved = result_payload["moved"]
    blocked = result_payload["blocked"]
    markdown = {
        AUDIT_DIR / "README.md": "# R0-03B-1 Contract Taxonomy Migration\n\nBatch 1 moves clear audit, fixture, and preview schemas from `contracts/` into `control/schemas/` while leaving product, unknown, runtime-referenced, and later-batch schemas untouched.\n",
        AUDIT_DIR / "migration_result.md": render_summary(result),
        AUDIT_DIR / "moved_schema_summary.md": render_moved_summary(moved),
        AUDIT_DIR / "remaining_product_contract_summary.md": render_remaining_summary(result_payload),
        AUDIT_DIR / "compatibility_shim_summary.md": render_shim_summary(shim_report),
        AUDIT_DIR / "reference_update_summary.md": render_reference_summary(reference_report),
        AUDIT_DIR / "validation.md": "# Validation\n\nValidation commands are recorded after R0-03B-1 checks run.\n",
        Path("docs/operations/R0_CONTRACT_TAXONOMY_MIGRATION_BATCH_1.md"): render_operation_doc(result),
    }
    for rel, text in markdown.items():
        write_text(root / rel, text)


def refresh_taxonomy_inventory(root: Path) -> None:
    audit_script = root / "scripts/audit_contract_taxonomy.py"
    spec = importlib.util.spec_from_file_location("audit_contract_taxonomy", audit_script)
    if spec is None or spec.loader is None:
        return
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    audit = module.build_contract_taxonomy_audit(root)
    outputs = {
        "control/inventory/contract_taxonomy_inventory.json": audit["contract_taxonomy_inventory"],
        "control/inventory/contract_migration_plan.json": audit["contract_migration_plan"],
        "control/inventory/contract_reference_graph.json": audit["contract_reference_graph"],
        "control/inventory/contract_risk_register.json": audit["contract_risk_register"],
        "control/inventory/r0_03b_execution_plan.json": audit["r0_03b_execution_plan"],
    }
    for rel, payload in outputs.items():
        write_json(root / rel, payload)


def blocked_item(move: Mapping[str, Any], reason: str) -> dict[str, Any]:
    return {
        "source_path": str(move.get("source_path", "")),
        "target_path": str(move.get("target_path", "")),
        "contract_class": str(move.get("contract_class_before", "")),
        "reason": reason,
        "blocks": ["R0-03B-1"],
    }


def deferred_item(move: Mapping[str, Any], reason: str) -> dict[str, Any]:
    return {
        "source_path": str(move.get("source_path", "")),
        "target_path": str(move.get("target_path", "")),
        "contract_class": str(move.get("contract_class_before", "")),
        "reason": reason,
    }


def blocked_result(errors: Sequence[str]) -> dict[str, Any]:
    result = {
        "schema_version": "r0_03b_1_migration_result.v0",
        "task": TASK_ID,
        "status": "blocked",
        "batch_id": BATCH_ID,
        "moves_attempted": 0,
        "moves_completed": 0,
        "moves_blocked": len(errors),
        "schemas_deleted": 0,
        "product_contracts_moved": 0,
        "unknown_contracts_moved": 0,
        "runtime_files_modified": 0,
        "moved": [],
        "blocked": [{"reason": error, "blocks": ["R0-03B-1"]} for error in errors],
        "warnings": [],
        "f0_should_remain_blocked": True,
        "dev_to_main_should_remain_blocked": True,
    }
    reference_report = {"schema_version": "r0_03b_1_reference_update_report.v0", "task": TASK_ID, "updates": [], "unresolved_references": [], "historical_references_left_intact": []}
    shim_report = {"schema_version": "r0_03b_1_compatibility_shim_report.v0", "task": TASK_ID, "shims": []}
    return {"migration_result": result, "reference_update_report": reference_report, "compatibility_shim_report": shim_report, "audit_report": build_audit_report(result, reference_report, shim_report)}


def render_console_summary(result: Mapping[str, Any]) -> str:
    payload = result["migration_result"]
    return "\n".join(
        [
            "R0-03B-1 contract taxonomy migration",
            f"status: {payload['status']}",
            f"mode: {payload.get('mode', 'blocked')}",
            f"moves_completed: {payload['moves_completed']}",
            f"moves_blocked: {payload['moves_blocked']}",
            f"schemas_deleted: {payload['schemas_deleted']}",
            f"runtime_files_modified: {payload['runtime_files_modified']}",
            "f0_should_remain_blocked: true",
            "dev_to_main_should_remain_blocked: true",
        ]
    )


def render_summary(result: Mapping[str, Any]) -> str:
    payload = result["migration_result"]
    counts = Counter(item["contract_class"] for item in payload.get("moved", []))
    lines = [
        "# R0-03B-1 Migration Summary",
        "",
        f"- status: {payload['status']}",
        f"- moves completed: {payload['moves_completed']}",
        f"- moves blocked: {payload['moves_blocked']}",
        f"- schemas deleted: {payload['schemas_deleted']}",
        f"- product contracts moved: {payload['product_contracts_moved']}",
        f"- unknown contracts moved: {payload['unknown_contracts_moved']}",
        f"- runtime files modified: {payload['runtime_files_modified']}",
        "- F0 remains blocked: true",
        "- dev-to-main remains blocked: true",
        "",
        "## Moved Classes",
        "",
    ]
    for key, count in sorted(counts.items()):
        lines.append(f"- {key}: {count}")
    if payload.get("blocked"):
        lines.extend(["", "## Blocked Moves", ""])
        for item in payload["blocked"][:50]:
            lines.append(f"- {item.get('source_path')}: {item.get('reason')}")
        if len(payload["blocked"]) > 50:
            lines.append(f"- ... {len(payload['blocked']) - 50} additional blocked moves in JSON.")
    return "\n".join(lines) + "\n"


def render_moved_summary(moved: Sequence[Mapping[str, Any]]) -> str:
    lines = ["# Moved Schema Summary", "", f"count: {len(moved)}", ""]
    for item in moved[:250]:
        lines.append(f"- {item['source_path']} -> {item['target_path']} ({item['contract_class']})")
    if len(moved) > 250:
        lines.append(f"- ... {len(moved) - 250} additional moved schemas in JSON.")
    return "\n".join(lines) + "\n"


def render_remaining_summary(result: Mapping[str, Any]) -> str:
    lines = [
        "# Remaining Product Contract Summary",
        "",
        "R0-03B-1 deliberately did not move product contracts, unknown contracts, or schemas with runtime/unsupported references.",
        "",
        f"- product contracts moved: {result['product_contracts_moved']}",
        f"- unknown contracts moved: {result['unknown_contracts_moved']}",
        f"- deferred records: {len(result.get('deferred', []))}",
        f"- blocked records: {len(result.get('blocked', []))}",
    ]
    return "\n".join(lines) + "\n"


def render_shim_summary(report: Mapping[str, Any]) -> str:
    shims = report.get("shims", [])
    lines = ["# Compatibility Shim Summary", "", f"shim records: {len(shims)}", ""]
    for item in shims[:150]:
        lines.append(f"- {item['old_path']} -> {item['new_path']} ({item['shim_kind']}, expires {item['expires_after_task']})")
    if len(shims) > 150:
        lines.append(f"- ... {len(shims) - 150} additional shim records in JSON.")
    return "\n".join(lines) + "\n"


def render_reference_summary(report: Mapping[str, Any]) -> str:
    lines = [
        "# Reference Update Summary",
        "",
        f"updates: {len(report.get('updates', []))}",
        f"unresolved references: {len(report.get('unresolved_references', []))}",
        f"historical references left intact: {len(report.get('historical_references_left_intact', []))}",
        "",
    ]
    for item in report.get("updates", [])[:150]:
        lines.append(f"- {item['path']}: {item['old_reference']} -> {item['new_reference']}")
    if len(report.get("updates", [])) > 150:
        lines.append(f"- ... {len(report['updates']) - 150} additional updates in JSON.")
    return "\n".join(lines) + "\n"


def render_operation_doc(result: Mapping[str, Any]) -> str:
    payload = result["migration_result"]
    return "\n".join(
        [
            "# R0 Contract Taxonomy Migration Batch 1",
            "",
            "R0-03B-1 executed the first contract taxonomy migration batch using the R0-03A migration plan.",
            "",
            "## What Moved",
            "",
            f"- moved schemas: {payload['moves_completed']}",
            "- moved classes: audit_schema, fixture_schema, preview_schema",
            "- target roots: control/schemas/audits/, control/schemas/fixtures/, control/schemas/previews/",
            "",
            "## What Did Not Move",
            "",
            "- product contracts remained in contracts/",
            "- unknown contracts remained in contracts/",
            "- schemas with runtime or unsupported active references remained in place",
            "- task, validator, generated, deprecated, and generic control schemas are deferred to R0-03B-2",
            "",
            "## References And Shims",
            "",
            "Allowed references were updated only when `--update-references` was used. Historical audit body references were left intact as evidence.",
            "No compatibility schema files were left under contracts/; path mappings are recorded in the shim report.",
            "",
            "## Boundaries",
            "",
            "- no runtime files were modified",
            "- no product behavior changed",
            "- no schemas were deleted",
            "- no live/network/model/provider calls were made",
            "- F0 remains blocked",
            "- dev-to-main promotion remains blocked",
            "",
            "## Next",
            "",
            "R0-03B-2 should update remaining references and clean up product contract placement after the control schema move.",
            "",
        ]
    )


def dedupe_dicts(items: Iterable[Mapping[str, Any]]) -> list[dict[str, Any]]:
    seen: set[str] = set()
    deduped: list[dict[str, Any]] = []
    for item in items:
        key = json.dumps(dict(item), sort_keys=True)
        if key in seen:
            continue
        seen.add(key)
        deduped.append(dict(item))
    return deduped


def check_output_path(root: Path, output: Path, errors: list[str]) -> None:
    candidate = output if output.is_absolute() else root / output
    try:
        resolved = candidate.resolve()
    except OSError:
        resolved = candidate.absolute()
    try:
        relative = resolved.relative_to(root).as_posix()
    except ValueError:
        return
    for forbidden in FORBIDDEN_OUTPUT_ROOTS:
        if relative == forbidden or relative.startswith(forbidden.rstrip("/") + "/"):
            errors.append(f"refusing forbidden output root: {relative}")
            return
    if not any(relative == prefix or relative.startswith(prefix.rstrip("/") + "/") for prefix in APPROVED_REPO_OUTPUT_ROOTS):
        errors.append(f"refusing repo output outside approved R0-03B-1 paths: {relative}")


def resolve_repo_path(root: Path, path: Path) -> Path:
    return path if path.is_absolute() else root / path


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, payload: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(payload, encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
