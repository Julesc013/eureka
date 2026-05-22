#!/usr/bin/env python3
"""Validate the R0-01 production reality inventory outputs offline."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
AUDIT_DIR = Path("control/audits/r0-01-dev-production-reality-inventory-v0")

REQUIRED_JSON = {
    "control/inventory/artifact_taxonomy.json": "r0.artifact_taxonomy.v0",
    "control/inventory/runtime_maturity_matrix.json": "r0.runtime_maturity_matrix.v0",
    "control/inventory/production_gap_register.json": "r0.production_gap_register.v0",
    "control/inventory/scaffold_to_runtime_map.json": "r0.scaffold_to_runtime_map.v0",
    "control/inventory/runtime_architecture_leakage_report.json": "r0.runtime_architecture_leakage_report.v0",
    "control/inventory/r0_next_task_decision.json": "r0.next_task_decision.v0",
    f"{AUDIT_DIR.as_posix()}/r0_01_report.json": "r0_01_report.v0",
    f"{AUDIT_DIR.as_posix()}/generated/sample_artifact_inventory.json": "r0.artifact_taxonomy.v0",
    f"{AUDIT_DIR.as_posix()}/generated/sample_runtime_maturity_matrix.json": "r0.runtime_maturity_matrix.v0",
    f"{AUDIT_DIR.as_posix()}/generated/sample_gap_register.json": "r0.production_gap_register.v0",
}

REQUIRED_MARKDOWN = (
    "docs/operations/DEV_PRODUCTION_REALITY_INVENTORY.md",
    "docs/operations/R0_PRODUCTION_RECOVERY_PLAN.md",
    f"{AUDIT_DIR.as_posix()}/README.md",
    f"{AUDIT_DIR.as_posix()}/artifact_taxonomy_summary.md",
    f"{AUDIT_DIR.as_posix()}/runtime_maturity_summary.md",
    f"{AUDIT_DIR.as_posix()}/production_gap_summary.md",
    f"{AUDIT_DIR.as_posix()}/scaffold_to_runtime_summary.md",
    f"{AUDIT_DIR.as_posix()}/architecture_leakage_summary.md",
    f"{AUDIT_DIR.as_posix()}/zero_byte_and_placeholder_summary.md",
    f"{AUDIT_DIR.as_posix()}/contract_taxonomy_summary.md",
    f"{AUDIT_DIR.as_posix()}/validator_quality_summary.md",
    f"{AUDIT_DIR.as_posix()}/recommendations.md",
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
        print("R0-01 production reality validation", file=stdout)
        print(f"status: {result['status']}", file=stdout)
        print(f"error_count: {len(result['errors'])}", file=stdout)
        for error in result["errors"]:
            print(f"ERROR: {error}", file=stdout)
    return 0 if result["status"] == "valid" else 1


def validate_repo(root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    payloads = {rel: load_json(root / rel, schema, errors) for rel, schema in REQUIRED_JSON.items()}
    validate_markdown(root, errors)
    validate_taxonomy(payloads.get("control/inventory/artifact_taxonomy.json", {}), errors)
    validate_runtime_matrix(payloads.get("control/inventory/runtime_maturity_matrix.json", {}), errors)
    validate_gap_register(payloads.get("control/inventory/production_gap_register.json", {}), errors)
    validate_leakage_report(payloads.get("control/inventory/runtime_architecture_leakage_report.json", {}), errors)
    validate_next_decision(payloads.get("control/inventory/r0_next_task_decision.json", {}), errors)
    validate_r0_report(payloads.get(f"{AUDIT_DIR.as_posix()}/r0_01_report.json", {}), errors)
    validate_audit_script_static_only(root, errors)
    return {
        "schema_version": "r0_01_validation.v0",
        "status": "valid" if not errors else "invalid",
        "task": "R0-01",
        "offline_default": True,
        "network_calls_made": False,
        "model_provider_calls_made": False,
        "source_discovery_runtime_used": False,
        "source_cache_runtime_mutated": False,
        "evidence_ledger_runtime_mutated": False,
        "review_queue_runtime_mutated": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "errors": errors,
    }


def validate_taxonomy(payload: Mapping[str, Any], errors: list[str]) -> None:
    artifacts = payload.get("artifacts")
    if not isinstance(artifacts, list) or not artifacts:
        errors.append("artifact taxonomy must contain artifacts")
        return
    if payload.get("artifact_count") != len(artifacts):
        errors.append("artifact taxonomy artifact_count must equal artifact list length")
    required_fields = {"path", "artifact_kind", "maturity", "product_role", "recommended_action", "signals", "risks", "notes"}
    for index, artifact in enumerate(artifacts[:25]):
        if not isinstance(artifact, Mapping):
            errors.append(f"artifact {index} must be an object")
            continue
        missing = required_fields - set(artifact)
        if missing:
            errors.append(f"artifact {artifact.get('path', index)} missing fields: {sorted(missing)}")
    counts = payload.get("counts", {})
    if not isinstance(counts, Mapping) or "artifact_kind" not in counts or "maturity" not in counts:
        errors.append("artifact taxonomy counts must include artifact_kind and maturity")


def validate_runtime_matrix(payload: Mapping[str, Any], errors: list[str]) -> None:
    seams = payload.get("seams")
    if not isinstance(seams, list) or not seams:
        errors.append("runtime maturity matrix must contain seams")
        return
    seam_names = {str(item.get("seam")) for item in seams if isinstance(item, Mapping)}
    for required in ("source_observation", "source_cache_durable_store", "evidence_ledger_durable_store", "review_queue", "public_index_rebuild", "live_metadata_probe"):
        if required not in seam_names:
            errors.append(f"runtime maturity matrix missing seam: {required}")
    if payload.get("summary", {}).get("f0_should_remain_blocked") is not True:
        errors.append("runtime maturity matrix must keep F0 blocked")


def validate_gap_register(payload: Mapping[str, Any], errors: list[str]) -> None:
    gaps = payload.get("gaps")
    if not isinstance(gaps, list) or not gaps:
        errors.append("production gap register must contain gaps")
        return
    if not any(item.get("severity") == "blocker" for item in gaps if isinstance(item, Mapping)):
        errors.append("production gap register must contain at least one blocker")


def validate_leakage_report(payload: Mapping[str, Any], errors: list[str]) -> None:
    leaks = payload.get("leaks")
    if not isinstance(leaks, list):
        errors.append("runtime architecture leakage report must contain leaks list")
        return
    if payload.get("summary", {}).get("next_required_task") != "R0-02 - Runtime architecture leakage gate":
        errors.append("leakage report must route to R0-02")


def validate_next_decision(payload: Mapping[str, Any], errors: list[str]) -> None:
    if payload.get("recommended_next_task") != "R0-02 - Runtime architecture leakage gate":
        errors.append("next task decision must recommend R0-02")
    if payload.get("f0_should_remain_blocked") is not True:
        errors.append("next task decision must keep F0 blocked")
    if payload.get("dev_to_main_should_remain_blocked") is not True:
        errors.append("next task decision must block dev-to-main promotion")


def validate_r0_report(payload: Mapping[str, Any], errors: list[str]) -> None:
    if payload.get("recommended_next_task") != "R0-02 - Runtime architecture leakage gate":
        errors.append("R0 report must recommend R0-02")
    if payload.get("f0_should_remain_blocked") is not True:
        errors.append("R0 report must keep F0 blocked")
    if payload.get("dev_to_main_should_remain_blocked") is not True:
        errors.append("R0 report must block dev-to-main promotion")
    if int(payload.get("artifact_count") or 0) <= 0:
        errors.append("R0 report artifact_count must be positive")


def validate_markdown(root: Path, errors: list[str]) -> None:
    for rel in REQUIRED_MARKDOWN:
        path = root / rel
        if not path.is_file():
            errors.append(f"missing markdown: {rel}")
            continue
        if not path.read_text(encoding="utf-8").strip():
            errors.append(f"empty markdown: {rel}")


def validate_audit_script_static_only(root: Path, errors: list[str]) -> None:
    script = root / "scripts/audit_dev_production_reality.py"
    if not script.is_file():
        errors.append("missing audit script")
        return
    text = script.read_text(encoding="utf-8")
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("import ") or stripped.startswith("from "):
            imported = stripped.split()[1].split(".")[0]
            if imported in BANNED_IMPORT_ROOTS:
                errors.append(f"audit script imports forbidden live/network/provider module: {imported}")
    for forbidden_call in ("urlopen(", "requests.", "openai.", "anthropic.", "playwright.", "selenium."):
        if forbidden_call in text:
            errors.append(f"audit script contains forbidden call marker: {forbidden_call}")


def load_json(path: Path, schema_version: str, errors: list[str]) -> dict[str, Any]:
    if not path.is_file():
        errors.append(f"missing JSON: {rel_display(path)}")
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        errors.append(f"invalid JSON {rel_display(path)}: {exc}")
        return {}
    if not isinstance(payload, Mapping):
        errors.append(f"JSON must be an object: {rel_display(path)}")
        return {}
    result = dict(payload)
    if result.get("schema_version") != schema_version:
        errors.append(f"{rel_display(path)} schema_version must be {schema_version}")
    return result


def rel_display(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
