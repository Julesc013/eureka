#!/usr/bin/env python3
"""Audit public-alpha launch blockers from a staging bundle and rehearsal report."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local.corpus_gate_closeout import CLOSEOUT_JSON as CORPUS_CLOSEOUT_FILE
from runtime.local.corpus_gate_closeout import PUBLIC_ARTIFACT_RECORDS_JSONL, PUBLIC_EVIDENCE_SUMMARY_JSONL
from runtime.local.staging_mvp import MANIFEST_FILE, PUBLIC_INDEX_FILE, RUNTIME_CONFIG_FILE, bundle_status, validate_bundle
from scripts.eureka_public_alpha_rehearsal import validate_report as validate_rehearsal_report


TASK_ID = "PUBLIC-ALPHA-LAUNCH-BLOCKER-CLOSEOUT-00"
REPORT_SCHEMA_VERSION = "eureka.public_alpha_launch_gate_report.v0"
DEFAULT_OUT = ".eureka/launch/public-alpha/latest"
REPORT_JSON = "launch_gate_report.json"
REPORT_MD = "LAUNCH_GATE_REPORT.md"
BLOCKER_CATEGORIES = (
    "local_rehearsal_blockers",
    "safety_blockers",
    "corpus_evidence_blockers",
    "deployment_blockers",
    "release_process_blockers",
    "approval_blockers",
    "unknown_authority_blockers",
)
LAUNCH_STATUSES = ("BLOCKED", "READY_FOR_EXTERNAL_STAGING", "READY_FOR_PUBLIC_APPROVAL", "READY")
REPORT_STATUSES = ("PASS", "PASS_WITH_WARNINGS", "FAIL")
SECRET_MARKERS = (
    "local-dev-token",
    "X-Eureka-Workbench-Token",
    "OPENAI_API_KEY",
    "ANTHROPIC_API_KEY",
    "DEEPSEEK_API_KEY",
    "BEGIN PRIVATE KEY",
    "sk-",
)
LOCAL_REVIEW_ARTIFACTS = (
    ".eureka/local_review_ledger.jsonl",
    ".eureka/local_reviewed_records.jsonl",
    ".eureka/local_search_index.json",
    ".eureka/local_search_index.reviewed.json",
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    audit_parser = subparsers.add_parser("audit", help="Audit public-alpha launch blockers and write reports.")
    audit_parser.add_argument("--bundle", required=True)
    audit_parser.add_argument("--rehearsal-report", required=True)
    audit_parser.add_argument("--out", default=DEFAULT_OUT)
    audit_parser.add_argument("--fail-on-blocked", action="store_true")
    audit_parser.add_argument("--external-staging-url", default="")
    audit_parser.add_argument("--public-url", default="")
    audit_parser.add_argument("--approval-file", default="")
    audit_parser.add_argument("--full-discovery-report", default="")
    audit_parser.add_argument("--artifact-gate-report", default="")
    audit_parser.add_argument("--corpus-gate-closeout", default="")
    audit_parser.add_argument("--verified-evidence-report", default="")
    audit_parser.add_argument("--release-check-report", default="")
    audit_parser.add_argument("--production-auth-posture", choices=("approved", "missing", "unknown"), default="missing")
    audit_parser.add_argument("--allow-readonly-noauth", action="store_true")

    validate_parser = subparsers.add_parser("validate-report", help="Validate a launch gate JSON report.")
    validate_parser.add_argument("--report", required=True)
    validate_parser.add_argument("--json", action="store_true")

    status_parser = subparsers.add_parser("status", help="Print a concise launch gate report summary.")
    status_parser.add_argument("--report", required=True)

    args = parser.parse_args(argv)
    if args.command == "audit":
        options = {
            "external_staging_url": args.external_staging_url,
            "public_url": args.public_url,
            "approval_file": args.approval_file,
            "full_discovery_report": args.full_discovery_report,
            "artifact_gate_report": args.artifact_gate_report,
            "corpus_gate_closeout": args.corpus_gate_closeout,
            "verified_evidence_report": args.verified_evidence_report,
            "release_check_report": args.release_check_report,
            "production_auth_posture": args.production_auth_posture,
            "allow_readonly_noauth": args.allow_readonly_noauth,
        }
        report = audit_launch_gate(args.bundle, args.rehearsal_report, options=options)
        report_path = write_launch_gate_reports(report, args.out)
        print(f"Public alpha launch gate report: {report_path}", file=stdout)
        print(f"status: {report.get('status')}", file=stdout)
        print(f"launch_status: {report.get('launch_status')}", file=stdout)
        print(f"local_rehearsal: {report.get('local_rehearsal_status')}", file=stdout)
        print(f"blockers: {len(report.get('blockers') or [])}", file=stdout)
        if report.get("status") == "FAIL":
            for failure in report.get("local_audit_failures") or []:
                print(f"- {failure}", file=stderr)
            return 1
        if args.fail_on_blocked and report.get("launch_status") != "READY":
            print("public alpha launch remains blocked", file=stderr)
            return 1
        return 0

    if args.command == "validate-report":
        errors = validate_launch_gate_report(args.report)
        payload = {
            "schema_version": "eureka.public_alpha_launch_gate_validate_report.v0",
            "status": "pass" if not errors else "fail",
            "report": str(args.report),
            "errors": errors,
        }
        if args.json:
            print(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True), file=stdout)
        elif errors:
            print(f"Public alpha launch gate report validation failed: {args.report}", file=stderr)
            for error in errors:
                print(f"- {error}", file=stderr)
        else:
            print(f"Public alpha launch gate report validation passed: {args.report}", file=stdout)
        return 0 if not errors else 1

    if args.command == "status":
        try:
            report = load_report(args.report)
        except (OSError, json.JSONDecodeError) as exc:
            print(f"Could not read launch gate report: {type(exc).__name__}", file=stderr)
            return 1
        print(render_status(report), end="", file=stdout)
        return 0

    parser.error(f"unsupported command: {args.command}")
    return 2


def audit_launch_gate(
    bundle: str | Path,
    rehearsal_report: str | Path,
    *,
    options: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    opts = dict(options or {})
    bundle_path = Path(bundle)
    rehearsal_path = Path(rehearsal_report)
    before_hashes = _artifact_hashes(bundle_path, rehearsal_path)
    bundle_errors = validate_bundle(bundle_path)
    rehearsal_errors = validate_rehearsal_report(rehearsal_path)
    manifest = _read_json(bundle_path / MANIFEST_FILE)
    runtime_config = _read_json(bundle_path / RUNTIME_CONFIG_FILE)
    staging_status = bundle_status(bundle_path)
    rehearsal = _read_json(rehearsal_path)
    git_state = _git_state()

    local_audit_failures: list[str] = []
    local_audit_failures.extend(f"bundle validation: {error}" for error in bundle_errors)
    local_audit_failures.extend(f"rehearsal report validation: {error}" for error in rehearsal_errors)

    local_safety = _local_safety_status(rehearsal)
    if local_safety["local_safety_status"] == "fail":
        local_audit_failures.extend(local_safety["failures"])

    optional_sources = _optional_sources(opts)
    official_gate = _official_artifact_gate(optional_sources.get("artifact_gate_report"))
    corpus_gate = _corpus_gate_closeout(optional_sources.get("corpus_gate_closeout"))
    verified_evidence = _generic_report_status(optional_sources.get("verified_evidence_report"), default="unknown")
    if corpus_gate["status"] == "pass":
        verified_evidence = {"status": "pass", "evidence": corpus_gate["evidence"]}
    full_discovery = _generic_report_status(optional_sources.get("full_discovery_report"), default="not_run")
    release_promotion = _generic_report_status(optional_sources.get("release_check_report"), default="not_run")
    approval = _approval_status(optional_sources.get("approval_file"))

    external_staging_host_status = "configured" if _has_value(opts.get("external_staging_url")) else "missing"
    production_hosting_status = "configured" if _has_value(opts.get("public_url")) else "missing"
    tls_domain_status = _tls_status(str(opts.get("public_url") or ""))
    production_auth_status = _production_auth_status(opts)

    blocker_categories = {category: [] for category in BLOCKER_CATEGORIES}
    blockers: list[dict[str, Any]] = []

    def add_blocker(category: str, blocker_id: str, message: str, *, evidence: str, status: str = "blocked") -> None:
        item = {
            "category": category,
            "id": blocker_id,
            "status": status,
            "message": message,
            "evidence": evidence,
        }
        blockers.append(item)
        blocker_categories.setdefault(category, []).append(blocker_id)

    for failure in local_audit_failures:
        category = "local_rehearsal_blockers" if failure.startswith("rehearsal") or "rehearsal" in failure else "safety_blockers"
        add_blocker(category, _slug(failure), failure, evidence="staging bundle and rehearsal report validation", status="failed")

    if rehearsal and rehearsal.get("status") == "FAIL":
        add_blocker(
            "local_rehearsal_blockers",
            "local_rehearsal_failed",
            "local public-alpha rehearsal failed",
            evidence="rehearsal_report.status",
            status="failed",
        )
    elif not rehearsal or rehearsal.get("status") not in {"PASS", "PASS_WITH_WARNINGS"}:
        add_blocker(
            "local_rehearsal_blockers",
            "local_rehearsal_status_unknown",
            "local public-alpha rehearsal status is unknown",
            evidence="rehearsal_report.status",
            status="unknown",
        )

    _add_safety_blockers(add_blocker, local_safety)

    artifact_verified_count = int(staging_status.get("artifact_verified_count") or manifest.get("artifact_verified_count") or 0)
    if artifact_verified_count <= 0:
        add_blocker(
            "corpus_evidence_blockers",
            "artifact_verified_count_zero",
            "staging bundle reports artifact_verified_count=0",
            evidence="staging bundle manifest",
        )
    if corpus_gate["status"] == "pass" and artifact_verified_count != int(corpus_gate.get("artifact_verified_count") or 0):
        add_blocker(
            "corpus_evidence_blockers",
            "staging_corpus_count_mismatch",
            "staging bundle artifact count does not match corpus gate closeout",
            evidence=corpus_gate["evidence"],
        )
    if corpus_gate["status"] != "pass" and int(staging_status.get("reviewed_record_count") or manifest.get("reviewed_record_count") or 0) > 0:
        add_blocker(
            "corpus_evidence_blockers",
            "local_demo_reviewed_records_not_official_gate",
            "local demo reviewed records do not satisfy the official reviewed-artifact gate",
            evidence="staging bundle manifest reviewed_record_count",
        )
    if official_gate["status"] != "pass":
        add_blocker(
            "corpus_evidence_blockers",
            "official_reviewed_artifact_gate_not_passed",
            "official reviewed-artifact gate is not passed",
            evidence=official_gate["evidence"],
            status=official_gate["status"],
        )
    if verified_evidence["status"] != "pass" and corpus_gate["status"] != "pass":
        add_blocker(
            "corpus_evidence_blockers",
            "verified_artifact_evidence_not_promoted",
            "verified artifact evidence is not promoted or not discoverable",
            evidence=verified_evidence["evidence"],
            status=verified_evidence["status"],
        )

    if external_staging_host_status != "configured":
        add_blocker("deployment_blockers", "external_staging_host_missing", "external staging host is missing", evidence="--external-staging-url not provided")
    if production_hosting_status != "configured":
        add_blocker("deployment_blockers", "production_hosting_missing", "production hosting is missing", evidence="--public-url not provided")
    if tls_domain_status != "configured":
        add_blocker("deployment_blockers", "tls_domain_missing", "TLS/domain setup is missing", evidence="--public-url is not an https URL")
    if production_auth_status != "approved":
        add_blocker(
            "deployment_blockers",
            "production_auth_or_noauth_posture_missing",
            "production auth or approved read-only no-auth posture is missing",
            evidence="--production-auth-posture/--allow-readonly-noauth",
            status=production_auth_status,
        )

    if full_discovery["status"] != "pass":
        add_blocker(
            "release_process_blockers",
            "full_discovery_not_passed",
            "full discovery check is not passed for this launch gate",
            evidence=full_discovery["evidence"],
            status=full_discovery["status"],
        )
    if release_promotion["status"] != "pass":
        add_blocker(
            "release_process_blockers",
            "release_promotion_not_passed",
            "release promotion checks are not passed for this launch gate",
            evidence=release_promotion["evidence"],
            status=release_promotion["status"],
        )

    if approval["status"] != "approved":
        add_blocker(
            "approval_blockers",
            "public_launch_approval_missing",
            "public launch approval is missing",
            evidence=approval["evidence"],
            status=approval["status"],
        )

    if official_gate["status"] == "unknown":
        add_blocker(
            "unknown_authority_blockers",
            "artifact_gate_authority_unknown",
            "artifact gate authority report was not provided or could not be interpreted",
            evidence=official_gate["evidence"],
            status="unknown",
        )
    if verified_evidence["status"] == "unknown" and corpus_gate["status"] != "pass":
        add_blocker(
            "unknown_authority_blockers",
            "verified_evidence_authority_unknown",
            "verified evidence authority report was not provided or could not be interpreted",
            evidence=verified_evidence["evidence"],
            status="unknown",
        )

    after_hashes = _artifact_hashes(bundle_path, rehearsal_path)
    mutation_checks = _mutation_checks(before_hashes, after_hashes)
    if any(item["mutated"] for item in mutation_checks["per_artifact"].values()):
        add_blocker(
            "safety_blockers",
            "launch_gate_audit_mutated_inputs",
            "launch gate audit mutated input artifacts",
            evidence="before/after artifact hashes",
            status="failed",
        )
        local_audit_failures.append("launch gate audit mutated input artifacts")

    launch_status = _launch_status(blockers)
    report_status = "FAIL" if local_audit_failures else ("PASS_WITH_WARNINGS" if launch_status != "READY" else "PASS")
    warnings = []
    if launch_status == "BLOCKED":
        warnings.append("local readiness is separate from public launch readiness; launch remains blocked")
    if git_state.get("dirty"):
        warnings.append("git working tree was dirty during audit")

    return {
        "schema_version": REPORT_SCHEMA_VERSION,
        "task_id": TASK_ID,
        "status": report_status,
        "local_rehearsal_status": _local_rehearsal_summary(rehearsal, rehearsal_errors),
        "launch_status": launch_status,
        "bundle_path": str(bundle_path),
        "bundle_id": str(staging_status.get("bundle_id") or manifest.get("bundle_id") or ""),
        "bundle_manifest_digest": _file_sha256(bundle_path / MANIFEST_FILE),
        "public_index_digest": str(staging_status.get("public_index_digest") or manifest.get("public_index_digest") or ""),
        "rehearsal_report_path": str(rehearsal_path),
        "rehearsal_report_digest": _file_sha256(rehearsal_path),
        "document_count": int(staging_status.get("document_count") or manifest.get("document_count") or 0),
        "status_counts": dict(staging_status.get("status_counts") or manifest.get("status_counts") or {}),
        "local_reviewed_record_count": int(staging_status.get("reviewed_record_count") or manifest.get("reviewed_record_count") or 0),
        "artifact_verified_count": artifact_verified_count,
        "corpus_gate_closeout_status": corpus_gate["status"],
        "corpus_gate_closeout_digest": corpus_gate["digest"],
        "reviewed_artifact_gate_count": corpus_gate["reviewed_artifact_gate_count"],
        "public_artifact_identity_record_count": corpus_gate["public_artifact_identity_record_count"],
        "public_artifact_evidence_summary_count": corpus_gate["public_artifact_evidence_summary_count"],
        "verification_scope_counts": corpus_gate["verification_scope_counts"],
        "binary_verified_count": corpus_gate["binary_verified_count"],
        "download_safe_count": corpus_gate["download_safe_count"],
        "execution_safe_count": corpus_gate["execution_safe_count"],
        "rights_cleared_count": corpus_gate["rights_cleared_count"],
        "official_reviewed_artifact_count": official_gate["count"],
        "official_reviewed_artifact_gate_target": official_gate["target"],
        "official_reviewed_artifact_gate_status": official_gate["status"],
        "verified_artifact_evidence_status": verified_evidence["status"],
        "full_discovery_status": full_discovery["status"],
        "release_promotion_status": release_promotion["status"],
        "external_staging_host_status": external_staging_host_status,
        "production_hosting_status": production_hosting_status,
        "tls_domain_status": tls_domain_status,
        "production_auth_or_noauth_posture_status": production_auth_status,
        "public_launch_approval_status": approval["status"],
        "local_safety_status": local_safety["local_safety_status"],
        "mutation_safety_status": local_safety["mutation_safety_status"],
        "public_readonly_status": local_safety["public_readonly_status"],
        "workbench_exposure_status": local_safety["workbench_exposure_status"],
        "live_metadata_exposure_status": local_safety["live_metadata_exposure_status"],
        "blocker_categories": blocker_categories,
        "blockers": blockers,
        "warnings": warnings,
        "next_recommended_task": _next_task(blocker_categories, official_gate=official_gate),
        "generated_at": "not_recorded_deterministic_local_launch_gate",
        "evidence_sources": _evidence_sources(bundle_path, rehearsal_path, optional_sources, git_state),
        "optional_inputs": _optional_input_summary(opts, optional_sources),
        "local_audit_failures": _dedupe(local_audit_failures),
        "mutation_checks": mutation_checks,
        "local_safety_checks": local_safety,
        "staging_validation_errors": bundle_errors,
        "rehearsal_report_validation_errors": rehearsal_errors,
        "git_state": git_state,
        "public_alpha_mode": bool(manifest.get("public_alpha_mode") is True or staging_status.get("public_alpha_mode") is True),
        "read_only": bool(manifest.get("read_only") is True or staging_status.get("read_only") is True),
        "live_metadata_enabled": bool(manifest.get("live_metadata_enabled") is True or runtime_config.get("live_metadata_enabled") is True),
        "public_live_fanout": bool(manifest.get("public_live_fanout") is True or runtime_config.get("public_live_fanout") is True),
        "workbench_exposed": bool(manifest.get("workbench_exposed") is True or runtime_config.get("workbench_exposed") is True),
        "mutation_enabled": bool(manifest.get("mutation_enabled") is True or runtime_config.get("mutation_enabled") is True),
        "downloads_enabled": bool(manifest.get("downloads_enabled") is True or runtime_config.get("downloads_enabled") is True),
        "truth_promotion_performed": False,
        "verified_artifact_truth_created": False,
        "public_launch_ready_claimed": launch_status == "READY",
    }


def write_launch_gate_reports(report: Mapping[str, Any], out_dir: str | Path) -> Path:
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    json_path = out / REPORT_JSON
    markdown_path = out / REPORT_MD
    payload = dict(report)
    payload["report_path"] = str(json_path)
    json_path.write_bytes(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True).encode("utf-8") + b"\n")
    markdown_path.write_bytes(render_markdown_report(payload).encode("utf-8"))
    return json_path


def validate_launch_gate_report(report_path: str | Path) -> list[str]:
    try:
        report = load_report(report_path)
    except OSError as exc:
        return [f"report could not be read: {type(exc).__name__}"]
    except json.JSONDecodeError as exc:
        return [f"report is invalid JSON: {exc.msg}"]

    required = (
        "task_id",
        "status",
        "local_rehearsal_status",
        "launch_status",
        "bundle_path",
        "bundle_id",
        "bundle_manifest_digest",
        "public_index_digest",
        "rehearsal_report_path",
        "rehearsal_report_digest",
        "document_count",
        "status_counts",
        "local_reviewed_record_count",
        "artifact_verified_count",
        "corpus_gate_closeout_status",
        "corpus_gate_closeout_digest",
        "reviewed_artifact_gate_count",
        "public_artifact_identity_record_count",
        "public_artifact_evidence_summary_count",
        "verification_scope_counts",
        "binary_verified_count",
        "download_safe_count",
        "execution_safe_count",
        "rights_cleared_count",
        "official_reviewed_artifact_count",
        "official_reviewed_artifact_gate_target",
        "official_reviewed_artifact_gate_status",
        "verified_artifact_evidence_status",
        "full_discovery_status",
        "release_promotion_status",
        "external_staging_host_status",
        "production_hosting_status",
        "tls_domain_status",
        "production_auth_or_noauth_posture_status",
        "public_launch_approval_status",
        "local_safety_status",
        "mutation_safety_status",
        "public_readonly_status",
        "workbench_exposure_status",
        "live_metadata_exposure_status",
        "blocker_categories",
        "blockers",
        "warnings",
        "next_recommended_task",
        "mutation_checks",
        "local_safety_checks",
    )
    errors: list[str] = []
    for key in required:
        if key not in report:
            errors.append(f"missing required field: {key}")
    if errors:
        return errors

    if report.get("task_id") != TASK_ID:
        errors.append(f"task_id must be {TASK_ID}")
    if report.get("status") not in REPORT_STATUSES:
        errors.append("status must be PASS, PASS_WITH_WARNINGS, or FAIL")
    if report.get("launch_status") not in LAUNCH_STATUSES:
        errors.append("launch_status must be a known launch gate status")
    if report.get("local_rehearsal_status") not in {"GREEN", "RED", "UNKNOWN"}:
        errors.append("local_rehearsal_status must be GREEN, RED, or UNKNOWN")
    if report.get("public_readonly_status") not in {"pass", "fail", "unknown"}:
        errors.append("public_readonly_status must be pass, fail, or unknown")
    if report.get("corpus_gate_closeout_status") not in {"pass", "fail", "blocked", "unknown", "missing"}:
        errors.append("corpus_gate_closeout_status must be pass, fail, blocked, unknown, or missing")
    if report.get("workbench_exposure_status") not in {"not_exposed", "exposed", "unknown"}:
        errors.append("workbench_exposure_status must be not_exposed, exposed, or unknown")
    if report.get("live_metadata_exposure_status") not in {"not_exposed", "exposed", "unknown"}:
        errors.append("live_metadata_exposure_status must be not_exposed, exposed, or unknown")
    categories = report.get("blocker_categories")
    if not isinstance(categories, Mapping):
        errors.append("blocker_categories must be an object")
    else:
        for category in BLOCKER_CATEGORIES:
            if category not in categories:
                errors.append(f"blocker_categories missing {category}")
    blockers = report.get("blockers")
    if not isinstance(blockers, list):
        errors.append("blockers must be a list")
    if report.get("launch_status") == "READY" and blockers:
        errors.append("launch_status READY requires no blockers")
    if report.get("launch_status") != "READY" and not blockers:
        errors.append("non-READY launch_status requires blockers")
    if report.get("artifact_verified_count") == 0 and report.get("launch_status") == "READY":
        errors.append("artifact_verified_count=0 cannot be launch READY")
    for key in ("binary_verified_count", "download_safe_count", "execution_safe_count", "rights_cleared_count"):
        if int(report.get(key) or 0) != 0:
            errors.append(f"{key} must remain 0")
    mutation = report.get("mutation_checks") if isinstance(report.get("mutation_checks"), Mapping) else {}
    for key in ("bundle_mutated", "rehearsal_report_mutated", "local_review_artifacts_mutated", "any_input_mutated"):
        if mutation.get(key) is not False:
            errors.append(f"mutation_checks.{key} must be false")
    if any(marker in json.dumps(report, sort_keys=True) for marker in SECRET_MARKERS):
        errors.append("report contains a forbidden secret/token marker")
    return errors


def load_report(report_path: str | Path) -> dict[str, Any]:
    return json.loads(Path(report_path).read_text(encoding="utf-8"))


def render_status(report: Mapping[str, Any]) -> str:
    lines = [
        f"local rehearsal: {report.get('local_rehearsal_status')}",
        f"launch status: {report.get('launch_status')}",
        f"report status: {report.get('status')}",
        f"blocker count: {len(report.get('blockers') or [])}",
        f"next recommended task: {report.get('next_recommended_task')}",
        f"corpus gate closeout: {report.get('corpus_gate_closeout_status')}",
        f"artifact verified count: {report.get('artifact_verified_count')}",
        f"reviewed artifact gate count: {report.get('reviewed_artifact_gate_count')}",
        "blockers by category:",
    ]
    categories = report.get("blocker_categories") if isinstance(report.get("blocker_categories"), Mapping) else {}
    for category in BLOCKER_CATEGORIES:
        lines.append(f"- {category}: {len(categories.get(category) or [])}")
    lines.append(f"report path: {report.get('report_path', '')}")
    return "\n".join(lines) + "\n"


def render_markdown_report(report: Mapping[str, Any]) -> str:
    categories = report.get("blocker_categories") if isinstance(report.get("blocker_categories"), Mapping) else {}
    blockers = [item for item in report.get("blockers") or [] if isinstance(item, Mapping)]
    evidence_sources = report.get("evidence_sources") if isinstance(report.get("evidence_sources"), Mapping) else {}
    not_checked = _not_checked(report)
    lines = [
        "# Public Alpha Launch Gate Report",
        "",
        "## Summary",
        "",
        f"- Report status: {report.get('status')}",
        f"- Local rehearsal: {report.get('local_rehearsal_status')}",
        f"- Launch status: {report.get('launch_status')}",
        f"- Blockers: {len(blockers)}",
        f"- Next recommended task: {report.get('next_recommended_task')}",
        "",
        "Local rehearsal passing is not public launch approval. This report only audits the local bundle, rehearsal, and supplied gate evidence.",
        "",
        "## Blocker Categories",
        "",
    ]
    for category in BLOCKER_CATEGORIES:
        ids = categories.get(category) or []
        lines.append(f"- {category}: {len(ids)}")
    lines.extend(["", "## Blockers Remaining", ""])
    if blockers:
        for blocker in blockers:
            lines.append(f"- [{blocker.get('category')}] {blocker.get('id')}: {blocker.get('message')}")
    else:
        lines.append("- none")
    lines.extend(["", "## Evidence Sources Used", ""])
    for key, value in evidence_sources.items():
        if isinstance(value, Mapping):
            lines.append(f"- {key}: present={str(value.get('present')).lower()}, status={value.get('status', '')}")
        else:
            lines.append(f"- {key}: {value}")
    lines.extend(["", "## What Was Not Checked", ""])
    for item in not_checked:
        lines.append(f"- {item}")
    lines.extend(
        [
            "",
            "## Safety Posture",
            "",
            f"- Public read-only: {report.get('public_readonly_status')}",
            f"- Mutation safety: {report.get('mutation_safety_status')}",
            f"- Workbench exposure: {report.get('workbench_exposure_status')}",
            f"- Live metadata exposure: {report.get('live_metadata_exposure_status')}",
            f"- Artifact verified count: {report.get('artifact_verified_count')}",
            f"- Corpus gate closeout: {report.get('corpus_gate_closeout_status')}",
            f"- Reviewed artifact gate count: {report.get('reviewed_artifact_gate_count')}",
            f"- Public artifact identity records: {report.get('public_artifact_identity_record_count')}",
            f"- Binary verified count: {report.get('binary_verified_count')}",
            f"- Download safe count: {report.get('download_safe_count')}",
            f"- Execution safe count: {report.get('execution_safe_count')}",
            f"- Rights cleared count: {report.get('rights_cleared_count')}",
            "",
            "## Recommended Next Task",
            "",
            f"`{report.get('next_recommended_task')}`",
            "",
            "This generated report is operational evidence only. It is not canon, release state, queue state, verified evidence promotion, or public launch approval.",
            "",
        ]
    )
    return "\n".join(lines)


def _local_safety_status(rehearsal: Mapping[str, Any]) -> dict[str, Any]:
    failures: list[str] = []
    if not rehearsal:
        return {
            "local_safety_status": "unknown",
            "mutation_safety_status": "unknown",
            "public_readonly_status": "unknown",
            "workbench_exposure_status": "unknown",
            "live_metadata_exposure_status": "unknown",
            "failures": ["rehearsal report could not be read"],
        }
    bool_expectations = {
        "public_alpha_mode": True,
        "read_only": True,
        "live_metadata_enabled": False,
        "public_live_fanout": False,
        "workbench_exposed": False,
        "mutation_enabled": False,
        "downloads_enabled": False,
    }
    for key, expected in bool_expectations.items():
        if rehearsal.get(key) is not expected:
            failures.append(f"rehearsal {key} expected {str(expected).lower()}")
    leakage = rehearsal.get("leakage_checks") if isinstance(rehearsal.get("leakage_checks"), Mapping) else {}
    if leakage.get("passed") is not True:
        failures.append("rehearsal leakage checks did not pass")
    mutation = rehearsal.get("mutation_checks") if isinstance(rehearsal.get("mutation_checks"), Mapping) else {}
    for key in ("public_routes_mutated_bundle", "blocked_workbench_mutated_anything", "search_mutated_anything"):
        if mutation.get(key) is not False:
            failures.append(f"rehearsal mutation_checks.{key} expected false")
    blocked_routes = [item for item in rehearsal.get("blocked_routes_probed") or [] if isinstance(item, Mapping)]
    if not blocked_routes:
        failures.append("rehearsal did not include blocked Workbench probes")
    for route in blocked_routes:
        if int(route.get("status_code") or 0) not in {403, 404}:
            failures.append(f"blocked route {route.get('path')} returned {route.get('status_code')}")
    for check in rehearsal.get("safety_conflict_checks") or []:
        if isinstance(check, Mapping) and check.get("passed") is not True:
            failures.append(f"safety conflict check did not pass: {check.get('name')}")

    public_readonly = "pass" if rehearsal.get("public_alpha_mode") is True and rehearsal.get("read_only") is True else "fail"
    mutation_safety = "pass" if all(mutation.get(key) is False for key in ("public_routes_mutated_bundle", "blocked_workbench_mutated_anything", "search_mutated_anything")) else "fail"
    return {
        "local_safety_status": "pass" if not failures else "fail",
        "mutation_safety_status": mutation_safety,
        "public_readonly_status": public_readonly,
        "workbench_exposure_status": "not_exposed" if rehearsal.get("workbench_exposed") is False else "exposed",
        "live_metadata_exposure_status": "not_exposed" if rehearsal.get("live_metadata_enabled") is False and rehearsal.get("public_live_fanout") is False else "exposed",
        "failures": failures,
    }


def _add_safety_blockers(add_blocker: Any, local_safety: Mapping[str, Any]) -> None:
    for failure in local_safety.get("failures") or []:
        add_blocker("safety_blockers", _slug(str(failure)), str(failure), evidence="rehearsal safety fields", status="failed")
    if local_safety.get("public_readonly_status") != "pass":
        add_blocker("safety_blockers", "public_readonly_not_passed", "public read-only posture is not passing", evidence="rehearsal report", status="failed")
    if local_safety.get("mutation_safety_status") != "pass":
        add_blocker("safety_blockers", "mutation_safety_not_passed", "mutation safety is not passing", evidence="rehearsal report", status="failed")
    if local_safety.get("workbench_exposure_status") != "not_exposed":
        add_blocker("safety_blockers", "workbench_exposed", "Workbench is exposed", evidence="rehearsal report", status="failed")
    if local_safety.get("live_metadata_exposure_status") != "not_exposed":
        add_blocker("safety_blockers", "live_metadata_exposed", "live metadata or public live fanout is exposed", evidence="rehearsal report", status="failed")


def _official_artifact_gate(source: Mapping[str, Any] | None) -> dict[str, Any]:
    if not source or not source.get("present"):
        return {
            "status": "unknown",
            "count": 0,
            "target": 0,
            "evidence": "artifact gate report not provided",
            "next_recommended_task": "",
        }
    payload = source.get("payload") if isinstance(source.get("payload"), Mapping) else {}
    count = int(
        payload.get("official_reviewed_artifact_count")
        or payload.get("reviewed_artifact_gate_count")
        or payload.get("reviewed_artifact_count")
        or payload.get("artifact_verified_count")
        or 0
    )
    target = int(
        payload.get("official_reviewed_artifact_gate_target")
        or payload.get("gate_target_reviewed_artifacts")
        or payload.get("minimum_public_alpha_reviewed_artifact_records")
        or payload.get("target")
        or payload.get("gate_target")
        or 0
    )
    status = _status_from_payload(payload)
    if status == "pass" and target and count < target:
        status = "fail"
    if status == "unknown" and target and count >= target:
        status = "pass"
    return {
        "status": status,
        "count": count,
        "target": target,
        "evidence": str(source.get("path") or "artifact gate report"),
        "next_recommended_task": str(payload.get("next_recommended_task") or ""),
    }


def _corpus_gate_closeout(source: Mapping[str, Any] | None) -> dict[str, Any]:
    if not source or not source.get("present"):
        return {
            "status": "missing",
            "digest": "",
            "reviewed_artifact_gate_count": 0,
            "artifact_verified_count": 0,
            "public_artifact_identity_record_count": 0,
            "public_artifact_evidence_summary_count": 0,
            "verification_scope_counts": {},
            "binary_verified_count": 0,
            "download_safe_count": 0,
            "execution_safe_count": 0,
            "rights_cleared_count": 0,
            "evidence": "corpus gate closeout not provided",
        }
    payload = source.get("payload") if isinstance(source.get("payload"), Mapping) else {}
    status = str(payload.get("corpus_gate_status") or _status_from_payload(payload)).strip().casefold()
    if status not in {"pass", "fail", "blocked"}:
        status = "unknown"
    return {
        "status": status,
        "digest": _file_sha256(Path(str(source.get("path") or ""))) if source.get("present") else "",
        "reviewed_artifact_gate_count": int(payload.get("reviewed_artifact_gate_count") or 0),
        "artifact_verified_count": int(payload.get("artifact_verified_count") or 0),
        "public_artifact_identity_record_count": int(payload.get("public_artifact_identity_record_count") or 0),
        "public_artifact_evidence_summary_count": int(payload.get("public_artifact_evidence_summary_count") or 0),
        "verification_scope_counts": dict(payload.get("verification_scope_counts") or {}),
        "binary_verified_count": int(payload.get("binary_verified_count") or 0),
        "download_safe_count": int(payload.get("download_safe_count") or 0),
        "execution_safe_count": int(payload.get("execution_safe_count") or 0),
        "rights_cleared_count": int(payload.get("rights_cleared_count") or 0),
        "evidence": str(source.get("path") or "corpus gate closeout"),
    }


def _generic_report_status(source: Mapping[str, Any] | None, *, default: str) -> dict[str, str]:
    if not source or not source.get("present"):
        return {"status": default, "evidence": "report not provided"}
    payload = source.get("payload") if isinstance(source.get("payload"), Mapping) else {}
    status = _status_from_payload(payload)
    if status == "approved":
        status = "pass"
    if status not in {"pass", "fail", "unknown", "not_run"}:
        status = "unknown"
    return {"status": status, "evidence": str(source.get("path") or "report")}


def _approval_status(source: Mapping[str, Any] | None) -> dict[str, str]:
    if not source or not source.get("present"):
        return {"status": "missing", "evidence": "approval file not provided"}
    payload = source.get("payload") if isinstance(source.get("payload"), Mapping) else {}
    status = _status_from_payload(payload)
    if status == "pass":
        status = "approved"
    if status not in {"approved", "missing", "unknown", "fail"}:
        status = "unknown"
    return {"status": status, "evidence": str(source.get("path") or "approval file")}


def _optional_sources(options: Mapping[str, Any]) -> dict[str, dict[str, Any]]:
    result = {}
    for key in ("approval_file", "full_discovery_report", "artifact_gate_report", "corpus_gate_closeout", "verified_evidence_report", "release_check_report"):
        raw = str(options.get(key) or "")
        if not raw:
            result[key] = {"path": "", "present": False, "payload": {}, "read_error": ""}
            continue
        path = Path(raw)
        payload: dict[str, Any] = {}
        read_error = ""
        if path.is_file():
            try:
                loaded = json.loads(path.read_text(encoding="utf-8"))
                payload = loaded if isinstance(loaded, dict) else {}
            except (OSError, json.JSONDecodeError) as exc:
                read_error = type(exc).__name__
        result[key] = {"path": str(path), "present": path.is_file(), "payload": payload, "read_error": read_error}
    return result


def _status_from_payload(payload: Mapping[str, Any]) -> str:
    for key in ("status", "result", "gate_status", "launch_status", "approval_status"):
        value = str(payload.get(key) or "").strip().casefold()
        if value in {"pass", "passed", "green", "ready", "approved"}:
            return "approved" if value == "approved" else "pass"
        if value in {"fail", "failed", "red", "blocked", "missing"}:
            return "missing" if value == "missing" else "fail"
        if value in {"unknown", "not_run"}:
            return value
    for key in ("passed", "approved", "ready"):
        if payload.get(key) is True:
            return "approved" if key == "approved" else "pass"
    return "unknown"


def _launch_status(blockers: Sequence[Mapping[str, Any]]) -> str:
    if not blockers:
        return "READY"
    categories = {str(item.get("category")) for item in blockers}
    if categories <= {"approval_blockers"}:
        return "READY_FOR_PUBLIC_APPROVAL"
    if categories <= {"deployment_blockers"}:
        return "READY_FOR_EXTERNAL_STAGING"
    return "BLOCKED"


def _next_task(blocker_categories: Mapping[str, Sequence[str]], *, official_gate: Mapping[str, Any] | None = None) -> str:
    unknown = set(blocker_categories.get("unknown_authority_blockers") or [])
    if "artifact_gate_authority_unknown" in unknown:
        return "REVIEWED-ARTIFACT-GATE-SEED-00"
    if blocker_categories.get("corpus_evidence_blockers") and official_gate:
        recommended = str(official_gate.get("next_recommended_task") or "")
        if recommended:
            return recommended
    if blocker_categories.get("corpus_evidence_blockers") or unknown:
        return "MANUAL-ARTIFACT-EVIDENCE-BATCH-01"
    if blocker_categories.get("deployment_blockers"):
        return "EXTERNAL-STAGING-HOST-PROVISION-00"
    if blocker_categories.get("local_rehearsal_blockers") or blocker_categories.get("safety_blockers"):
        return "PUBLIC-ALPHA-LAUNCH-BLOCKER-CLOSEOUT-00-FIX"
    if blocker_categories.get("release_process_blockers"):
        return "PUBLIC-ALPHA-RELEASE-GATE-CLOSEOUT-00"
    if blocker_categories.get("approval_blockers"):
        return "PUBLIC-ALPHA-APPROVAL-RECORD-00"
    return "PUBLIC-ALPHA-LAUNCH-00"


def _local_rehearsal_summary(rehearsal: Mapping[str, Any], errors: Sequence[str]) -> str:
    if errors:
        return "RED"
    if rehearsal.get("status") in {"PASS", "PASS_WITH_WARNINGS"} and not rehearsal.get("local_rehearsal_failures"):
        return "GREEN"
    if rehearsal.get("status") == "FAIL":
        return "RED"
    return "UNKNOWN"


def _production_auth_status(options: Mapping[str, Any]) -> str:
    if options.get("allow_readonly_noauth") is True:
        return "approved"
    value = str(options.get("production_auth_posture") or "missing").strip().casefold()
    return value if value in {"approved", "missing", "unknown"} else "unknown"


def _tls_status(public_url: str) -> str:
    if not public_url:
        return "missing"
    return "configured" if public_url.strip().casefold().startswith("https://") else "missing"


def _evidence_sources(bundle: Path, rehearsal: Path, optional_sources: Mapping[str, Mapping[str, Any]], git_state: Mapping[str, Any]) -> dict[str, Any]:
    sources: dict[str, Any] = {
        "staging_bundle": {"path": str(bundle), "present": bundle.is_dir(), "status": "present" if bundle.is_dir() else "missing"},
        "rehearsal_report": {"path": str(rehearsal), "present": rehearsal.is_file(), "status": "present" if rehearsal.is_file() else "missing"},
        "git": {"present": bool(git_state), "status": "dirty" if git_state.get("dirty") else "clean"},
    }
    sources.update({key: {"path": value.get("path", ""), "present": value.get("present", False), "status": "present" if value.get("present") else "missing"} for key, value in optional_sources.items()})
    return sources


def _optional_input_summary(options: Mapping[str, Any], optional_sources: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    return {
        "external_staging_url_provided": _has_value(options.get("external_staging_url")),
        "public_url_provided": _has_value(options.get("public_url")),
        "production_auth_posture": str(options.get("production_auth_posture") or ""),
        "allow_readonly_noauth": bool(options.get("allow_readonly_noauth") is True),
        "reports": {key: {"path": value.get("path", ""), "present": bool(value.get("present"))} for key, value in optional_sources.items()},
    }


def _not_checked(report: Mapping[str, Any]) -> list[str]:
    items = []
    if report.get("external_staging_host_status") != "configured":
        items.append("external staging host was not checked because no URL was provided")
    if report.get("production_hosting_status") != "configured":
        items.append("production hosting was not checked because no public URL was provided")
    if report.get("full_discovery_status") != "pass":
        items.append("full discovery/release promotion evidence was not supplied as passing")
    if report.get("official_reviewed_artifact_gate_status") != "pass":
        items.append("official reviewed-artifact gate evidence was not supplied as passing")
    if report.get("public_launch_approval_status") != "approved":
        items.append("public launch approval was not supplied as approved")
    return items or ["none"]


def _artifact_hashes(bundle: Path, rehearsal_report: Path) -> dict[str, dict[str, Any]]:
    paths: dict[str, Path] = {
        "bundle_manifest": bundle / MANIFEST_FILE,
        "bundle_public_index": bundle / PUBLIC_INDEX_FILE,
        "bundle_runtime_config": bundle / RUNTIME_CONFIG_FILE,
        "bundle_corpus_gate_closeout": bundle / CORPUS_CLOSEOUT_FILE,
        "bundle_public_artifact_identity_records": bundle / PUBLIC_ARTIFACT_RECORDS_JSONL,
        "bundle_public_artifact_evidence_summary": bundle / PUBLIC_EVIDENCE_SUMMARY_JSONL,
        "rehearsal_report": rehearsal_report,
    }
    for raw in LOCAL_REVIEW_ARTIFACTS:
        paths[raw.replace("/", "_").replace(".", "").replace("-", "_")] = REPO_ROOT / raw
    return {
        name: {
            "name": name,
            "path": str(path),
            "present": path.is_file(),
            "sha256": _file_sha256(path) if path.is_file() else "",
        }
        for name, path in paths.items()
    }


def _mutation_checks(before: Mapping[str, Mapping[str, Any]], after: Mapping[str, Mapping[str, Any]]) -> dict[str, Any]:
    per_artifact = {}
    for name, before_item in before.items():
        after_item = after.get(name, {})
        per_artifact[name] = {
            "name": name,
            "present_before": bool(before_item.get("present")),
            "present_after": bool(after_item.get("present")),
            "mutated": before_item.get("sha256") != after_item.get("sha256"),
        }
    bundle_file_names = {
        "bundle_manifest",
        "bundle_public_index",
        "bundle_runtime_config",
        "bundle_corpus_gate_closeout",
        "bundle_public_artifact_identity_records",
        "bundle_public_artifact_evidence_summary",
    }
    bundle_mutated = any(per_artifact.get(name, {}).get("mutated") for name in bundle_file_names)
    rehearsal_mutated = bool(per_artifact.get("rehearsal_report", {}).get("mutated"))
    local_review_mutated = any(item.get("mutated") for name, item in per_artifact.items() if name not in {*bundle_file_names, "rehearsal_report"})
    return {
        "per_artifact": per_artifact,
        "bundle_mutated": bundle_mutated,
        "rehearsal_report_mutated": rehearsal_mutated,
        "local_review_artifacts_mutated": local_review_mutated,
        "any_input_mutated": any(item.get("mutated") for item in per_artifact.values()),
    }


def _git_state() -> dict[str, Any]:
    try:
        status = subprocess.run(["git", "status", "--short", "--branch"], cwd=REPO_ROOT, capture_output=True, text=True, check=False)
        head = subprocess.run(["git", "rev-parse", "HEAD"], cwd=REPO_ROOT, capture_output=True, text=True, check=False)
    except OSError:
        return {"available": False, "dirty": True, "head": "", "status": "unavailable"}
    lines = [line for line in status.stdout.splitlines() if line.strip()]
    dirty_lines = [line for line in lines if not line.startswith("## ")]
    return {
        "available": True,
        "dirty": bool(dirty_lines),
        "head": head.stdout.strip() if head.returncode == 0 else "",
        "status_sample": lines[:8],
    }


def _read_json(path: str | Path) -> dict[str, Any]:
    try:
        payload = json.loads(Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    return payload if isinstance(payload, dict) else {}


def _file_sha256(path: str | Path) -> str:
    target = Path(path)
    return hashlib.sha256(target.read_bytes()).hexdigest() if target.is_file() else ""


def _slug(value: str) -> str:
    chars = []
    for char in value.strip().casefold():
        if char.isalnum():
            chars.append(char)
        elif chars and chars[-1] != "_":
            chars.append("_")
    return "".join(chars).strip("_")[:80] or "blocker"


def _has_value(value: Any) -> bool:
    return bool(str(value or "").strip())


def _dedupe(values: Sequence[str]) -> list[str]:
    seen = set()
    result = []
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


if __name__ == "__main__":
    raise SystemExit(main())
