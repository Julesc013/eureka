#!/usr/bin/env python3
"""Audit R0 production recovery and decide F0/main-promotion gates."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[2]

GOOD_STATUSES = {"pass", "pass_with_warnings"}
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

R0_REPORTS: tuple[tuple[str, str], ...] = (
    ("R0-01", "control/audits/r0-01-dev-production-reality-inventory-v0/r0_01_report.json"),
    ("R0-02", "control/audits/r0-02-runtime-architecture-leakage-gate-v0/r0_02_report.json"),
    ("R0-03A", "control/audits/r0-03a-contract-taxonomy-refactor-plan-v0/r0_03a_report.json"),
    ("R0-03B-1", "control/audits/r0-03b-1-contract-taxonomy-migration-v0/r0_03b_1_report.json"),
    ("R0-03B-2", "control/audits/r0-03b-2-contract-reference-product-cleanup-v0/r0_03b_2_report.json"),
    ("R0-04", "control/audits/r0-04-source-observation-production-seam-v0/r0_04_report.json"),
    ("R0-05", "control/audits/r0-05-durable-source-cache-store-v0/r0_05_report.json"),
    ("R0-06", "control/audits/r0-06-durable-evidence-ledger-store-v0/r0_06_report.json"),
    ("R0-07", "control/audits/r0-07-review-queue-product-seam-v0/r0_07_report.json"),
    ("R0-08", "control/audits/r0-08-reviewed-public-index-rebuild-v0/r0_08_report.json"),
    ("R0-09", "control/audits/r0-09-one-source-live-test-v0/r0_09_report.json"),
)

RUNTIME_SEAM_INVENTORIES = {
    "source_observation": ("control/inventory/source_observation_seam_inventory.json", "ready_for_r0_05"),
    "source_cache": ("control/inventory/source_cache_store_inventory.json", "ready_for_r0_06"),
    "evidence_ledger": ("control/inventory/evidence_ledger_store_inventory.json", "ready_for_r0_07"),
    "review_queue": ("control/inventory/review_queue_store_inventory.json", "ready_for_r0_08"),
    "reviewed_public_index": ("control/inventory/public_index_store_inventory.json", "ready_for_r0_09"),
}


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--output")
    parser.add_argument("--matrix-output")
    parser.add_argument("--blockers-output")
    parser.add_argument("--warnings-output")
    parser.add_argument("--decision-output")
    parser.add_argument("--summary-output")
    parser.add_argument("--check", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    root = Path(args.repo_root).resolve()
    audit = build_r0_production_review(root)
    write_requested_outputs(root, audit, args)
    if args.json:
        print(json.dumps(audit["r0_production_review_result"], indent=2, sort_keys=True), file=stdout)
    else:
        print(format_summary(audit), file=stdout)
    return 0


def build_r0_production_review(root: Path = REPO_ROOT) -> dict[str, Any]:
    reports, report_warnings, report_blockers = load_r0_reports(root)
    blockers: list[dict[str, Any]] = list(report_blockers)
    warning_items: list[dict[str, Any]] = list(report_warnings)
    checks: list[dict[str, Any]] = []

    all_reports_good = not report_blockers and all(
        _status(reports.get(task)) in GOOD_STATUSES for task, _path in R0_REPORTS
    )
    checks.append(_check("r0_reports", "R0 task reports", True, all_reports_good, [path for _task, path in R0_REPORTS]))

    seam_ready = evaluate_runtime_seams(root, blockers, checks)
    leakage_ready = evaluate_leakage_gate(root, blockers, warning_items, checks)
    taxonomy_ready = evaluate_contract_taxonomy(root, blockers, warning_items, checks)
    live_ready = evaluate_one_source_live_test(root, blockers, warning_items, checks)

    for task, report in reports.items():
        if _status(report) == "pass_with_warnings":
            warning_items.append(
                _warning(
                    area="r0_prior_task",
                    warning=f"{task} completed with warnings",
                    disposition="assigned_to_next_task" if task in {"R0-02", "R0-03B-2"} else "harmless",
                    next_task="R0-REMEDIATION — Resolve remaining production blockers" if task in {"R0-02", "R0-03B-2"} else "",
                    notes=[f"Evidence: {report.get('recommended_next_task', '')}".strip()],
                )
            )

    f0_can_resume = (
        all_reports_good
        and all(seam_ready.values())
        and leakage_ready
        and taxonomy_ready
        and live_ready
        and not blockers
    )
    _assign_ids(blockers, "R0-PROD-BLOCKER", "blocker_id")
    dev_can_promote = f0_can_resume
    status = "pass" if f0_can_resume and dev_can_promote else "blocked"
    if warning_items and status == "pass":
        status = "pass_with_warnings"

    review_result = {
        "schema_version": "r0_production_review_result.v0",
        "task": "R0-10",
        "status": status,
        "r0_tasks_reviewed": [task for task, _path in R0_REPORTS],
        "all_required_r0_tasks_passed": all_reports_good,
        "source_observation_ready": seam_ready["source_observation"],
        "source_cache_ready": seam_ready["source_cache"],
        "evidence_ledger_ready": seam_ready["evidence_ledger"],
        "review_queue_ready": seam_ready["review_queue"],
        "reviewed_public_index_ready": seam_ready["reviewed_public_index"],
        "one_source_live_test_ready": live_ready,
        "architecture_leakage_gate_ready": leakage_ready,
        "contract_taxonomy_ready": taxonomy_ready,
        "f0_can_resume": f0_can_resume,
        "dev_can_promote_to_main": dev_can_promote,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
        "warnings": warning_items,
        "blockers": blockers,
    }
    matrix = {
        "schema_version": "r0_promotion_readiness_matrix.v0",
        "task": "R0-10",
        "checks": checks,
        "overall_promotion_status": "ready_with_warnings" if dev_can_promote and warning_items else ("ready" if dev_can_promote else "blocked"),
    }
    remaining_blockers = {
        "schema_version": "r0_remaining_blockers.v0",
        "task": "R0-10",
        "blockers": blockers,
    }
    warning_disposition = {
        "schema_version": "r0_warning_disposition.v0",
        "task": "R0-10",
        "warnings": [
            {"warning_id": f"R0-WARN-{index:03d}", **warning}
            for index, warning in enumerate(warning_items, start=1)
        ],
    }
    next_phase = {
        "schema_version": "r0_next_phase_decision.v0",
        "task": "R0-10",
        "f0_decision": "resume_f0" if f0_can_resume else "remediation_required",
        "main_promotion_decision": "promote_ready" if dev_can_promote else "remain_blocked",
        "recommended_next_task": (
            "F0-BUNDLE-01 — Deep extraction source-family and extraction-boundary policy packs"
            if f0_can_resume
            else "R0-REMEDIATION — Resolve remaining production blockers"
        ),
        "alternative_next_task": (
            "R0-REMEDIATION — Resolve remaining production blockers"
            if f0_can_resume
            else "F0-BUNDLE-01 — Deep extraction source-family and extraction-boundary policy packs"
        ),
        "reason": "All R0 product seams are ready." if f0_can_resume else "Contract taxonomy blockers remain unresolved.",
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }
    return {
        "r0_production_review_result": review_result,
        "r0_promotion_readiness_matrix": matrix,
        "r0_remaining_blockers": remaining_blockers,
        "r0_warning_disposition": warning_disposition,
        "r0_next_phase_decision": next_phase,
    }


def load_r0_reports(root: Path) -> tuple[dict[str, dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    reports: dict[str, dict[str, Any]] = {}
    warnings: list[dict[str, Any]] = []
    blockers: list[dict[str, Any]] = []
    for task, rel in R0_REPORTS:
        path = root / rel
        try:
            report = json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            blockers.append(_blocker("r0_report_missing", f"{task} report is missing", [rel], "Restore or regenerate the required R0 report."))
            continue
        except json.JSONDecodeError as exc:
            blockers.append(_blocker("r0_report_invalid", f"{task} report is invalid JSON: {exc}", [rel], "Fix the report JSON."))
            continue
        reports[task] = report
        if _status(report) not in GOOD_STATUSES:
            blockers.append(_blocker("r0_report_status", f"{task} status is {_status(report)}", [rel], "Complete remediation before promotion."))
    return reports, warnings, blockers


def evaluate_runtime_seams(root: Path, blockers: list[dict[str, Any]], checks: list[dict[str, Any]]) -> dict[str, bool]:
    result: dict[str, bool] = {}
    for area, (rel, ready_key) in RUNTIME_SEAM_INVENTORIES.items():
        payload = _read_json(root / rel)
        ready = bool(payload and payload.get(ready_key) is True)
        result[area] = ready
        checks.append(_check(area, area.replace("_", " "), True, ready, [rel]))
        if not ready:
            blockers.append(_blocker(area, f"{area} is not ready", [rel], f"Complete the {area} runtime seam."))
    return result


def evaluate_leakage_gate(root: Path, blockers: list[dict[str, Any]], warnings: list[dict[str, Any]], checks: list[dict[str, Any]]) -> bool:
    rel = "control/inventory/runtime_architecture_leakage_gate_report.json"
    payload = _read_json(root / rel)
    ready = bool(
        payload
        and payload.get("status") in GOOD_STATUSES
        and payload.get("blocker_count", 1) == 0
        and payload.get("new_violation_count", 1) == 0
        and payload.get("expired_allowlist_count", 1) == 0
    )
    checks.append(_check("architecture_leakage_gate", "architecture leakage gate", True, ready, [rel]))
    if not ready:
        blockers.append(_blocker("architecture_leakage_gate", "Architecture leakage gate has blockers or new violations.", [rel], "Resolve leakage gate blockers."))
    elif payload and payload.get("known_allowlisted_violation_count", 0):
        warnings.append(
            _warning(
                area="architecture_leakage",
                warning=f"{payload.get('known_allowlisted_violation_count')} known allowlisted legacy violations remain",
                disposition="assigned_to_next_task",
                next_task="R0-REMEDIATION — Resolve remaining production blockers",
                notes=["No new production-path leakage blockers were reported."],
            )
        )
    return ready


def evaluate_contract_taxonomy(root: Path, blockers: list[dict[str, Any]], warnings: list[dict[str, Any]], checks: list[dict[str, Any]]) -> bool:
    rel = "control/inventory/r0_03b_2_final_contract_taxonomy.json"
    payload = _read_json(root / rel)
    ready = bool(
        payload
        and payload.get("contracts_clean_enough_for_r0_04") is True
        and int(payload.get("unresolved_contract_count", 1)) == 0
        and payload.get("contracts_root_status") in {"clean", "clean_with_warnings"}
    )
    checks.append(_check("contract_taxonomy", "contract taxonomy", True, ready, [rel]))
    if not ready:
        blockers.append(
            _blocker(
                "contract_taxonomy",
                "Contract taxonomy is not clean enough for promotion.",
                [rel],
                "Resolve unresolved contract taxonomy items before F0 or main promotion.",
            )
        )
    if payload and int(payload.get("compatibility_shim_count", 0)):
        warnings.append(
            _warning(
                area="contract_taxonomy",
                warning=f"{payload.get('compatibility_shim_count')} compatibility shims remain",
                disposition="assigned_to_next_task",
                next_task="R0-REMEDIATION — Resolve remaining production blockers",
                notes=[f"contracts_root_status={payload.get('contracts_root_status')}"],
            )
        )
    return ready


def evaluate_one_source_live_test(root: Path, blockers: list[dict[str, Any]], warnings: list[dict[str, Any]], checks: list[dict[str, Any]]) -> bool:
    rel = "control/inventory/one_source_live_test_result.json"
    payload = _read_json(root / rel)
    ready = bool(
        payload
        and payload.get("status") in GOOD_STATUSES
        and payload.get("source_id") == "pypi_json_metadata"
        and payload.get("package_name") == "sampleproject"
        and payload.get("network_used") is True
        and payload.get("request_count") == 1
        and payload.get("download_count") == 0
        and payload.get("install_execution_count") == 0
        and payload.get("source_sync_used") is False
        and payload.get("search_hit_count", 0) >= 1
        and payload.get("absence_hit_count") == 0
        and payload.get("site_dist_mutated") is False
        and payload.get("master_index_mutated") is False
    )
    checks.append(_check("one_source_live_test", "one-source live test", True, ready, [rel]))
    if not ready:
        if payload and payload.get("network_used") is False and str(payload.get("reason", "")).lower().find("network") >= 0:
            warnings.append(
                _warning(
                    area="one_source_live_test",
                    warning="One-source live test was blocked by environment/network availability.",
                    disposition="not_evaluable",
                    next_task="R0-09-REMEDIATION — Complete one-source live test gaps",
                    notes=["A mocked path is not enough for promotion."],
                )
            )
        blockers.append(_blocker("one_source_live_test", "One-source live test is not ready.", [rel], "Run or remediate R0-09."))
    return ready


def write_requested_outputs(root: Path, audit: Mapping[str, Any], args: argparse.Namespace) -> None:
    outputs = {
        "output": ("r0_production_review_result", args.output),
        "matrix_output": ("r0_promotion_readiness_matrix", args.matrix_output),
        "blockers_output": ("r0_remaining_blockers", args.blockers_output),
        "warnings_output": ("r0_warning_disposition", args.warnings_output),
        "decision_output": ("r0_next_phase_decision", args.decision_output),
    }
    for _name, (key, target) in outputs.items():
        if target:
            _write_json(root, Path(target), audit[key])
    if args.summary_output:
        _write_text(root, Path(args.summary_output), format_markdown_summary(audit))


def format_summary(audit: Mapping[str, Any]) -> str:
    result = audit["r0_production_review_result"]
    return "\n".join(
        [
            "R0 production review",
            f"status: {result['status']}",
            f"f0_can_resume: {str(result['f0_can_resume']).lower()}",
            f"dev_can_promote_to_main: {str(result['dev_can_promote_to_main']).lower()}",
            f"blocker_count: {len(result['blockers'])}",
        ]
    )


def format_markdown_summary(audit: Mapping[str, Any]) -> str:
    result = audit["r0_production_review_result"]
    matrix = audit["r0_promotion_readiness_matrix"]
    lines = [
        "# R0 Production Review Summary",
        "",
        f"- status: {result['status']}",
        f"- f0_can_resume: {str(result['f0_can_resume']).lower()}",
        f"- dev_can_promote_to_main: {str(result['dev_can_promote_to_main']).lower()}",
        f"- overall_promotion_status: {matrix['overall_promotion_status']}",
        f"- blocker_count: {len(result['blockers'])}",
        "",
        "## Blockers",
    ]
    if result["blockers"]:
        lines.extend(f"- {item['area']}: {item['finding']}" for item in result["blockers"])
    else:
        lines.append("- none")
    lines.append("")
    return "\n".join(lines)


def _read_json(path: Path) -> dict[str, Any] | None:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return None
    return payload if isinstance(payload, dict) else None


def _status(report: Mapping[str, Any] | None) -> str:
    return str((report or {}).get("status", "missing")).lower()


def _check(check_id: str, area: str, required: bool, passed: bool, evidence: list[str], notes: list[str] | None = None) -> dict[str, Any]:
    return {
        "check_id": check_id,
        "area": area,
        "required": required,
        "status": "pass" if passed else "fail",
        "evidence": evidence,
        "notes": notes or [],
    }


def _blocker(area: str, finding: str, evidence: list[str], required_fix: str) -> dict[str, Any]:
    return {
        "blocker_id": "",
        "severity": "blocker",
        "area": area,
        "finding": finding,
        "evidence": evidence,
        "required_fix": required_fix,
        "blocks_f0": True,
        "blocks_main_promotion": True,
    }


def _warning(area: str, warning: str, disposition: str, next_task: str, notes: list[str]) -> dict[str, Any]:
    return {
        "area": area,
        "warning": warning,
        "disposition": disposition,
        "next_task": next_task,
        "notes": notes,
    }


def _assign_ids(items: list[dict[str, Any]], prefix: str, field: str) -> None:
    for index, item in enumerate(items, start=1):
        item[field] = f"{prefix}-{index:03d}"


def _write_json(root: Path, target: Path, payload: Mapping[str, Any]) -> None:
    path = _resolve_output(root, target)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _write_text(root: Path, target: Path, text: str) -> None:
    path = _resolve_output(root, target)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def _resolve_output(root: Path, target: Path) -> Path:
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


if __name__ == "__main__":
    raise SystemExit(main())
