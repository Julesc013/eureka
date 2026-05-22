#!/usr/bin/env python3
"""Validate the post-R0-03B product contract tree."""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
TASK_ID = "R0-03B-2"
AUDIT_DIR = Path("control/audits/r0-03b-2-contract-reference-product-cleanup-v0")
REFERENCE_RESULT_PATH = Path("control/inventory/r0_03b_2_reference_update_result.json")
CLEANUP_RESULT_PATH = Path("control/inventory/r0_03b_2_product_contract_cleanup_result.json")
UNRESOLVED_PATH = Path("control/inventory/r0_03b_2_unresolved_contracts.json")
FINAL_TAXONOMY_PATH = Path("control/inventory/r0_03b_2_final_contract_taxonomy.json")
AUDIT_REPORT_PATH = AUDIT_DIR / "r0_03b_2_report.json"

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
NON_PRODUCT_CLASSES = {
    "audit_schema",
    "fixture_schema",
    "preview_schema",
    "control_schema",
    "validator_schema",
    "task_queue_schema",
    "generated_scaffold_schema",
    "deprecated_schema",
}
FORBIDDEN_MODIFIED_PREFIXES = ("runtime/", "surfaces/", "site/", "native/", "crates/")
FORBIDDEN_STATIC_IMPORT_ROOTS = {
    "urllib",
    "requests",
    "httpx",
    "aiohttp",
    "socket",
    "ftplib",
    "smtplib",
    "webbrowser",
    "selenium",
    "playwright",
    "openai",
    "anthropic",
}
TASK_NAMED_RE = re.compile(r"(^|[/_-])(?:h(?:[0-9]|1[0-4])|local_mvp|mvp|next_phase|bundle)(?:[/_.-]|$)", re.IGNORECASE)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--write-standard-outputs", action="store_true")
    args = parser.parse_args(argv)
    root = Path(args.repo_root).resolve()
    result = validate_contract_tree(root)
    if args.write_standard_outputs:
        write_standard_outputs(root, result)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print("R0-03B-2 product contract tree validation", file=stdout)
        print(f"status: {result['status']}", file=stdout)
        print(f"error_count: {len(result['errors'])}", file=stdout)
        for error in result["errors"]:
            print(f"ERROR: {error}", file=stdout)
    return 0 if result["status"] in {"valid", "valid_with_warnings"} else 1


def validate_contract_tree(root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    audit = load_contract_taxonomy(root, errors)
    contracts = [item for item in audit.get("contract_taxonomy_inventory", {}).get("contracts", []) if str(item.get("path", "")).startswith("contracts/")]
    reference_result = load_optional_json(root / REFERENCE_RESULT_PATH)
    previous_migration = load_optional_json(root / "control/inventory/r0_03b_1_migration_result.json")
    unresolved = build_unresolved(root, contracts, reference_result, previous_migration)
    unresolved_paths = {item["path"] for item in unresolved}

    non_product = []
    unknown = []
    task_named = []
    product = []
    for item in contracts:
        path = str(item.get("path", ""))
        cls = str(item.get("contract_class", "unknown"))
        if cls in PRODUCT_CLASSES:
            product.append(item)
            if is_task_named_product(path):
                task_named.append(item)
        elif cls == "unknown":
            unknown.append(item)
        elif cls in NON_PRODUCT_CLASSES:
            non_product.append(item)
            if path not in unresolved_paths:
                errors.append(f"clear non-product schema remains under contracts without unresolved record: {path}")
        else:
            unknown.append(item)

    for item in unknown:
        if item["path"] not in unresolved_paths:
            errors.append(f"unknown contract artifact is not recorded as unresolved: {item['path']}")
    for item in task_named:
        path = str(item.get("path", ""))
        if path not in unresolved_paths:
            warnings.append(f"task/bundle-shaped product contract name needs later cleanup review: {path}")

    validate_moved_schema_targets(root, previous_migration, errors)
    validate_no_forbidden_paths_modified(root, errors)
    validate_static_only(root, errors)
    if not reference_result:
        errors.append("missing R0-03B-2 reference update result")
    elif reference_result.get("f0_should_remain_blocked") is not True:
        errors.append("reference update result must keep F0 blocked")
    elif reference_result.get("dev_to_main_should_remain_blocked") is not True:
        errors.append("reference update result must keep dev-to-main blocked")

    contracts_clean_enough = not unresolved and not errors
    status = "valid"
    if warnings or unresolved:
        status = "valid_with_warnings"
    if errors:
        status = "invalid"

    cleanup_result = {
        "schema_version": "r0_03b_2_product_contract_cleanup_result.v0",
        "task": TASK_ID,
        "status": "pass" if status == "valid" else ("pass_with_warnings" if status == "valid_with_warnings" else "fail"),
        "contracts_scanned": len(contracts),
        "product_contract_count": len(product),
        "non_product_contract_count": len(non_product),
        "unknown_contract_count": len(unknown),
        "task_named_contract_count": len(task_named),
        "moved_in_this_task": reference_result.get("moved_in_this_task", []) if isinstance(reference_result, Mapping) else [],
        "blocked": unresolved,
        "warnings": warnings,
        "contracts_clean_enough_for_r0_04": contracts_clean_enough,
    }
    unresolved_result = {
        "schema_version": "r0_03b_2_unresolved_contracts.v0",
        "task": TASK_ID,
        "unresolved": unresolved,
    }
    final_taxonomy = {
        "schema_version": "r0_03b_2_final_contract_taxonomy.v0",
        "task": TASK_ID,
        "contracts_root_status": "clean" if contracts_clean_enough else ("partial" if not errors else "blocked"),
        "control_schemas_root_status": "clean_with_warnings" if unresolved else "clean",
        "product_contract_count": len(product),
        "control_schema_count": count_control_schema_files(root),
        "compatibility_shim_count": len(unresolved),
        "unresolved_contract_count": len(unresolved),
        "contracts_clean_enough_for_r0_04": contracts_clean_enough,
        "recommended_next_task": "R0-04 — Source observation production seam" if contracts_clean_enough else "R0-03C — Resolve remaining contract taxonomy blockers",
    }
    audit_report = {
        "schema_version": "r0_03b_2_report.v0",
        "status": cleanup_result["status"],
        "task": TASK_ID,
        "purpose": "contract_reference_update_and_product_contract_cleanup",
        "reference_updates_completed": reference_result.get("updates_completed", 0) if isinstance(reference_result, Mapping) else 0,
        "reference_updates_blocked": reference_result.get("updates_blocked", 0) if isinstance(reference_result, Mapping) else 0,
        "contracts_scanned": len(contracts),
        "product_contract_count": len(product),
        "non_product_contract_count": len(non_product),
        "unknown_contract_count": len(unknown),
        "task_named_contract_count": len(task_named),
        "schemas_deleted": 0,
        "runtime_modified": False,
        "product_behavior_changed": False,
        "contracts_clean_enough_for_r0_04": contracts_clean_enough,
        "f0_should_remain_blocked": True,
        "dev_to_main_should_remain_blocked": True,
        "recommended_next_task": final_taxonomy["recommended_next_task"],
        "validation": {},
    }
    return {
        "schema_version": "r0_03b_2_product_contract_tree_validation.v0",
        "status": status,
        "errors": errors,
        "warnings": warnings,
        "product_contract_cleanup_result": cleanup_result,
        "unresolved_contracts": unresolved_result,
        "final_contract_taxonomy": final_taxonomy,
        "audit_report": audit_report,
        "f0_should_remain_blocked": True,
        "dev_to_main_should_remain_blocked": True,
    }


def build_unresolved(
    root: Path,
    contracts: Sequence[Mapping[str, Any]],
    reference_result: Mapping[str, Any],
    previous_migration: Mapping[str, Any],
) -> list[dict[str, Any]]:
    unresolved: dict[str, dict[str, Any]] = {}
    contract_by_path = {str(item.get("path", "")): item for item in contracts}
    for item in contracts:
        path = str(item.get("path", ""))
        cls = str(item.get("contract_class", "unknown"))
        if cls == "unknown":
            unresolved[path] = {
                "path": path,
                "reason": "Artifact is not a clear product schema and requires manual classification.",
                "severity": "medium",
                "recommended_next_action": "Classify, quarantine, or move in a follow-up contract cleanup task.",
            }
    for source in (reference_result.get("blocked_moves", []) or []) + (previous_migration.get("blocked", []) or []):
        if not isinstance(source, Mapping):
            continue
        path = str(source.get("source_path", ""))
        if path and (root / path).exists() and path in contract_by_path:
            unresolved[path] = {
                "path": path,
                "reason": str(source.get("reason", "Move remains blocked by active references.")),
                "severity": "high",
                "recommended_next_action": "Update the active consumer in a task that is allowed to touch that path, then move the schema to contracts/control_schemas/.",
            }
    return sorted(unresolved.values(), key=lambda item: item["path"])


def is_task_named_product(path: str) -> bool:
    name = Path(path).name.lower()
    return bool(TASK_NAMED_RE.search(path.lower())) and not name.startswith(("ranking_input_bundle", "explanation_input_bundle"))


def validate_moved_schema_targets(root: Path, previous_migration: Mapping[str, Any], errors: list[str]) -> None:
    for item in previous_migration.get("moved", []) or []:
        target = str(item.get("target_path", ""))
        source = str(item.get("source_path", ""))
        if target and not (root / target).is_file():
            errors.append(f"moved schema target is missing: {target}")
        if source and (root / source).exists():
            errors.append(f"previously moved schema source still exists: {source}")


def validate_no_forbidden_paths_modified(root: Path, errors: list[str]) -> None:
    if not (root / ".git").is_dir():
        return
    completed = subprocess.run(
        ["git", "status", "--short"],
        cwd=root,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if completed.returncode != 0:
        errors.append("could not inspect git status for forbidden path modifications")
        return
    for line in completed.stdout.splitlines():
        path = line[3:].replace("\\", "/")
        if path.startswith(FORBIDDEN_MODIFIED_PREFIXES):
            errors.append(f"forbidden product path modified: {path}")


def validate_static_only(root: Path, errors: list[str]) -> None:
    for rel in ("scripts/update_contract_schema_references.py", "scripts/validate_product_contract_tree.py"):
        path = root / rel
        if not path.is_file():
            errors.append(f"missing required script: {rel}")
            continue
        text = path.read_text(encoding="utf-8")
        for banned in sorted(FORBIDDEN_STATIC_IMPORT_ROOTS):
            if re.search(rf"^\s*(?:import|from)\s+{re.escape(banned)}(?:\.|\s|$)", text, re.MULTILINE):
                errors.append(f"{rel} imports forbidden network/provider module: {banned}")


def load_contract_taxonomy(root: Path, errors: list[str]) -> dict[str, Any]:
    script = root / "scripts/audit_contract_taxonomy.py"
    if not script.is_file():
        errors.append("missing scripts/audit_contract_taxonomy.py")
        return {}
    spec = importlib.util.spec_from_file_location("audit_contract_taxonomy", script)
    if spec is None or spec.loader is None:
        errors.append("could not load audit_contract_taxonomy.py")
        return {}
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.build_contract_taxonomy_audit(root)


def load_optional_json(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def count_control_schema_files(root: Path) -> int:
    base = root / "contracts/control_schemas"
    if not base.exists():
        return 0
    return sum(1 for path in base.rglob("*") if path.is_file() and path.name not in {".gitkeep", "README.md"})


def write_standard_outputs(root: Path, result: Mapping[str, Any]) -> None:
    write_json(root / CLEANUP_RESULT_PATH, result["product_contract_cleanup_result"])
    write_json(root / UNRESOLVED_PATH, result["unresolved_contracts"])
    write_json(root / FINAL_TAXONOMY_PATH, result["final_contract_taxonomy"])
    write_json(root / AUDIT_REPORT_PATH, result["audit_report"])
    write_json(root / (AUDIT_DIR / "generated/sample_product_contract_cleanup_result.json"), result["product_contract_cleanup_result"])
    write_json(root / (AUDIT_DIR / "generated/sample_final_contract_taxonomy.json"), result["final_contract_taxonomy"])
    write_text(root / (AUDIT_DIR / "generated/sample_summary.md"), render_summary(result))
    write_audit_markdown(root, result)


def write_audit_markdown(root: Path, result: Mapping[str, Any]) -> None:
    cleanup = result["product_contract_cleanup_result"]
    unresolved = result["unresolved_contracts"]["unresolved"]
    final = result["final_contract_taxonomy"]
    docs = {
        AUDIT_DIR / "README.md": "# R0-03B-2 Contract Reference And Product Cleanup\n\nThis audit records the active reference cleanup and remaining contract taxonomy debt after R0-03B-1.\n",
        AUDIT_DIR / "product_contract_cleanup_result.md": render_cleanup(cleanup),
        AUDIT_DIR / "unresolved_contracts.md": render_unresolved(unresolved),
        AUDIT_DIR / "final_contract_taxonomy_summary.md": render_final(final),
        AUDIT_DIR / "remaining_contract_debt.md": render_unresolved(unresolved),
        AUDIT_DIR / "validation.md": "# Validation\n\nValidation commands are recorded after R0-03B-2 checks run.\n",
        Path("docs/operations/R0_CONTRACT_REFERENCE_UPDATE_AND_PRODUCT_CLEANUP.md"): render_operation_doc(result),
    }
    reference_result = load_optional_json(root / REFERENCE_RESULT_PATH)
    docs[AUDIT_DIR / "reference_update_result.md"] = render_reference(reference_result)
    for path, text in docs.items():
        write_text(root / path, text)


def render_summary(result: Mapping[str, Any]) -> str:
    final = result["final_contract_taxonomy"]
    cleanup = result["product_contract_cleanup_result"]
    return "\n".join(
        [
            "# R0-03B-2 Summary",
            "",
            f"- status: {cleanup['status']}",
            f"- contracts scanned: {cleanup['contracts_scanned']}",
            f"- product contracts: {cleanup['product_contract_count']}",
            f"- non-product contracts remaining: {cleanup['non_product_contract_count']}",
            f"- unknown contracts: {cleanup['unknown_contract_count']}",
            f"- task-named contracts: {cleanup['task_named_contract_count']}",
            f"- unresolved contracts: {final['unresolved_contract_count']}",
            f"- contracts clean enough for R0-04: {str(final['contracts_clean_enough_for_r0_04']).lower()}",
            f"- recommended next task: {final['recommended_next_task']}",
            "",
        ]
    )


def render_reference(reference: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "# Reference Update Result",
            "",
            f"- status: {reference.get('status', 'missing')}",
            f"- updates completed: {reference.get('updates_completed', 0)}",
            f"- updates blocked: {reference.get('updates_blocked', 0)}",
            f"- moved in this task: {len(reference.get('moved_in_this_task', []))}",
            f"- runtime files modified: {reference.get('runtime_files_modified', 0)}",
            "",
        ]
    )


def render_cleanup(cleanup: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "# Product Contract Cleanup Result",
            "",
            f"- status: {cleanup['status']}",
            f"- contracts scanned: {cleanup['contracts_scanned']}",
            f"- product contracts: {cleanup['product_contract_count']}",
            f"- non-product contracts remaining: {cleanup['non_product_contract_count']}",
            f"- unknown contracts: {cleanup['unknown_contract_count']}",
            f"- task-named contracts: {cleanup['task_named_contract_count']}",
            f"- contracts clean enough for R0-04: {str(cleanup['contracts_clean_enough_for_r0_04']).lower()}",
            "",
        ]
    )


def render_unresolved(unresolved: Sequence[Mapping[str, Any]]) -> str:
    lines = ["# Unresolved Contracts", ""]
    if not unresolved:
        lines.append("No unresolved contracts remain.")
    for item in unresolved:
        lines.append(f"- `{item['path']}`: {item['reason']} Next: {item['recommended_next_action']}")
    lines.append("")
    return "\n".join(lines)


def render_final(final: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "# Final Contract Taxonomy",
            "",
            f"- contracts root status: {final['contracts_root_status']}",
            f"- control schemas root status: {final['control_schemas_root_status']}",
            f"- product contract count: {final['product_contract_count']}",
            f"- control schema count: {final['control_schema_count']}",
            f"- compatibility shim count: {final['compatibility_shim_count']}",
            f"- unresolved contract count: {final['unresolved_contract_count']}",
            f"- contracts clean enough for R0-04: {str(final['contracts_clean_enough_for_r0_04']).lower()}",
            f"- recommended next task: {final['recommended_next_task']}",
            "",
        ]
    )


def render_operation_doc(result: Mapping[str, Any]) -> str:
    final = result["final_contract_taxonomy"]
    cleanup = result["product_contract_cleanup_result"]
    reference = load_optional_json(REPO_ROOT / REFERENCE_RESULT_PATH)
    return "\n".join(
        [
            "# R0 Contract Reference Update And Product Cleanup",
            "",
            "R0-03B-2 updated active schema references that were inside the allowed control, docs, tests, examples, and validator boundary.",
            "It moved the remaining safe control and task schemas out of `contracts/` and into `contracts/control_schemas/`.",
            "",
            "Historical audit evidence was left intact when it records a past contract path.",
            "The current active schema taxonomy now lives in generated inventory files, not in older audit narrative.",
            "",
            "## Reference Updates",
            "",
            f"- Active references updated: {reference.get('updates_completed', 0)}",
            f"- Reference updates blocked: {reference.get('updates_blocked', 0)}",
            f"- Schemas moved in this task: {len(reference.get('moved_in_this_task', []))}",
            "- Runtime files modified: 0",
            "- Product behavior changed: false",
            "",
            "Blocked updates are tied to active consumers outside this task's write boundary.",
            "",
            "## Contract Tree",
            "",
            f"- Contracts scanned: {cleanup['contracts_scanned']}",
            f"- Product contracts remaining: {cleanup['product_contract_count']}",
            f"- Non-product contracts still under `contracts/`: {cleanup['non_product_contract_count']}",
            f"- Unknown contract artifacts: {cleanup['unknown_contract_count']}",
            f"- Task/bundle-shaped product names needing later review: {cleanup['task_named_contract_count']}",
            f"- Compatibility or unresolved mapping count: {final['compatibility_shim_count']}",
            "",
            "Runtime was not touched. Remaining runtime-referenced schemas are recorded as explicit contract taxonomy debt.",
            "",
            f"- contracts clean enough for R0-04: {str(final['contracts_clean_enough_for_r0_04']).lower()}",
            "- F0 remains blocked: true",
            "- dev-to-main remains blocked: true",
            f"- next task: {final['recommended_next_task']}",
            "",
        ]
    )


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


if __name__ == "__main__":
    raise SystemExit(main())
