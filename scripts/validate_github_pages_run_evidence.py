from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
PACK_DIR = REPO_ROOT / "control" / "audits" / "github-pages-run-evidence-v0"
REPORT_PATH = PACK_DIR / "github_pages_run_evidence_report.json"
WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "pages.yml"
LEGACY_STATIC_ROOT = "public" + "_site"

REQUIRED_FILES = {
    "README.md",
    "WORKFLOW_CONFIGURATION.md",
    "RUN_EVIDENCE.md",
    "ARTIFACT_EVIDENCE.md",
    "DEPLOYMENT_EVIDENCE.md",
    "LOCAL_VALIDATION_EVIDENCE.md",
    "GAPS_AND_OPERATOR_ACTIONS.md",
    "PROMOTION_IMPLICATIONS.md",
    "github_pages_run_evidence_report.json",
}
VALID_OVERALL_DECISIONS = {
    "verified_deployed",
    "workflow_configured_unverified",
    "failed",
    "unavailable",
}
VALID_TOOL_STATUSES = {
    "gh_authenticated",
    "gh_unavailable",
    "github_connector_available",
    "github_public_api_available_gh_unavailable",
    "unavailable_or_unverified",
}
VALID_RUN_STATUSES = {"queued", "in_progress", "completed", "unavailable", None}
VALID_RUN_CONCLUSIONS = {
    "success",
    "failure",
    "cancelled",
    "skipped",
    "timed_out",
    "action_required",
    "neutral",
    "startup_failure",
    "stale",
    "unavailable",
    None,
}


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate GitHub Pages Run Evidence Review v0 without network access."
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_github_pages_run_evidence()
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


def validate_github_pages_run_evidence() -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    _validate_pack_files(errors)
    payload = _load_json(REPORT_PATH, errors)
    _validate_report(payload, errors)
    _validate_workflow(payload, errors)
    _validate_markdown_claims(payload, errors)

    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "github_pages_run_evidence_validator_v0",
        "pack_dir": "control/audits/github-pages-run-evidence-v0",
        "report_id": _mapping(payload).get("report_id"),
        "current_head": _mapping(payload).get("current_head"),
        "workflow_upload_path": _mapping(payload).get("workflow_upload_path"),
        "github_actions_tool_status": _mapping(payload).get("github_actions_tool_status"),
        "latest_run_conclusion": _mapping(_mapping(payload).get("latest_pages_run")).get("conclusion"),
        "overall_decision": _mapping(payload).get("overall_decision"),
        "success_claim_allowed": _mapping(_mapping(payload).get("deployment_evidence")).get(
            "success_claim_allowed"
        ),
        "errors": errors,
        "warnings": warnings,
    }


def _validate_pack_files(errors: list[str]) -> None:
    if not PACK_DIR.is_dir():
        errors.append("GitHub Pages run evidence audit pack is missing.")
        return
    present = {path.name for path in PACK_DIR.iterdir() if path.is_file()}
    missing = sorted(REQUIRED_FILES - present)
    if missing:
        errors.append(f"GitHub Pages run evidence audit pack missing files {missing}.")


def _validate_report(report: Any, errors: list[str]) -> None:
    if not isinstance(report, Mapping):
        errors.append("github_pages_run_evidence_report.json: report must be a JSON object.")
        return

    expected = {
        "report_id": "github_pages_run_evidence_v0",
        "created_by_slice": "github_pages_run_evidence_review_v0",
        "workflow_path": ".github/workflows/pages.yml",
        "workflow_upload_path": "site/dist",
        "workflow_static_only": True,
        "workflow_runs_backend_or_live_probes": False,
    }
    for key, expected_value in expected.items():
        if report.get(key) != expected_value:
            errors.append(f"github_pages_run_evidence_report.json: {key} must be {expected_value!r}.")

    for key in ("current_head", "origin_main_head"):
        value = report.get(key)
        if not _looks_like_sha(value):
            errors.append(f"github_pages_run_evidence_report.json: {key} must record a full commit SHA.")

    local_status = report.get("local_validation_status")
    if not isinstance(local_status, str) or not local_status:
        errors.append("github_pages_run_evidence_report.json: local_validation_status is required.")

    tool_status = report.get("github_actions_tool_status")
    if tool_status not in VALID_TOOL_STATUSES:
        errors.append(
            "github_pages_run_evidence_report.json: github_actions_tool_status must be one of "
            f"{sorted(VALID_TOOL_STATUSES)}."
        )

    overall = report.get("overall_decision")
    if overall not in VALID_OVERALL_DECISIONS:
        errors.append(
            "github_pages_run_evidence_report.json: overall_decision must be one of "
            f"{sorted(VALID_OVERALL_DECISIONS)}."
        )

    _validate_latest_run(report.get("latest_pages_run"), errors)
    _validate_artifact_evidence(report.get("artifact_evidence"), errors)
    _validate_deployment_evidence(report.get("deployment_evidence"), overall, errors)

    actions = report.get("operator_actions")
    if overall != "verified_deployed":
        if not isinstance(actions, list) or not actions or not all(isinstance(action, str) for action in actions):
            errors.append(
                "github_pages_run_evidence_report.json: operator_actions are required unless deployment is verified."
            )

    blockers = report.get("blockers")
    if overall == "failed" and (not isinstance(blockers, list) or not blockers):
        errors.append("github_pages_run_evidence_report.json: failed decision requires blockers.")

    next_milestone = report.get("next_recommended_milestone")
    if overall == "failed" and next_milestone != "GitHub Pages Workflow Repair v0":
        errors.append(
            "github_pages_run_evidence_report.json: failed decision must recommend GitHub Pages Workflow Repair v0."
        )


def _validate_latest_run(value: Any, errors: list[str]) -> None:
    if not isinstance(value, Mapping):
        errors.append("github_pages_run_evidence_report.json: latest_pages_run must be an object.")
        return
    available = value.get("available")
    if not isinstance(available, bool):
        errors.append("github_pages_run_evidence_report.json: latest_pages_run.available must be boolean.")
    if available:
        run_id = value.get("run_id")
        if not isinstance(run_id, int):
            errors.append("github_pages_run_evidence_report.json: latest_pages_run.run_id must be an integer.")
        if not _looks_like_sha(value.get("head_sha")):
            errors.append("github_pages_run_evidence_report.json: latest_pages_run.head_sha must be a full SHA.")
    if value.get("status") not in VALID_RUN_STATUSES:
        errors.append("github_pages_run_evidence_report.json: latest_pages_run.status has an unexpected value.")
    if value.get("conclusion") not in VALID_RUN_CONCLUSIONS:
        errors.append("github_pages_run_evidence_report.json: latest_pages_run.conclusion has an unexpected value.")


def _validate_artifact_evidence(value: Any, errors: list[str]) -> None:
    if not isinstance(value, Mapping):
        errors.append("github_pages_run_evidence_report.json: artifact_evidence must be an object.")
        return
    for key in ("available", "downloaded", "verified_contents"):
        if not isinstance(value.get(key), bool):
            errors.append(f"github_pages_run_evidence_report.json: artifact_evidence.{key} must be boolean.")
    if value.get("verified_contents") and not value.get("downloaded"):
        errors.append("github_pages_run_evidence_report.json: artifact contents cannot be verified if not downloaded.")


def _validate_deployment_evidence(value: Any, overall: Any, errors: list[str]) -> None:
    if not isinstance(value, Mapping):
        errors.append("github_pages_run_evidence_report.json: deployment_evidence must be an object.")
        return
    success_claim = value.get("success_claim_allowed")
    if not isinstance(success_claim, bool):
        errors.append("github_pages_run_evidence_report.json: deployment_evidence.success_claim_allowed must be boolean.")
        return
    if overall != "verified_deployed" and success_claim:
        errors.append("deployment success may not be claimed unless overall_decision is verified_deployed.")
    if overall == "verified_deployed" and not success_claim:
        errors.append("verified_deployed requires deployment_evidence.success_claim_allowed true.")
    if success_claim and not value.get("page_url"):
        errors.append("deployment success claim requires a page_url.")


def _validate_workflow(report: Any, errors: list[str]) -> None:
    if not WORKFLOW_PATH.is_file():
        errors.append(".github/workflows/pages.yml: workflow is missing.")
        return
    text = WORKFLOW_PATH.read_text(encoding="utf-8")
    if "path: site/dist" not in text:
        errors.append(".github/workflows/pages.yml: upload path must be site/dist.")
    if "path: " + LEGACY_STATIC_ROOT in text:
        errors.append(".github/workflows/pages.yml: active workflow uploads the retired static artifact.")
    for needle in (
        "actions/configure-pages@v5",
        "actions/upload-pages-artifact@v3",
        "actions/deploy-pages@v4",
    ):
        if needle not in text:
            errors.append(f".github/workflows/pages.yml: missing {needle!r}.")
    if isinstance(report, Mapping) and report.get("workflow_upload_path") != _workflow_upload_path():
        errors.append("github_pages_run_evidence_report.json: workflow_upload_path does not match workflow file.")


def _validate_markdown_claims(report: Any, errors: list[str]) -> None:
    if not PACK_DIR.is_dir():
        return
    text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in PACK_DIR.glob("*.md")
        if path.is_file()
    ).casefold()
    deployment = _mapping(_mapping(report).get("deployment_evidence"))
    success_claim_allowed = deployment.get("success_claim_allowed") is True
    if not success_claim_allowed:
        prohibited = (
            "deployment success is verified",
            "github pages deployment succeeded",
            "deployed static publication is live",
            "production backend is deployed",
            "live search is deployed",
        )
        for phrase in prohibited:
            if phrase in text:
                errors.append(f"audit pack claims {phrase!r} without deployment evidence.")


def _workflow_upload_path() -> str | None:
    if not WORKFLOW_PATH.is_file():
        return None
    previous_line = ""
    for line in WORKFLOW_PATH.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if previous_line == "with:" and stripped.startswith("path: "):
            return stripped.removeprefix("path: ").strip()
        previous_line = stripped
    return None


def _load_json(path: Path, errors: list[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"{_rel(path)}: JSON file is missing.")
    except json.JSONDecodeError as exc:
        errors.append(f"{_rel(path)}: invalid JSON: {exc}.")
    return None


def _format_plain(report: Mapping[str, Any]) -> str:
    lines = [
        "GitHub Pages run evidence validation",
        f"status: {report['status']}",
        f"report_id: {report.get('report_id')}",
        f"current_head: {report.get('current_head')}",
        f"workflow_upload_path: {report.get('workflow_upload_path')}",
        f"github_actions_tool_status: {report.get('github_actions_tool_status')}",
        f"latest_run_conclusion: {report.get('latest_run_conclusion')}",
        f"overall_decision: {report.get('overall_decision')}",
        f"success_claim_allowed: {report.get('success_claim_allowed')}",
    ]
    if report["errors"]:
        lines.append("errors:")
        lines.extend(f"- {error}" for error in report["errors"])
    if report["warnings"]:
        lines.append("warnings:")
        lines.extend(f"- {warning}" for warning in report["warnings"])
    return "\n".join(lines) + "\n"


def _looks_like_sha(value: Any) -> bool:
    return isinstance(value, str) and len(value) == 40 and all(char in "0123456789abcdef" for char in value)


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
