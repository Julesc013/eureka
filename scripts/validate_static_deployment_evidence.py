#!/usr/bin/env python3
"""Validate P52 Static Deployment Evidence / GitHub Pages Repair v0."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO


ROOT = Path(__file__).resolve().parents[1]
AUDIT_ROOT = ROOT / "control" / "audits" / "static-deployment-evidence-v0"
REPORT_PATH = AUDIT_ROOT / "static_deployment_evidence_report.json"
WORKFLOW_PATH = ROOT / ".github" / "workflows" / "pages.yml"
PAGES_DOC = ROOT / "docs" / "operations" / "GITHUB_PAGES_DEPLOYMENT.md"
LEGACY_STATIC_ROOT = "public" + "_site"

REQUIRED_FILES = {
    "README.md",
    "DEPLOYMENT_SUMMARY.md",
    "WORKFLOW_REVIEW.md",
    "STATIC_ARTIFACT_REVIEW.md",
    "GITHUB_PAGES_STATUS.md",
    "OPERATOR_STEPS.md",
    "DEPLOYMENT_EVIDENCE.md",
    "DEPLOYMENT_VERIFICATION.md",
    "FAILURE_OR_UNVERIFIED_STATUS.md",
    "PUBLIC_CLAIM_REVIEW.md",
    "REMAINING_BLOCKERS.md",
    "NEXT_STEPS.md",
    "COMMAND_RESULTS.md",
    "static_deployment_evidence_report.json",
}

REQUIRED_REPORT_KEYS = {
    "report_id",
    "created_by_slice",
    "repo_head",
    "origin_main_head",
    "branch",
    "worktree_status",
    "workflow_path",
    "workflow_review",
    "artifact_root",
    "static_artifact_review",
    "github_pages_status",
    "github_actions_evidence",
    "pages_api_evidence",
    "deployment_url",
    "deployment_verified",
    "deployment_success_claimed",
    "operator_action_required",
    "operator_steps",
    "public_claim_review",
    "command_results",
    "repaired_items",
    "remaining_blockers",
    "next_recommended_branch",
    "notes",
}

ALLOWED_STATUS_VALUES = {
    "workflow_configured",
    "workflow_repaired",
    "deployment_verified",
    "deployment_failed",
    "deployment_unverified",
    "pages_not_enabled",
    "gh_unavailable",
    "gh_unauthenticated",
    "operator_gated",
    "blocked",
}

FORBIDDEN_TEXT_WITHOUT_EVIDENCE = {
    "github pages deployment succeeded",
    "deployment success is verified",
    "deployed static publication is live",
    "hosted backend is deployed",
    "hosted public search is live",
    "dynamic backend is deployed",
    "production ready: true",
    '"production_readiness_claimed": true',
}


def validate_static_deployment_evidence() -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    _validate_pack_files(errors)
    report = _load_json(REPORT_PATH, errors)
    _validate_report(report, errors)
    _validate_workflow(report, errors)
    _validate_docs_and_claims(report, errors)

    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "static_deployment_evidence_validator_v0",
        "audit_root": "control/audits/static-deployment-evidence-v0",
        "report_id": _mapping(report).get("report_id"),
        "artifact_root": _mapping(report).get("artifact_root"),
        "workflow_path": _mapping(report).get("workflow_path"),
        "deployment_verified": _mapping(report).get("deployment_verified"),
        "deployment_success_claimed": _mapping(report).get("deployment_success_claimed"),
        "github_pages_status": _mapping(report).get("github_pages_status"),
        "required_files": sorted(REQUIRED_FILES),
        "errors": errors,
        "warnings": warnings,
    }


def _validate_pack_files(errors: list[str]) -> None:
    if not AUDIT_ROOT.is_dir():
        errors.append("P52 static deployment evidence audit pack is missing.")
        return
    present = {path.name for path in AUDIT_ROOT.iterdir() if path.is_file()}
    missing = sorted(REQUIRED_FILES - present)
    if missing:
        errors.append(f"P52 audit pack missing required files: {missing}.")


def _validate_report(report: Any, errors: list[str]) -> None:
    if not isinstance(report, Mapping):
        errors.append("static_deployment_evidence_report.json must be a JSON object.")
        return

    missing = sorted(REQUIRED_REPORT_KEYS - set(report))
    if missing:
        errors.append(f"static_deployment_evidence_report.json missing keys: {missing}.")

    if report.get("report_id") != "static_deployment_evidence_v0":
        errors.append("report_id must be static_deployment_evidence_v0.")
    if report.get("artifact_root") != "site/dist":
        errors.append("artifact_root must be site/dist.")
    if report.get("workflow_path") != ".github/workflows/pages.yml":
        errors.append("workflow_path must be .github/workflows/pages.yml.")

    statuses = report.get("github_pages_status")
    if not isinstance(statuses, list) or not statuses:
        errors.append("github_pages_status must be a non-empty list.")
    else:
        invalid = sorted(str(status) for status in statuses if status not in ALLOWED_STATUS_VALUES)
        if invalid:
            errors.append(f"github_pages_status contains invalid values: {invalid}.")

    deployment_verified = report.get("deployment_verified")
    success_claimed = report.get("deployment_success_claimed")
    if not isinstance(deployment_verified, bool):
        errors.append("deployment_verified must be boolean.")
    if not isinstance(success_claimed, bool):
        errors.append("deployment_success_claimed must be boolean.")
    if success_claimed and not deployment_verified:
        errors.append("deployment_success_claimed may not be true unless deployment_verified is true.")

    if success_claimed:
        actions = _mapping(report.get("github_actions_evidence"))
        if not report.get("deployment_url"):
            errors.append("deployment_success_claimed requires deployment_url.")
        if not actions.get("current_head_query_status") == "verified":
            errors.append("deployment_success_claimed requires verified current-head Actions evidence.")

    for key in (
        "hosted_backend_claimed",
        "live_search_claimed",
        "live_probes_claimed",
        "dynamic_backend_deployed",
    ):
        if report.get(key) is not False:
            errors.append(f"{key} must be false.")

    if deployment_verified is not True:
        steps = report.get("operator_steps")
        if not isinstance(steps, list) or len([step for step in steps if isinstance(step, str)]) < 5:
            errors.append("operator_steps must be present when deployment is not verified.")
        blockers = report.get("remaining_blockers")
        if not isinstance(blockers, list) or not blockers:
            errors.append("remaining_blockers must be non-empty when deployment is not verified.")

    commands = report.get("command_results")
    if not isinstance(commands, list) or not commands:
        errors.append("command_results must be a non-empty list.")
    else:
        command_text = "\n".join(str(item.get("command", "")) for item in commands if isinstance(item, Mapping))
        for required in (
            "python scripts/check_github_pages_static_artifact.py --path site/dist",
            "gh --version",
        ):
            if required not in command_text:
                errors.append(f"command_results missing {required!r}.")


def _validate_workflow(report: Any, errors: list[str]) -> None:
    if not WORKFLOW_PATH.is_file():
        errors.append(".github/workflows/pages.yml is missing.")
        return
    text = WORKFLOW_PATH.read_text(encoding="utf-8")
    if "path: site/dist" not in text:
        errors.append("Pages workflow must upload site/dist.")
    if "path: " + LEGACY_STATIC_ROOT in text or LEGACY_STATIC_ROOT in _upload_lines(text):
        errors.append("Pages workflow must not upload the retired static artifact.")
    for required in (
        "actions/upload-pages-artifact@v3",
        "actions/deploy-pages@v4",
        "python scripts/validate_publication_inventory.py",
        "python site/validate.py",
        "python scripts/check_github_pages_static_artifact.py --path site/dist",
    ):
        if required not in text:
            errors.append(f"Pages workflow missing required step text: {required}.")

    review = _mapping(_mapping(report).get("workflow_review"))
    if review and review.get("upload_path") != "site/dist":
        errors.append("workflow_review.upload_path must be site/dist.")
    if review and review.get("references_legacy_static_upload") is not False:
        errors.append("workflow_review.references_legacy_static_upload must be false.")


def _validate_docs_and_claims(report: Any, errors: list[str]) -> None:
    if not PAGES_DOC.is_file():
        errors.append("docs/operations/GITHUB_PAGES_DEPLOYMENT.md is missing.")

    success_claimed = _mapping(report).get("deployment_success_claimed") is True
    text_parts: list[str] = []
    if AUDIT_ROOT.is_dir():
        for path in AUDIT_ROOT.rglob("*"):
            if path.is_file() and path.suffix.lower() in {".md", ".json", ".txt"}:
                text_parts.append(path.read_text(encoding="utf-8"))
    if PAGES_DOC.is_file():
        text_parts.append(PAGES_DOC.read_text(encoding="utf-8"))
    text = "\n".join(text_parts).casefold()

    if not success_claimed:
        for phrase in FORBIDDEN_TEXT_WITHOUT_EVIDENCE:
            if phrase in text:
                errors.append(f"forbidden deployment/product claim without evidence: {phrase}.")
        public_claim_doc = (AUDIT_ROOT / "PUBLIC_CLAIM_REVIEW.md").read_text(
            encoding="utf-8"
        ).casefold() if (AUDIT_ROOT / "PUBLIC_CLAIM_REVIEW.md").is_file() else ""
        if "static-only" not in public_claim_doc:
            errors.append("PUBLIC_CLAIM_REVIEW.md must say static-only when deployment is unverified.")
        if "no hosted backend" not in public_claim_doc:
            errors.append(
                "PUBLIC_CLAIM_REVIEW.md must record no hosted backend when deployment is unverified."
            )

    claims = _mapping(_mapping(report).get("public_claim_review"))
    if claims:
        if claims.get("static_only") is not True:
            errors.append("public_claim_review.static_only must be true.")
        if claims.get("no_hosted_backend") is not True:
            errors.append("public_claim_review.no_hosted_backend must be true.")
        if claims.get("production_readiness_claimed") is not False:
            errors.append("public_claim_review.production_readiness_claimed must be false.")


def _upload_lines(text: str) -> str:
    lines = []
    previous = ""
    for line in text.splitlines():
        stripped = line.strip()
        if previous == "with:" and stripped.startswith("path: "):
            lines.append(stripped)
        previous = stripped
    return "\n".join(lines)


def _load_json(path: Path, errors: list[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"{_rel(path)} is missing.")
    except json.JSONDecodeError as exc:
        errors.append(f"{_rel(path)} is invalid JSON: {exc}.")
    return None


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [
        "Static deployment evidence validation",
        f"status: {report['status']}",
        f"report_id: {report.get('report_id')}",
        f"artifact_root: {report.get('artifact_root')}",
        f"workflow_path: {report.get('workflow_path')}",
        f"deployment_verified: {report.get('deployment_verified')}",
        f"deployment_success_claimed: {report.get('deployment_success_claimed')}",
    ]
    if report["errors"]:
        lines.append("errors:")
        lines.extend(f"- {error}" for error in report["errors"])
    if report["warnings"]:
        lines.append("warnings:")
        lines.extend(f"- {warning}" for warning in report["warnings"])
    return "\n".join(lines) + "\n"


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_static_deployment_evidence()
    output = stdout or __import__("sys").stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
