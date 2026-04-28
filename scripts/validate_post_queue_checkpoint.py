#!/usr/bin/env python3
"""Validate the post-queue checkpoint audit pack."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
CHECKPOINT_ROOT = ROOT / "control" / "audits" / "post-queue-state-checkpoint-v0"

REQUIRED_FILES = [
    "README.md",
    "CURRENT_STATE.md",
    "MILESTONE_STATUS.md",
    "VERIFICATION_RESULTS.md",
    "PUBLICATION_PLANE_STATUS.md",
    "PUBLIC_ALPHA_STATUS.md",
    "STATIC_SITE_STATUS.md",
    "EXTERNAL_BASELINE_STATUS.md",
    "EVAL_AND_AUDIT_STATUS.md",
    "RUST_PARITY_STATUS.md",
    "SOURCE_AND_RETRIEVAL_STATUS.md",
    "COMPATIBILITY_SURFACE_STATUS.md",
    "SNAPSHOT_AND_RELAY_STATUS.md",
    "RISK_REGISTER.md",
    "NEXT_MILESTONE_PLAN.md",
    "DEFERRED_AND_BLOCKED_WORK.md",
    "COMMAND_RESULTS.md",
    "checkpoint_report.json",
]

FORBIDDEN_POSITIVE_CLAIMS = [
    "eureka is production-ready",
    "eureka is production ready",
    "github pages deployment succeeded",
    "custom domain is configured",
    "live probes are available",
    "live probes are enabled",
    "external baselines were observed",
    "production signed snapshots are available",
]


def _load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _all_checkpoint_text() -> str:
    parts = []
    for path in CHECKPOINT_ROOT.rglob("*"):
        if path.is_file() and path.suffix.lower() in {".md", ".txt", ".json"}:
            parts.append(path.read_text(encoding="utf-8").lower())
    return "\n".join(parts)


def validate() -> dict[str, Any]:
    errors: list[str] = []

    if not CHECKPOINT_ROOT.exists():
        errors.append(f"checkpoint directory missing: {CHECKPOINT_ROOT.relative_to(ROOT)}")
        report: dict[str, Any] = {}
    else:
        for name in REQUIRED_FILES:
            if not (CHECKPOINT_ROOT / name).exists():
                errors.append(f"required checkpoint file missing: {name}")
        report_path = CHECKPOINT_ROOT / "checkpoint_report.json"
        try:
            report = _load_json(report_path)
        except Exception as exc:  # pragma: no cover - exact parser message is not important
            report = {}
            errors.append(f"checkpoint_report.json did not parse: {exc}")

    if report:
        required_top_level = [
            "report_id",
            "git_status",
            "origin_sync_status",
            "current_milestones",
            "command_results",
            "eval_status",
            "public_alpha_status",
            "publication_status",
            "static_site_status",
            "rust_status",
            "snapshot_status",
            "source_status",
            "key_risks",
            "next_recommended_milestones",
            "human_operated_work",
            "explicit_deferrals",
            "final_recommendation",
        ]
        for key in required_top_level:
            if key not in report:
                errors.append(f"checkpoint_report.json missing top-level key: {key}")

        if not report.get("git_status"):
            errors.append("checkpoint_report.json must include current git status")
        if not report.get("next_recommended_milestones"):
            errors.append("checkpoint_report.json must include next milestones")
        if not report.get("command_results"):
            errors.append("checkpoint_report.json must include command results")

        eval_status = report.get("eval_status", {})
        if "archive_resolution" not in eval_status:
            errors.append("checkpoint_report.json missing archive_resolution eval status")
        if "search_usefulness" not in eval_status:
            errors.append("checkpoint_report.json missing search_usefulness eval status")
        if "external_baselines" not in eval_status:
            errors.append("checkpoint_report.json missing external baseline status")

        human_work = " ".join(report.get("human_operated_work", [])).lower()
        if "manual observation batch 0" not in human_work:
            errors.append("human-operated manual observation work is not represented")

        deferrals = " ".join(report.get("explicit_deferrals", [])).lower()
        required_deferral_terms = {
            "internet archive live probe": ["internet archive", "live probe"],
            "google external-search automation": ["google", "scraping"],
            "live backend": ["live backend"],
        }
        for label, terms in required_deferral_terms.items():
            if not all(term in deferrals for term in terms):
                errors.append(f"explicit deferral missing: {label}")

        observed = (
            eval_status.get("external_baselines", {}).get("global_observed_count")
            if isinstance(eval_status.get("external_baselines"), dict)
            else None
        )
        if observed == 0:
            all_text = _all_checkpoint_text()
            if "external baselines were observed" in all_text:
                errors.append("checkpoint claims external baselines were observed despite zero observed count")

    if CHECKPOINT_ROOT.exists():
        all_text = _all_checkpoint_text()
        for phrase in FORBIDDEN_POSITIVE_CLAIMS:
            if phrase in all_text:
                errors.append(f"forbidden positive claim found: {phrase}")

    return {
        "check_id": "post_queue_state_checkpoint_v0",
        "checkpoint_root": str(CHECKPOINT_ROOT.relative_to(ROOT)),
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
            "post queue checkpoint validation passed: "
            f"{result['required_file_count']} required files checked"
        )
    else:
        print("post queue checkpoint validation failed:")
        for error in result["errors"]:
            print(f"- {error}")
    return 0 if result["status"] == "passed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
