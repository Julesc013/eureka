"""Public-alpha release-check helpers."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
import hashlib
import json
from pathlib import Path
import subprocess
from typing import Any

from runtime.local.corpus_gate_closeout import DEFAULT_GATE_TARGET
from runtime.local.external_staging import validate_report as validate_external_staging_report
from runtime.local.local_machine_public_exposure import validate_report as validate_local_machine_public_exposure_report
from runtime.local.local_machine_staging_mvp import validate_report as validate_local_machine_staging_report
from runtime.local.staging_package import bundle_status, validate_bundle
from scripts.eureka_public_alpha_launch_gate import validate_launch_gate_report
from scripts.eureka_public_alpha_rehearsal import validate_report as validate_rehearsal_report


TASK_ID = "PUBLIC-ALPHA-RELEASE-CHECKS-00"
REPORT_SCHEMA_VERSION = "eureka.public_alpha_release_check_report.v0"
REPORT_JSON = "release_check_report.json"
REPORT_MD = "RELEASE_CHECK_REPORT.md"
DEFAULT_OUT = ".eureka/release-checks/public-alpha/latest"

SECRET_MARKERS = (
    "local-dev-token",
    "X-Eureka-Workbench-Token",
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "DEEPSEEK_API_KEY",
    "BEGIN PRIVATE KEY",
    "PRIVATE KEY",
    "api_key",
    "apikey",
    "sk-",
    "token=",
    "authorization:",
    "bearer ",
)
SAFETY_ZERO_FIELDS = (
    "binary_verified_count",
    "download_safe_count",
    "execution_safe_count",
    "rights_cleared_count",
)
BLOCKER_CATEGORIES = (
    "git_blockers",
    "local_release_blockers",
    "external_staging_blockers",
    "deployment_blockers",
    "release_process_blockers",
    "approval_blockers",
    "safety_blockers",
)
FOCUSED_TEST_COMMAND = (
    "python",
    "-m",
    "unittest",
    "tests.e2e.test_public_alpha_corpus_gate_closeout",
    "tests.e2e.test_local_to_staging_deployment",
    "tests.e2e.test_public_alpha_rehearsal",
    "tests.e2e.test_public_alpha_launch_blocker_closeout",
    "tests.e2e.test_external_staging_host_provision",
    "tests.e2e.test_external_staging_host_config",
    "tests.e2e.test_local_machine_staging_provision",
    "tests.e2e.test_local_machine_public_exposure_plan",
)

CommandRunner = Callable[[Sequence[str]], Mapping[str, Any]]


def run_release_checks(
    *,
    bundle: str | Path,
    corpus_gate_closeout: str | Path,
    rehearsal_report: str | Path,
    external_staging_report: str | Path,
    launch_gate_report: str | Path,
    out_dir: str | Path,
    local_machine_staging_report: str | Path | None = None,
    local_machine_public_exposure_report: str | Path | None = None,
    full_discovery_report: str | Path | None = None,
    release_promotion_report: str | Path | None = None,
    run_tests: bool = True,
    allow_dirty: bool = False,
    require_origin_sync: bool = True,
    command_runner: CommandRunner | None = None,
) -> dict[str, Any]:
    runner = command_runner or _run_command
    bundle_path = Path(bundle)
    corpus_path = Path(corpus_gate_closeout)
    rehearsal_path = Path(rehearsal_report)
    external_path = Path(external_staging_report)
    local_machine_path = Path(local_machine_staging_report) if local_machine_staging_report else None
    exposure_path = Path(local_machine_public_exposure_report) if local_machine_public_exposure_report else None
    launch_path = Path(launch_gate_report)

    commands = _release_commands(
        bundle_path=bundle_path,
        corpus_path=corpus_path,
        rehearsal_path=rehearsal_path,
        external_path=external_path,
        local_machine_path=local_machine_path,
        exposure_path=exposure_path,
        launch_path=launch_path,
        run_tests=run_tests,
    )
    command_results = [_normalize_command_result(runner(command)) for command in commands]
    command_statuses = {str(item["id"]): str(item["status"]) for item in command_results}

    git_state = _git_state_from_results(command_results)
    corpus = _read_json_for_audit(corpus_path)
    rehearsal = _read_json_for_audit(rehearsal_path)
    external = _read_json_for_audit(external_path)
    local_machine = _read_json_for_audit(local_machine_path) if local_machine_path else {}
    exposure = _read_json_for_audit(exposure_path) if exposure_path else {}
    launch = _read_json_for_audit(launch_path)
    staging = bundle_status(bundle_path)
    full_discovery = _optional_gate_status(full_discovery_report, default="not_run")
    release_promotion = _optional_gate_status(release_promotion_report, default="not_run")

    blocker_categories: dict[str, list[str]] = {category: [] for category in BLOCKER_CATEGORIES}
    blockers: list[dict[str, str]] = []
    warnings: list[str] = []

    def add_blocker(category: str, blocker_id: str, message: str, *, status: str = "blocked", evidence: str = "") -> None:
        blockers.append({"category": category, "id": blocker_id, "status": status, "message": message, "evidence": evidence})
        blocker_categories.setdefault(category, []).append(blocker_id)

    if not git_state["git_clean"] and not allow_dirty:
        add_blocker("git_blockers", "git_worktree_dirty", "git working tree is dirty", status="failed", evidence="git status --short --branch")
    if require_origin_sync and git_state["origin_synced"] is not True:
        add_blocker("git_blockers", "origin_dev_not_synced", "local HEAD does not match origin/dev", status="failed", evidence="git rev-parse HEAD/origin/dev")

    _add_command_blockers(add_blocker, command_results)
    _add_input_blockers(
        add_blocker,
        bundle_path,
        corpus_path,
        rehearsal_path,
        external_path,
        local_machine_path,
        exposure_path,
        launch_path,
        staging,
        rehearsal,
        external,
        local_machine,
        exposure,
        launch,
    )
    _add_launch_blockers(add_blocker, launch)

    if full_discovery["status"] != "pass":
        add_blocker("release_process_blockers", "full_discovery_not_passed", "full discovery report is not passed", status=full_discovery["status"], evidence=full_discovery["evidence"])
    if release_promotion["status"] != "pass":
        add_blocker("release_process_blockers", "release_promotion_not_passed", "release promotion report is not passed", status=release_promotion["status"], evidence=release_promotion["evidence"])

    local_failure = any(blocker["status"] == "failed" and blocker["category"] in {"git_blockers", "local_release_blockers", "safety_blockers"} for blocker in blockers)
    status = "FAIL" if local_failure else ("PASS_WITH_WARNINGS" if blockers else "PASS")
    release_status = _release_status(status=status, blockers=blockers)
    if status == "PASS_WITH_WARNINGS":
        warnings.append("local release checks passed but launch remains blocked by unresolved gates")
    if _local_machine_staging_status(local_machine) == "pass":
        warnings.append("local-machine staging passed but does not satisfy external/public hosting")
    if _local_machine_public_exposure_status(exposure) == "pass" and exposure.get("external_staging_deferred") is True:
        warnings.append("external SSH staging is deferred by the local-machine public exposure plan")
    if external.get("smoke_status") in {"blocked", "not_run"}:
        warnings.append("external staging smoke has not passed")
    if full_discovery["status"] != "pass":
        warnings.append("full discovery report is not passed or not provided")
    if release_promotion["status"] != "pass":
        warnings.append("release promotion report is not passed or not provided")

    report = {
        "schema_version": REPORT_SCHEMA_VERSION,
        "task_id": TASK_ID,
        "status": status,
        "release_status": release_status,
        "git_branch": git_state["git_branch"],
        "git_head": git_state["git_head"],
        "origin_dev_head": git_state["origin_dev_head"],
        "git_clean": git_state["git_clean"],
        "origin_synced": git_state["origin_synced"],
        "generated_artifacts_clean": command_statuses.get("generated_artifact_cleanliness") == "pass",
        "corpus_gate_status": str(corpus.get("corpus_gate_status") or staging.get("corpus_gate_status") or "unknown"),
        "reviewed_artifact_gate_count": int(corpus.get("reviewed_artifact_gate_count") or staging.get("reviewed_artifact_gate_count") or 0),
        "artifact_verified_count": int(corpus.get("artifact_verified_count") or staging.get("artifact_verified_count") or 0),
        "binary_verified_count": int(corpus.get("binary_verified_count") or staging.get("binary_verified_count") or 0),
        "download_safe_count": int(corpus.get("download_safe_count") or staging.get("download_safe_count") or 0),
        "execution_safe_count": int(corpus.get("execution_safe_count") or staging.get("execution_safe_count") or 0),
        "rights_cleared_count": int(corpus.get("rights_cleared_count") or staging.get("rights_cleared_count") or 0),
        "staging_bundle_status": str(staging.get("status") or "unknown"),
        "rehearsal_status": _rehearsal_status(rehearsal),
        "external_staging_status": _external_staging_status(external),
        "external_staging_deployment_status": str(external.get("deployment_status") or "not_configured"),
        "external_staging_smoke_status": str(external.get("smoke_status") or "not_run"),
        "local_machine_staging_status": _local_machine_staging_status(local_machine),
        "local_machine_staging_report_status": str(local_machine.get("status") or ("not_provided" if not local_machine_path else "missing")),
        "local_machine_staging_report_digest": _file_sha256(local_machine_path) if local_machine_path else "",
        "local_machine_public_exposure_status": _local_machine_public_exposure_status(exposure),
        "local_machine_public_exposure_report_status": str(exposure.get("status") or ("not_provided" if not exposure_path else "missing")),
        "local_machine_public_exposure_report_digest": _file_sha256(exposure_path) if exposure_path else "",
        "selected_hosting_path": str(exposure.get("selected_hosting_path") or ""),
        "exposure_mode": str(exposure.get("exposure_mode") or ""),
        "public_exposure_enabled": bool(exposure.get("public_exposure_enabled") is True),
        "external_staging_deferred": bool(exposure.get("external_staging_deferred") is True),
        "public_readiness_status": str(exposure.get("public_readiness_status") or "unknown"),
        "ops_posture_status": str(exposure.get("ops_posture_status") or "unknown"),
        "full_discovery_status": full_discovery["status"],
        "full_discovery_report_digest": full_discovery["digest"],
        "release_promotion_status": release_promotion["status"],
        "release_promotion_report_digest": release_promotion["digest"],
        "public_launch_approval_status": str(launch.get("public_launch_approval_status") or "missing"),
        "aide_doctor_status": command_statuses.get("aide_doctor", "unknown"),
        "aide_validate_status": command_statuses.get("aide_validate", "unknown"),
        "architecture_boundary_status": command_statuses.get("architecture_boundaries", "unknown"),
        "generated_artifact_cleanliness_status": command_statuses.get("generated_artifact_cleanliness", "unknown"),
        "diff_check_status": command_statuses.get("git_diff_check", "unknown"),
        "cached_diff_check_status": command_statuses.get("git_diff_cached_check", "unknown"),
        "focused_test_status": command_statuses.get("focused_tests", "skipped"),
        "command_results": command_results,
        "blocker_categories": blocker_categories,
        "blockers": blockers,
        "warnings": _dedupe(warnings),
        "next_recommended_task": _next_recommended_task(
            blocker_categories,
            external_status=_external_staging_status(external),
            local_machine_status=_local_machine_staging_status(local_machine),
            exposure_status=_local_machine_public_exposure_status(exposure),
            ops_posture_status=str(exposure.get("ops_posture_status") or "unknown"),
        ),
        "generated_at": "not_recorded_deterministic_public_alpha_release_checks",
    }
    write_release_check_reports(report, out_dir)
    return report


def validate_release_check_report(report: str | Path) -> list[str]:
    errors: list[str] = []
    try:
        payload = _read_json(report)
    except (OSError, json.JSONDecodeError) as exc:
        return [f"report could not be read: {type(exc).__name__}"]
    required = (
        "task_id",
        "status",
        "release_status",
        "git_branch",
        "git_head",
        "origin_dev_head",
        "git_clean",
        "origin_synced",
        "generated_artifacts_clean",
        "corpus_gate_status",
        "reviewed_artifact_gate_count",
        "artifact_verified_count",
        "staging_bundle_status",
        "rehearsal_status",
        "external_staging_status",
        "local_machine_staging_status",
        "local_machine_staging_report_status",
        "local_machine_staging_report_digest",
        "local_machine_public_exposure_status",
        "local_machine_public_exposure_report_status",
        "local_machine_public_exposure_report_digest",
        "selected_hosting_path",
        "exposure_mode",
        "public_exposure_enabled",
        "external_staging_deferred",
        "public_readiness_status",
        "ops_posture_status",
        "full_discovery_status",
        "release_promotion_status",
        "aide_doctor_status",
        "aide_validate_status",
        "architecture_boundary_status",
        "generated_artifact_cleanliness_status",
        "diff_check_status",
        "focused_test_status",
        "command_results",
        "blocker_categories",
        "blockers",
        "warnings",
        "next_recommended_task",
    )
    for key in required:
        if key not in payload:
            errors.append(f"missing required field: {key}")
    if payload.get("task_id") != TASK_ID:
        errors.append(f"task_id must be {TASK_ID}")
    if payload.get("status") not in {"PASS", "PASS_WITH_WARNINGS", "FAIL"}:
        errors.append("status must be PASS, PASS_WITH_WARNINGS, or FAIL")
    if payload.get("release_status") not in {"blocked", "local_release_checks_green", "ready_for_external_staging", "ready_for_release_promotion", "ready_for_launch_approval", "ready"}:
        errors.append("release_status is not recognized")
    if payload.get("local_machine_staging_status") not in {"pass", "fail", "unknown", "missing", "not_provided"}:
        errors.append("local_machine_staging_status is not recognized")
    if payload.get("local_machine_staging_report_status") not in {"PASS", "PASS_WITH_WARNINGS", "FAIL", "missing", "not_provided", "unknown"}:
        errors.append("local_machine_staging_report_status is not recognized")
    if payload.get("local_machine_public_exposure_status") not in {"pass", "fail", "unknown", "missing", "not_provided"}:
        errors.append("local_machine_public_exposure_status is not recognized")
    if payload.get("local_machine_public_exposure_report_status") not in {"PASS", "PASS_WITH_WARNINGS", "FAIL", "missing", "not_provided", "unknown"}:
        errors.append("local_machine_public_exposure_report_status is not recognized")
    if payload.get("public_exposure_enabled") is True:
        errors.append("release-check report must not claim public exposure is enabled")
    if payload.get("status") == "PASS":
        for key in ("git_clean", "generated_artifacts_clean"):
            if payload.get(key) is not True:
                errors.append(f"report claims PASS while {key} is not true")
        if payload.get("focused_test_status") != "pass":
            errors.append("report claims PASS while focused tests did not pass")
    for key in ("aide_doctor_status", "aide_validate_status", "architecture_boundary_status", "generated_artifact_cleanliness_status", "diff_check_status"):
        if payload.get(key) == "fail" and payload.get("status") != "FAIL":
            errors.append(f"report must be FAIL when {key} failed")
    if payload.get("full_discovery_status") == "pass" and not payload.get("full_discovery_report_digest"):
        errors.append("report claims full discovery passed without report evidence")
    if payload.get("release_promotion_status") == "pass" and not payload.get("release_promotion_report_digest"):
        errors.append("report claims release promotion passed without report evidence")
    if payload.get("external_staging_status") == "pass" and payload.get("external_staging_deployment_status") == "dry_run_pass":
        errors.append("report claims external staging pass while external report is dry-run only")
    if payload.get("local_machine_staging_status") == "pass" and not payload.get("local_machine_staging_report_digest"):
        errors.append("report claims local-machine staging passed without report evidence")
    if payload.get("local_machine_public_exposure_status") == "pass" and not payload.get("local_machine_public_exposure_report_digest"):
        errors.append("report claims local-machine public exposure planning passed without report evidence")
    if payload.get("public_launch_approval_status") == "approved":
        errors.append("release-check report must not claim public launch approval")
    for key in SAFETY_ZERO_FIELDS:
        if int(payload.get(key) or 0) != 0:
            errors.append(f"{key} must remain 0")
    if payload.get("full_discovery_status") != "pass" and not _has_blocker(payload, "full_discovery_not_passed"):
        errors.append("missing blocker for full discovery status")
    if payload.get("release_promotion_status") != "pass" and not _has_blocker(payload, "release_promotion_not_passed"):
        errors.append("missing blocker for release promotion status")
    if payload.get("external_staging_status") != "pass" and payload.get("external_staging_deferred") is not True and not _has_category_blocker(payload, "external_staging_blockers"):
        errors.append("missing blocker for external staging status")
    errors.extend(_payload_secret_errors("release_check_report", payload))
    return _dedupe(errors)


def write_release_check_reports(report: Mapping[str, Any], out_dir: str | Path) -> Path:
    output = Path(out_dir)
    output.mkdir(parents=True, exist_ok=True)
    json_path = output / REPORT_JSON
    _write_json(json_path, report)
    (output / REPORT_MD).write_text(render_release_markdown(report), encoding="utf-8")
    return json_path


def render_status(report: Mapping[str, Any]) -> str:
    return "\n".join(
        [
            f"status: {report.get('status')}",
            f"release_status: {report.get('release_status')}",
            f"git_branch: {report.get('git_branch')}",
            f"git_clean: {str(report.get('git_clean')).lower()}",
            f"origin_synced: {str(report.get('origin_synced')).lower()}",
            f"corpus_gate_status: {report.get('corpus_gate_status')}",
            f"staging_bundle_status: {report.get('staging_bundle_status')}",
            f"rehearsal_status: {report.get('rehearsal_status')}",
            f"external_staging_status: {report.get('external_staging_status')} ({report.get('external_staging_deployment_status')}/{report.get('external_staging_smoke_status')})",
            f"local_machine_staging_status: {report.get('local_machine_staging_status')} ({report.get('local_machine_staging_report_status')})",
            f"local_machine_public_exposure_status: {report.get('local_machine_public_exposure_status')} ({report.get('exposure_mode')})",
            f"full_discovery_status: {report.get('full_discovery_status')}",
            f"release_promotion_status: {report.get('release_promotion_status')}",
            f"focused_test_status: {report.get('focused_test_status')}",
            f"blockers: {len(report.get('blockers') or [])}",
            f"next_recommended_task: {report.get('next_recommended_task')}",
        ]
    ) + "\n"


def render_release_markdown(report: Mapping[str, Any]) -> str:
    blockers = report.get("blockers") or []
    blocker_lines = [f"- {item.get('id')}: {item.get('message')}" for item in blockers if isinstance(item, Mapping)] or ["- none"]
    warnings = [f"- {item}" for item in report.get("warnings") or []] or ["- none"]
    return "\n".join(
        [
            "# Public Alpha Release Checks",
            "",
            f"- Status: {report.get('status')}",
            f"- Release status: {report.get('release_status')}",
            f"- Git branch: {report.get('git_branch')}",
            f"- Git clean: {report.get('git_clean')}",
            f"- Origin synced: {report.get('origin_synced')}",
            f"- Corpus gate: {report.get('corpus_gate_status')}",
            f"- Staging bundle: {report.get('staging_bundle_status')}",
            f"- Rehearsal: {report.get('rehearsal_status')}",
            f"- External staging: {report.get('external_staging_status')} ({report.get('external_staging_deployment_status')}/{report.get('external_staging_smoke_status')})",
            f"- Local-machine staging: {report.get('local_machine_staging_status')} ({report.get('local_machine_staging_report_status')})",
            f"- Local-machine public exposure: {report.get('local_machine_public_exposure_status')} ({report.get('exposure_mode')})",
            f"- Full discovery: {report.get('full_discovery_status')}",
            f"- Release promotion: {report.get('release_promotion_status')}",
            "",
            "## Blockers",
            "",
            *blocker_lines,
            "",
            "## Warnings",
            "",
            *warnings,
            "",
            "Release checks are operational evidence only. They are not public launch, production hosting, release promotion, or public launch approval.",
            "",
        ]
    )


def _release_commands(
    *,
    bundle_path: Path,
    corpus_path: Path,
    rehearsal_path: Path,
    external_path: Path,
    local_machine_path: Path | None,
    exposure_path: Path | None,
    launch_path: Path,
    run_tests: bool,
) -> list[tuple[str, ...]]:
    corpus_dir = corpus_path.parent if corpus_path.name == "corpus_gate_closeout.json" else corpus_path
    commands = [
        ("git", "status", "--short", "--branch"),
        ("git", "rev-parse", "HEAD"),
        ("git", "rev-parse", "origin/dev"),
        ("python", "scripts/eureka_public_alpha_corpus_gate.py", "validate", "--closeout", str(corpus_dir)),
        ("python", "scripts/eureka_staging.py", "validate", "--bundle", str(bundle_path)),
        ("python", "scripts/eureka_public_alpha_rehearsal.py", "validate-report", "--report", str(rehearsal_path)),
        ("python", "scripts/eureka_external_staging.py", "validate-report", "--report", str(external_path)),
        ("python", "scripts/eureka_public_alpha_launch_gate.py", "validate-report", "--report", str(launch_path)),
        ("python", "scripts/check_architecture_boundaries.py"),
        ("python", "scripts/check_generated_artifact_cleanliness.py", "--check", "--json"),
        ("git", "diff", "--check"),
        ("git", "diff", "--cached", "--check"),
        ("py", "-3", ".aide/scripts/aide_lite.py", "doctor"),
        ("py", "-3", ".aide/scripts/aide_lite.py", "validate"),
    ]
    if local_machine_path is not None:
        commands.insert(7, ("python", "scripts/eureka_local_machine_staging.py", "validate-report", "--report", str(local_machine_path)))
    if exposure_path is not None:
        commands.insert(8, ("python", "scripts/eureka_local_machine_public_exposure.py", "validate-report", "--report", str(exposure_path)))
    if run_tests:
        commands.append(FOCUSED_TEST_COMMAND)
    return commands


def _run_command(command: Sequence[str]) -> dict[str, Any]:
    result = subprocess.run(list(command), capture_output=True, text=True, timeout=180, check=False)
    return {
        "command": list(command),
        "returncode": result.returncode,
        "stdout": result.stdout,
        "stderr": result.stderr,
    }


def _normalize_command_result(raw: Mapping[str, Any]) -> dict[str, Any]:
    command = [str(item) for item in raw.get("command") or []]
    returncode = int(raw.get("returncode") or 0)
    stdout = str(raw.get("stdout") or "")
    stderr = str(raw.get("stderr") or "")
    return {
        "id": _command_id(command),
        "command": command,
        "status": "pass" if returncode == 0 else "fail",
        "returncode": returncode,
        "stdout_summary": _summarize_output(stdout),
        "stderr_summary": _summarize_output(stderr),
    }


def _command_id(command: Sequence[str]) -> str:
    text = " ".join(command)
    if text.startswith("git status"):
        return "git_status"
    if text.startswith("git rev-parse HEAD"):
        return "git_head"
    if text.startswith("git rev-parse origin/dev"):
        return "origin_dev_head"
    if "eureka_public_alpha_corpus_gate.py" in text:
        return "corpus_gate_validate"
    if "eureka_staging.py" in text:
        return "staging_validate"
    if "eureka_public_alpha_rehearsal.py" in text:
        return "rehearsal_validate"
    if "eureka_external_staging.py" in text:
        return "external_staging_validate"
    if "eureka_local_machine_staging.py" in text:
        return "local_machine_staging_validate"
    if "eureka_local_machine_public_exposure.py" in text:
        return "local_machine_public_exposure_validate"
    if "eureka_public_alpha_launch_gate.py" in text:
        return "launch_gate_validate"
    if "check_architecture_boundaries.py" in text:
        return "architecture_boundaries"
    if "check_generated_artifact_cleanliness.py" in text:
        return "generated_artifact_cleanliness"
    if text.startswith("git diff --cached"):
        return "git_diff_cached_check"
    if text.startswith("git diff --check"):
        return "git_diff_check"
    if "aide_lite.py doctor" in text:
        return "aide_doctor"
    if "aide_lite.py validate" in text:
        return "aide_validate"
    if "unittest" in text:
        return "focused_tests"
    return _slug(text)


def _git_state_from_results(results: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    by_id = {str(item.get("id")): item for item in results}
    status = str(by_id.get("git_status", {}).get("stdout_summary") or "")
    branch_line = status.splitlines()[0] if status else ""
    branch = branch_line.replace("##", "").strip().split("...")[0] if branch_line.startswith("##") else ""
    dirty_lines = [line for line in status.splitlines() if line and not line.startswith("##")]
    head = _first_line(str(by_id.get("git_head", {}).get("stdout_summary") or ""))
    origin = _first_line(str(by_id.get("origin_dev_head", {}).get("stdout_summary") or ""))
    origin_synced: bool | str
    if not head or not origin:
        origin_synced = "unknown"
    else:
        origin_synced = head == origin
    return {
        "git_branch": branch,
        "git_head": head,
        "origin_dev_head": origin,
        "git_clean": not dirty_lines,
        "origin_synced": origin_synced,
    }


def _add_command_blockers(add_blocker: Callable[..., None], command_results: Sequence[Mapping[str, Any]]) -> None:
    local_ids = {"corpus_gate_validate", "staging_validate", "rehearsal_validate", "external_staging_validate", "local_machine_staging_validate", "local_machine_public_exposure_validate", "launch_gate_validate", "focused_tests"}
    safety_ids = {"architecture_boundaries", "generated_artifact_cleanliness", "git_diff_check", "git_diff_cached_check", "aide_doctor", "aide_validate"}
    for item in command_results:
        if item.get("status") == "pass":
            continue
        command_id = str(item.get("id") or "command")
        category = "local_release_blockers" if command_id in local_ids else "safety_blockers" if command_id in safety_ids else "git_blockers"
        add_blocker(category, f"{command_id}_failed", f"command failed: {command_id}", status="failed", evidence=" ".join(item.get("command") or []))


def _add_input_blockers(
    add_blocker: Callable[..., None],
    bundle_path: Path,
    corpus_path: Path,
    rehearsal_path: Path,
    external_path: Path,
    local_machine_path: Path | None,
    exposure_path: Path | None,
    launch_path: Path,
    staging: Mapping[str, Any],
    rehearsal: Mapping[str, Any],
    external: Mapping[str, Any],
    local_machine: Mapping[str, Any],
    exposure: Mapping[str, Any],
    launch: Mapping[str, Any],
) -> None:
    required_paths: list[tuple[str, Path]] = [
        ("bundle", bundle_path),
        ("corpus gate closeout", corpus_path),
        ("rehearsal report", rehearsal_path),
        ("external staging report", external_path),
        ("launch gate report", launch_path),
    ]
    if local_machine_path is not None:
        required_paths.append(("local-machine staging report", local_machine_path))
    if exposure_path is not None:
        required_paths.append(("local-machine public exposure report", exposure_path))
    for label, path in required_paths:
        if not path.exists():
            add_blocker("local_release_blockers", f"{_slug(label)}_missing", f"{label} is missing", status="failed", evidence=str(path))
    if staging.get("status") != "pass":
        add_blocker("local_release_blockers", "staging_bundle_invalid", "staging bundle is invalid", status="failed", evidence=str(bundle_path))
    if _rehearsal_status(rehearsal) != "GREEN":
        add_blocker("local_release_blockers", "local_rehearsal_not_green", "local rehearsal is not green", status="failed", evidence=str(rehearsal_path))
    if int(staging.get("reviewed_artifact_gate_count") or 0) < DEFAULT_GATE_TARGET:
        add_blocker("local_release_blockers", "reviewed_artifact_gate_below_target", "reviewed artifact gate count is below target", status="failed", evidence=str(bundle_path))
    for key in SAFETY_ZERO_FIELDS:
        if int(staging.get(key) or 0) != 0:
            add_blocker("safety_blockers", f"{key}_nonzero", f"{key} must remain 0", status="failed", evidence=str(bundle_path))
    exposure_defers_external = exposure_path is not None and _local_machine_public_exposure_status(exposure) == "pass" and exposure.get("external_staging_deferred") is True
    if _external_staging_status(external) != "pass" and not exposure_defers_external:
        add_blocker(
            "external_staging_blockers",
            "external_staging_not_smoked",
            "external staging is not deployed and smoked",
            status=_external_staging_status(external),
            evidence=str(external_path),
        )
    if local_machine_path is not None and _local_machine_staging_status(local_machine) != "pass":
        add_blocker(
            "local_release_blockers",
            "local_machine_staging_not_passed",
            "local-machine staging report is not passed",
            status=_local_machine_staging_status(local_machine),
            evidence=str(local_machine_path),
        )
    if exposure_path is not None:
        exposure_status = _local_machine_public_exposure_status(exposure)
        if exposure_status != "pass":
            add_blocker(
                "local_release_blockers",
                "local_machine_public_exposure_plan_not_passed",
                "local-machine public exposure report is not passed",
                status=exposure_status,
                evidence=str(exposure_path),
            )
        else:
            _add_exposure_blockers(add_blocker, exposure)
    if launch.get("launch_status") == "READY":
        add_blocker("approval_blockers", "launch_gate_claims_ready", "launch gate unexpectedly claims READY", status="failed", evidence=str(launch_path))


def _add_launch_blockers(add_blocker: Callable[..., None], launch: Mapping[str, Any]) -> None:
    categories = launch.get("blocker_categories") if isinstance(launch.get("blocker_categories"), Mapping) else {}
    for category, blocker_ids in categories.items():
        if category not in {"deployment_blockers", "approval_blockers"}:
            continue
        for blocker_id in blocker_ids if isinstance(blocker_ids, Sequence) and not isinstance(blocker_ids, str) else []:
            message = str(blocker_id).replace("_", " ")
            add_blocker(str(category), str(blocker_id), message, evidence="launch_gate_report")


def _add_exposure_blockers(add_blocker: Callable[..., None], exposure: Mapping[str, Any]) -> None:
    for item in exposure.get("blockers") or []:
        if not isinstance(item, Mapping):
            continue
        blocker_id = str(item.get("id") or "")
        if blocker_id in {"full_discovery_not_passed", "release_promotion_not_passed", "public_launch_approval_missing"}:
            continue
        category = str(item.get("category") or "deployment_blockers")
        add_blocker(
            category,
            blocker_id,
            str(item.get("message") or blocker_id.replace("_", " ")),
            status=str(item.get("status") or "blocked"),
            evidence="local_machine_public_exposure_report",
        )


def _optional_gate_status(path: str | Path | None, *, default: str) -> dict[str, str]:
    if not path:
        return {"status": default, "digest": "", "evidence": "report not provided"}
    report_path = Path(path)
    if not report_path.is_file():
        return {"status": "missing", "digest": "", "evidence": str(report_path)}
    payload = _read_json(report_path)
    status = _status_from_payload(payload)
    return {"status": status, "digest": _file_sha256(report_path), "evidence": str(report_path)}


def _status_from_payload(payload: Mapping[str, Any]) -> str:
    for key in ("status", "result", "gate_status", "release_status"):
        value = str(payload.get(key) or "").strip().casefold()
        if value in {"pass", "passed", "green", "ready", "approved"}:
            return "pass"
        if value in {"fail", "failed", "red", "blocked", "missing"}:
            return "missing" if value == "missing" else "fail"
        if value in {"not_run", "unknown"}:
            return value
    return "unknown"


def _rehearsal_status(rehearsal: Mapping[str, Any]) -> str:
    if rehearsal.get("status") == "FAIL":
        return "RED"
    if rehearsal.get("status") in {"PASS", "PASS_WITH_WARNINGS"} and int(rehearsal.get("local_rehearsal_failures") or 0) == 0:
        return "GREEN"
    return "UNKNOWN"


def _external_staging_status(external: Mapping[str, Any]) -> str:
    deployment = str(external.get("deployment_status") or "not_configured")
    smoke = str(external.get("smoke_status") or "not_run")
    if deployment in {"deployed", "transfer_complete_manual_start_required"} and smoke == "pass":
        return "pass"
    if deployment == "dry_run_pass":
        return "dry_run"
    if deployment in {"missing_config", "not_configured"}:
        return "missing_config"
    if deployment == "confirmation_required":
        return "confirmation_required"
    if smoke == "blocked":
        return "blocked"
    if deployment == "failed" or smoke == "fail":
        return "fail"
    return "unknown"


def _local_machine_staging_status(report: Mapping[str, Any]) -> str:
    if not report:
        return "not_provided"
    if report.get("local_machine_staging_status") == "pass" and report.get("status") in {"PASS", "PASS_WITH_WARNINGS"}:
        errors = validate_local_machine_staging_report(report)
        return "pass" if not errors else "fail"
    if report.get("status") == "FAIL" or report.get("local_machine_staging_status") == "fail":
        return "fail"
    return "unknown"


def _local_machine_public_exposure_status(report: Mapping[str, Any]) -> str:
    if not report:
        return "not_provided"
    if report.get("status") in {"PASS", "PASS_WITH_WARNINGS"} and report.get("selected_hosting_path") == "local_machine" and report.get("public_exposure_enabled") is False:
        errors = validate_local_machine_public_exposure_report(report)
        return "pass" if not errors else "fail"
    if report.get("status") == "FAIL" or report.get("public_exposure_enabled") is True:
        return "fail"
    return "unknown"


def _release_status(*, status: str, blockers: Sequence[Mapping[str, str]]) -> str:
    if status == "FAIL":
        return "blocked"
    if not blockers:
        return "ready"
    categories = {str(item.get("category")) for item in blockers}
    if categories <= {"approval_blockers"}:
        return "ready_for_launch_approval"
    if categories <= {"release_process_blockers", "approval_blockers"}:
        return "ready_for_release_promotion"
    if categories <= {"external_staging_blockers", "deployment_blockers", "release_process_blockers", "approval_blockers"}:
        return "local_release_checks_green"
    return "blocked"


def _next_recommended_task(
    blocker_categories: Mapping[str, Sequence[str]],
    *,
    external_status: str,
    local_machine_status: str = "not_provided",
    exposure_status: str = "not_provided",
    ops_posture_status: str = "unknown",
) -> str:
    if exposure_status == "pass" and ops_posture_status != "pass":
        return "PUBLIC-ALPHA-OPS-POSTURE-00"
    if blocker_categories.get("external_staging_blockers") and external_status in {"dry_run", "missing_config", "blocked", "confirmation_required"}:
        if local_machine_status == "pass":
            return "LOCAL-MACHINE-PUBLIC-EXPOSURE-PLAN-00"
        return "EXTERNAL-STAGING-HOST-PROVISION-00-CONFIG"
    if blocker_categories.get("release_process_blockers"):
        return "PUBLIC-ALPHA-FULL-DISCOVERY-RELEASE-CHECK-00"
    if blocker_categories.get("deployment_blockers"):
        return "EXTERNAL-STAGING-HOST-PROVISION-00-CONFIG"
    return "PUBLIC-ALPHA-RELEASE-CHECKS-00-FIX" if blocker_categories else "PUBLIC-ALPHA-LAUNCH-APPROVAL-00"


def _has_blocker(report: Mapping[str, Any], blocker_id: str) -> bool:
    return any(isinstance(item, Mapping) and item.get("id") == blocker_id for item in report.get("blockers") or [])


def _has_category_blocker(report: Mapping[str, Any], category: str) -> bool:
    categories = report.get("blocker_categories") if isinstance(report.get("blocker_categories"), Mapping) else {}
    return bool(categories.get(category))


def _payload_secret_errors(label: str, value: Any) -> list[str]:
    text = value if isinstance(value, str) else json.dumps(value, sort_keys=True, ensure_ascii=True)
    lowered = text.casefold()
    return [f"{label} contains forbidden secret marker {marker}" for marker in SECRET_MARKERS if marker.casefold() in lowered]


def _summarize_output(value: str) -> str:
    lines = [line.rstrip() for line in str(value or "").splitlines() if line.strip()]
    return "\n".join(lines[-20:])


def _first_line(value: str) -> str:
    return value.splitlines()[0].strip() if value.splitlines() else ""


def _read_json(path: str | Path) -> dict[str, Any]:
    loaded = json.loads(Path(path).read_text(encoding="utf-8"))
    return loaded if isinstance(loaded, dict) else {}


def _read_json_for_audit(path: str | Path) -> dict[str, Any]:
    try:
        return _read_json(path)
    except (OSError, json.JSONDecodeError):
        return {}


def _write_json(path: str | Path, payload: Mapping[str, Any]) -> None:
    Path(path).write_text(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True) + "\n", encoding="utf-8")


def _file_sha256(path: str | Path) -> str:
    target = Path(path)
    return hashlib.sha256(target.read_bytes()).hexdigest() if target.is_file() else ""


def _dedupe(values: Sequence[str]) -> list[str]:
    seen = set()
    result = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


def _slug(value: str) -> str:
    return "".join(ch if ch.isalnum() else "_" for ch in value.lower()).strip("_")[:80] or "item"
