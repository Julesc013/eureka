#!/usr/bin/env python3
"""Validate the R0-02 runtime architecture leakage gate offline."""

from __future__ import annotations

import argparse
import ast
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
AUDIT_DIR = Path("control/audits/r0-02-runtime-architecture-leakage-gate-v0")
POLICY_PATH = Path("control/policies/runtime_architecture_leakage_policy.json")
ALLOWLIST_PATH = Path("control/policies/runtime_architecture_leakage_allowlist.json")
AUDIT_SCRIPT = Path("scripts/audit_runtime_architecture_leakage.py")

REQUIRED_JSON = {
    POLICY_PATH.as_posix(): "runtime_architecture_leakage_policy.v0",
    ALLOWLIST_PATH.as_posix(): "runtime_architecture_leakage_allowlist.v0",
    "control/inventory/runtime_architecture_leakage_gate_report.json": "runtime_architecture_leakage_gate_report.v0",
    "control/inventory/runtime_architecture_leakage_blockers.json": "runtime_architecture_leakage_blockers.v0",
    "control/inventory/runtime_architecture_leakage_remediation_plan.json": "runtime_architecture_leakage_remediation_plan.v0",
    f"{AUDIT_DIR.as_posix()}/r0_02_report.json": "r0_02_report.v0",
    f"{AUDIT_DIR.as_posix()}/generated/sample_leakage_gate_report.json": "runtime_architecture_leakage_gate_report.v0",
}

REQUIRED_MARKDOWN = (
    "docs/architecture/RUNTIME_NAMING_BOUNDARY.md",
    "docs/operations/R0_RUNTIME_LEAKAGE_GATE.md",
    f"{AUDIT_DIR.as_posix()}/README.md",
    f"{AUDIT_DIR.as_posix()}/leakage_policy_summary.md",
    f"{AUDIT_DIR.as_posix()}/allowlist_summary.md",
    f"{AUDIT_DIR.as_posix()}/production_path_scan_summary.md",
    f"{AUDIT_DIR.as_posix()}/known_violations.md",
    f"{AUDIT_DIR.as_posix()}/remediation_plan.md",
    f"{AUDIT_DIR.as_posix()}/validation.md",
    f"{AUDIT_DIR.as_posix()}/generated/sample_leakage_summary.md",
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

PRODUCT_PREFIXES = (
    "runtime/",
    "contracts/",
    "surfaces/",
    "site/",
    "native/",
    "crates/",
    "examples/",
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    result = validate_repo(Path(args.repo_root).resolve())
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print("R0-02 runtime architecture leakage validation", file=stdout)
        print(f"status: {result['status']}", file=stdout)
        print(f"error_count: {len(result['errors'])}", file=stdout)
        for error in result["errors"]:
            print(f"ERROR: {error}", file=stdout)
    return 0 if result["status"] == "valid" else 1


def validate_repo(root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    payloads = {rel: load_json(root / rel, schema, errors) for rel, schema in REQUIRED_JSON.items()}
    validate_required_markdown(root, errors)
    validate_policy(payloads.get(POLICY_PATH.as_posix(), {}), errors)
    validate_allowlist(payloads.get(ALLOWLIST_PATH.as_posix(), {}), errors)
    validate_gate_report(payloads.get("control/inventory/runtime_architecture_leakage_gate_report.json", {}), errors)
    validate_blockers(payloads.get("control/inventory/runtime_architecture_leakage_blockers.json", {}), errors)
    validate_remediation(payloads.get("control/inventory/runtime_architecture_leakage_remediation_plan.json", {}), errors)
    validate_r0_report(payloads.get(f"{AUDIT_DIR.as_posix()}/r0_02_report.json", {}), errors)
    validate_scripts_static_only(root, errors)
    validate_audit_check_mode(root, errors)
    validate_no_product_paths_modified(root, errors)
    return {
        "schema_version": "r0_02_validation.v0",
        "status": "valid" if not errors else "invalid",
        "task": "R0-02",
        "network_calls_made": False,
        "model_provider_calls_made": False,
        "runtime_modules_imported": False,
        "source_cache_runtime_mutated": False,
        "evidence_ledger_runtime_mutated": False,
        "review_queue_runtime_mutated": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "f0_should_remain_blocked": True,
        "dev_to_main_should_remain_blocked": True,
        "recommended_next_task": "R0-03 — Contract taxonomy refactor",
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


def validate_required_markdown(root: Path, errors: list[str]) -> None:
    for rel in REQUIRED_MARKDOWN:
        path = root / rel
        if not path.is_file():
            errors.append(f"missing markdown output: {rel}")
            continue
        if path.stat().st_size == 0:
            errors.append(f"empty markdown output: {rel}")


def validate_policy(policy: Mapping[str, Any], errors: list[str]) -> None:
    if policy.get("status") != "active":
        errors.append("policy must be active")
    if policy.get("enforcement_mode") != "report_then_block_new":
        errors.append("policy enforcement_mode must be report_then_block_new")
    for required in ("runtime/**", "surfaces/**", "site/**", "native/**", "crates/**", "contracts/domain/**", "contracts/runtime/**", "contracts/api/**", "contracts/snapshot/**", "contracts/native/**"):
        if required not in policy.get("production_paths", []):
            errors.append(f"policy production_paths missing {required}")
    for required in ("H1", "H14", "BUNDLE", "AIDE", "prompt", "agent", "fixture_only", "preview_only", "truth_boundary", "product_boundary", "review_seed"):
        if required not in policy.get("forbidden_terms", []):
            errors.append(f"policy forbidden_terms missing {required}")


def validate_allowlist(allowlist: Mapping[str, Any], errors: list[str]) -> None:
    entries = allowlist.get("entries")
    if not isinstance(entries, list):
        errors.append("allowlist entries must be a list")
        return
    required = {"path", "term", "reason", "expires_after_task", "owner", "replacement", "severity_after_expiry"}
    for index, entry in enumerate(entries[:25]):
        if not isinstance(entry, Mapping):
            errors.append(f"allowlist entry {index} must be an object")
            continue
        missing = required - set(entry)
        if missing:
            errors.append(f"allowlist entry {index} missing fields: {sorted(missing)}")
        if entry.get("expires_after_task") == "never":
            errors.append(f"allowlist entry {index} must not silently bless leaks forever")


def validate_gate_report(report: Mapping[str, Any], errors: list[str]) -> None:
    if report.get("f0_should_remain_blocked") is not True:
        errors.append("gate report must keep F0 blocked")
    if report.get("dev_to_main_should_remain_blocked") is not True:
        errors.append("gate report must keep dev-to-main blocked")
    if report.get("recommended_next_task") not in {"R0-03 — Contract taxonomy refactor", "R0-04 — Source observation production seam"}:
        errors.append("gate report must recommend R0-03 or R0-04")
    if report.get("new_violation_count") != 0:
        errors.append("current repo gate report must have no unallowlisted new violations")


def validate_blockers(payload: Mapping[str, Any], errors: list[str]) -> None:
    blockers = payload.get("blockers")
    if not isinstance(blockers, list):
        errors.append("blockers output must contain blockers list")


def validate_remediation(payload: Mapping[str, Any], errors: list[str]) -> None:
    sequence = payload.get("recommended_sequence")
    if not isinstance(sequence, list) or not sequence:
        errors.append("remediation plan must contain recommended_sequence")
    if "R0-03 — Contract taxonomy refactor" not in sequence:
        errors.append("remediation plan must include R0-03")


def validate_r0_report(report: Mapping[str, Any], errors: list[str]) -> None:
    required_true = {
        "policy_added",
        "allowlist_added",
        "audit_script_added",
        "validator_added",
        "tests_added",
        "docs_added",
        "f0_should_remain_blocked",
        "dev_to_main_should_remain_blocked",
    }
    for key in required_true:
        if report.get(key) is not True:
            errors.append(f"R0 report must set {key}=true")
    if report.get("production_paths_modified") is not False:
        errors.append("R0 report must record production_paths_modified=false")
    if report.get("runtime_refactor_performed") is not False:
        errors.append("R0 report must record runtime_refactor_performed=false")
    if report.get("contract_moves_performed") is not False:
        errors.append("R0 report must record contract_moves_performed=false")
    if report.get("recommended_next_task") != "R0-03 — Contract taxonomy refactor":
        errors.append("R0 report must recommend R0-03")


def validate_scripts_static_only(root: Path, errors: list[str]) -> None:
    for rel in (AUDIT_SCRIPT, Path("scripts/validate_runtime_architecture_leakage.py")):
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
                    root_name = alias.name.split(".")[0]
                    if root_name in BANNED_IMPORT_ROOTS:
                        errors.append(f"{rel.as_posix()} imports forbidden module {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                root_name = (node.module or "").split(".")[0]
                if root_name in BANNED_IMPORT_ROOTS:
                    errors.append(f"{rel.as_posix()} imports forbidden module {node.module}")
    audit_text = (root / AUDIT_SCRIPT).read_text(encoding="utf-8")
    for marker in ("url" + "open(", "requests" + ".", "httpx" + ".", "openai" + ".", "anthropic" + "."):
        if marker in audit_text:
            errors.append(f"audit script contains forbidden call marker {marker}")


def validate_audit_check_mode(root: Path, errors: list[str]) -> None:
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
    if payload.get("summary", {}).get("new_violation_count") != 0:
        errors.append("audit script check mode found unallowlisted violations")
    if payload.get("runtime_modules_imported") is not False:
        errors.append("audit script must not import runtime modules")


def validate_no_product_paths_modified(root: Path, errors: list[str]) -> None:
    if not (root / ".git").exists():
        return
    queue_text = (root / ".aide/queue/index.yaml").read_text(encoding="utf-8") if (root / ".aide/queue/index.yaml").is_file() else ""
    if "current_recommended_task: R0-02" not in queue_text:
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
        if normalized.startswith(PRODUCT_PREFIXES):
            errors.append(f"R0-02 modified forbidden product path: {normalized}")


if __name__ == "__main__":
    raise SystemExit(main())
