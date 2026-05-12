#!/usr/bin/env python3
"""Validate the R0-03A contract taxonomy refactor plan offline."""

from __future__ import annotations

import argparse
import ast
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
AUDIT_DIR = Path("control/audits/r0-03a-contract-taxonomy-refactor-plan-v0")
AUDIT_SCRIPT = Path("scripts/audit_contract_taxonomy.py")

REQUIRED_JSON = {
    "control/policies/contract_taxonomy_policy.json": "contract_taxonomy_policy.v0",
    "control/policies/contract_migration_policy.json": "contract_migration_policy.v0",
    "control/inventory/contract_taxonomy_inventory.json": "contract_taxonomy_inventory.v0",
    "control/inventory/contract_migration_plan.json": "contract_migration_plan.v0",
    "control/inventory/contract_reference_graph.json": "contract_reference_graph.v0",
    "control/inventory/contract_risk_register.json": "contract_risk_register.v0",
    "control/inventory/r0_03b_execution_plan.json": "r0_03b_execution_plan.v0",
    f"{AUDIT_DIR.as_posix()}/r0_03a_report.json": "r0_03a_report.v0",
    f"{AUDIT_DIR.as_posix()}/generated/sample_contract_taxonomy_inventory.json": "contract_taxonomy_inventory.v0",
    f"{AUDIT_DIR.as_posix()}/generated/sample_contract_migration_plan.json": "contract_migration_plan.v0",
    f"{AUDIT_DIR.as_posix()}/generated/sample_contract_reference_graph.json": "contract_reference_graph.v0",
}

REQUIRED_MARKDOWN = (
    "docs/architecture/CONTRACT_TAXONOMY.md",
    "docs/operations/R0_CONTRACT_TAXONOMY_REFACTOR_PLAN.md",
    f"{AUDIT_DIR.as_posix()}/README.md",
    f"{AUDIT_DIR.as_posix()}/contract_taxonomy_summary.md",
    f"{AUDIT_DIR.as_posix()}/product_contract_summary.md",
    f"{AUDIT_DIR.as_posix()}/control_schema_summary.md",
    f"{AUDIT_DIR.as_posix()}/fixture_schema_summary.md",
    f"{AUDIT_DIR.as_posix()}/audit_schema_summary.md",
    f"{AUDIT_DIR.as_posix()}/preview_schema_summary.md",
    f"{AUDIT_DIR.as_posix()}/migration_plan_summary.md",
    f"{AUDIT_DIR.as_posix()}/reference_graph_summary.md",
    f"{AUDIT_DIR.as_posix()}/risk_register.md",
    f"{AUDIT_DIR.as_posix()}/r0_03b_execution_plan.md",
    f"{AUDIT_DIR.as_posix()}/validation.md",
    f"{AUDIT_DIR.as_posix()}/generated/sample_summary.md",
)

BANNED_IMPORT_ROOTS = {
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
    "runtime",
}

FORBIDDEN_MODIFIED_PREFIXES = (
    "contracts/",
    "runtime/",
    "surfaces/",
    "site/",
    "native/",
    "crates/",
    "examples/",
)

REQUIRED_CLASSES = {
    "product_domain_contract",
    "product_runtime_contract",
    "public_api_contract",
    "snapshot_contract",
    "native_contract",
    "durable_store_contract",
    "connector_interface_contract",
    "source_policy_contract",
    "control_schema",
    "audit_schema",
    "fixture_schema",
    "preview_schema",
    "validator_schema",
    "task_queue_schema",
    "generated_scaffold_schema",
    "deprecated_schema",
    "unknown",
}


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    result = validate_repo(Path(args.repo_root).resolve())
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print("R0-03A contract taxonomy validation", file=stdout)
        print(f"status: {result['status']}", file=stdout)
        print(f"error_count: {len(result['errors'])}", file=stdout)
        for error in result["errors"]:
            print(f"ERROR: {error}", file=stdout)
    return 0 if result["status"] == "valid" else 1


def validate_repo(root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    payloads = {rel: load_json(root / rel, schema, errors) for rel, schema in REQUIRED_JSON.items()}
    validate_markdown(root, errors)
    validate_taxonomy_policy(payloads.get("control/policies/contract_taxonomy_policy.json", {}), errors)
    validate_migration_policy(payloads.get("control/policies/contract_migration_policy.json", {}), errors)
    validate_inventory(payloads.get("control/inventory/contract_taxonomy_inventory.json", {}), root, errors)
    validate_migration_plan(payloads.get("control/inventory/contract_migration_plan.json", {}), errors)
    validate_reference_graph(payloads.get("control/inventory/contract_reference_graph.json", {}), errors)
    validate_risk_register(payloads.get("control/inventory/contract_risk_register.json", {}), errors)
    validate_execution_plan(payloads.get("control/inventory/r0_03b_execution_plan.json", {}), errors)
    validate_report(payloads.get(f"{AUDIT_DIR.as_posix()}/r0_03a_report.json", {}), errors)
    validate_static_only(root, errors)
    validate_audit_check(root, errors)
    validate_no_forbidden_paths_modified(root, errors)
    return {
        "schema_version": "r0_03a_validation.v0",
        "status": "valid" if not errors else "invalid",
        "task": "R0-03A",
        "planning_only": True,
        "contracts_moved": False,
        "runtime_modified": False,
        "network_calls_made": False,
        "model_provider_calls_made": False,
        "f0_should_remain_blocked": True,
        "dev_to_main_should_remain_blocked": True,
        "recommended_next_task": "R0-03B — Contract taxonomy refactor execution",
        "errors": errors,
    }


def load_json(path: Path, schema: str, errors: list[str]) -> dict[str, Any]:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"missing JSON output: {path.as_posix()}")
        return {}
    except json.JSONDecodeError as exc:
        errors.append(f"malformed JSON output {path.as_posix()}: {exc}")
        return {}
    if payload.get("schema_version") != schema:
        errors.append(f"{path.as_posix()} schema_version must be {schema}")
    return payload


def validate_markdown(root: Path, errors: list[str]) -> None:
    for rel in REQUIRED_MARKDOWN:
        path = root / rel
        if not path.is_file():
            errors.append(f"missing markdown output: {rel}")
        elif path.stat().st_size == 0:
            errors.append(f"empty markdown output: {rel}")


def validate_taxonomy_policy(policy: Mapping[str, Any], errors: list[str]) -> None:
    if policy.get("status") != "active":
        errors.append("taxonomy policy must be active")
    classes = set(policy.get("contract_classes", []))
    missing = REQUIRED_CLASSES - classes
    if missing:
        errors.append(f"taxonomy policy missing classes: {sorted(missing)}")
    target_roots = policy.get("target_roots", {})
    for required in ("contracts/domain/", "contracts/runtime/", "contracts/api/", "contracts/snapshot/", "contracts/native/", "contracts/stores/", "contracts/connectors/", "control/schemas/audits/", "control/schemas/fixtures/", "control/schemas/previews/", "control/schemas/policies/", "control/schemas/validators/", "control/schemas/tasks/", "control/schemas/deprecated/"):
        if required not in set(target_roots.values()):
            errors.append(f"taxonomy policy target roots missing {required}")
    for required in ("h14", "bundle", "quality_delta", "next_phase", "truth_boundary", "product_boundary"):
        if required not in policy.get("forbidden_product_contract_signals", []):
            errors.append(f"taxonomy policy forbidden signals missing {required}")


def validate_migration_policy(policy: Mapping[str, Any], errors: list[str]) -> None:
    required_values = {
        "migration_allowed_current": False,
        "planning_only_current": True,
        "r0_03b_may_move_contracts_after_plan": True,
        "runtime_changes_allowed_current": False,
        "compatibility_shims_required": True,
        "import_update_required": True,
        "validation_required_after_move": True,
        "deletion_allowed_current": False,
        "quarantine_before_delete": True,
        "dev_to_main_blocked_until_complete": True,
        "f0_blocked_until_complete": True,
    }
    for key, expected in required_values.items():
        if policy.get(key) is not expected:
            errors.append(f"migration policy {key} must be {expected}")


def validate_inventory(inventory: Mapping[str, Any], root: Path, errors: list[str]) -> None:
    contracts = inventory.get("contracts")
    if not isinstance(contracts, list) or not contracts:
        errors.append("inventory must contain contracts")
        return
    expected = sorted(path.relative_to(root).as_posix() for path in (root / "contracts").rglob("*") if path.is_file())
    actual = sorted(str(item.get("path")) for item in contracts if isinstance(item, Mapping))
    if actual != expected:
        missing = sorted(set(expected) - set(actual))[:10]
        extra = sorted(set(actual) - set(expected))[:10]
        errors.append(f"inventory must classify every contract-like file; missing={missing} extra={extra}")
    if inventory.get("contract_count") != len(contracts):
        errors.append("inventory contract_count must equal contracts list length")
    required_fields = {"path", "current_root", "contract_class", "maturity", "target_root", "target_path", "recommended_action", "signals", "references", "risks", "notes"}
    for item in contracts[:50]:
        missing = required_fields - set(item)
        if missing:
            errors.append(f"inventory entry {item.get('path')} missing fields {sorted(missing)}")
        if item.get("contract_class") not in REQUIRED_CLASSES:
            errors.append(f"inventory entry {item.get('path')} has invalid class {item.get('contract_class')}")


def validate_migration_plan(plan: Mapping[str, Any], errors: list[str]) -> None:
    if plan.get("migration_allowed_now") is not False:
        errors.append("migration plan must keep migration_allowed_now=false")
    if plan.get("r0_03b_ready") is not True:
        errors.append("migration plan must be ready for R0-03B")
    required_fields = {"source_path", "target_path", "action", "contract_class_before", "contract_class_after", "rationale", "references_to_update", "compatibility_shim_required", "risk", "validation"}
    for move in plan.get("moves", [])[:100]:
        missing = required_fields - set(move)
        if missing:
            errors.append(f"move {move.get('source_path')} missing fields {sorted(missing)}")
        if move.get("risk") not in {"blocker", "high", "medium", "low"}:
            errors.append(f"move {move.get('source_path')} has invalid risk {move.get('risk')}")
        if not isinstance(move.get("references_to_update"), list):
            errors.append(f"move {move.get('source_path')} references_to_update must be list")


def validate_reference_graph(graph: Mapping[str, Any], errors: list[str]) -> None:
    if not isinstance(graph.get("nodes"), list):
        errors.append("reference graph nodes must be a list")
    if not isinstance(graph.get("edges"), list):
        errors.append("reference graph edges must be a list")
        return
    for edge in graph.get("edges", [])[:100]:
        if not {"from_path", "to_path", "edge_kind"} <= set(edge):
            errors.append("reference graph edges must contain from_path, to_path, edge_kind")
        if edge.get("edge_kind") not in {"references", "validates", "example_of", "imports", "documents", "unknown"}:
            errors.append(f"invalid reference edge kind {edge.get('edge_kind')}")


def validate_risk_register(register: Mapping[str, Any], errors: list[str]) -> None:
    risks = register.get("risks")
    if not isinstance(risks, list):
        errors.append("risk register risks must be a list")
        return
    for risk in risks[:50]:
        if not {"risk_id", "severity", "path", "finding", "impact", "recommended_fix", "blocks"} <= set(risk):
            errors.append(f"risk entry {risk.get('risk_id')} missing required fields")


def validate_execution_plan(plan: Mapping[str, Any], errors: list[str]) -> None:
    if plan.get("ready") is not True:
        errors.append("R0-03B execution plan must be ready")
    if plan.get("recommended_next_task") != "R0-03B — Contract taxonomy refactor execution":
        errors.append("R0-03B execution plan must recommend R0-03B")
    if plan.get("f0_should_remain_blocked") is not True:
        errors.append("R0-03B execution plan must keep F0 blocked")
    if plan.get("dev_to_main_should_remain_blocked") is not True:
        errors.append("R0-03B execution plan must keep dev-to-main blocked")
    if not isinstance(plan.get("execution_batches"), list) or not plan.get("execution_batches"):
        errors.append("R0-03B execution plan must define execution batches")


def validate_report(report: Mapping[str, Any], errors: list[str]) -> None:
    if report.get("planning_only") is not True:
        errors.append("R0 report must be planning_only")
    if report.get("contracts_moved") is not False:
        errors.append("R0 report must record contracts_moved=false")
    if report.get("runtime_modified") is not False:
        errors.append("R0 report must record runtime_modified=false")
    if report.get("f0_should_remain_blocked") is not True:
        errors.append("R0 report must keep F0 blocked")
    if report.get("dev_to_main_should_remain_blocked") is not True:
        errors.append("R0 report must keep dev-to-main blocked")
    if report.get("recommended_next_task") != "R0-03B — Contract taxonomy refactor execution":
        errors.append("R0 report must recommend R0-03B")


def validate_static_only(root: Path, errors: list[str]) -> None:
    for rel in (AUDIT_SCRIPT, Path("scripts/validate_contract_taxonomy_plan.py")):
        path = root / rel
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except OSError as exc:
            errors.append(f"cannot read {rel.as_posix()}: {exc}")
            continue
        except SyntaxError as exc:
            errors.append(f"cannot parse {rel.as_posix()}: {exc}")
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.split(".")[0] in BANNED_IMPORT_ROOTS:
                        errors.append(f"{rel.as_posix()} imports forbidden module {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                root_name = (node.module or "").split(".")[0]
                if root_name in BANNED_IMPORT_ROOTS:
                    errors.append(f"{rel.as_posix()} imports forbidden module {node.module}")


def validate_audit_check(root: Path, errors: list[str]) -> None:
    proc = subprocess.run(
        [sys.executable, str(root / AUDIT_SCRIPT), "--repo-root", str(root), "--check", "--json"],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if proc.returncode != 0:
        errors.append(f"audit script check mode failed: {proc.stdout} {proc.stderr}".strip())
        return
    try:
        payload = json.loads(proc.stdout)
    except json.JSONDecodeError as exc:
        errors.append(f"audit script check mode did not return JSON: {exc}")
        return
    if payload.get("contracts_moved") is not False:
        errors.append("audit script must not move contracts")
    if payload.get("runtime_modified") is not False:
        errors.append("audit script must not modify runtime")


def validate_no_forbidden_paths_modified(root: Path, errors: list[str]) -> None:
    if not (root / ".git").exists():
        return
    proc = subprocess.run(["git", "status", "--short"], cwd=root, text=True, capture_output=True, check=False)
    if proc.returncode != 0:
        errors.append(f"git status failed: {proc.stderr.strip()}")
        return
    for line in proc.stdout.splitlines():
        if not line.strip():
            continue
        path = line[3:].strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1].strip()
        normalized = path.replace("\\", "/")
        if normalized.startswith(FORBIDDEN_MODIFIED_PREFIXES):
            errors.append(f"R0-03A modified forbidden path: {normalized}")


if __name__ == "__main__":
    raise SystemExit(main())
