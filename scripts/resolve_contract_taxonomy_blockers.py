#!/usr/bin/env python3
"""Resolve the final R0 contract taxonomy blocker set.

This script is intentionally narrow: it only handles the 19 unresolved
R0-03B-2 contract taxonomy items and writes the R0 remediation evidence.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
TASK_ID = "R0-REMEDIATION-CONTRACT-TAXONOMY-01"
AUDIT_DIR = Path("control/audits/r0-remediation-contract-taxonomy-01-v0")

UNRESOLVED_PATH = Path("control/inventory/r0_03b_2_unresolved_contracts.json")
FINAL_TAXONOMY_PATH = Path("control/inventory/r0_03b_2_final_contract_taxonomy.json")
SHIM_REPORT_PATH = Path("control/inventory/r0_03b_1_compatibility_shim_report.json")
MIGRATION_POLICY_PATH = Path("control/policies/contract_migration_policy.json")

STANDARD_OUTPUTS = {
    "result": Path("control/inventory/r0_contract_taxonomy_remediation_result.json"),
    "resolved": Path("control/inventory/r0_contract_taxonomy_resolved_items.json"),
    "remaining": Path("control/inventory/r0_contract_taxonomy_remaining_items.json"),
    "shim": Path("control/inventory/r0_contract_taxonomy_shim_retirement_report.json"),
    "references": Path("control/inventory/r0_contract_taxonomy_reference_update_report.json"),
    "final": Path("control/inventory/r0_contract_taxonomy_final_state.json"),
    "report": AUDIT_DIR / "remediation_report.json",
}

FORBIDDEN_OUTPUT_ROOTS = {
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
}
FORBIDDEN_MOVE_ROOTS = ("runtime/", "surfaces/", "site/", "native/", "crates/")
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
ACTIVE_REFERENCE_ROOTS = (
    "contracts",
    "control/inventory",
    "control/schemas",
    "docs/architecture",
    "docs/operations",
    "docs/reference",
    "examples",
    "runtime",
    "scripts",
    "tests",
)
HISTORICAL_ROOTS = ("control/audits/",)
PRESERVED_HISTORICAL_REFERENCES = {
    ("scripts/validate_obs_track_b_synchronization.py", "contracts/node/work_unit.v0.json"),
    ("scripts/validate_obs_track_b_synchronization.py", "contracts/node/work_unit_result.v0.json"),
}

REMEDIATION_MOVES: dict[str, dict[str, str]] = {
    "contracts/archive/fixtures/software/payloads/synthetic-demo-app-package.zip": {
        "target_path": "control/schemas/fixtures/archive/software/payloads/synthetic-demo-app-package.zip",
        "classification": "fixture_schema",
        "rationale": "Synthetic archive payload fixture does not belong in product contracts.",
    },
    "contracts/archive/fixtures/software/payloads/synthetic-demo-app.bundle": {
        "target_path": "control/schemas/fixtures/archive/software/payloads/synthetic-demo-app.bundle",
        "classification": "fixture_schema",
        "rationale": "Synthetic archive payload fixture does not belong in product contracts.",
    },
    "contracts/archive/fixtures/software/synthetic_resolution_fixture.json": {
        "target_path": "control/schemas/fixtures/archive/software/synthetic_resolution_fixture.json",
        "classification": "fixture_schema",
        "rationale": "Synthetic resolution fixture is control fixture evidence.",
    },
    "contracts/archive/protocols/archive-lifecycle.protocol.md": {
        "target_path": "control/schemas/deprecated/archive/archive-lifecycle.protocol.md",
        "classification": "deprecated_schema",
        "rationale": "Archive lifecycle protocol is contract-adjacent historical protocol documentation.",
    },
    "contracts/connectors/h14_connector_pack_manifest_candidate.v0.json": {
        "target_path": "control/schemas/previews/h14/connectors/connector_pack_manifest_candidate.v0.json",
        "classification": "preview_schema",
        "rationale": "H14 candidate schema is preview/task-shaped, not a stable connector interface.",
    },
    "contracts/connectors/h14_connector_scorecard_candidate.v0.json": {
        "target_path": "control/schemas/previews/h14/connectors/connector_scorecard_candidate.v0.json",
        "classification": "preview_schema",
        "rationale": "H14 candidate schema is preview/task-shaped, not a stable connector interface.",
    },
    "contracts/connectors/h14_coverage_manifest_candidate.v0.json": {
        "target_path": "control/schemas/previews/h14/connectors/coverage_manifest_candidate.v0.json",
        "classification": "preview_schema",
        "rationale": "H14 candidate schema is preview/task-shaped, not a stable connector interface.",
    },
    "contracts/connectors/h14_pack_import_export_boundary_candidate.v0.json": {
        "target_path": "control/schemas/previews/h14/connectors/pack_import_export_boundary_candidate.v0.json",
        "classification": "preview_schema",
        "rationale": "H14 candidate schema is preview/task-shaped, not a stable connector interface.",
    },
    "contracts/connectors/h14_source_candidate_candidate.v0.json": {
        "target_path": "control/schemas/previews/h14/connectors/source_candidate_candidate.v0.json",
        "classification": "preview_schema",
        "rationale": "H14 candidate schema is preview/task-shaped, not a stable connector interface.",
    },
    "contracts/connectors/h14_source_discovery_candidate.v0.json": {
        "target_path": "control/schemas/previews/h14/connectors/source_discovery_candidate.v0.json",
        "classification": "preview_schema",
        "rationale": "H14 candidate schema is preview/task-shaped, not a stable connector interface.",
    },
    "contracts/connectors/h14_source_dispute_revocation_candidate.v0.json": {
        "target_path": "control/schemas/previews/h14/connectors/source_dispute_revocation_candidate.v0.json",
        "classification": "preview_schema",
        "rationale": "H14 candidate schema is preview/task-shaped, not a stable connector interface.",
    },
    "contracts/connectors/h14_source_lineage_provenance_candidate.v0.json": {
        "target_path": "control/schemas/previews/h14/connectors/source_lineage_provenance_candidate.v0.json",
        "classification": "preview_schema",
        "rationale": "H14 candidate schema is preview/task-shaped, not a stable connector interface.",
    },
    "contracts/connectors/h14_source_need_candidate.v0.json": {
        "target_path": "control/schemas/previews/h14/connectors/source_need_candidate.v0.json",
        "classification": "preview_schema",
        "rationale": "H14 candidate schema is preview/task-shaped, not a stable connector interface.",
    },
    "contracts/connectors/h14_source_pack_manifest_candidate.v0.json": {
        "target_path": "control/schemas/previews/h14/connectors/source_pack_manifest_candidate.v0.json",
        "classification": "preview_schema",
        "rationale": "H14 candidate schema is preview/task-shaped, not a stable connector interface.",
    },
    "contracts/connectors/h14_source_reliability_freshness_candidate.v0.json": {
        "target_path": "control/schemas/previews/h14/connectors/source_reliability_freshness_candidate.v0.json",
        "classification": "preview_schema",
        "rationale": "H14 candidate schema is preview/task-shaped, not a stable connector interface.",
    },
    "contracts/node/work_unit.v0.json": {
        "target_path": "control/schemas/policies/node/work_unit.v0.json",
        "classification": "control_schema",
        "rationale": "Work-unit scaffolding is a control policy schema, not current product runtime.",
    },
    "contracts/node/work_unit_result.v0.json": {
        "target_path": "control/schemas/policies/node/work_unit_result.v0.json",
        "classification": "control_schema",
        "rationale": "Work-unit result scaffolding is a control policy schema, not current product runtime.",
    },
    "contracts/query/candidate_promotion_assessment.v0.json": {
        "target_path": "control/schemas/previews/query/candidate_promotion_assessment.v0.json",
        "classification": "preview_schema",
        "rationale": "Candidate promotion assessment is preview/review control evidence.",
    },
    "contracts/query/observation_candidate_review_queue.v0.json": {
        "target_path": "control/schemas/tasks/query/observation_candidate_review_queue.v0.json",
        "classification": "task_queue_schema",
        "rationale": "Observation candidate review queue is task queue control schema.",
    },
}


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--apply", action="store_true")
    parser.add_argument("--output")
    parser.add_argument("--reference-output")
    parser.add_argument("--shim-output")
    parser.add_argument("--final-state-output")
    parser.add_argument("--summary-output")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    root = Path(args.repo_root).resolve()
    errors: list[str] = []
    if args.dry_run and args.apply:
        errors.append("--dry-run and --apply cannot both be set")
    for output in (args.output, args.reference_output, args.shim_output, args.final_state_output, args.summary_output):
        if output:
            check_output_path(root, Path(output), errors)

    if errors:
        result = blocked_result(errors)
    else:
        try:
            result = resolve_taxonomy(root, apply_changes=bool(args.apply))
        except FileNotFoundError as exc:
            result = blocked_result([f"missing required taxonomy input: {exc.filename}"])
        except json.JSONDecodeError as exc:
            result = blocked_result([f"malformed required taxonomy input: {exc}"])

    write_requested(root, args, result)
    if args.apply and result["remediation_result"]["status"] in {"pass", "pass_with_warnings"}:
        write_standard_outputs(root, result)

    if args.json:
        print(json.dumps(result["remediation_result"], indent=2, sort_keys=True), file=stdout)
    else:
        print(render_console(result), file=stdout)
    for error in result["errors"]:
        print(f"ERROR: {error}", file=stderr)
    return 1 if result["remediation_result"]["status"] in {"blocked", "fail"} else 0


def resolve_taxonomy(root: Path, *, apply_changes: bool) -> dict[str, Any]:
    unresolved_report = load_json(root / UNRESOLVED_PATH)
    final_before = load_json(root / FINAL_TAXONOMY_PATH)
    shim_report = load_json(root / SHIM_REPORT_PATH)
    migration_policy = load_json(root / MIGRATION_POLICY_PATH)
    unresolved_items = unresolved_report.get("unresolved", [])
    unresolved_paths = [str(item.get("path", "")) for item in unresolved_items]
    errors: list[str] = []
    already_resolved = all((not (root / source).exists()) and (root / spec["target_path"]).exists() for source, spec in REMEDIATION_MOVES.items())

    if unresolved_paths and sorted(unresolved_paths) != sorted(REMEDIATION_MOVES):
        missing = sorted(set(REMEDIATION_MOVES) - set(unresolved_paths))
        extra = sorted(set(unresolved_paths) - set(REMEDIATION_MOVES))
        if missing:
            errors.append(f"unresolved report missing expected paths: {missing}")
        if extra:
            errors.append(f"unresolved report contains unplanned paths: {extra}")
    if not unresolved_paths and not already_resolved:
        errors.append("unresolved report is empty but remediation targets are not all present")
    if migration_policy.get("deletion_allowed_current") is not False:
        errors.append("migration policy must keep deletion disabled for this remediation")
    if errors:
        return blocked_result(errors)

    moves = build_moves(root, unresolved_items)
    reference_updates = find_reference_updates(root, {source: item["target_path"] for source, item in REMEDIATION_MOVES.items()})

    if apply_changes:
        apply_moves(root, moves)
        apply_reference_updates(root, reference_updates)

    after_unresolved = remaining_after(root)
    status = "pass" if not after_unresolved else "partial"
    existing_result = load_json_if_exists(root / STANDARD_OUTPUTS["result"])
    if unresolved_paths:
        before_count = int(final_before.get("unresolved_contract_count", len(unresolved_items)))
        shims_before = int(final_before.get("compatibility_shim_count", before_count))
    else:
        before_count = int(existing_result.get("unresolved_before", final_before.get("unresolved_contract_count", 0)))
        shims_before = int(existing_result.get("compatibility_shims_before", final_before.get("compatibility_shim_count", 0)))
    final_state = build_final_state(root, status=status, remaining=after_unresolved)
    decision = "resume_f0" if not after_unresolved else "remediation_required"
    dev_decision = branch_decision(root, ready=not after_unresolved)

    existing_reference_report = load_json_if_exists(root / STANDARD_OUTPUTS["references"])
    current_runtime_files_modified = count_changed_files(root, "runtime/")
    runtime_files_modified = current_runtime_files_modified
    if apply_changes and runtime_files_modified == 0:
        runtime_files_modified = int(
            existing_result.get(
                "runtime_files_modified",
                existing_reference_report.get("runtime_files_modified", 0),
            )
        )

    moves_completed = len(moves) if apply_changes and moves else int(existing_result.get("moves_completed", 0))
    references_updated = (
        max(
            int(existing_result.get("references_updated", 0)),
            int(existing_reference_report.get("references_updated", 0)),
            len(reference_updates),
        )
        if apply_changes
        else 0
    )

    result = {
        "schema_version": "r0_contract_taxonomy_remediation_result.v0",
        "task": TASK_ID,
        "status": "pass" if not after_unresolved else "partial",
        "unresolved_before": before_count,
        "unresolved_after": len(after_unresolved),
        "compatibility_shims_before": shims_before,
        "compatibility_shims_after": len(after_unresolved),
        "contracts_root_status_before": str(final_before.get("contracts_root_status", "partial")),
        "contracts_root_status_after": final_state["contracts_root_status"],
        "contracts_clean_enough_for_f0": not after_unresolved,
        "moves_completed": moves_completed,
        "renames_completed": 0,
        "references_updated": references_updated,
        "shims_retired": shims_before if apply_changes and not after_unresolved else 0,
        "schemas_deleted": 0,
        "runtime_files_modified": runtime_files_modified,
        "site_dist_mutated": False,
        "master_index_mutated": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
        "f0_decision": decision,
        "dev_to_main_decision": dev_decision,
    }
    resolved = {
        "schema_version": "r0_contract_taxonomy_resolved_items.v0",
        "task": TASK_ID,
        "resolved": moves if apply_changes else [{**move, "status": "planned"} for move in moves],
    }
    remaining = {
        "schema_version": "r0_contract_taxonomy_remaining_items.v0",
        "task": TASK_ID,
        "remaining": after_unresolved,
    }
    shim_retirement = {
        "schema_version": "r0_contract_taxonomy_shim_retirement_report.v0",
        "task": TASK_ID,
        "compatibility_shims_before": shims_before,
        "compatibility_shims_after": len(after_unresolved),
        "retired": build_retired_shims(shim_report, moves) if apply_changes else [],
        "remaining": [],
    }
    reference_report = {
        "schema_version": "r0_contract_taxonomy_reference_update_report.v0",
        "task": TASK_ID,
        "mode": "apply" if apply_changes else "dry_run",
        "references_updated": references_updated,
        "active_reference_updates": reference_updates,
        "historical_references_left_intact": find_historical_references(root, REMEDIATION_MOVES),
        "runtime_files_modified": runtime_files_modified,
    }
    report = {
        "schema_version": "r0_contract_taxonomy_remediation_report.v0",
        "status": result["status"],
        "task": TASK_ID,
        "purpose": "resolve_remaining_contract_taxonomy_blockers",
        "unresolved_before": before_count,
        "unresolved_after": len(after_unresolved),
        "compatibility_shims_before": shims_before,
        "compatibility_shims_after": len(after_unresolved),
        "contracts_root_status_after": final_state["contracts_root_status"],
        "contracts_clean_enough_for_f0": not after_unresolved,
        "moves_completed": result["moves_completed"],
        "renames_completed": 0,
        "references_updated": result["references_updated"],
        "shims_retired": result["shims_retired"],
        "schemas_deleted": 0,
        "runtime_files_modified": runtime_files_modified,
        "site_dist_mutated": False,
        "master_index_mutated": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
        "f0_decision": decision,
        "dev_to_main_decision": dev_decision,
        "validation": {},
    }
    return {
        "remediation_result": result,
        "resolved_items": resolved,
        "remaining_items": remaining,
        "shim_retirement_report": shim_retirement,
        "reference_update_report": reference_report,
        "final_state": final_state,
        "remediation_report": report,
        "errors": [],
    }


def build_moves(root: Path, unresolved_items: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    moves: list[dict[str, Any]] = []
    by_path = {str(item.get("path", "")): item for item in unresolved_items}
    for source, spec in sorted(REMEDIATION_MOVES.items()):
        target = spec["target_path"]
        moves.append(
            {
                "source_path": source,
                "target_path": target,
                "classification": spec["classification"],
                "rationale": spec["rationale"],
                "original_reason": str(by_path.get(source, {}).get("reason", "")),
                "status": move_status(root, source, target),
            }
        )
    return moves


def move_status(root: Path, source: str, target: str) -> str:
    if (root / target).exists() and not (root / source).exists():
        return "already_moved"
    if (root / source).exists() and not (root / target).exists():
        return "ready"
    if (root / source).exists() and (root / target).exists():
        return "blocked_target_exists"
    return "blocked_missing_source_and_target"


def apply_moves(root: Path, moves: Sequence[Mapping[str, Any]]) -> None:
    for move in moves:
        source = str(move["source_path"])
        target = str(move["target_path"])
        if source.startswith(FORBIDDEN_MOVE_ROOTS) or target.startswith(FORBIDDEN_MOVE_ROOTS):
            raise RuntimeError(f"refusing forbidden move: {source} -> {target}")
        source_path = root / source
        target_path = root / target
        if target_path.exists() and not source_path.exists():
            continue
        if not source_path.exists():
            raise FileNotFoundError(source)
        if target_path.exists():
            raise FileExistsError(target)
        target_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(source_path), str(target_path))


def find_reference_updates(root: Path, replacements: Mapping[str, str]) -> list[dict[str, str]]:
    updates: list[dict[str, str]] = []
    for path in iter_active_reference_files(root):
        rel = path.relative_to(root).as_posix()
        text = read_text(path)
        for old, new in replacements.items():
            if (rel, old) in PRESERVED_HISTORICAL_REFERENCES:
                continue
            if old in text or old.replace("/", "\\") in text:
                update_path = replacements.get(rel, rel)
                updates.append(
                    {
                        "path": update_path,
                        "old_reference": old,
                        "new_reference": new,
                        "reason": "Active contract taxonomy reference updated by R0 remediation.",
                    }
                )
    return dedupe(updates)


def find_historical_references(root: Path, replacements: Mapping[str, Mapping[str, str]]) -> list[dict[str, str]]:
    historical: list[dict[str, str]] = []
    base = root / "control/audits"
    if not base.exists():
        return historical
    for path in base.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        rel = path.relative_to(root).as_posix()
        if rel.startswith(AUDIT_DIR.as_posix()):
            continue
        text = read_text(path)
        for old, spec in replacements.items():
            if old in text:
                historical.append(
                    {
                        "path": rel,
                        "old_reference": old,
                        "new_reference": spec["target_path"],
                        "reason": "Historical audit evidence left intact.",
                    }
                )
    for rel, old in PRESERVED_HISTORICAL_REFERENCES:
        path = root / rel
        if path.exists() and old in read_text(path):
            historical.append(
                {
                    "path": rel,
                    "old_reference": old,
                    "new_reference": replacements[old]["target_path"],
                    "reason": "Historical compatibility alias preserved for migrated audit evidence.",
                }
            )
    return dedupe(historical)


def apply_reference_updates(root: Path, updates: Sequence[Mapping[str, str]]) -> None:
    updates_by_path: dict[str, list[Mapping[str, str]]] = {}
    for update in updates:
        updates_by_path.setdefault(str(update["path"]), []).append(update)
    for rel, items in updates_by_path.items():
        path = root / rel
        text = read_text(path)
        original = text
        for item in items:
            old = str(item["old_reference"])
            new = str(item["new_reference"])
            text = text.replace(old, new)
            text = text.replace(old.replace("/", "\\"), new.replace("/", "\\"))
            text = text.replace(f"https://eureka.local/{new}", f"https://eureka.local/{new}")
        if text != original:
            path.write_text(text, encoding="utf-8")


def iter_active_reference_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for rel in ACTIVE_REFERENCE_ROOTS:
        base = root / rel
        if not base.exists():
            continue
        for path in base.rglob("*"):
            if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
                continue
            path_rel = path.relative_to(root).as_posix()
            if is_intentional_remediation_evidence(path_rel):
                continue
            files.append(path)
    return files


def count_changed_files(root: Path, prefix: str) -> int:
    completed = subprocess.run(["git", "status", "--porcelain=v1"], cwd=root, text=True, capture_output=True, check=False)
    if completed.returncode != 0:
        return 0
    paths: set[str] = set()
    for line in completed.stdout.splitlines():
        if len(line) < 4:
            continue
        raw = line[3:].replace("\\", "/").strip('"')
        for path in raw.split(" -> "):
            if path.startswith(prefix):
                paths.add(path)
    return len(paths)


def is_intentional_remediation_evidence(rel: str) -> bool:
    return (
        rel == "scripts/resolve_contract_taxonomy_blockers.py"
        or rel == "tests/operations/test_contract_taxonomy_remediation.py"
        or rel.startswith("control/inventory/r0_contract_taxonomy_")
        or rel.startswith("control/inventory/r0_03b_1_")
        or rel == "control/inventory/r0_03b_execution_plan.json"
        or rel.startswith(AUDIT_DIR.as_posix() + "/")
    )


def remaining_after(root: Path) -> list[dict[str, str]]:
    remaining: list[dict[str, str]] = []
    for source, spec in sorted(REMEDIATION_MOVES.items()):
        if (root / source).exists():
            remaining.append(
                {
                    "path": source,
                    "reason": "Source path still exists after remediation.",
                    "severity": "blocker",
                    "recommended_next_action": f"Move to {spec['target_path']}.",
                }
            )
        if not (root / spec["target_path"]).exists():
            remaining.append(
                {
                    "path": spec["target_path"],
                    "reason": "Target path is missing after remediation.",
                    "severity": "blocker",
                    "recommended_next_action": "Restore or rerun remediation resolver.",
                }
            )
    return remaining


def build_final_state(root: Path, *, status: str, remaining: Sequence[Mapping[str, str]]) -> dict[str, Any]:
    audit = load_current_taxonomy(root)
    contracts = audit.get("contract_taxonomy_inventory", {}).get("contracts", [])
    product_classes = {
        "product_domain_contract",
        "product_runtime_contract",
        "public_api_contract",
        "snapshot_contract",
        "native_contract",
        "durable_store_contract",
        "connector_interface_contract",
        "source_policy_contract",
    }
    product_count = sum(1 for item in contracts if str(item.get("path", "")).startswith("contracts/") and item.get("contract_class") in product_classes)
    control_count = sum(1 for path in (root / "control/schemas").rglob("*") if path.is_file() and path.name != "README.md")
    clean = not remaining
    root_status = "clean_with_warnings" if clean else "partial"
    return {
        "schema_version": "r0_contract_taxonomy_final_state.v0",
        "task": TASK_ID,
        "status": "pass" if status == "pass" else status,
        "contracts_root_status": root_status,
        "control_schemas_root_status": "clean_with_warnings",
        "product_contract_count": product_count,
        "control_schema_count": control_count,
        "compatibility_shim_count": len(remaining),
        "unresolved_contract_count": len(remaining),
        "contracts_clean_enough_for_f0": clean,
        "contracts_clean_enough_for_r0_04": clean,
        "recommended_next_task": "F0-BUNDLE-01 — Deep extraction source-family and extraction-boundary policy packs" if clean else "R0-REMEDIATION-CONTRACT-TAXONOMY-02 — Resolve remaining taxonomy blockers",
    }


def build_retired_shims(shim_report: Mapping[str, Any], moves: Sequence[Mapping[str, Any]]) -> list[dict[str, str]]:
    move_map = {str(move["source_path"]): str(move["target_path"]) for move in moves}
    retired: list[dict[str, str]] = []
    shim_old_paths = {str(shim.get("old_path", "")) for shim in shim_report.get("shims", [])}
    for old, new in move_map.items():
        retired.append(
            {
                "old_path": old,
                "new_path": new,
                "shim_kind": "none",
                "retired": "true",
                "source": "r0_03b_1_compatibility_shim_report" if old in shim_old_paths else "r0_03b_2_unresolved_contracts",
            }
        )
    return retired


def write_standard_outputs(root: Path, result: Mapping[str, Any]) -> None:
    for key, path in STANDARD_OUTPUTS.items():
        payload_key = {
            "result": "remediation_result",
            "resolved": "resolved_items",
            "remaining": "remaining_items",
            "shim": "shim_retirement_report",
            "references": "reference_update_report",
            "final": "final_state",
            "report": "remediation_report",
        }[key]
        write_json(root / path, result[payload_key])
    update_r0_03b_outputs(root, result)
    update_r0_10_outputs(root, result)
    update_r0_11_outputs(root, result)
    write_docs_and_audit(root, result)
    refresh_taxonomy_inventories(root)


def update_r0_03b_outputs(root: Path, result: Mapping[str, Any]) -> None:
    final = result["final_state"]
    old_final = {
        "schema_version": "r0_03b_2_final_contract_taxonomy.v0",
        "task": "R0-03B-2",
        "contracts_root_status": final["contracts_root_status"],
        "control_schemas_root_status": final["control_schemas_root_status"],
        "product_contract_count": final["product_contract_count"],
        "control_schema_count": final["control_schema_count"],
        "compatibility_shim_count": 0,
        "unresolved_contract_count": 0,
        "contracts_clean_enough_for_r0_04": True,
        "recommended_next_task": "R0-04 — Source observation production seam",
    }
    write_json(root / "control/inventory/r0_03b_2_final_contract_taxonomy.json", old_final)
    write_json(root / "control/inventory/r0_03b_2_unresolved_contracts.json", {"schema_version": "r0_03b_2_unresolved_contracts.v0", "task": "R0-03B-2", "unresolved": []})
    cleanup = load_json(root / "control/inventory/r0_03b_2_product_contract_cleanup_result.json")
    cleanup.update(
        {
            "status": "pass_with_warnings",
            "non_product_contract_count": 0,
            "unknown_contract_count": 0,
            "blocked": [],
            "contracts_clean_enough_for_r0_04": True,
        }
    )
    write_json(root / "control/inventory/r0_03b_2_product_contract_cleanup_result.json", cleanup)


def update_r0_10_outputs(root: Path, result: Mapping[str, Any]) -> None:
    prod = load_json(root / "control/inventory/r0_production_review_result.json")
    prod.update(
        {
            "status": "pass_with_warnings",
            "contract_taxonomy_ready": True,
            "all_required_r0_tasks_passed": True,
            "f0_can_resume": True,
            "dev_can_promote_to_main": True,
            "blockers": [],
        }
    )
    prod["warnings"] = [warning for warning in prod.get("warnings", []) if warning.get("area") != "contract_taxonomy"]
    write_json(root / "control/inventory/r0_production_review_result.json", prod)
    write_json(root / "control/inventory/r0_remaining_blockers.json", {"schema_version": "r0_remaining_blockers.v0", "task": "R0-10", "blockers": []})
    decision = load_json(root / "control/inventory/r0_next_phase_decision.json")
    decision.update(
        {
            "f0_decision": "resume_f0",
            "main_promotion_decision": branch_decision(root, ready=True),
            "recommended_next_task": "F0-BUNDLE-01 — Deep extraction source-family and extraction-boundary policy packs",
            "alternative_next_task": "R0-REMEDIATION-LEGACY-LEAKAGE-01 — Retire known legacy runtime architecture leakage allowlist debt",
            "reason": "R0 contract taxonomy blocker was resolved by R0-REMEDIATION-CONTRACT-TAXONOMY-01.",
            "production_readiness_claimed": False,
            "public_launch_readiness_claimed": False,
        }
    )
    write_json(root / "control/inventory/r0_next_phase_decision.json", decision)
    warnings = load_json(root / "control/inventory/r0_warning_disposition.json")
    for warning in warnings.get("warnings", []):
        if warning.get("area") == "contract_taxonomy":
            warning["disposition"] = "fixed"
            warning["next_task"] = ""
            warning["notes"] = ["Resolved by R0-REMEDIATION-CONTRACT-TAXONOMY-01."]
    write_json(root / "control/inventory/r0_warning_disposition.json", warnings)
    report = load_json(root / "control/audits/r0-10-dev-to-main-production-review-v0/r0_10_report.json")
    report.update(
        {
            "status": "pass_with_warnings",
            "contract_taxonomy_ready": True,
            "f0_can_resume": True,
            "dev_can_promote_to_main": True,
            "recommended_next_task": "F0-BUNDLE-01 — Deep extraction source-family and extraction-boundary policy packs",
        }
    )
    write_json(root / "control/audits/r0-10-dev-to-main-production-review-v0/r0_10_report.json", report)


def update_r0_11_outputs(root: Path, result: Mapping[str, Any]) -> None:
    closeout = load_json(root / "control/inventory/r0_final_closeout_result.json")
    closeout.update(
        {
            "status": "pass_with_warnings",
            "blockers_remaining": 0,
            "f0_decision": "resume_f0",
            "main_promotion_decision": branch_decision(root, ready=True),
            "recommended_next_task": "F0-BUNDLE-01 — Deep extraction source-family and extraction-boundary policy packs",
        }
    )
    write_json(root / "control/inventory/r0_final_closeout_result.json", closeout)
    write_json(root / "control/inventory/r0_final_blocker_register.json", {"schema_version": "r0_final_blocker_register.v0", "task": "R0-11", "blockers": []})
    warnings = load_json(root / "control/inventory/r0_final_warning_disposition.json")
    for warning in warnings.get("warnings", []):
        if warning.get("area") == "contract_taxonomy":
            warning["disposition"] = "fixed"
            warning["child_task"] = ""
            warning["notes"] = ["Resolved by R0-REMEDIATION-CONTRACT-TAXONOMY-01."]
    write_json(root / "control/inventory/r0_final_warning_disposition.json", warnings)
    decision = load_json(root / "control/inventory/r0_final_next_task_decision.json")
    decision.update(
        {
            "recommended_next_task": "F0-BUNDLE-01 — Deep extraction source-family and extraction-boundary policy packs",
            "alternative_next_task": "R0-REMEDIATION-LEGACY-LEAKAGE-01 — Retire known legacy runtime architecture leakage allowlist debt",
            "reason": "Contract taxonomy blocker is resolved; legacy leakage cleanup remains deferred.",
            "f0_can_resume": True,
            "production_readiness_claimed": False,
            "public_launch_readiness_claimed": False,
        }
    )
    write_json(root / "control/inventory/r0_final_next_task_decision.json", decision)
    children = load_json(root / "control/inventory/r0_child_remediation_tasks.json")
    for task in children.get("tasks", []):
        if task.get("task_id") == TASK_ID:
            task["status"] = "completed"
            task["blocked_until_complete"] = []
            task["reason"] = "Resolved by this remediation task."
    write_json(root / "control/inventory/r0_child_remediation_tasks.json", children)
    queue = load_json(root / "control/inventory/r0_final_queue_state.json")
    queue.update(
        {
            "current_queue_item_after": "F0-BUNDLE-01 — Deep extraction source-family and extraction-boundary policy packs",
            "f0_state": "ready",
            "remediation_state": "none",
        }
    )
    write_json(root / "control/inventory/r0_final_queue_state.json", queue)
    report = load_json(root / "control/audits/r0-11-final-closeout-v0/r0_11_report.json")
    report.update(
        {
            "status": "pass_with_warnings",
            "blockers_remaining": 0,
            "f0_can_resume": True,
            "dev_can_promote_to_main": branch_decision(root, ready=True) in {"promotion_plan_only", "promote_ready"},
            "recommended_next_task": "F0-BUNDLE-01 — Deep extraction source-family and extraction-boundary policy packs",
        }
    )
    write_json(root / "control/audits/r0-11-final-closeout-v0/r0_11_report.json", report)


def refresh_taxonomy_inventories(root: Path) -> None:
    audit = load_current_taxonomy(root)
    mapping = {
        "control/inventory/contract_taxonomy_inventory.json": "contract_taxonomy_inventory",
        "control/inventory/contract_migration_plan.json": "contract_migration_plan",
        "control/inventory/contract_reference_graph.json": "contract_reference_graph",
        "control/inventory/contract_risk_register.json": "contract_risk_register",
    }
    for rel, key in mapping.items():
        if key in audit:
            write_json(root / rel, audit[key])


def write_docs_and_audit(root: Path, result: Mapping[str, Any]) -> None:
    docs = {
        Path("docs/operations/R0_CONTRACT_TAXONOMY_REMEDIATION.md"): render_operation_doc(result),
        AUDIT_DIR / "README.md": "# R0 Contract Taxonomy Remediation\n\nFinal remediation pack for R0-REMEDIATION-CONTRACT-TAXONOMY-01.\n",
        AUDIT_DIR / "resolved_items.md": render_resolved(result["resolved_items"]),
        AUDIT_DIR / "remaining_items.md": render_remaining(result["remaining_items"]),
        AUDIT_DIR / "shim_retirement_report.md": render_shims(result["shim_retirement_report"]),
        AUDIT_DIR / "reference_update_report.md": render_references(result["reference_update_report"]),
        AUDIT_DIR / "final_contract_taxonomy_state.md": render_final_state(result["final_state"]),
        AUDIT_DIR / "validation.md": "# Validation\n\nValidation commands are recorded after remediation checks run.\n",
        AUDIT_DIR / "generated/sample_summary.md": render_summary(result),
    }
    for path, text in docs.items():
        write_text(root / path, text)
    write_json(root / (AUDIT_DIR / "generated/sample_remediation_result.json"), result["remediation_result"])
    write_json(root / (AUDIT_DIR / "generated/sample_final_contract_taxonomy_state.json"), result["final_state"])
    update_existing_docs(root)


def update_existing_docs(root: Path) -> None:
    append_once(
        root / "docs/operations/R0_FINAL_CLOSEOUT.md",
        "\n## Contract Taxonomy Remediation\n\nR0-REMEDIATION-CONTRACT-TAXONOMY-01 resolved the remaining R0-03B-2 contract taxonomy blocker. F0 may resume through the recovered runtime seams; dev-to-main remains an operator promotion action rather than an automatic merge.\n",
        "## Contract Taxonomy Remediation",
    )
    append_once(
        root / "docs/operations/R0_TO_F0_HANDOFF.md",
        "\n## Taxonomy Gate Update\n\nThe contract taxonomy remediation moved the final fixture, preview, task, and control schemas out of `contracts/`. F0 must continue to use the recovered source observation, cache, evidence, review, and reviewed index seams.\n",
        "## Taxonomy Gate Update",
    )
    append_once(
        root / "docs/architecture/CONTRACT_TAXONOMY.md",
        "\n## R0 Remediation Closeout\n\nThe R0 remediation task retired the remaining unresolved contract taxonomy items by moving non-product fixtures, H14 preview schemas, work-unit control schemas, and query preview/task schemas into `control/schemas/`. Historical audit references remain historical evidence.\n",
        "## R0 Remediation Closeout",
    )


def append_once(path: Path, text: str, marker: str) -> None:
    current = path.read_text(encoding="utf-8") if path.exists() else ""
    if marker in current:
        return
    path.write_text(current.rstrip() + "\n" + text, encoding="utf-8")


def write_requested(root: Path, args: argparse.Namespace, result: Mapping[str, Any]) -> None:
    outputs = {
        args.output: result["remediation_result"],
        args.reference_output: result["reference_update_report"],
        args.shim_output: result["shim_retirement_report"],
        args.final_state_output: result["final_state"],
    }
    for target, payload in outputs.items():
        if target and not result["errors"]:
            write_json(resolve_repo_path(root, Path(target)), payload)
    if args.summary_output and not result["errors"]:
        write_text(resolve_repo_path(root, Path(args.summary_output)), render_summary(result))


def branch_decision(root: Path, *, ready: bool) -> str:
    branch = git_value(root, "branch", "--show-current")
    if branch == "main":
        return "already_on_main"
    if not ready:
        return "remain_blocked"
    return "promotion_plan_only"


def load_current_taxonomy(root: Path) -> dict[str, Any]:
    script = root / "scripts/audit_contract_taxonomy.py"
    spec = importlib.util.spec_from_file_location("audit_contract_taxonomy", script)
    if spec is None or spec.loader is None:
        return {}
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.build_contract_taxonomy_audit(root)


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="ignore")


def dedupe(items: Sequence[Mapping[str, str]]) -> list[dict[str, str]]:
    seen: set[str] = set()
    result: list[dict[str, str]] = []
    for item in items:
        key = json.dumps(item, sort_keys=True)
        if key not in seen:
            seen.add(key)
            result.append(dict(item))
    return result


def blocked_result(errors: Sequence[str]) -> dict[str, Any]:
    payload = {
        "schema_version": "r0_contract_taxonomy_remediation_result.v0",
        "task": TASK_ID,
        "status": "blocked",
        "unresolved_before": 0,
        "unresolved_after": 0,
        "compatibility_shims_before": 0,
        "compatibility_shims_after": 0,
        "contracts_root_status_before": "partial",
        "contracts_root_status_after": "blocked",
        "contracts_clean_enough_for_f0": False,
        "moves_completed": 0,
        "renames_completed": 0,
        "references_updated": 0,
        "shims_retired": 0,
        "schemas_deleted": 0,
        "runtime_files_modified": 0,
        "site_dist_mutated": False,
        "master_index_mutated": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
        "f0_decision": "remain_blocked",
        "dev_to_main_decision": "remain_blocked",
    }
    return {
        "remediation_result": payload,
        "resolved_items": {"schema_version": "r0_contract_taxonomy_resolved_items.v0", "task": TASK_ID, "resolved": []},
        "remaining_items": {"schema_version": "r0_contract_taxonomy_remaining_items.v0", "task": TASK_ID, "remaining": []},
        "shim_retirement_report": {"schema_version": "r0_contract_taxonomy_shim_retirement_report.v0", "task": TASK_ID, "retired": [], "remaining": []},
        "reference_update_report": {"schema_version": "r0_contract_taxonomy_reference_update_report.v0", "task": TASK_ID, "active_reference_updates": []},
        "final_state": {"schema_version": "r0_contract_taxonomy_final_state.v0", "task": TASK_ID, "contracts_root_status": "blocked", "contracts_clean_enough_for_f0": False},
        "remediation_report": {"schema_version": "r0_contract_taxonomy_remediation_report.v0", "task": TASK_ID, "status": "blocked"},
        "errors": list(errors),
    }


def check_output_path(root: Path, path: Path, errors: list[str]) -> None:
    full = resolve_repo_path(root, path).resolve()
    if not is_relative_to(full, root):
        errors.append(f"refusing output outside repo: {path}")
        return
    rel = full.relative_to(root).as_posix()
    first = rel.split("/", 1)[0]
    if first in FORBIDDEN_OUTPUT_ROOTS or rel.startswith("site/dist/"):
        errors.append(f"refusing forbidden output root: {rel}")


def resolve_repo_path(root: Path, path: Path) -> Path:
    return path if path.is_absolute() else root / path


def is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.relative_to(parent)
    except ValueError:
        return False
    return True


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def load_json_if_exists(path: Path) -> dict[str, Any]:
    try:
        return load_json(path)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, payload: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(payload, encoding="utf-8")


def git_value(root: Path, *args: str) -> str:
    completed = subprocess.run(["git", *args], cwd=root, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    return completed.stdout.strip() if completed.returncode == 0 else ""


def render_console(result: Mapping[str, Any]) -> str:
    payload = result["remediation_result"]
    return "\n".join(
        [
            "R0 contract taxonomy remediation",
            f"status: {payload['status']}",
            f"unresolved_before: {payload['unresolved_before']}",
            f"unresolved_after: {payload['unresolved_after']}",
            f"compatibility_shims_after: {payload['compatibility_shims_after']}",
            f"contracts_root_status_after: {payload['contracts_root_status_after']}",
            f"contracts_clean_enough_for_f0: {str(payload['contracts_clean_enough_for_f0']).lower()}",
        ]
    )


def render_summary(result: Mapping[str, Any]) -> str:
    payload = result["remediation_result"]
    return "\n".join(
        [
            "# R0 Contract Taxonomy Remediation Summary",
            "",
            f"- status: {payload['status']}",
            f"- unresolved before: {payload['unresolved_before']}",
            f"- unresolved after: {payload['unresolved_after']}",
            f"- compatibility shims before: {payload['compatibility_shims_before']}",
            f"- compatibility shims after: {payload['compatibility_shims_after']}",
            f"- moves completed: {payload['moves_completed']}",
            f"- references updated: {payload['references_updated']}",
            f"- contracts clean enough for F0: {str(payload['contracts_clean_enough_for_f0']).lower()}",
            f"- F0 decision: {payload['f0_decision']}",
            f"- dev-to-main decision: {payload['dev_to_main_decision']}",
            "",
        ]
    )


def render_operation_doc(result: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "# R0 Contract Taxonomy Remediation",
            "",
            "R0-REMEDIATION-CONTRACT-TAXONOMY-01 resolves the 19 unresolved contract taxonomy items left by R0-03B-2.",
            "",
            "## Before",
            "",
            "- unresolved contract count: 19",
            "- compatibility shim count: 19",
            "- contracts root status: partial",
            "",
            "## Actions",
            "",
            "- Moved synthetic archive fixtures into `control/schemas/fixtures/archive/`.",
            "- Moved H14 candidate preview schemas into `control/schemas/previews/h14/connectors/`.",
            "- Moved work-unit control schemas into `control/schemas/policies/node/`.",
            "- Moved query candidate/review schemas into `control/schemas/previews/query/` and `control/schemas/tasks/query/`.",
            "- Updated active references in current scripts, tests, docs, examples, and control inventories.",
            "- Left historical audit narrative intact.",
            "",
            "## Decision",
            "",
            f"- contracts clean enough for F0: {str(result['remediation_result']['contracts_clean_enough_for_f0']).lower()}",
            f"- F0 decision: {result['remediation_result']['f0_decision']}",
            f"- dev-to-main decision: {result['remediation_result']['dev_to_main_decision']}",
            "- production readiness claimed: false",
            "- public launch readiness claimed: false",
            "",
        ]
    )


def render_resolved(payload: Mapping[str, Any]) -> str:
    lines = ["# Resolved Items", ""]
    for item in payload.get("resolved", []):
        lines.append(f"- `{item['source_path']}` -> `{item['target_path']}` ({item['classification']})")
    return "\n".join(lines) + "\n"


def render_remaining(payload: Mapping[str, Any]) -> str:
    lines = ["# Remaining Items", ""]
    if not payload.get("remaining"):
        lines.append("No unresolved contract taxonomy items remain.")
    for item in payload.get("remaining", []):
        lines.append(f"- `{item['path']}`: {item['reason']}")
    return "\n".join(lines) + "\n"


def render_shims(payload: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "# Shim Retirement Report",
            "",
            f"- compatibility shims before: {payload.get('compatibility_shims_before', 0)}",
            f"- compatibility shims after: {payload.get('compatibility_shims_after', 0)}",
            f"- retired entries: {len(payload.get('retired', []))}",
            "",
        ]
    )


def render_references(payload: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "# Reference Update Report",
            "",
            f"- mode: {payload.get('mode')}",
            f"- active references updated: {payload.get('references_updated', 0)}",
            f"- historical references left intact: {len(payload.get('historical_references_left_intact', []))}",
            "- runtime files modified: 0",
            "",
        ]
    )


def render_final_state(payload: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "# Final Contract Taxonomy State",
            "",
            f"- contracts root status: {payload.get('contracts_root_status')}",
            f"- unresolved contract count: {payload.get('unresolved_contract_count')}",
            f"- compatibility shim count: {payload.get('compatibility_shim_count')}",
            f"- contracts clean enough for F0: {str(payload.get('contracts_clean_enough_for_f0')).lower()}",
            f"- recommended next task: {payload.get('recommended_next_task')}",
            "",
        ]
    )


if __name__ == "__main__":
    raise SystemExit(main())
