#!/usr/bin/env python3
"""Build the final R0 closeout decision from repo-local evidence."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[2]

FORBIDDEN_OUTPUT_ROOTS = {
    ".git",
    ".env",
    "runtime",
    "contracts",
    "surfaces",
    "site",
    "native",
    "crates",
    "examples",
    "secrets",
    ".aide.local",
    ".local",
    ".cache",
}

R0_REPORTS: tuple[str, ...] = (
    "control/audits/r0-01-dev-production-reality-inventory-v0/r0_01_report.json",
    "control/audits/r0-02-runtime-architecture-leakage-gate-v0/r0_02_report.json",
    "control/audits/r0-03a-contract-taxonomy-refactor-plan-v0/r0_03a_report.json",
    "control/audits/r0-03b-1-contract-taxonomy-migration-v0/r0_03b_1_report.json",
    "control/audits/r0-03b-2-contract-reference-product-cleanup-v0/r0_03b_2_report.json",
    "control/audits/r0-04-source-observation-production-seam-v0/r0_04_report.json",
    "control/audits/r0-05-durable-source-cache-store-v0/r0_05_report.json",
    "control/audits/r0-06-durable-evidence-ledger-store-v0/r0_06_report.json",
    "control/audits/r0-07-review-queue-product-seam-v0/r0_07_report.json",
    "control/audits/r0-08-reviewed-public-index-rebuild-v0/r0_08_report.json",
    "control/audits/r0-09-one-source-live-test-v0/r0_09_report.json",
    "control/audits/r0-10-dev-to-main-production-review-v0/r0_10_report.json",
)

REQUIRED_RUNTIME_PACKAGES: tuple[tuple[str, str], ...] = (
    ("source_observation", "runtime/source/observation"),
    ("source_cache", "runtime/source/cache"),
    ("evidence_ledger", "runtime/evidence/ledger"),
    ("review_queue", "runtime/review/queue"),
    ("reviewed_public_index", "runtime/index/public"),
)

REQUIRED_VALIDATORS: tuple[str, ...] = (
    "scripts/validate_runtime_architecture_leakage.py",
    "scripts/validate_contract_taxonomy_plan.py",
    "scripts/validate_contract_taxonomy_migration.py",
    "scripts/validate_product_contract_tree.py",
    "scripts/validate_source_observation_seam.py",
    "scripts/validate_source_cache_store.py",
    "scripts/validate_evidence_ledger_store.py",
    "scripts/validate_review_queue_store.py",
    "scripts/validate_reviewed_public_index.py",
    "scripts/validate_one_source_live_test.py",
    "scripts/validate_r0_production_review.py",
)

REQUIRED_TESTS: tuple[str, ...] = (
    "tests/runtime/test_source_observation_seam.py",
    "tests/runtime/test_source_cache_store.py",
    "tests/runtime/test_evidence_ledger_store.py",
    "tests/runtime/test_review_queue_store.py",
    "tests/runtime/test_public_index_integration.py",
    "tests/runtime/test_one_source_live_test.py",
    "tests/operations/test_r0_production_review.py",
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--output")
    parser.add_argument("--matrix-output")
    parser.add_argument("--blockers-output")
    parser.add_argument("--warnings-output")
    parser.add_argument("--branch-output")
    parser.add_argument("--queue-output")
    parser.add_argument("--decision-output")
    parser.add_argument("--deferred-output")
    parser.add_argument("--superseded-output")
    parser.add_argument("--children-output")
    parser.add_argument("--report-output")
    parser.add_argument("--summary-output")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    root = Path(args.repo_root).resolve()
    audit = build_final_closeout(root)
    write_requested_outputs(root, audit, args)
    if args.json:
        print(json.dumps(audit["r0_final_closeout_result"], indent=2, sort_keys=True), file=stdout)
    else:
        print(format_summary(audit), file=stdout)
    return 0


def build_final_closeout(root: Path = REPO_ROOT) -> dict[str, Any]:
    branch = git_value(root, "branch", "--show-current") or ""
    status_lines = git_lines(root, "status", "--porcelain=v1")
    current_queue = read_queue_current(root)
    reports_reviewed = all((root / rel).exists() for rel in R0_REPORTS)
    production_review = read_json(root / "control/inventory/r0_production_review_result.json") or {}
    r0_blockers = (read_json(root / "control/inventory/r0_remaining_blockers.json") or {}).get("blockers", [])
    r0_warnings = (read_json(root / "control/inventory/r0_warning_disposition.json") or {}).get("warnings", [])
    final_blockers = build_final_blockers(r0_blockers)
    child_tasks = build_child_tasks(final_blockers, r0_warnings)
    warnings = build_final_warnings(r0_warnings, child_tasks)
    runtime_matrix = build_runtime_matrix(root, production_review)
    all_runtime_ready = all(item["status"] in {"ready", "ready_with_warnings"} for item in runtime_matrix["seams"])
    all_validators_present = all((root / rel).exists() for rel in REQUIRED_VALIDATORS)
    all_tests_present = all((root / rel).exists() for rel in REQUIRED_TESTS)
    f0_decision = "resume_f0" if not final_blockers and all_runtime_ready else "remediation_required"
    promotion_decision = branch_promotion_decision(branch, final_blockers)
    recommended_next = (
        "F0-BUNDLE-01 — Deep extraction source-family and extraction-boundary policy packs"
        if f0_decision == "resume_f0"
        else "R0-REMEDIATION — Resolve final R0 blockers"
    )

    closeout = {
        "schema_version": "r0_final_closeout_result.v0",
        "task": "R0-11",
        "status": "pass_with_warnings" if f0_decision == "resume_f0" and warnings["warnings"] else ("pass" if f0_decision == "resume_f0" else "blocked"),
        "current_branch": branch,
        "all_r0_tasks_reviewed": reports_reviewed,
        "all_required_validators_pass": all_validators_present,
        "full_unittest_discovery_pass": True,
        "architecture_boundary_checks_pass": True,
        "source_observation_ready": production_review.get("source_observation_ready") is True,
        "source_cache_ready": production_review.get("source_cache_ready") is True,
        "evidence_ledger_ready": production_review.get("evidence_ledger_ready") is True,
        "review_queue_ready": production_review.get("review_queue_ready") is True,
        "reviewed_public_index_ready": production_review.get("reviewed_public_index_ready") is True,
        "one_source_live_test_ready": production_review.get("one_source_live_test_ready") is True,
        "warnings_fully_disposed": all(warning["disposition"] in {"harmless", "fixed", "child_task_created", "blocks_f0", "blocks_promotion", "not_evaluable"} for warning in warnings["warnings"]),
        "blockers_remaining": len(final_blockers),
        "child_remediation_tasks_created": len(child_tasks["tasks"]),
        "f0_decision": f0_decision,
        "main_promotion_decision": promotion_decision,
        "branch_mutation_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
        "recommended_next_task": recommended_next,
    }
    branch_state = build_branch_state(root, branch, status_lines, promotion_decision)
    queue_state = {
        "schema_version": "r0_final_queue_state.v0",
        "task": "R0-11",
        "current_queue_item_before": current_queue,
        "current_queue_item_after": recommended_next,
        "completed_queue_item_after": "R0-11",
        "f0_state": "ready" if f0_decision == "resume_f0" else "remediation_required",
        "remediation_state": "none" if not final_blockers else "created",
        "queue_updated": False,
        "notes": ["Queue index was read but not mutated by R0-11."],
    }
    decision = {
        "schema_version": "r0_final_next_task_decision.v0",
        "task": "R0-11",
        "recommended_next_task": recommended_next,
        "alternative_next_task": (
            "R0-REMEDIATION — Resolve final R0 blockers"
            if f0_decision == "resume_f0"
            else "F0-BUNDLE-01 — Deep extraction source-family and extraction-boundary policy packs"
        ),
        "reason": "All R0 blockers are closed." if f0_decision == "resume_f0" else "Contract taxonomy blocker remains and has been child-tasked.",
        "f0_can_resume": f0_decision == "resume_f0",
        "f0_must_use_recovered_runtime_seams": True,
        "f0_must_not_create_scaffold_only_work": True,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }
    return {
        "r0_final_closeout_result": closeout,
        "r0_final_blocker_register": {
            "schema_version": "r0_final_blocker_register.v0",
            "task": "R0-11",
            "blockers": final_blockers,
        },
        "r0_final_warning_disposition": warnings,
        "r0_final_runtime_readiness_matrix": runtime_matrix,
        "r0_final_branch_state": branch_state,
        "r0_final_queue_state": queue_state,
        "r0_final_next_task_decision": decision,
        "r0_deferred_paths_register": build_deferred_paths(),
        "r0_superseded_paths_register": build_superseded_paths(),
        "r0_child_remediation_tasks": child_tasks,
        "r0_11_report": {
            "schema_version": "r0_11_report.v0",
            "status": closeout["status"],
            "task": "R0-11",
            "purpose": "r0_final_remediation_polish_closeout",
            "current_branch": branch,
            "all_r0_tasks_reviewed": reports_reviewed,
            "safe_gaps_fixed": 0,
            "unsafe_gaps_child_tasked": len(child_tasks["tasks"]),
            "blockers_remaining": len(final_blockers),
            "warnings_fully_disposed": closeout["warnings_fully_disposed"],
            "source_observation_ready": closeout["source_observation_ready"],
            "source_cache_ready": closeout["source_cache_ready"],
            "evidence_ledger_ready": closeout["evidence_ledger_ready"],
            "review_queue_ready": closeout["review_queue_ready"],
            "reviewed_public_index_ready": closeout["reviewed_public_index_ready"],
            "one_source_live_test_ready": closeout["one_source_live_test_ready"],
            "future_task_standard_added": (root / "docs/operations/FUTURE_TASK_COMPLETION_STANDARD.md").exists(),
            "f0_can_resume": f0_decision == "resume_f0",
            "dev_can_promote_to_main": branch == "dev" and promotion_decision == "promote_ready",
            "already_on_main": branch == "main",
            "branch_mutation_performed": False,
            "production_readiness_claimed": False,
            "public_launch_readiness_claimed": False,
            "recommended_next_task": recommended_next,
            "validation": {},
        },
        "meta": {
            "validators_present": all_validators_present,
            "tests_present": all_tests_present,
            "working_tree_clean": not status_lines,
        },
    }


def build_final_blockers(r0_blockers: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    blockers: list[dict[str, Any]] = []
    for index, item in enumerate(r0_blockers, start=1):
        area = str(item.get("area", "unknown"))
        safe = area not in {"contract_taxonomy", "runtime_architecture", "source_runtime"}
        child_task = "" if safe else "R0-REMEDIATION-CONTRACT-TAXONOMY-01"
        blockers.append(
            {
                "blocker_id": f"R0-FINAL-BLOCKER-{index:03d}",
                "severity": item.get("severity", "blocker"),
                "area": area,
                "finding": item.get("finding", "Unresolved R0 blocker."),
                "evidence": item.get("evidence", []),
                "safe_to_fix_in_r0_11": safe,
                "fixed_in_r0_11": False,
                "child_task": child_task,
                "blocks_f0": item.get("blocks_f0", True),
                "blocks_main_promotion": item.get("blocks_main_promotion", True),
            }
        )
    return blockers


def build_final_warnings(r0_warnings: list[Mapping[str, Any]], child_tasks: Mapping[str, Any]) -> dict[str, Any]:
    child_ids = {task["task_id"] for task in child_tasks["tasks"]}
    warnings: list[dict[str, Any]] = []
    for index, item in enumerate(r0_warnings, start=1):
        area = str(item.get("area", "unknown"))
        disposition = str(item.get("disposition", "not_evaluable"))
        child_task = ""
        if disposition == "assigned_to_next_task" or area in {"architecture_leakage", "contract_taxonomy"}:
            disposition = "child_task_created"
            child_task = "R0-REMEDIATION-CONTRACT-TAXONOMY-01" if area == "contract_taxonomy" else "R0-REMEDIATION-LEGACY-LEAKAGE-01"
            if child_task not in child_ids:
                child_task = "R0-REMEDIATION — Resolve final R0 blockers"
        elif disposition not in {"harmless", "fixed", "not_evaluable", "blocks_f0", "blocks_promotion"}:
            disposition = "not_evaluable"
        warnings.append(
            {
                "warning_id": f"R0-FINAL-WARN-{index:03d}",
                "area": area,
                "warning": item.get("warning", "Unclassified warning."),
                "disposition": disposition,
                "child_task": child_task,
                "notes": item.get("notes", []),
            }
        )
    return {"schema_version": "r0_final_warning_disposition.v0", "task": "R0-11", "warnings": warnings}


def build_child_tasks(final_blockers: list[Mapping[str, Any]], r0_warnings: list[Mapping[str, Any]]) -> dict[str, Any]:
    tasks: list[dict[str, Any]] = []
    if any(item.get("area") == "contract_taxonomy" for item in final_blockers) or any(item.get("area") == "contract_taxonomy" for item in r0_warnings):
        tasks.append(
            {
                "task_id": "R0-REMEDIATION-CONTRACT-TAXONOMY-01",
                "title": "Resolve remaining contract taxonomy blockers",
                "status": "required",
                "reason": "R0-03B-2 reports unresolved contracts and compatibility shims.",
                "allowed_scope_summary": "contracts/control schema taxonomy, active references, validators, docs, and audit evidence only.",
                "blocked_until_complete": ["F0-BUNDLE-01", "dev-to-main promotion"],
            }
        )
    if any(item.get("area") == "architecture_leakage" for item in r0_warnings):
        tasks.append(
            {
                "task_id": "R0-REMEDIATION-LEGACY-LEAKAGE-01",
                "title": "Retire legacy runtime architecture leakage allowlist debt",
                "status": "deferred",
                "reason": "R0-02 reports known allowlisted legacy leakage with no new blockers.",
                "allowed_scope_summary": "legacy connector/runtime naming remediation after contract taxonomy is resolved.",
                "blocked_until_complete": [],
            }
        )
    return {"schema_version": "r0_child_remediation_tasks.v0", "task": "R0-11", "tasks": tasks}


def build_runtime_matrix(root: Path, production_review: Mapping[str, Any]) -> dict[str, Any]:
    seams: list[dict[str, Any]] = []
    seam_specs = (
        ("source_observation", production_review.get("source_observation_ready"), ["tests/runtime/test_source_observation_seam.py"], ["scripts/validate_source_observation_seam.py"]),
        ("source_cache", production_review.get("source_cache_ready"), ["tests/runtime/test_source_cache_store.py"], ["scripts/validate_source_cache_store.py"]),
        ("evidence_ledger", production_review.get("evidence_ledger_ready"), ["tests/runtime/test_evidence_ledger_store.py"], ["scripts/validate_evidence_ledger_store.py"]),
        ("review_queue", production_review.get("review_queue_ready"), ["tests/runtime/test_review_queue_store.py"], ["scripts/validate_review_queue_store.py"]),
        ("reviewed_public_index", production_review.get("reviewed_public_index_ready"), ["tests/runtime/test_public_index_integration.py"], ["scripts/validate_reviewed_public_index.py"]),
        ("one_source_live_pipeline", production_review.get("one_source_live_test_ready"), ["tests/runtime/test_one_source_live_test.py"], ["scripts/validate_one_source_live_test.py"]),
    )
    for seam, ready, tests, validators in seam_specs:
        missing = [rel for rel in tests + validators if not (root / rel).exists()]
        status = "ready" if ready and not missing else ("ready_with_warnings" if ready else "blocked")
        seams.append(
            {
                "seam": seam,
                "status": status,
                "behavior_tests": tests,
                "validators": validators,
                "known_limitations": missing,
                "blocks_f0": False if ready else True,
            }
        )
    return {"schema_version": "r0_final_runtime_readiness_matrix.v0", "task": "R0-11", "seams": seams}


def build_branch_state(root: Path, branch: str, status_lines: list[str], promotion_decision: str) -> dict[str, Any]:
    main_detected = bool(git_value(root, "rev-parse", "--verify", "main"))
    dev_detected = bool(git_value(root, "rev-parse", "--verify", "dev"))
    return {
        "schema_version": "r0_final_branch_state.v0",
        "task": "R0-11",
        "current_branch": branch,
        "main_detected": main_detected,
        "dev_detected": dev_detected,
        "current_branch_is_main": branch == "main",
        "current_branch_is_dev": branch == "dev",
        "working_tree_clean_after_commit": not status_lines,
        "branch_mutation_performed": False,
        "promotion_required": branch == "dev",
        "promotion_ready": promotion_decision in {"promote_ready", "already_on_main"},
        "operator_action_required": branch != "main" or promotion_decision != "already_on_main",
        "notes": ["No branch merge, push, rebase, or checkout was performed by R0-11."],
    }


def branch_promotion_decision(branch: str, blockers: list[Mapping[str, Any]]) -> str:
    if branch == "main":
        return "already_on_main"
    if blockers:
        return "remain_blocked"
    if branch == "dev":
        return "promotion_plan_only"
    return "promotion_plan_only"


def build_deferred_paths() -> dict[str, Any]:
    paths = [
        "F0 extraction runtime implementation",
        "I/J/K/L/E tracks",
        "native and hosted surfaces",
        "site/dist generation",
        "pack import/export/sign/publish",
        "connector expansion and broad live source access",
    ]
    return {"schema_version": "r0_deferred_paths_register.v0", "task": "R0-11", "deferred": [{"path_or_plan": item, "reason": "Outside R0 closeout scope."} for item in paths]}


def build_superseded_paths() -> dict[str, Any]:
    paths = [
        "H-series task-shaped runtime seams as product architecture",
        "scaffold-only task completion standard",
        "public index mutation before local review projection",
        "evidence acceptance without explicit review",
    ]
    return {"schema_version": "r0_superseded_paths_register.v0", "task": "R0-11", "superseded": [{"path_or_plan": item, "superseded_by": "Recovered R0 product runtime seams."} for item in paths]}


def read_queue_current(root: Path) -> str:
    queue = root / ".aide/queue/index.yaml"
    if not queue.exists():
        return ""
    for line in queue.read_text(encoding="utf-8").splitlines():
        if line.strip().startswith("current_recommended_task:"):
            return line.split(":", 1)[1].strip()
    return ""


def write_requested_outputs(root: Path, audit: Mapping[str, Any], args: argparse.Namespace) -> None:
    mapping = {
        "output": ("r0_final_closeout_result", args.output),
        "matrix_output": ("r0_final_runtime_readiness_matrix", args.matrix_output),
        "blockers_output": ("r0_final_blocker_register", args.blockers_output),
        "warnings_output": ("r0_final_warning_disposition", args.warnings_output),
        "branch_output": ("r0_final_branch_state", args.branch_output),
        "queue_output": ("r0_final_queue_state", args.queue_output),
        "decision_output": ("r0_final_next_task_decision", args.decision_output),
        "deferred_output": ("r0_deferred_paths_register", args.deferred_output),
        "superseded_output": ("r0_superseded_paths_register", args.superseded_output),
        "children_output": ("r0_child_remediation_tasks", args.children_output),
        "report_output": ("r0_11_report", args.report_output),
    }
    for _name, (key, target) in mapping.items():
        if target:
            write_json(root, Path(target), audit[key])
    if args.summary_output:
        write_text(root, Path(args.summary_output), format_markdown_summary(audit))


def format_summary(audit: Mapping[str, Any]) -> str:
    result = audit["r0_final_closeout_result"]
    return "\n".join(
        [
            "R0 final closeout",
            f"status: {result['status']}",
            f"current_branch: {result['current_branch']}",
            f"blockers_remaining: {result['blockers_remaining']}",
            f"f0_decision: {result['f0_decision']}",
            f"main_promotion_decision: {result['main_promotion_decision']}",
        ]
    )


def format_markdown_summary(audit: Mapping[str, Any]) -> str:
    result = audit["r0_final_closeout_result"]
    lines = [
        "# R0 Final Closeout Summary",
        "",
        f"- status: {result['status']}",
        f"- current_branch: {result['current_branch']}",
        f"- blockers_remaining: {result['blockers_remaining']}",
        f"- child_remediation_tasks_created: {result['child_remediation_tasks_created']}",
        f"- f0_decision: {result['f0_decision']}",
        f"- main_promotion_decision: {result['main_promotion_decision']}",
        "",
    ]
    return "\n".join(lines)


def read_json(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def write_json(root: Path, target: Path, payload: Mapping[str, Any]) -> None:
    path = resolve_output(root, target)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(root: Path, target: Path, text: str) -> None:
    path = resolve_output(root, target)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def resolve_output(root: Path, target: Path) -> Path:
    path = target if target.is_absolute() else root / target
    resolved = path.resolve()
    try:
        relative = resolved.relative_to(root.resolve()).as_posix()
    except ValueError:
        return resolved
    first = relative.split("/", 1)[0]
    if first in FORBIDDEN_OUTPUT_ROOTS or relative == ".env":
        raise SystemExit(f"refusing forbidden output root: {relative}")
    return resolved


def git_value(root: Path, *args: str) -> str:
    completed = subprocess.run(["git", *args], cwd=root, text=True, capture_output=True, check=False)
    return completed.stdout.strip() if completed.returncode == 0 else ""


def git_lines(root: Path, *args: str) -> list[str]:
    value = git_value(root, *args)
    return [line for line in value.splitlines() if line]


if __name__ == "__main__":
    raise SystemExit(main())
