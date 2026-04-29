#!/usr/bin/env python3
"""Validate the Full Project State Audit v0 pack."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
AUDIT_ROOT = ROOT / "control" / "audits" / "full-project-state-audit-v0"
REPORT_PATH = AUDIT_ROOT / "full_project_audit_report.json"

REQUIRED_FILES = [
    "README.md",
    "EXECUTIVE_SUMMARY.md",
    "CURRENT_STATE.md",
    "MILESTONE_INVENTORY.md",
    "VERIFICATION_MATRIX.md",
    "EVAL_AND_SEARCH_USEFULNESS_STATUS.md",
    "EXTERNAL_BASELINE_STATUS.md",
    "SOURCE_AND_RETRIEVAL_STATUS.md",
    "PUBLICATION_AND_STATIC_SITE_STATUS.md",
    "PUBLIC_ALPHA_AND_HOSTING_STATUS.md",
    "LIVE_BACKEND_AND_PROBE_STATUS.md",
    "SNAPSHOT_RELAY_AND_COMPATIBILITY_STATUS.md",
    "NATIVE_CLIENT_STATUS.md",
    "RUST_PARITY_STATUS.md",
    "PRIVACY_SECURITY_ACTION_POLICY_STATUS.md",
    "RISK_REGISTER.md",
    "BLOCKERS.md",
    "NEXT_20_MILESTONES.md",
    "HUMAN_OPERATED_WORK.md",
    "DO_NOT_DO_NEXT.md",
    "PROMPT_QUEUE_RECOMMENDATIONS.md",
    "COMMAND_RESULTS.md",
    "full_project_audit_report.json",
]

FORBIDDEN_POSITIVE_CLAIMS = [
    "eureka is production ready",
    "eureka is production-ready",
    "github pages deployment succeeded",
    "github pages deployment success: true",
    "external baselines were observed",
    "relay runtime is implemented",
    "native gui is implemented",
    "live probes are enabled",
]


def _load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _audit_text() -> str:
    if not AUDIT_ROOT.exists():
        return ""
    parts = []
    for path in AUDIT_ROOT.rglob("*"):
        if path.is_file() and path.suffix.lower() in {".md", ".json", ".txt"}:
            parts.append(path.read_text(encoding="utf-8").lower())
    return "\n".join(parts)


def validate() -> dict[str, Any]:
    errors: list[str] = []
    report: dict[str, Any] = {}

    if not AUDIT_ROOT.exists():
        errors.append(f"audit pack missing: {AUDIT_ROOT.relative_to(ROOT)}")
    else:
        for name in REQUIRED_FILES:
            if not (AUDIT_ROOT / name).exists():
                errors.append(f"required audit file missing: {name}")

    if REPORT_PATH.exists():
        try:
            report = _load_json(REPORT_PATH)
        except Exception as exc:  # pragma: no cover - parser text is not stable
            errors.append(f"full_project_audit_report.json did not parse: {exc}")
    else:
        errors.append("full_project_audit_report.json missing")

    if report:
        required_keys = [
            "report_id",
            "created_by_slice",
            "repo",
            "branch",
            "commit_sha",
            "git_status",
            "origin_sync_status",
            "report_scope",
            "milestone_counts",
            "verification_summary",
            "eval_status",
            "search_usefulness_status",
            "external_baseline_status",
            "publication_status",
            "public_alpha_status",
            "live_backend_status",
            "live_probe_status",
            "snapshot_status",
            "relay_status",
            "native_status",
            "rust_status",
            "privacy_security_action_policy_status",
            "source_status",
            "risks",
            "blockers",
            "next_recommended_milestones",
            "human_operated_parallel_work",
            "explicit_deferrals",
            "immediate_next_codex_prompt",
            "command_results",
        ]
        for key in required_keys:
            if key not in report:
                errors.append(f"report missing top-level key: {key}")

        milestone_counts = report.get("milestone_counts", {})
        if not isinstance(milestone_counts, dict) or not milestone_counts:
            errors.append("report must contain milestone summary counts")

        verification = report.get("verification_summary", {})
        if not isinstance(verification, dict) or "passed_count" not in verification:
            errors.append("report must contain verification summary")

        eval_status = report.get("eval_status", {})
        if "archive_resolution" not in eval_status:
            errors.append("report missing archive/search eval status: archive_resolution")
        if "search_usefulness" not in eval_status:
            errors.append("report missing archive/search eval status: search_usefulness")

        external = report.get("external_baseline_status", {})
        if "global_observed_slots" not in external or "global_pending_slots" not in external:
            errors.append("report must represent external baseline status")

        if not report.get("risks"):
            errors.append("report must include risk register summary")
        if not report.get("next_recommended_milestones"):
            errors.append("report must include next milestone plan")
        if not report.get("human_operated_parallel_work"):
            errors.append("report must include human-operated work")
        if not report.get("explicit_deferrals"):
            errors.append("report must include explicit deferrals")
        if not report.get("command_results"):
            errors.append("report must include command results")

        cargo_text = json.dumps(report.get("rust_status", {})).lower()
        if "cargo" not in cargo_text:
            errors.append("report must mention Cargo availability status")

        human_work = " ".join(report.get("human_operated_parallel_work", [])).lower()
        if "manual observation batch 0" not in human_work:
            errors.append("manual observation human-operated work is not represented")

        observed = external.get("global_observed_slots")
        if observed == 0 and "external baselines were observed" in _audit_text():
            errors.append("audit claims external observations despite zero observed slots")

    text = _audit_text()
    for phrase in FORBIDDEN_POSITIVE_CLAIMS:
        if phrase in text:
            errors.append(f"forbidden positive claim found: {phrase}")

    return {
        "check_id": "full_project_state_audit_v0",
        "audit_root": str(AUDIT_ROOT.relative_to(ROOT)),
        "required_file_count": len(REQUIRED_FILES),
        "errors": errors,
        "status": "passed" if not errors else "failed",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Print machine-readable validation result.")
    args = parser.parse_args()

    result = validate()
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    elif result["status"] == "passed":
        print(
            "full project state audit validation passed: "
            f"{result['required_file_count']} required files checked"
        )
    else:
        print("full project state audit validation failed:")
        for error in result["errors"]:
            print(f"- {error}")
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
