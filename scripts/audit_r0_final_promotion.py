#!/usr/bin/env python3
"""Audit final R0 dev-to-main promotion readiness from repo-local evidence."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[1]

TASK_ID = "R0-FINAL-PROMOTION-REVIEW"
GOOD_STATUSES = {"pass", "pass_with_warnings", "partial"}
BLOCKING_STATUS_VALUES = {"fail", "blocked"}

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

FORBIDDEN_CHANGED_ROOTS = (
    "runtime/",
    "contracts/",
    "surfaces/",
    "site/",
    "native/",
    "crates/",
    "examples/",
    "control/prototypes/",
    "secrets/",
    ".aide.local/",
    ".local/",
    ".cache/",
)

ALLOWED_TASK_PATHS = (
    "control/inventory/r0_final_promotion_review_result.json",
    "control/inventory/r0_final_promotion_readiness_matrix.json",
    "control/inventory/r0_final_promotion_blockers.json",
    "control/inventory/r0_final_promotion_warning_disposition.json",
    "control/inventory/r0_final_promotion_git_state.json",
    "control/inventory/r0_final_promotion_next_task_decision.json",
    "scripts/audit_r0_final_promotion.py",
    "scripts/validate_r0_final_promotion.py",
    "scripts/prepare_r0_dev_to_main_merge.py",
    "tests/operations/test_r0_final_promotion.py",
    "tests/operations/test_r0_dev_to_main_merge_plan.py",
    "docs/operations/R0_FINAL_PROMOTION_REVIEW.md",
    "docs/operations/DEV_TO_MAIN_R0_PROMOTION_PLAN.md",
    "docs/operations/F0_START_BRANCH_POLICY.md",
    "control/audits/r0-final-promotion-review-v0/",
    ".aide/context/latest-task-packet.md",
    "aide/context/latest-task-packet.md",
    ".aide/context/latest-review-packet.md",
    "aide/context/latest-review-packet.md",
    ".aide/reports/eureka-repo-health.json",
    ".aide/reports/eureka-repo-health.md",
    ".aide/queue/index.yaml",
)

PROMOTION_INVENTORIES = {
    "final_closeout": Path("control/inventory/r0_final_closeout_result.json"),
    "final_blockers": Path("control/inventory/r0_final_blocker_register.json"),
    "final_warnings": Path("control/inventory/r0_final_warning_disposition.json"),
    "production_review": Path("control/inventory/r0_production_review_result.json"),
    "remaining_blockers": Path("control/inventory/r0_remaining_blockers.json"),
    "r0_warnings": Path("control/inventory/r0_warning_disposition.json"),
    "contract_taxonomy": Path("control/inventory/r0_contract_taxonomy_remediation_result.json"),
    "generated_artifacts": Path("control/inventory/r0_generated_artifact_remediation_result.json"),
    "legacy_leakage": Path("control/inventory/legacy_runtime_leakage_remediation_result.json"),
}

R0_RUNTIME_READY_FIELDS = (
    "source_observation_ready",
    "source_cache_ready",
    "evidence_ledger_ready",
    "review_queue_ready",
    "reviewed_public_index_ready",
    "one_source_live_test_ready",
)

FORBIDDEN_CLAIM_ROOTS = (
    Path("control/inventory"),
    Path("control/audits"),
    Path("docs/operations"),
)

CLAIM_SCAN_ALLOWED_PREFIXES = (
    "control/inventory/r0",
    "control/inventory/legacy_runtime_leakage",
    "control/inventory/generated_artifact",
    "control/inventory/runtime_architecture_leakage",
    "control/inventory/one_source_live_test",
    "control/inventory/source_observation",
    "control/inventory/source_cache",
    "control/inventory/evidence_ledger",
    "control/inventory/review_queue",
    "control/inventory/public_index",
    "control/audits/r0-",
    "control/audits/r0-final-promotion-review-v0/",
    "docs/operations/R0_",
    "docs/operations/DEV_TO_MAIN_R0_PROMOTION_PLAN.md",
    "docs/operations/F0_START_BRANCH_POLICY.md",
)

POSITIVE_CLAIM_PATTERNS = (
    ("deployment_completed", re.compile(r"\bdeployment completed\b", re.IGNORECASE)),
    ("hosted_search_ready", re.compile(r"\bhosted search ready\b", re.IGNORECASE)),
    ("legal_approval", re.compile(r"\blegal approval (granted|approved|complete|completed)\b", re.IGNORECASE)),
    ("rights_clearance", re.compile(r"\brights clearance (granted|approved|complete|completed)\b", re.IGNORECASE)),
    ("malware_safety", re.compile(r"\bmalware safety (approved|complete|completed|guaranteed)\b", re.IGNORECASE)),
    ("exhaustive_source_coverage", re.compile(r"\bexhaustive source coverage\b", re.IGNORECASE)),
    ("production_ready", re.compile(r"\bproduction ready\b", re.IGNORECASE)),
    ("public_launch_ready", re.compile(r"\bpublic launch ready\b", re.IGNORECASE)),
)

NEGATING_WORDS = ("no ", "not ", "does not ", "do not ", "must not ", "without ", "is not ")


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--output")
    parser.add_argument("--matrix-output")
    parser.add_argument("--git-state-output")
    parser.add_argument("--blockers-output")
    parser.add_argument("--warnings-output")
    parser.add_argument("--decision-output")
    parser.add_argument("--report-output")
    parser.add_argument("--summary-output")
    parser.add_argument("--fetch", action="store_true", help="Fetch origin before reading remote refs.")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    root = Path(args.repo_root).resolve()
    audit = build_final_promotion(root, fetch=args.fetch)
    write_requested_outputs(root, audit, args)
    result = audit["r0_final_promotion_review_result"]
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print(format_summary(audit), file=stdout)
    if args.check and (result["hard_blockers_remaining"] or result["production_readiness_claimed"] or result["public_launch_readiness_claimed"]):
        return 1
    return 0


def build_final_promotion(root: Path = REPO_ROOT, *, fetch: bool = False) -> dict[str, Any]:
    git_state = build_git_state(root, fetch=fetch)
    evidence = {key: read_json(root / rel) for key, rel in PROMOTION_INVENTORIES.items()}
    claim_findings = find_forbidden_claims(root)
    warning_disposition = classify_warnings(evidence)
    checks = build_readiness_checks(git_state, evidence, claim_findings, warning_disposition)
    blockers = build_blockers(checks, git_state, claim_findings, evidence)

    full_unittest_pass = check_passed(checks, "full_unittest_discovery")
    generated_cleanliness_pass = check_passed(checks, "generated_artifact_cleanliness")
    architecture_pass = check_passed(checks, "architecture_boundaries")
    r0_validators_pass = check_passed(checks, "r0_validators")
    warnings_fully_disposed = all(
        item["classification"] in {"harmless_for_promotion", "child_task_created", "deferred_with_expiry"}
        for item in warning_disposition["warnings"]
    )
    r0_ready_for_f0 = all(
        check_passed(checks, check_id)
        for check_id in (
            "r0_final_closeout",
            "runtime_seams",
            "contract_taxonomy_remediation",
            "generated_artifact_drift",
            "legacy_runtime_leakage",
            "full_unittest_discovery",
            "generated_artifact_cleanliness",
            "architecture_boundaries",
            "r0_validators",
            "no_forbidden_claims",
        )
    )
    promotion_ready = (
        r0_ready_for_f0
        and git_state["working_tree_clean"]
        and git_state["dev_synced_to_origin"]
        and git_state["dev_contains_main"]
        and git_state["current_branch_equals_dev"]
        and not blockers
        and warnings_fully_disposed
    )
    current_branch = git_state["current_branch"]
    if current_branch == "main":
        dev_to_main_decision = "already_on_main"
    elif promotion_ready:
        dev_to_main_decision = "promotion_plan_only"
    else:
        dev_to_main_decision = "remain_blocked"
    f0_decision = "resume_f0" if r0_ready_for_f0 and not claim_findings else "remediation_required"
    if current_branch not in {"dev", "main"}:
        f0_decision = "remain_blocked"

    status = "blocked" if blockers else ("pass_with_warnings" if warning_disposition["warnings"] else "pass")
    production_claimed = any(item["claim"] == "production_readiness_claimed" for item in claim_findings)
    public_launch_claimed = any(item["claim"] == "public_launch_readiness_claimed" for item in claim_findings)

    result = {
        "schema_version": "r0_final_promotion_review_result.v0",
        "task": TASK_ID,
        "status": status,
        "current_branch": current_branch,
        "working_tree_clean": git_state["working_tree_clean"],
        "dev_synced_to_origin": git_state["dev_synced_to_origin"],
        "dev_contains_main": git_state["dev_contains_main"],
        "full_unittest_discovery_pass": full_unittest_pass,
        "generated_artifact_cleanliness_pass": generated_cleanliness_pass,
        "architecture_boundary_checks_pass": architecture_pass,
        "r0_validators_pass": r0_validators_pass,
        "warnings_fully_disposed": warnings_fully_disposed,
        "hard_blockers_remaining": len(blockers),
        "dev_to_main_decision": dev_to_main_decision,
        "f0_decision": f0_decision,
        "branch_mutation_performed": False,
        "production_readiness_claimed": production_claimed,
        "public_launch_readiness_claimed": public_launch_claimed,
        "promotion_ready": promotion_ready,
        "promotion_plan_only": dev_to_main_decision == "promotion_plan_only",
        "merge_performed": False,
        "push_main_performed": False,
    }

    matrix = {
        "schema_version": "r0_final_promotion_readiness_matrix.v0",
        "task": TASK_ID,
        "overall_status": "ready_with_warnings" if promotion_ready and warning_disposition["warnings"] else ("ready" if promotion_ready else "blocked"),
        "promotion_ready": promotion_ready,
        "promotion_plan_only": dev_to_main_decision == "promotion_plan_only",
        "branch_mutation_performed": False,
        "checks": checks,
    }
    blockers_payload = {
        "schema_version": "r0_final_promotion_blockers.v0",
        "task": TASK_ID,
        "hard_blocker_count": len(blockers),
        "blockers": blockers,
    }
    next_task = build_next_task_decision(result, git_state)
    report = {
        "schema_version": "r0_final_promotion_review_report.v0",
        "status": result["status"],
        "task": TASK_ID,
        "purpose": "final_dev_to_main_promotion_review_before_f0",
        "current_branch": current_branch,
        "origin_dev": git_state["origin_dev"],
        "origin_main": git_state["origin_main"],
        "working_tree_clean": git_state["working_tree_clean"],
        "dev_synced_to_origin": git_state["dev_synced_to_origin"],
        "dev_contains_main": git_state["dev_contains_main"],
        "full_unittest_discovery_pass": full_unittest_pass,
        "generated_artifact_cleanliness_pass": generated_cleanliness_pass,
        "architecture_boundary_checks_pass": architecture_pass,
        "r0_validators_pass": r0_validators_pass,
        "hard_blockers_remaining": len(blockers),
        "warnings_fully_disposed": warnings_fully_disposed,
        "dev_to_main_decision": dev_to_main_decision,
        "f0_decision": f0_decision,
        "branch_mutation_performed": False,
        "production_readiness_claimed": production_claimed,
        "public_launch_readiness_claimed": public_launch_claimed,
        "validation": {},
    }
    return {
        "r0_final_promotion_review_result": result,
        "r0_final_promotion_readiness_matrix": matrix,
        "r0_final_promotion_blockers": blockers_payload,
        "r0_final_promotion_warning_disposition": warning_disposition,
        "r0_final_promotion_git_state": git_state,
        "r0_final_promotion_next_task_decision": next_task,
        "promotion_review_report": report,
    }


def build_git_state(root: Path, *, fetch: bool) -> dict[str, Any]:
    if fetch:
        subprocess.run(["git", "fetch", "origin"], cwd=root, text=True, capture_output=True, check=False)
    current_branch = git_value(root, "branch", "--show-current")
    head = git_value(root, "rev-parse", "HEAD")
    local_dev = git_value(root, "rev-parse", "dev")
    origin_dev = git_value(root, "rev-parse", "origin/dev")
    origin_main = git_value(root, "rev-parse", "origin/main")
    status_lines = git_lines(root, "status", "--porcelain=v1")
    changed_paths = parse_status_paths(status_lines)
    forbidden_changed_paths = [path for path in changed_paths if path.startswith(FORBIDDEN_CHANGED_ROOTS) or path == ".env"]
    non_task_changed_paths = [path for path in changed_paths if not is_allowed_task_path(path)]
    local_ahead_paths = git_lines(root, "diff", "--name-only", "origin/dev...dev") if origin_dev and local_dev else []
    local_ahead_non_task_paths = [path.replace("\\", "/") for path in local_ahead_paths if not is_allowed_task_path(path.replace("\\", "/"))]
    local_dev_contains_origin_dev = git_returncode(root, "merge-base", "--is-ancestor", "origin/dev", "dev") == 0 if origin_dev and local_dev else False
    actual_clean = not status_lines
    review_clean = actual_clean or (not forbidden_changed_paths and not non_task_changed_paths)
    strict_dev_synced = bool(origin_dev and local_dev == origin_dev and (current_branch != "dev" or head == origin_dev))
    review_artifact_only_ahead = bool(
        origin_dev
        and local_dev
        and local_dev_contains_origin_dev
        and local_dev != origin_dev
        and not local_ahead_non_task_paths
    )
    left_right = parse_left_right(git_value(root, "rev-list", "--left-right", "--count", "origin/main...origin/dev"))
    dev_contains_main = git_returncode(root, "merge-base", "--is-ancestor", "origin/main", "origin/dev") == 0
    log_lines = git_lines(root, "log", "--oneline", "--decorate", "-10")
    return {
        "schema_version": "r0_final_promotion_git_state.v0",
        "task": TASK_ID,
        "current_branch": current_branch,
        "head": head,
        "local_dev": local_dev,
        "origin_dev": origin_dev,
        "origin_main": origin_main,
        "origin_main_only_commit_count": left_right["left"],
        "origin_dev_only_commit_count": left_right["right"],
        "dev_contains_main": dev_contains_main,
        "current_branch_equals_dev": current_branch == "dev",
        "working_tree_clean": review_clean,
        "working_tree_actual_clean": actual_clean,
        "working_tree_changed_paths": changed_paths,
        "working_tree_non_task_changed_paths": non_task_changed_paths,
        "forbidden_changed_paths": forbidden_changed_paths,
        "local_ahead_of_origin_dev_paths": local_ahead_paths,
        "local_ahead_of_origin_dev_non_task_paths": local_ahead_non_task_paths,
        "local_dev_contains_origin_dev": local_dev_contains_origin_dev,
        "dev_synced_to_origin": strict_dev_synced or review_artifact_only_ahead,
        "dev_synced_to_origin_strict": strict_dev_synced,
        "dev_sync_interpretation": (
            "strict"
            if strict_dev_synced
            else (
                "origin/dev is the reviewed recovered R0 baseline; local dev is ahead only by final promotion review artifacts"
                if review_artifact_only_ahead
                else "not_synced"
            )
        ),
        "head_equals_origin_dev": bool(origin_dev and head == origin_dev),
        "log_oneline_decorate_10": log_lines,
        "branch_mutation_performed": False,
        "merge_performed": False,
        "push_main_performed": False,
    }


def build_readiness_checks(
    git_state: Mapping[str, Any],
    evidence: Mapping[str, Any],
    claim_findings: list[dict[str, Any]],
    warning_disposition: Mapping[str, Any],
) -> list[dict[str, Any]]:
    final_closeout = evidence.get("final_closeout") or {}
    production_review = evidence.get("production_review") or {}
    contract_taxonomy = evidence.get("contract_taxonomy") or {}
    generated_artifacts = evidence.get("generated_artifacts") or {}
    legacy_leakage = evidence.get("legacy_leakage") or {}
    final_blockers = (evidence.get("final_blockers") or {}).get("blockers", [])
    remaining_blockers = (evidence.get("remaining_blockers") or {}).get("blockers", [])

    full_unittest_pass = final_closeout.get("full_unittest_discovery_pass") is True and generated_artifacts.get("full_unittest_discovery_pass") is True
    generated_clean = (
        generated_artifacts.get("generated_artifact_cleanliness_pass") is True
        or (
            generated_artifacts.get("generated_artifact_drift_resolved") is True
            and generated_artifacts.get("site_dist_clean") is True
        )
    )
    architecture_pass = final_closeout.get("architecture_boundary_checks_pass") is True and generated_artifacts.get("architecture_boundary_checks_pass") is True
    validators_pass = final_closeout.get("all_required_validators_pass") is True
    runtime_ready = all(final_closeout.get(field) is True or production_review.get(field) is True for field in R0_RUNTIME_READY_FIELDS)
    contract_ready = (
        contract_taxonomy.get("unresolved_after") == 0
        and contract_taxonomy.get("compatibility_shims_after") == 0
        and contract_taxonomy.get("contracts_clean_enough_for_f0") is True
        and contract_taxonomy.get("production_readiness_claimed") is False
        and contract_taxonomy.get("public_launch_readiness_claimed") is False
    )
    generated_ready = (
        generated_artifacts.get("generated_artifact_drift_resolved") is True
        and generated_artifacts.get("production_readiness_claimed") is False
        and generated_artifacts.get("public_launch_readiness_claimed") is False
    )
    legacy_ready = (
        legacy_leakage.get("new_unallowlisted_leaks") == 0
        and legacy_leakage.get("clean_r0_seams_still_clean") is True
        and legacy_leakage.get("production_readiness_claimed") is False
        and legacy_leakage.get("public_launch_readiness_claimed") is False
    )
    closeout_ready = (
        final_closeout.get("f0_decision") == "resume_f0"
        and int(final_closeout.get("blockers_remaining", 1)) == 0
        and final_closeout.get("warnings_fully_disposed") is True
        and final_closeout.get("production_readiness_claimed") is False
        and final_closeout.get("public_launch_readiness_claimed") is False
    )
    warnings_ready = all(
        item["classification"] in {"harmless_for_promotion", "child_task_created", "deferred_with_expiry"}
        for item in warning_disposition["warnings"]
    )
    no_hard_blockers = not final_blockers and not remaining_blockers
    no_claims = not claim_findings

    checks = [
        check("current_branch_dev", "git", git_state["current_branch_equals_dev"], [f"current_branch={git_state['current_branch']}"]),
        check("working_tree_clean", "git", git_state["working_tree_clean"], git_state.get("working_tree_changed_paths", [])),
        check("dev_synced_to_origin", "git", git_state["dev_synced_to_origin"], [f"local_dev={git_state.get('local_dev')}", f"origin_dev={git_state.get('origin_dev')}"]),
        check("dev_contains_main", "git", git_state["dev_contains_main"], [f"origin_main={git_state.get('origin_main')}", f"origin_dev={git_state.get('origin_dev')}"]),
        check("r0_final_closeout", "r0", closeout_ready, [str(PROMOTION_INVENTORIES["final_closeout"])]),
        check("runtime_seams", "r0", runtime_ready, list(R0_RUNTIME_READY_FIELDS)),
        check("contract_taxonomy_remediation", "r0", contract_ready, [str(PROMOTION_INVENTORIES["contract_taxonomy"])]),
        check("generated_artifact_drift", "r0", generated_ready, [str(PROMOTION_INVENTORIES["generated_artifacts"])]),
        check("legacy_runtime_leakage", "r0", legacy_ready, [str(PROMOTION_INVENTORIES["legacy_leakage"])]),
        check("full_unittest_discovery", "validation", full_unittest_pass, [str(PROMOTION_INVENTORIES["final_closeout"]), str(PROMOTION_INVENTORIES["generated_artifacts"])]),
        check("generated_artifact_cleanliness", "validation", generated_clean, [str(PROMOTION_INVENTORIES["generated_artifacts"])]),
        check("architecture_boundaries", "validation", architecture_pass, [str(PROMOTION_INVENTORIES["final_closeout"]), str(PROMOTION_INVENTORIES["generated_artifacts"])]),
        check("r0_validators", "validation", validators_pass, [str(PROMOTION_INVENTORIES["final_closeout"])]),
        check("no_hard_blockers", "blockers", no_hard_blockers, [str(PROMOTION_INVENTORIES["final_blockers"]), str(PROMOTION_INVENTORIES["remaining_blockers"])]),
        check("warning_disposition", "warnings", warnings_ready, ["r0_final_promotion_warning_disposition"]),
        check("no_forbidden_claims", "claims", no_claims, [item["path"] for item in claim_findings]),
        check("no_forbidden_path_changes", "scope", not git_state.get("forbidden_changed_paths"), git_state.get("forbidden_changed_paths", [])),
    ]
    return checks


def build_blockers(
    checks: Sequence[Mapping[str, Any]],
    git_state: Mapping[str, Any],
    claim_findings: list[dict[str, Any]],
    evidence: Mapping[str, Any],
) -> list[dict[str, Any]]:
    blockers: list[dict[str, Any]] = []
    for item in checks:
        if item["status"] == "pass":
            continue
        check_id = str(item["check_id"])
        if check_id == "warning_disposition":
            continue
        blockers.append(
            {
                "blocker_id": f"R0-FINAL-PROMOTION-BLOCKER-{len(blockers) + 1:03d}",
                "severity": "blocker",
                "area": item["category"],
                "finding": f"{check_id} did not pass",
                "evidence": item.get("evidence", []),
                "required_fix": blocker_fix(check_id),
                "blocks_promotion": True,
                "blocks_f0": check_id in {"r0_final_closeout", "runtime_seams", "contract_taxonomy_remediation", "generated_artifact_drift", "full_unittest_discovery", "architecture_boundaries", "r0_validators", "no_forbidden_claims"},
            }
        )
    for path in git_state.get("forbidden_changed_paths", []):
        blockers.append(
            {
                "blocker_id": f"R0-FINAL-PROMOTION-BLOCKER-{len(blockers) + 1:03d}",
                "severity": "blocker",
                "area": "scope",
                "finding": f"forbidden path changed: {path}",
                "evidence": [path],
                "required_fix": "Revert or move changes out of forbidden product/runtime paths for this review task.",
                "blocks_promotion": True,
                "blocks_f0": True,
            }
        )
    for claim in claim_findings:
        blockers.append(
            {
                "blocker_id": f"R0-FINAL-PROMOTION-BLOCKER-{len(blockers) + 1:03d}",
                "severity": "blocker",
                "area": "claims",
                "finding": f"forbidden claim detected: {claim['claim']}",
                "evidence": [f"{claim['path']}:{claim.get('line', 0)}"],
                "required_fix": "Remove production, public launch, deployment, approval, safety, or exhaustive-coverage claim.",
                "blocks_promotion": True,
                "blocks_f0": True,
            }
        )
    for source_key in ("final_blockers", "remaining_blockers"):
        for blocker in (evidence.get(source_key) or {}).get("blockers", []):
            blockers.append(
                {
                    "blocker_id": f"R0-FINAL-PROMOTION-BLOCKER-{len(blockers) + 1:03d}",
                    "severity": blocker.get("severity", "blocker"),
                    "area": blocker.get("area", source_key),
                    "finding": blocker.get("finding", "R0 hard blocker remains."),
                    "evidence": blocker.get("evidence", []),
                    "required_fix": blocker.get("required_fix", "Resolve the inherited R0 blocker."),
                    "blocks_promotion": True,
                    "blocks_f0": blocker.get("blocks_f0", True),
                }
            )
    return dedupe_blockers(blockers)


def classify_warnings(evidence: Mapping[str, Any]) -> dict[str, Any]:
    source_warnings: list[Mapping[str, Any]] = []
    source_warnings.extend((evidence.get("final_warnings") or {}).get("warnings", []))
    existing_ids: set[str] = set()
    warnings: list[dict[str, Any]] = []
    for index, item in enumerate(source_warnings, start=1):
        warning_id = str(item.get("warning_id") or f"R0-FINAL-PROMOTION-WARN-{index:03d}")
        existing_ids.add(warning_id)
        area = str(item.get("area", "unknown"))
        source_disposition = str(item.get("disposition", ""))
        classification = map_warning_classification(area, source_disposition, str(item.get("warning", "")))
        child_task = str(item.get("child_task", ""))
        warnings.append(
            {
                "warning_id": warning_id,
                "area": area,
                "warning": item.get("warning", "Unclassified warning."),
                "source_disposition": source_disposition,
                "classification": classification,
                "child_task": child_task,
                "expiry": "before production/public launch readiness review" if classification == "deferred_with_expiry" else "",
                "blocks_promotion": classification == "blocks_promotion",
                "blocks_f0": classification == "blocks_f0",
                "notes": item.get("notes", []),
            }
        )
    legacy = evidence.get("legacy_leakage") or {}
    remaining_allowlist = int(legacy.get("remaining_allowlist_count", 0) or 0)
    if remaining_allowlist and "R0-FINAL-PROMOTION-WARN-LEGACY-ALLOWLIST" not in existing_ids:
        warnings.append(
            {
                "warning_id": "R0-FINAL-PROMOTION-WARN-LEGACY-ALLOWLIST",
                "area": "architecture_leakage",
                "warning": f"{remaining_allowlist} legacy leakage allowlist entries remain after remediation",
                "source_disposition": "pass_with_warnings",
                "classification": "deferred_with_expiry",
                "child_task": "R0-REMEDIATION-LEGACY-LEAKAGE-01",
                "expiry": "before production/public launch readiness review",
                "blocks_promotion": False,
                "blocks_f0": False,
                "notes": [
                    "R0 runtime seams remain clean and no new unallowlisted leaks were reported.",
                    "This is warning-level debt for promotion, not a recovered-baseline blocker.",
                ],
            }
        )
    return {
        "schema_version": "r0_final_promotion_warning_disposition.v0",
        "task": TASK_ID,
        "warnings_fully_disposed": all(item["classification"] not in {"blocks_promotion", "blocks_f0"} for item in warnings),
        "warnings": warnings,
    }


def map_warning_classification(area: str, disposition: str, warning: str) -> str:
    text = f"{area} {disposition} {warning}".lower()
    if "blocks_promotion" in text:
        return "blocks_promotion"
    if "blocks_f0" in text:
        return "blocks_f0"
    if disposition in {"fixed", "harmless", "harmless_for_promotion"}:
        return "harmless_for_promotion"
    if disposition == "child_task_created" or "child_task" in text:
        return "child_task_created"
    if "allowlist" in text or "legacy" in text or "architecture_leakage" in text:
        return "deferred_with_expiry"
    if disposition in {"assigned_to_next_task", "not_evaluable"}:
        return "child_task_created"
    return "harmless_for_promotion"


def build_next_task_decision(result: Mapping[str, Any], git_state: Mapping[str, Any]) -> dict[str, Any]:
    promotion_ready = result["promotion_ready"]
    if result["f0_decision"] != "resume_f0":
        recommended_next = "R0-PROMOTION-REMEDIATION — Resolve final promotion blockers"
        reason = "Final promotion review found blockers that also affect F0 readiness."
        recommended_start_branch = "dev"
    elif promotion_ready and result["dev_to_main_decision"] == "promotion_plan_only":
        recommended_next = "DEV-TO-MAIN-MERGE-R0 — Promote recovered R0 dev to main"
        reason = "R0 is ready and main remains intentionally behind until an explicit merge/apply action."
        recommended_start_branch = "dev"
    else:
        recommended_next = "F0-BUNDLE-01 — Deep extraction source-family and extraction-boundary policy packs"
        reason = "R0 can resume into F0 from the recovered runtime baseline."
        recommended_start_branch = "main" if git_state["current_branch"] == "main" else "dev"
    return {
        "schema_version": "r0_final_promotion_next_task_decision.v0",
        "task": TASK_ID,
        "f0_decision": result["f0_decision"],
        "dev_to_main_decision": result["dev_to_main_decision"],
        "recommended_next_task": recommended_next,
        "alternative_next_task": "F0-BUNDLE-01 — Deep extraction source-family and extraction-boundary policy packs",
        "recommended_start_branch": recommended_start_branch,
        "reason": reason,
        "f0_must_use_r0_runtime_seams": True,
        "f0_must_not_reintroduce_scaffold_only_completion": True,
        "branch_mutation_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def check(check_id: str, category: str, passed: bool, evidence: Sequence[str]) -> dict[str, Any]:
    return {
        "check_id": check_id,
        "category": category,
        "required": True,
        "status": "pass" if passed else "fail",
        "evidence": list(evidence),
        "blocks_promotion": not passed,
    }


def check_passed(checks: Sequence[Mapping[str, Any]], check_id: str) -> bool:
    for item in checks:
        if item.get("check_id") == check_id:
            return item.get("status") == "pass"
    return False


def blocker_fix(check_id: str) -> str:
    fixes = {
        "current_branch_dev": "Run the final review from dev or explicitly document already-on-main state.",
        "working_tree_clean": "Clear uncommitted non-review changes before promotion.",
        "dev_synced_to_origin": "Sync local dev with origin/dev before promotion.",
        "dev_contains_main": "Merge or rebase main into dev through the repo integration workflow before promotion.",
        "r0_final_closeout": "Restore a passing R0 final closeout inventory.",
        "runtime_seams": "Restore passing R0 runtime seam evidence.",
        "contract_taxonomy_remediation": "Resolve remaining contract taxonomy blockers.",
        "generated_artifact_drift": "Resolve generated artifact drift and rerun cleanliness checks.",
        "legacy_runtime_leakage": "Remove new unallowlisted leakage and keep R0 seams clean.",
        "full_unittest_discovery": "Run and fix full unittest discovery.",
        "generated_artifact_cleanliness": "Run and fix generated artifact cleanliness.",
        "architecture_boundaries": "Run and fix architecture boundary checks.",
        "r0_validators": "Run and fix R0 validators.",
        "no_hard_blockers": "Resolve hard R0 blocker inventories.",
        "no_forbidden_claims": "Remove forbidden readiness, launch, deployment, approval, safety, or exhaustive coverage claims.",
        "no_forbidden_path_changes": "Keep this review scoped to allowed paths only.",
    }
    return fixes.get(check_id, "Resolve the failed promotion readiness check.")


def find_forbidden_claims(root: Path) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for base in FORBIDDEN_CLAIM_ROOTS:
        path = root / base
        if not path.exists():
            continue
        for file_path in path.rglob("*"):
            if file_path.suffix.lower() not in {".json", ".md", ".txt"} or not file_path.is_file():
                continue
            rel = file_path.relative_to(root).as_posix()
            if not rel.startswith(CLAIM_SCAN_ALLOWED_PREFIXES):
                continue
            try:
                text = file_path.read_text(encoding="utf-8")
            except UnicodeDecodeError:
                continue
            findings.extend(find_claims_in_text(rel, text))
    return findings


def find_claims_in_text(rel: str, text: str) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        lowered = line.lower()
        if re.search(r'"production_readiness_claimed"\s*:\s*true', line, re.IGNORECASE):
            findings.append({"claim": "production_readiness_claimed", "path": rel, "line": line_number, "text": line.strip()})
        if re.search(r'"public_launch_readiness_claimed"\s*:\s*true', line, re.IGNORECASE):
            findings.append({"claim": "public_launch_readiness_claimed", "path": rel, "line": line_number, "text": line.strip()})
        for claim, pattern in POSITIVE_CLAIM_PATTERNS:
            if pattern.search(line) and not has_nearby_negation(lowered, pattern):
                findings.append({"claim": claim, "path": rel, "line": line_number, "text": line.strip()})
    return findings


def has_nearby_negation(lowered_line: str, pattern: re.Pattern[str]) -> bool:
    match = pattern.search(lowered_line)
    if not match:
        return False
    prefix = lowered_line[max(0, match.start() - 240) : match.start()]
    return any(word in prefix for word in NEGATING_WORDS)


def dedupe_blockers(blockers: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    seen: set[tuple[str, str]] = set()
    result: list[dict[str, Any]] = []
    for item in blockers:
        key = (str(item.get("area")), str(item.get("finding")))
        if key in seen:
            continue
        seen.add(key)
        copied = dict(item)
        copied["blocker_id"] = f"R0-FINAL-PROMOTION-BLOCKER-{len(result) + 1:03d}"
        result.append(copied)
    return result


def write_requested_outputs(root: Path, audit: Mapping[str, Any], args: argparse.Namespace) -> None:
    outputs = {
        "output": ("r0_final_promotion_review_result", args.output),
        "matrix_output": ("r0_final_promotion_readiness_matrix", args.matrix_output),
        "git_state_output": ("r0_final_promotion_git_state", args.git_state_output),
        "blockers_output": ("r0_final_promotion_blockers", args.blockers_output),
        "warnings_output": ("r0_final_promotion_warning_disposition", args.warnings_output),
        "decision_output": ("r0_final_promotion_next_task_decision", args.decision_output),
        "report_output": ("promotion_review_report", args.report_output),
    }
    for _name, (key, target) in outputs.items():
        if target:
            write_json(root, Path(target), audit[key])
    if args.summary_output:
        write_text(root, Path(args.summary_output), format_markdown_summary(audit))


def format_summary(audit: Mapping[str, Any]) -> str:
    result = audit["r0_final_promotion_review_result"]
    return "\n".join(
        [
            "R0 final promotion review",
            f"status: {result['status']}",
            f"current_branch: {result['current_branch']}",
            f"dev_to_main_decision: {result['dev_to_main_decision']}",
            f"f0_decision: {result['f0_decision']}",
            f"hard_blockers_remaining: {result['hard_blockers_remaining']}",
            "branch_mutation_performed: false",
        ]
    )


def format_markdown_summary(audit: Mapping[str, Any]) -> str:
    result = audit["r0_final_promotion_review_result"]
    lines = [
        "# R0 Final Promotion Summary",
        "",
        f"- status: {result['status']}",
        f"- current_branch: {result['current_branch']}",
        f"- dev_to_main_decision: {result['dev_to_main_decision']}",
        f"- f0_decision: {result['f0_decision']}",
        f"- hard_blockers_remaining: {result['hard_blockers_remaining']}",
        f"- branch_mutation_performed: {str(result['branch_mutation_performed']).lower()}",
        "",
    ]
    return "\n".join(lines)


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


def read_json(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def git_value(root: Path, *args: str) -> str:
    completed = subprocess.run(["git", *args], cwd=root, text=True, capture_output=True, check=False)
    return completed.stdout.strip() if completed.returncode == 0 else ""


def git_returncode(root: Path, *args: str) -> int:
    completed = subprocess.run(["git", *args], cwd=root, text=True, capture_output=True, check=False)
    return completed.returncode


def git_lines(root: Path, *args: str) -> list[str]:
    value = git_value(root, *args)
    return [line for line in value.splitlines() if line]


def parse_left_right(value: str) -> dict[str, int]:
    parts = value.split()
    if len(parts) != 2:
        return {"left": -1, "right": -1}
    try:
        return {"left": int(parts[0]), "right": int(parts[1])}
    except ValueError:
        return {"left": -1, "right": -1}


def parse_status_paths(lines: Sequence[str]) -> list[str]:
    paths: list[str] = []
    for line in lines:
        if len(line) < 4:
            continue
        raw = line[3:].replace("\\", "/").strip('"')
        if " -> " in raw:
            paths.extend(part.strip('"') for part in raw.split(" -> "))
        else:
            paths.append(raw)
    return paths


def is_allowed_task_path(path: str) -> bool:
    normalized = path.replace("\\", "/").strip('"')
    return any(normalized == allowed.rstrip("/") or normalized.startswith(allowed) for allowed in ALLOWED_TASK_PATHS)


if __name__ == "__main__":
    raise SystemExit(main())
