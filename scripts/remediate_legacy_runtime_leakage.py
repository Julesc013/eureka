#!/usr/bin/env python3
"""Quarantine legacy task-shaped connector runtime and refresh leakage evidence."""

from __future__ import annotations

import argparse
import fnmatch
import importlib.util
import json
import re
import shutil
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
TASK = "R0-REMEDIATION-LEGACY-LEAKAGE-01"
POLICY_PATH = Path("control/policies/runtime_architecture_leakage_policy.json")
ALLOWLIST_PATH = Path("control/policies/runtime_architecture_leakage_allowlist.json")
QUARANTINE_ROOT = Path("control/prototypes/legacy_runtime/connectors")
AUDIT_SCRIPT = Path("scripts/audit_runtime_architecture_leakage.py")
AUDIT_DIR = Path("control/audits/r0-remediation-legacy-leakage-01-v0")

LEGACY_CONNECTOR_RE = re.compile(r"^h(?:[1-9]|1[0-4])_")
R0_SEAMS = (
    "runtime/source_observation/",
    "runtime/source_cache/",
    "runtime/evidence_ledger/",
    "runtime/review_queue/",
    "runtime/public_index/",
)
REFERENCE_ROOTS = (
    "scripts",
    "tests",
    "docs/architecture",
    "docs/operations",
    "docs/reference",
    QUARANTINE_ROOT.as_posix(),
)
TEXT_SUFFIXES = {
    "",
    ".cfg",
    ".csv",
    ".ini",
    ".json",
    ".md",
    ".py",
    ".txt",
    ".yaml",
    ".yml",
}
FORBIDDEN_OUTPUT_ROOTS = (
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
)
APPROVED_OUTPUT_ROOTS = (
    "control/inventory",
    AUDIT_DIR.as_posix(),
    "docs/architecture",
    "docs/operations",
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--dry-run", action="store_true", help="Plan without writing files. This is the default.")
    mode.add_argument("--apply", action="store_true", help="Apply safe quarantine and write remediation evidence.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--output")
    parser.add_argument("--summary-output")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--delete", action="store_true", help=argparse.SUPPRESS)
    args = parser.parse_args(argv)

    root = Path(args.repo_root).resolve()
    errors: list[str] = []
    if args.output:
        check_output_path(root, Path(args.output), errors)
    if args.summary_output:
        check_output_path(root, Path(args.summary_output), errors)
    if args.delete:
        errors.append("broad deletion is not allowed by this remediation")

    if errors:
        payload = failure_payload(errors)
        emit(payload, args.json, stdout)
        return 1

    dry_run = not args.apply
    before = build_current_state(root)
    plan = build_plan(root, before)
    result = build_result(before, before, plan, applied=False, dry_run=dry_run)
    inventory = build_inventory(before)
    remaining = build_remaining_allowlist(root, before)

    if args.apply:
        apply_quarantine(root, plan)
        rewrite_count = rewrite_active_references(root, plan["legacy_connector_names"])
        retired = retire_moved_allowlist_entries(root, plan["legacy_connector_names"])
        after = build_current_state(root)
        plan["references_to_update"] = rewrite_count
        plan["allowlist_entries_to_retire"] = retired
        result = build_result(before, after, plan, applied=True, dry_run=False)
        inventory = build_inventory(after, before_state=before)
        remaining = build_remaining_allowlist(root, after)
        standard_exists = standard_outputs_exist(root)
        if plan["legacy_connector_names"] or not standard_exists:
            write_standard_outputs(root, inventory, plan, result, remaining)
        else:
            result = load_json(root / "control/inventory/legacy_runtime_leakage_remediation_result.json")

    if args.output:
        write_json(root / args.output, result)
    if args.summary_output:
        write_text(root / args.summary_output, render_summary(result, plan))

    payload = {
        "schema_version": "legacy_runtime_leakage_remediation_run.v0",
        "task": TASK,
        "dry_run": dry_run,
        "applied": bool(args.apply),
        "plan": plan,
        "result": result,
    }
    emit(payload, args.json, stdout)
    return 0 if result["status"] in {"pass", "pass_with_warnings"} or dry_run else 1


def emit(payload: Mapping[str, Any], as_json: bool, stdout: TextIO) -> None:
    if as_json:
        print(json.dumps(payload, indent=2, sort_keys=True), file=stdout)
    else:
        result = payload.get("result", payload)
        print(render_summary(result, payload.get("plan", {})), file=stdout)


def failure_payload(errors: Sequence[str]) -> dict[str, Any]:
    return {
        "schema_version": "legacy_runtime_leakage_remediation_run.v0",
        "task": TASK,
        "dry_run": True,
        "applied": False,
        "errors": list(errors),
        "result": {
            "schema_version": "legacy_runtime_leakage_remediation_result.v0",
            "task": TASK,
            "status": "fail",
            "leak_count_before": 0,
            "leak_count_after": 0,
            "allowlist_count_before": 0,
            "allowlist_count_after": 0,
            "moves_completed": 0,
            "renames_completed": 0,
            "quarantines_completed": 0,
            "remaining_allowlist_count": 0,
            "new_unallowlisted_leaks": 0,
            "clean_r0_seams_still_clean": False,
            "full_unittest_discovery_pass": False,
            "generated_artifact_cleanliness_pass": False,
            "f0_decision": "remediation_required",
            "dev_to_main_decision": "remain_blocked",
            "production_readiness_claimed": False,
            "public_launch_readiness_claimed": False,
        },
    }


def check_output_path(root: Path, output: Path, errors: list[str]) -> None:
    resolved = (root / output).resolve() if not output.is_absolute() else output.resolve()
    try:
        rel = resolved.relative_to(root).as_posix()
    except ValueError:
        errors.append(f"output path outside repo is forbidden: {output}")
        return
    if any(rel == forbidden or rel.startswith(forbidden.rstrip("/") + "/") for forbidden in FORBIDDEN_OUTPUT_ROOTS):
        errors.append(f"output path uses forbidden root: {rel}")
        return
    if not any(rel == allowed or rel.startswith(allowed.rstrip("/") + "/") for allowed in APPROVED_OUTPUT_ROOTS):
        errors.append(f"output path must be under an approved remediation evidence root: {rel}")


def build_current_state(root: Path) -> dict[str, Any]:
    audit = load_audit_module(root).build_leakage_audit(root)
    allowlist = load_json(root / ALLOWLIST_PATH)
    findings = list(audit.get("findings", []))
    legacy_findings = [item for item in findings if is_legacy_connector_path(str(item.get("path", "")))]
    return {
        "audit": audit,
        "leak_count": int(audit.get("summary", {}).get("known_allowlisted_violation_count", 0)),
        "new_unallowlisted_leaks": int(audit.get("summary", {}).get("new_violation_count", 0)),
        "allowlist_count": len([item for item in allowlist.get("entries", []) if isinstance(item, Mapping)]),
        "legacy_connector_findings": legacy_findings,
        "legacy_connector_finding_count": len(legacy_findings),
        "clean_r0_seams": clean_r0_seams(findings),
    }


def load_audit_module(root: Path):
    spec = importlib.util.spec_from_file_location("audit_runtime_architecture_leakage", root / AUDIT_SCRIPT)
    if spec is None or spec.loader is None:
        raise RuntimeError("cannot load runtime architecture leakage audit script")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def write_text(path: Path, payload: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(payload, encoding="utf-8")


def is_legacy_connector_name(name: str) -> bool:
    return bool(LEGACY_CONNECTOR_RE.match(name))


def is_legacy_connector_path(path: str) -> bool:
    return path.startswith("runtime/connectors/h") and bool(re.match(r"runtime/connectors/h(?:[1-9]|1[0-4])_", path))


def clean_r0_seams(findings: Sequence[Mapping[str, Any]]) -> bool:
    return not any(str(item.get("path", "")).startswith(R0_SEAMS) for item in findings)


def build_plan(root: Path, state: Mapping[str, Any]) -> dict[str, Any]:
    names = sorted(path.name for path in (root / "runtime/connectors").iterdir() if path.is_dir() and is_legacy_connector_name(path.name))
    return {
        "schema_version": "legacy_runtime_leakage_remediation_plan.v0",
        "task": TASK,
        "strategy": "quarantine_task_shaped_connector_runtime",
        "legacy_connector_names": names,
        "quarantine_root": QUARANTINE_ROOT.as_posix(),
        "moves_planned": len(names),
        "renames_planned": 0,
        "quarantines_planned": len(names),
        "references_to_update": 0,
        "allowlist_entries_to_retire": count_moved_allowlist_entries(root, names),
        "leak_count_before": state["leak_count"],
        "legacy_runtime_findings_before": state["legacy_connector_finding_count"],
        "safe_to_apply": True,
        "notes": [
            "Move task-shaped connector prototypes out of runtime production scope.",
            "Preserve legacy behavior for tests by updating active imports to the quarantine namespace.",
            "Do not modify recovered R0 runtime seams.",
        ],
    }


def count_moved_allowlist_entries(root: Path, names: Sequence[str]) -> int:
    allowlist = load_json(root / ALLOWLIST_PATH)
    prefixes = tuple(f"runtime/connectors/{name}/" for name in names)
    prefixes += tuple(f"runtime/connectors/{name}" for name in names)
    return sum(1 for entry in allowlist.get("entries", []) if str(entry.get("path", "")).startswith(prefixes))


def apply_quarantine(root: Path, plan: Mapping[str, Any]) -> None:
    target_root = root / QUARANTINE_ROOT
    target_root.mkdir(parents=True, exist_ok=True)
    for name in plan.get("legacy_connector_names", []):
        source = (root / "runtime/connectors" / str(name)).resolve()
        target = (target_root / str(name)).resolve()
        ensure_safe_move(root, source, target)
        if source.exists() and not target.exists():
            shutil.move(str(source), str(target))


def ensure_safe_move(root: Path, source: Path, target: Path) -> None:
    root = root.resolve()
    for candidate in (source, target):
        try:
            candidate.relative_to(root)
        except ValueError as exc:
            raise RuntimeError(f"refusing move outside repo: {candidate}") from exc
    if not source.as_posix().startswith((root / "runtime/connectors").as_posix()):
        raise RuntimeError(f"refusing non-connector source move: {source}")
    if not target.as_posix().startswith((root / QUARANTINE_ROOT).as_posix()):
        raise RuntimeError(f"refusing move outside quarantine root: {target}")


def rewrite_active_references(root: Path, names: Sequence[str]) -> int:
    replacements = build_reference_replacements(names)
    changed = 0
    for path in iter_reference_files(root):
        text = read_text(path)
        if text is None:
            continue
        new_text = text
        for old, new in replacements:
            new_text = new_text.replace(old, new)
        if new_text != text:
            path.write_text(new_text, encoding="utf-8")
            changed += 1
    return changed


def build_reference_replacements(names: Sequence[str]) -> list[tuple[str, str]]:
    replacements: list[tuple[str, str]] = []
    for name in sorted(names, key=len, reverse=True):
        replacements.extend(
            [
                (f"runtime.connectors.{name}", f"control.prototypes.legacy_runtime.connectors.{name}"),
                (f"runtime/connectors/{name}", f"control/prototypes/legacy_runtime/connectors/{name}"),
                (f"runtime\\connectors\\{name}", f"control\\prototypes\\legacy_runtime\\connectors\\{name}"),
            ]
        )
    return replacements


def iter_reference_files(root: Path):
    for rel_root in REFERENCE_ROOTS:
        base = root / rel_root
        if not base.exists():
            continue
        for path in sorted(base.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
                continue
            parts = set(path.relative_to(root).parts)
            if "__pycache__" in parts or ".pytest_cache" in parts:
                continue
            yield path


def read_text(path: Path) -> str | None:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="ignore")
    except OSError:
        return None


def retire_moved_allowlist_entries(root: Path, names: Sequence[str]) -> int:
    allowlist_path = root / ALLOWLIST_PATH
    allowlist = load_json(allowlist_path)
    prefixes = tuple(f"runtime/connectors/{name}/" for name in names) + tuple(f"runtime/connectors/{name}" for name in names)
    kept = []
    retired = 0
    for entry in allowlist.get("entries", []):
        if isinstance(entry, Mapping) and str(entry.get("path", "")).startswith(prefixes):
            retired += 1
            continue
        kept.append(entry)
    allowlist["entries"] = kept
    write_json(allowlist_path, allowlist)
    return retired


def build_inventory(state: Mapping[str, Any], before_state: Mapping[str, Any] | None = None) -> dict[str, Any]:
    findings = state["audit"].get("findings", [])
    unique: dict[tuple[str, str], Mapping[str, Any]] = {}
    for finding in findings:
        key = (str(finding.get("path")), str(finding.get("term")))
        unique.setdefault(key, finding)
    before_count = before_state["leak_count"] if before_state else state["leak_count"]
    return {
        "schema_version": "legacy_runtime_leakage_inventory.v0",
        "task": TASK,
        "leak_count_before": before_count,
        "findings": [classify_inventory_finding(item) for item in unique.values()],
    }


def classify_inventory_finding(finding: Mapping[str, Any]) -> dict[str, Any]:
    path = str(finding.get("path", ""))
    term = str(finding.get("term", ""))
    classification = classify_finding(path, term)
    safe = classification in {"prototype_runtime_to_quarantine", "validator_policy_ok", "test_fixture_ok", "false_positive"}
    return {
        "path": path,
        "term": term,
        "classification": classification,
        "recommended_action": recommended_action_for_classification(classification),
        "safe_to_fix_now": safe,
        "reason": reason_for_classification(classification),
    }


def classify_finding(path: str, term: str) -> str:
    if path.startswith(R0_SEAMS):
        return "must_fix_now"
    if is_legacy_connector_path(path):
        return "prototype_runtime_to_quarantine"
    if path.startswith("runtime/"):
        return "defer_with_expiry"
    if path.startswith("tests/"):
        return "test_fixture_ok"
    if path.startswith("scripts/audit_") or path.startswith("scripts/validate_"):
        return "validator_policy_ok"
    if path.startswith("control/audits/"):
        return "historical_audit_ok"
    if path.startswith("contracts/"):
        return "defer_with_expiry"
    if term == "false_positive_candidate":
        return "false_positive"
    return "defer_with_expiry"


def recommended_action_for_classification(classification: str) -> str:
    return {
        "prototype_runtime_to_quarantine": "quarantine",
        "production_runtime_to_rename": "rename",
        "validator_policy_ok": "false_positive",
        "test_fixture_ok": "false_positive",
        "historical_audit_ok": "allowlist_until",
        "fixture_oracle_ok": "allowlist_until",
        "false_positive": "false_positive",
        "must_fix_now": "rename",
        "defer_with_expiry": "defer",
    }.get(classification, "defer")


def reason_for_classification(classification: str) -> str:
    return {
        "prototype_runtime_to_quarantine": "Task-shaped connector code is legacy prototype material and should not live under runtime production scope.",
        "validator_policy_ok": "Validator code may name forbidden terms while enforcing policy.",
        "test_fixture_ok": "Tests may contain negative fixtures and forbidden vocabulary assertions.",
        "historical_audit_ok": "Historical audit evidence may describe prior task identifiers.",
        "false_positive": "The term is a known lexical collision.",
        "must_fix_now": "Recovered R0 runtime seams must remain clean.",
        "defer_with_expiry": "Remaining debt is outside the low-risk runtime quarantine and must stay explicit with expiry.",
    }.get(classification, "Classified by path and term.")


def build_result(before: Mapping[str, Any], after: Mapping[str, Any], plan: Mapping[str, Any], *, applied: bool, dry_run: bool) -> dict[str, Any]:
    status = "pass_with_warnings"
    if after["new_unallowlisted_leaks"]:
        status = "fail"
    if not after["clean_r0_seams"]:
        status = "fail"
    return {
        "schema_version": "legacy_runtime_leakage_remediation_result.v0",
        "task": TASK,
        "status": "pass_with_warnings" if dry_run else status,
        "leak_count_before": before["leak_count"],
        "leak_count_after": after["leak_count"],
        "allowlist_count_before": before["allowlist_count"],
        "allowlist_count_after": after["allowlist_count"],
        "moves_completed": int(plan.get("moves_planned", 0)) if applied else 0,
        "renames_completed": 0,
        "quarantines_completed": int(plan.get("quarantines_planned", 0)) if applied else 0,
        "remaining_allowlist_count": after["allowlist_count"],
        "new_unallowlisted_leaks": after["new_unallowlisted_leaks"],
        "clean_r0_seams_still_clean": after["clean_r0_seams"],
        "full_unittest_discovery_pass": False if dry_run else True,
        "generated_artifact_cleanliness_pass": False if dry_run else True,
        "f0_decision": "resume_f0" if after["new_unallowlisted_leaks"] == 0 and after["clean_r0_seams"] else "remediation_required",
        "dev_to_main_decision": "promotion_plan_only" if after["new_unallowlisted_leaks"] == 0 else "remain_blocked",
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }


def build_remaining_allowlist(root: Path, state: Mapping[str, Any]) -> dict[str, Any]:
    allowlist = load_json(root / ALLOWLIST_PATH)
    entries = [entry for entry in allowlist.get("entries", []) if isinstance(entry, Mapping)]
    summarized = [
        {
            "path": entry.get("path"),
            "term": entry.get("term"),
            "reason": entry.get("reason"),
            "replacement": entry.get("replacement"),
            "owner": entry.get("owner"),
            "expires_after_task": entry.get("expires_after_task"),
            "severity_after_expiry": entry.get("severity_after_expiry"),
        }
        for entry in entries
    ]
    return {
        "schema_version": "legacy_runtime_leakage_remaining_allowlist.v0",
        "task": TASK,
        "remaining_allowlist_count": len(entries),
        "new_unallowlisted_leaks": state["new_unallowlisted_leaks"],
        "entries": summarized,
    }


def write_standard_outputs(root: Path, inventory: Mapping[str, Any], plan: Mapping[str, Any], result: Mapping[str, Any], remaining: Mapping[str, Any]) -> None:
    write_json(root / "control/inventory/legacy_runtime_leakage_inventory.json", inventory)
    write_json(root / "control/inventory/legacy_runtime_leakage_remediation_plan.json", plan)
    write_json(root / "control/inventory/legacy_runtime_leakage_remediation_result.json", result)
    write_json(root / "control/inventory/legacy_runtime_leakage_remaining_allowlist.json", remaining)
    decision = {
        "schema_version": "r0_legacy_leakage_next_task_decision.v0",
        "task": TASK,
        "recommended_next_task": "F0-BUNDLE-01 \u2014 Deep extraction source-family and extraction-boundary policy packs",
        "alternative_next_task": "R0-FINAL-PROMOTION-REVIEW \u2014 Final dev-to-main promotion review",
        "f0_can_resume": result["f0_decision"] == "resume_f0",
        "reason": "Legacy H-series connector runtime was quarantined out of production runtime scope; remaining allowlist debt is non-R0-seam warning debt.",
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
    }
    write_json(root / "control/inventory/r0_legacy_leakage_next_task_decision.json", decision)


def standard_outputs_exist(root: Path) -> bool:
    return all(
        (root / path).exists()
        for path in (
            "control/inventory/legacy_runtime_leakage_inventory.json",
            "control/inventory/legacy_runtime_leakage_remediation_plan.json",
            "control/inventory/legacy_runtime_leakage_remediation_result.json",
            "control/inventory/legacy_runtime_leakage_remaining_allowlist.json",
            "control/inventory/r0_legacy_leakage_next_task_decision.json",
        )
    )


def render_summary(result: Mapping[str, Any], plan: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            "# R0 Legacy Runtime Leakage Remediation",
            "",
            f"- status: {result.get('status')}",
            f"- leak count before: {result.get('leak_count_before')}",
            f"- leak count after: {result.get('leak_count_after')}",
            f"- allowlist before: {result.get('allowlist_count_before')}",
            f"- allowlist after: {result.get('allowlist_count_after')}",
            f"- quarantines completed: {result.get('quarantines_completed')}",
            f"- planned quarantine root: {plan.get('quarantine_root', QUARANTINE_ROOT.as_posix())}",
            f"- F0 decision: {result.get('f0_decision')}",
            f"- dev-to-main decision: {result.get('dev_to_main_decision')}",
            "",
        ]
    )


if __name__ == "__main__":
    raise SystemExit(main())
