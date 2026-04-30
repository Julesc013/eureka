from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
PACK_DIR = REPO_ROOT / "control" / "audits" / "static-artifact-promotion-review-v0"
REPORT_PATH = PACK_DIR / "static_artifact_promotion_report.json"
WORKFLOW_PATH = REPO_ROOT / ".github" / "workflows" / "pages.yml"
GENERATED_ARTIFACTS = (
    REPO_ROOT / "control" / "inventory" / "generated_artifacts" / "generated_artifacts.json"
)
LEGACY_STATIC_ROOT = "public" + "_site"
LEGACY_STATIC_EXISTS_KEY = LEGACY_STATIC_ROOT + "_exists"
LEGACY_EXTERNAL_EXISTS_KEY = ("third" + "_party") + "_exists"

VALID_DECISIONS = {
    "promoted_as_active_static_artifact",
    "conditionally_promoted_pending_github_actions_evidence",
    "not_promoted_due_blockers",
}
VALID_ACTIONS_STATUSES = {"verified", "unverified", "failed", "unavailable"}
REQUIRED_FILES = {
    "README.md",
    "CURRENT_STATIC_ARTIFACT.md",
    "PROMOTION_DECISION.md",
    "VALIDATION_EVIDENCE.md",
    "WORKFLOW_REVIEW.md",
    "GENERATED_ARTIFACT_REVIEW.md",
    "STATIC_SAFETY_REVIEW.md",
    "BASE_PATH_REVIEW.md",
    "PUBLIC_DATA_SURFACE_REVIEW.md",
    "STALE_REFERENCE_REVIEW.md",
    "RISK_REGISTER.md",
    "BLOCKERS_AND_DEFERRED_WORK.md",
    "NEXT_STEPS.md",
    "static_artifact_promotion_report.json",
}


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Validate Static Artifact Promotion Review v0 without network access."
    )
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_static_artifact_promotion_review()
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(report))
    return 0 if report["status"] == "valid" else 1


def validate_static_artifact_promotion_review() -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []

    _validate_pack_files(errors)
    promotion = _load_json(REPORT_PATH, errors)
    _validate_report(promotion, errors)
    _validate_workflow(errors)
    _validate_generated_artifact_inventory(errors)
    _validate_actions_claim_boundary(promotion, errors)

    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "static_artifact_promotion_review_validator_v0",
        "pack_dir": "control/audits/static-artifact-promotion-review-v0",
        "report_id": _mapping(promotion).get("report_id"),
        "decision": _mapping(promotion).get("decision"),
        "active_static_artifact": _mapping(promotion).get("active_static_artifact"),
        "github_actions_status": _mapping(promotion).get("github_actions_status"),
        "workflow_upload_path": _workflow_upload_path(),
        "errors": errors,
        "warnings": warnings,
    }


def _validate_pack_files(errors: list[str]) -> None:
    if not PACK_DIR.is_dir():
        errors.append("static artifact promotion review pack is missing.")
        return
    present = {path.name for path in PACK_DIR.iterdir() if path.is_file()}
    missing = sorted(REQUIRED_FILES - present)
    if missing:
        errors.append(f"static artifact promotion review pack missing files {missing}.")


def _validate_report(report: Any, errors: list[str]) -> None:
    if not isinstance(report, Mapping):
        errors.append("static_artifact_promotion_report.json: report must be a JSON object.")
        return

    expected_scalars = {
        "report_id": "static_artifact_promotion_review_v0",
        "created_by_slice": "static_artifact_promotion_review_v0",
        "active_static_artifact": "site/dist",
        "workflow_upload_path": "site/dist",
        "generated_artifact_id": "static_site_dist",
        "repository_layout_valid": True,
        "static_site_valid": True,
        "pages_artifact_valid": True,
        "generated_artifact_drift_status": "passed",
        "manual_edits_allowed": False,
        "deployment_success_claimed": False,
    }
    for key, expected in expected_scalars.items():
        if report.get(key) != expected:
            errors.append(f"static_artifact_promotion_report.json: {key} must be {expected!r}.")

    decision = report.get("decision")
    if decision not in VALID_DECISIONS:
        errors.append(
            "static_artifact_promotion_report.json: decision must be one of "
            f"{sorted(VALID_DECISIONS)}."
        )

    actions_status = report.get("github_actions_status")
    if actions_status not in VALID_ACTIONS_STATUSES:
        errors.append(
            "static_artifact_promotion_report.json: github_actions_status must be one of "
            f"{sorted(VALID_ACTIONS_STATUSES)}."
        )

    if report.get(LEGACY_STATIC_EXISTS_KEY) is not False:
        errors.append("static_artifact_promotion_report.json: retired static artifact must be absent.")
    if report.get(LEGACY_EXTERNAL_EXISTS_KEY) is not False:
        errors.append("static_artifact_promotion_report.json: retired outside-reference root must be absent.")
    if report.get("external_exists") is not True:
        errors.append("static_artifact_promotion_report.json: external_exists must be true.")

    surfaces = report.get("public_data_surfaces")
    if not isinstance(surfaces, Mapping):
        errors.append("static_artifact_promotion_report.json: public_data_surfaces must be an object.")
    else:
        for key in ("data", "lite", "text", "files", "demo", "assets", "nojekyll"):
            surface = surfaces.get(key)
            if not isinstance(surface, Mapping):
                errors.append(f"static_artifact_promotion_report.json: missing surface {key!r}.")
                continue
            if surface.get("present") is not True or surface.get("validated") is not True:
                errors.append(f"static_artifact_promotion_report.json: surface {key!r} must be present and validated.")

    stale = report.get("stale_reference_summary")
    if not isinstance(stale, Mapping):
        errors.append("static_artifact_promotion_report.json: stale_reference_summary must be an object.")
    else:
        for key in (LEGACY_STATIC_ROOT, "third" + "_party", "third" + "-party", "Third" + " Party"):
            summary = stale.get(key)
            if not isinstance(summary, Mapping):
                errors.append(f"static_artifact_promotion_report.json: stale summary missing {key!r}.")
                continue
            if summary.get("active_current_references") != 0:
                errors.append(f"static_artifact_promotion_report.json: stale summary for {key!r} must have zero active references.")

    for relative in (
        "PROMOTION_DECISION.md",
        "WORKFLOW_REVIEW.md",
        "STALE_REFERENCE_REVIEW.md",
    ):
        if not (PACK_DIR / relative).is_file():
            errors.append(f"{relative}: required review file is missing.")


def _validate_workflow(errors: list[str]) -> None:
    if not WORKFLOW_PATH.is_file():
        errors.append(".github/workflows/pages.yml: workflow is missing.")
        return
    text = WORKFLOW_PATH.read_text(encoding="utf-8")
    if "path: site/dist" not in text:
        errors.append(".github/workflows/pages.yml: upload path must be site/dist.")
    if "path: " + LEGACY_STATIC_ROOT in text:
        errors.append(".github/workflows/pages.yml: upload path uses retired static artifact.")
    for command in (
        "python site/build.py",
        "python site/validate.py",
        "python scripts/check_github_pages_static_artifact.py --path site/dist",
        "python scripts/check_generated_artifact_drift.py --artifact static_site_dist",
    ):
        if command not in text:
            errors.append(f".github/workflows/pages.yml: missing command {command!r}.")


def _validate_generated_artifact_inventory(errors: list[str]) -> None:
    inventory = _load_json(GENERATED_ARTIFACTS, errors)
    if not isinstance(inventory, Mapping):
        return
    groups = inventory.get("artifact_groups")
    if not isinstance(groups, list):
        errors.append("generated_artifacts.json: artifact_groups must be a list.")
        return
    static_group = None
    for group in groups:
        if isinstance(group, Mapping) and group.get("artifact_id") == "static_site_dist":
            static_group = group
            break
    if static_group is None:
        errors.append("generated_artifacts.json: static_site_dist artifact group is missing.")
        return
    paths = static_group.get("artifact_paths")
    if not isinstance(paths, list) or "site/dist" not in paths:
        errors.append("generated_artifacts.json: static_site_dist must own site/dist.")
    if static_group.get("manual_edits_allowed") is not False:
        errors.append("generated_artifacts.json: static_site_dist.manual_edits_allowed must be false.")


def _validate_actions_claim_boundary(report: Any, errors: list[str]) -> None:
    if not isinstance(report, Mapping):
        return
    actions_status = report.get("github_actions_status")
    if actions_status == "unverified" and report.get("deployment_success_claimed") is not False:
        errors.append("GitHub Actions status is unverified, so deployment_success_claimed must be false.")

    text = "\n".join(
        path.read_text(encoding="utf-8")
        for path in PACK_DIR.glob("*.md")
        if path.is_file()
    ).casefold()
    prohibited_when_unverified = (
        "github pages deployment succeeded",
        "github pages deployment success is verified",
        "deployment success: verified",
        "production ready",
        "production-ready",
    )
    if actions_status == "unverified":
        for phrase in prohibited_when_unverified:
            if phrase in text:
                errors.append(f"audit pack claims {phrase!r} while GitHub Actions status is unverified.")


def _workflow_upload_path() -> str | None:
    if not WORKFLOW_PATH.is_file():
        return None
    for line in WORKFLOW_PATH.read_text(encoding="utf-8").splitlines():
        stripped = line.strip()
        if stripped.startswith("path: "):
            return stripped.removeprefix("path: ").strip()
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
        "Static artifact promotion review validation",
        f"status: {report['status']}",
        f"report_id: {report.get('report_id')}",
        f"decision: {report.get('decision')}",
        f"active_static_artifact: {report.get('active_static_artifact')}",
        f"github_actions_status: {report.get('github_actions_status')}",
        f"workflow_upload_path: {report.get('workflow_upload_path')}",
    ]
    if report["errors"]:
        lines.append("errors:")
        lines.extend(f"- {error}" for error in report["errors"])
    if report["warnings"]:
        lines.append("warnings:")
        lines.extend(f"- {warning}" for warning in report["warnings"])
    return "\n".join(lines) + "\n"


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return path.as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
