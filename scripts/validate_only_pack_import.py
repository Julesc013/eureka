from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO

import validate_pack_set


REPO_ROOT = Path(__file__).resolve().parents[1]
AI_OUTPUT_EXAMPLES = REPO_ROOT / "control" / "inventory" / "ai_providers" / "typed_output_examples.json"
VALIDATOR_ID = "validate_only_pack_import_tool_v0"
TOOL_VERSION = "0.1.0"
SCHEMA_VERSION = "pack_import_report.v0"

HARD_FALSE_FIELDS = (
    "import_performed",
    "staging_performed",
    "indexing_performed",
    "upload_performed",
    "master_index_mutation_performed",
    "runtime_mutation_performed",
    "network_performed",
)
FORBIDDEN_OUTPUT_REPO_ROOTS = (
    ".aide",
    ".github",
    "contracts",
    "control/inventory",
    "crates",
    "docs",
    "evals",
    "external",
    "runtime",
    "site",
    "site/dist",
    "snapshots/examples",
    "surfaces",
)
PRIVATE_PATH_RE = re.compile(
    r"([A-Za-z]:[\\/](Users|Documents and Settings|Projects)[\\/]|"
    r"\\\\[^\\/\s]+[\\/][^\\/\s]+[\\/]|"
    r"/(Users|home|var/folders|private/tmp|tmp)/)",
    re.IGNORECASE,
)
SECRET_KEY_RE = re.compile(r"(api[_-]?key|auth[_-]?token|password|private[_-]?key|secret)", re.IGNORECASE)
SECRET_VALUE_RE = re.compile(r"(sk-[A-Za-z0-9_-]{8,}|-----BEGIN [A-Z ]*PRIVATE KEY-----)", re.IGNORECASE)
EXCERPT_MAX_CHARS = 800


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None, stderr: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Run validate-only pack import preflight and emit Pack Import Report v0."
    )
    parser.add_argument("--pack-root", action="append", default=[], help="Explicit pack or review-queue root.")
    parser.add_argument("--all-examples", action="store_true", help="Validate all known repo example packs.")
    parser.add_argument(
        "--include-ai-outputs",
        action="store_true",
        help="Also validate registered typed AI output examples as a report input bundle.",
    )
    parser.add_argument("--output", help="Write full report JSON to this explicit path; parent must already exist.")
    parser.add_argument("--json", action="store_true", help="Emit full report JSON to stdout.")
    parser.add_argument("--strict", action="store_true", help="Pass strict mode through to pack validators.")
    parser.add_argument("--list-examples", action="store_true", help="List known validation inputs without preflight.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    out = stdout or sys.stdout
    err = stderr or sys.stderr

    output_path = Path(args.output) if args.output else None
    if output_path is not None:
        resolved_output = _resolve(output_path)
        if not resolved_output.parent.exists():
            payload = _argument_error(f"--output parent does not exist: {_safe_path(resolved_output.parent)}")
            _emit(payload, json_output=args.json, output=out)
            return 2
        policy_error = _output_path_policy_error(resolved_output)
        if policy_error:
            payload = _argument_error(policy_error)
            _emit(payload, json_output=args.json, output=out)
            return 2
    else:
        resolved_output = None

    input_specs, spec_errors = _collect_input_specs(
        pack_roots=args.pack_root,
        all_examples=args.all_examples or not args.pack_root,
        include_ai_outputs=args.include_ai_outputs,
    )

    if args.list_examples:
        listing = _list_examples_report(input_specs, spec_errors, strict=args.strict)
        _emit(listing, json_output=args.json, output=out)
        return 0 if listing["ok"] else 1

    if spec_errors:
        report = _build_report([], input_specs, strict=args.strict, spec_errors=spec_errors, files_written=[])
    else:
        results = [_validate_input_spec(spec, strict=args.strict) for spec in input_specs]
        report = _build_report(
            results,
            input_specs,
            strict=args.strict,
            spec_errors=[],
            files_written=[_safe_path(resolved_output)] if resolved_output is not None else [],
        )

    report_errors = _validate_generated_report(report)
    if report_errors:
        report["report_status"] = "blocked_by_policy"
        report["next_actions"] = [
            {
                "action": "fix_pack_and_revalidate",
                "reason": "Generated report did not pass Pack Import Report v0 validation.",
            }
        ]
        report["notes"].extend(f"Generated report validation error: {error}" for error in report_errors)

    if resolved_output is not None:
        resolved_output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        err.write(f"Wrote validate-only pack import report: {_safe_path(resolved_output)}\n")

    _emit(report, json_output=args.json, output=out)
    return 0 if _report_success(report) else 1


def _collect_input_specs(
    *, pack_roots: Sequence[str], all_examples: bool, include_ai_outputs: bool
) -> tuple[list[dict[str, Any]], list[str]]:
    errors: list[str] = []
    specs: list[dict[str, Any]] = []

    if all_examples:
        examples = validate_pack_set.load_example_registry(errors=errors)
        for example in examples:
            specs.append(
                {
                    "root": REPO_ROOT / example["path"],
                    "display_root": example["path"],
                    "root_kind": "repo_example_root",
                    "pack_type": example["pack_type"],
                    "registry_id": example["pack_id"],
                    "provided_by": "control/inventory/packs/example_packs.json",
                }
            )

    for pack_root in pack_roots:
        root = _resolve(Path(pack_root))
        specs.append(
            {
                "root": root,
                "display_root": _safe_path(root),
                "root_kind": "explicit_pack_root",
                "pack_type": "auto",
                "registry_id": None,
                "provided_by": "cli --pack-root",
            }
        )

    if include_ai_outputs:
        ai_spec, ai_errors = _ai_output_spec()
        errors.extend(ai_errors)
        if ai_spec is not None:
            specs.append(ai_spec)

    if not specs and not errors:
        errors.append("No pack roots or examples were available for validate-only preflight.")
    return specs, errors


def _ai_output_spec() -> tuple[dict[str, Any] | None, list[str]]:
    errors: list[str] = []
    if not AI_OUTPUT_EXAMPLES.exists():
        return None, [f"{_safe_path(AI_OUTPUT_EXAMPLES)}: typed AI output example registry is missing."]
    try:
        payload = json.loads(AI_OUTPUT_EXAMPLES.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return None, [f"{_safe_path(AI_OUTPUT_EXAMPLES)}: invalid JSON: {exc}."]
    examples = payload.get("examples")
    if not isinstance(examples, list) or not examples:
        return None, [f"{_safe_path(AI_OUTPUT_EXAMPLES)}: examples must be a non-empty list."]
    roots = sorted({str(Path(item.get("path", "")).parent.as_posix()) for item in examples if isinstance(item, Mapping)})
    bundle_root = roots[0] if len(roots) == 1 else "examples/ai_providers"
    return (
        {
            "root": REPO_ROOT / bundle_root,
            "display_root": bundle_root,
            "root_kind": "repo_example_root",
            "pack_type": "ai_output_bundle",
            "registry_id": "example.typed_ai_output_bundle_v0",
            "provided_by": "control/inventory/ai_providers/typed_output_examples.json",
        },
        errors,
    )


def _validate_input_spec(spec: Mapping[str, Any], *, strict: bool) -> dict[str, Any]:
    if spec["pack_type"] == "ai_output_bundle":
        return _validate_ai_outputs(spec)

    aggregate = validate_pack_set.validate_pack_root(spec["root"], spec["pack_type"], strict=strict)
    aggregate = _sanitize_mapping(aggregate)
    pack_type = aggregate.get("pack_type", "unknown")
    status = aggregate.get("status", "failed")
    manifest = _read_pack_manifest(spec["root"], pack_type)
    issues = _issues_from_aggregate(aggregate, pack_type)

    return {
        "pack_root": spec["display_root"],
        "pack_type": pack_type,
        "pack_id": _manifest_id(manifest, fallback=spec.get("registry_id")),
        "pack_version": _manifest_version(manifest),
        "validator_id": _validator_id_for_type(pack_type),
        "validator_command": aggregate.get("validator_command") or "",
        "validation_status": _validation_status(status),
        "checksum_status": _checksum_status(status, aggregate),
        "schema_status": _schema_status(status),
        "privacy_status": _privacy_status(status, aggregate, spec),
        "rights_status": _rights_status(status, aggregate),
        "risk_status": _risk_status(status, aggregate),
        "issue_count": len(issues),
        "issues": issues,
        "record_counts": _record_counts(manifest),
        "limitations": _pack_limitations(status, pack_type),
        "recommended_next_action": _recommended_next_action(status),
        "_source_status": status,
    }


def _validate_ai_outputs(spec: Mapping[str, Any]) -> dict[str, Any]:
    validator = REPO_ROOT / "scripts" / "validate_ai_output.py"
    command = [sys.executable, str(validator), "--all-examples"]
    if not validator.exists():
        status = "unavailable"
        exit_code = None
        stdout = ""
        stderr = "Typed AI output validator is unavailable."
    else:
        import subprocess

        completed = subprocess.run(command, cwd=REPO_ROOT, capture_output=True, text=True)
        status = "passed" if completed.returncode == 0 else "failed"
        exit_code = completed.returncode
        stdout = completed.stdout
        stderr = completed.stderr

    aggregate = {
        "status": status,
        "exit_code": exit_code,
        "stdout_excerpt": _excerpt(stdout),
        "stderr_excerpt": _excerpt(stderr),
        "validator_command": "python scripts/validate_ai_output.py --all-examples",
    }
    issues = _issues_from_aggregate(aggregate, "ai_output_bundle")
    return {
        "pack_root": spec["display_root"],
        "pack_type": "ai_output_bundle",
        "pack_id": "example.typed_ai_output_bundle_v0",
        "pack_version": "0.1.0",
        "validator_id": "typed_ai_output_validator_v0",
        "validator_command": aggregate["validator_command"],
        "validation_status": _validation_status(status),
        "checksum_status": "not_applicable",
        "schema_status": _schema_status(status),
        "privacy_status": "public_safe" if status == "passed" else "unknown",
        "rights_status": "review_required",
        "risk_status": "metadata_only" if status == "passed" else "unknown",
        "issue_count": len(issues),
        "issues": issues,
        "record_counts": _ai_record_counts(),
        "limitations": _pack_limitations(status, "ai_output_bundle"),
        "recommended_next_action": _recommended_next_action(status),
        "_source_status": status,
    }


def _build_report(
    results: Sequence[Mapping[str, Any]],
    specs: Sequence[Mapping[str, Any]],
    *,
    strict: bool,
    spec_errors: Sequence[str],
    files_written: Sequence[str],
) -> dict[str, Any]:
    public_results = [_strip_internal_keys(result) for result in results]
    validation_summary = _validation_summary(public_results)
    report_status = _report_status(public_results, spec_errors)
    next_actions = _next_actions(report_status, public_results, spec_errors)
    safety = {field: False for field in HARD_FALSE_FIELDS}

    report = {
        "schema_version": SCHEMA_VERSION,
        "report_id": _report_id(public_results, specs, strict=strict, include_errors=spec_errors),
        "report_version": "0.1.0",
        "report_kind": "pack_import_report",
        "report_status": report_status,
        "mode": "validate_only",
        "created_by_tool": {
            "tool_id": VALIDATOR_ID,
            "tool_version": TOOL_VERSION,
            "tool_status": "validation_only",
        },
        "input_roots": [
            {
                "root": spec["display_root"],
                "root_kind": spec["root_kind"],
                "provided_by": spec["provided_by"],
            }
            for spec in specs
        ]
        or [
            {
                "root": "none",
                "root_kind": "synthetic_failure_fixture",
                "provided_by": "argument validation",
                "synthetic": True,
            }
        ],
        "pack_results": public_results
        or [
            _synthetic_failed_result(index, error)
            for index, error in enumerate(spec_errors or ["No validate-only inputs were available."])
        ],
        "validation_summary": validation_summary
        if public_results
        else _validation_summary(
            [
                _synthetic_failed_result(index, error)
                for index, error in enumerate(spec_errors or ["No validate-only inputs were available."])
            ]
        ),
        "privacy_rights_risk_summary": _privacy_rights_risk_summary(public_results),
        "provenance_summary": {
            "input_roots_recorded": True,
            "pack_checksums_recorded": True,
            "validator_commands_recorded": True,
            "source_reports": ["pack_set_validation.v0", "typed_ai_output_examples.v0"],
            "notes": [
                "Report preserves validator status and checksum status; it does not copy pack payloads.",
                "Local absolute paths outside the repository are redacted in report output.",
            ],
        },
        "mutation_summary": {
            **safety,
            "files_written": list(files_written),
            "notes": [
                "Validate-only preflight did not import, stage, index, upload, or mutate runtime/master-index state.",
                "Only an explicit --output report file may be written.",
            ],
        },
        "next_actions": next_actions,
        "limitations": [
            "Validate-only success is not canonical truth, rights clearance, malware safety, or master-index acceptance.",
            "Detailed privacy, rights, risk, and record-count fields are conservative summaries of existing validator output.",
            "No local quarantine, staging, import, or local-index mutation is implemented.",
        ],
        **safety,
        "notes": [
            f"strict={strict}",
            "Default preflight validates known repository examples when no explicit --pack-root is supplied.",
            "The tool delegates to existing validators and emits Pack Import Report v0 only.",
        ],
    }
    return report


def _argument_error(message: str) -> dict[str, Any]:
    return {
        "ok": False,
        "validator_id": VALIDATOR_ID,
        "error": message,
        "network_performed": False,
        "mutation_performed": False,
        "import_performed": False,
        "staging_performed": False,
        "indexing_performed": False,
        "upload_performed": False,
        "master_index_mutation_performed": False,
        "runtime_mutation_performed": False,
    }


def _list_examples_report(
    specs: Sequence[Mapping[str, Any]], errors: Sequence[str], *, strict: bool
) -> dict[str, Any]:
    return {
        "ok": not errors,
        "validator_id": VALIDATOR_ID,
        "mode": "list_examples",
        "strict": strict,
        "examples": [
            {
                "root": spec["display_root"],
                "root_kind": spec["root_kind"],
                "pack_type": spec["pack_type"],
                "provided_by": spec["provided_by"],
            }
            for spec in specs
        ],
        "errors": list(errors),
        "network_performed": False,
        "mutation_performed": False,
        "import_performed": False,
        "staging_performed": False,
        "indexing_performed": False,
        "upload_performed": False,
        "master_index_mutation_performed": False,
        "runtime_mutation_performed": False,
    }


def _validate_generated_report(report: Mapping[str, Any]) -> list[str]:
    try:
        import validate_pack_import_report
    except ImportError:
        return ["Pack Import Report validator is unavailable."]
    errors: list[str] = []
    validate_pack_import_report._validate_report(report, errors)  # noqa: SLF001 - local validator API reuse.
    return errors


def _report_success(report: Mapping[str, Any]) -> bool:
    return report.get("report_status") == "validate_only_passed" and not any(
        result.get("validation_status") != "passed" for result in report.get("pack_results", [])
    )


def _report_status(results: Sequence[Mapping[str, Any]], spec_errors: Sequence[str]) -> str:
    if spec_errors:
        return "blocked_by_policy"
    statuses = [result.get("validation_status") for result in results]
    if statuses and all(status == "passed" for status in statuses):
        return "validate_only_passed"
    if any(status == "unknown_type" for status in statuses):
        return "unsupported_pack_type" if len(statuses) == 1 else "partial_validation"
    if any(status == "unavailable" for status in statuses):
        return "unavailable_validator" if len(statuses) == 1 else "partial_validation"
    return "validate_only_failed"


def _next_actions(
    report_status: str, results: Sequence[Mapping[str, Any]], spec_errors: Sequence[str]
) -> list[dict[str, Any]]:
    if report_status == "validate_only_passed":
        return [
            {
                "action": "inspect_future",
                "reason": "Validated inputs may be reviewed by a future inspector; no staging or import occurred.",
                "requires_future_milestone": True,
            }
        ]
    if report_status in {"unsupported_pack_type", "partial_validation"} and any(
        result.get("validation_status") == "unknown_type" for result in results
    ):
        return [{"action": "unsupported", "reason": "At least one input root was not a known pack type."}]
    if spec_errors:
        return [{"action": "fix_pack_and_revalidate", "reason": "Input registry or argument errors blocked validation."}]
    return [{"action": "fix_pack_and_revalidate", "reason": "At least one validator reported failure."}]


def _issues_from_aggregate(result: Mapping[str, Any], pack_type: str) -> list[dict[str, Any]]:
    status = result.get("status")
    if status == "passed":
        return []
    excerpt = " ".join(
        str(result.get(field, "")) for field in ["stdout_excerpt", "stderr_excerpt"] if result.get(field)
    )
    issue_type = _issue_type(status, excerpt)
    severity = "blocked" if status in {"unknown_type", "unavailable"} else "error"
    return [
        {
            "issue_id": f"{pack_type}:{issue_type}:0",
            "severity": severity,
            "issue_type": issue_type,
            "message": _excerpt(excerpt) or f"{pack_type} validation status was {status}.",
            "remediation": _remediation(issue_type),
        }
    ]


def _issue_type(status: str, excerpt: str) -> str:
    lowered = excerpt.lower()
    if status == "unknown_type":
        return "unknown_pack_type"
    if status == "unavailable":
        return "validator_unavailable"
    if "checksum" in lowered:
        return "checksum_error"
    if "private path" in lowered or "privacy" in lowered:
        return "privacy_error"
    if "rights" in lowered:
        return "rights_review_required"
    if "executable" in lowered or "raw database" in lowered or "sqlite" in lowered:
        return "risk_review_required"
    return "schema_error"


def _remediation(issue_type: str) -> str:
    return {
        "unknown_pack_type": "Select a root containing a known Eureka pack manifest.",
        "validator_unavailable": "Restore the missing validator before rerunning validate-only preflight.",
        "checksum_error": "Regenerate or repair checksums, then revalidate.",
        "privacy_error": "Redact private data or mark the pack local-private, then revalidate.",
        "rights_review_required": "Add or repair rights/access documentation before sharing.",
        "risk_review_required": "Remove prohibited executable/raw database content or quarantine for future review.",
        "schema_error": "Repair the pack structure and rerun the validator.",
    }.get(issue_type, "Fix the pack and rerun validate-only preflight.")


def _validation_status(status: str) -> str:
    if status in {"passed", "failed", "unavailable", "unknown_type"}:
        return status
    return "failed"


def _checksum_status(status: str, result: Mapping[str, Any]) -> str:
    if status == "passed":
        return "passed"
    excerpt = f"{result.get('stdout_excerpt', '')} {result.get('stderr_excerpt', '')}".lower()
    if "checksum" in excerpt:
        return "failed"
    if status in {"unknown_type", "unavailable"}:
        return "unavailable"
    return "unavailable"


def _schema_status(status: str) -> str:
    if status == "passed":
        return "passed"
    if status == "unavailable":
        return "unavailable"
    return "failed"


def _privacy_status(status: str, result: Mapping[str, Any], spec: Mapping[str, Any]) -> str:
    if status == "passed" and spec.get("root_kind") == "repo_example_root":
        return "public_safe"
    excerpt = f"{result.get('stdout_excerpt', '')} {result.get('stderr_excerpt', '')}".lower()
    if "private path" in excerpt or "privacy" in excerpt:
        return "failed"
    return "unknown" if status != "passed" else "public_safe"


def _rights_status(status: str, result: Mapping[str, Any]) -> str:
    if status == "passed":
        return "review_required"
    excerpt = f"{result.get('stdout_excerpt', '')} {result.get('stderr_excerpt', '')}".lower()
    return "failed" if "rights" in excerpt else "unknown"


def _risk_status(status: str, result: Mapping[str, Any]) -> str:
    if status == "passed":
        return "metadata_only"
    excerpt = f"{result.get('stdout_excerpt', '')} {result.get('stderr_excerpt', '')}".lower()
    if "sqlite" in excerpt or "raw database" in excerpt:
        return "raw_database_detected"
    if "executable" in excerpt:
        return "executable_reference"
    if "credential" in excerpt:
        return "credential_risk"
    return "unknown"


def _recommended_next_action(status: str) -> str:
    if status == "passed":
        return "inspect_future"
    if status == "unknown_type":
        return "unsupported"
    return "fix_pack_and_revalidate"


def _pack_limitations(status: str, pack_type: str) -> list[str]:
    base = [
        "Validate-only result does not import, stage, index, upload, mutate runtime state, or accept master-index records.",
        "Validation does not prove truth, rights clearance, malware safety, or public acceptance.",
    ]
    if pack_type == "ai_output_bundle":
        base.append("Typed AI outputs remain review-required suggestions and no model calls were made.")
    if status != "passed":
        base.append("Failure details are summarized without exposing local absolute paths.")
    return base


def _validation_summary(results: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    summary = {"total": len(results), "passed": 0, "failed": 0, "unavailable": 0, "unknown_type": 0, "skipped": 0}
    for result in results:
        status = result.get("validation_status")
        if status in summary and status != "total":
            summary[status] += 1
    return summary


def _privacy_rights_risk_summary(results: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    issues = [
        issue
        for result in results
        for issue in result.get("issues", [])
        if isinstance(issue, Mapping)
    ]
    return {
        "privacy_issues": sum(1 for issue in issues if issue.get("issue_type") == "privacy_error"),
        "rights_issues": sum(1 for issue in issues if issue.get("issue_type") == "rights_review_required"),
        "risk_issues": sum(1 for issue in issues if issue.get("issue_type") == "risk_review_required"),
        "private_path_issues": sum(1 for issue in issues if issue.get("issue_type") == "private_path_detected"),
        "credential_issues": sum(1 for issue in issues if issue.get("issue_type") == "credential_detected"),
        "executable_payload_issues": sum(
            1 for issue in issues if issue.get("issue_type") == "executable_payload_detected"
        ),
        "raw_database_issues": sum(1 for issue in issues if issue.get("issue_type") == "raw_database_detected"),
        "notes": [
            "Counts summarize validator/report issues only; they are not rights clearance or malware safety decisions."
        ],
    }


def _synthetic_failed_result(index: int, message: str) -> dict[str, Any]:
    return {
        "pack_root": "none",
        "pack_type": "unknown",
        "validator_id": VALIDATOR_ID,
        "validator_command": "",
        "validation_status": "failed",
        "checksum_status": "unavailable",
        "schema_status": "failed",
        "privacy_status": "unknown",
        "rights_status": "unknown",
        "risk_status": "unknown",
        "issue_count": 1,
        "issues": [
            {
                "issue_id": f"input_error:{index}",
                "severity": "blocked",
                "issue_type": "policy_blocked",
                "message": _sanitize_text(message),
                "remediation": "Fix validate-only input selection and rerun.",
            }
        ],
        "record_counts": {},
        "limitations": ["Input validation failed before pack validation could run."],
        "recommended_next_action": "fix_pack_and_revalidate",
    }


def _strip_internal_keys(result: Mapping[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in result.items() if not key.startswith("_")}


def _read_pack_manifest(root: Path, pack_type: str) -> Mapping[str, Any]:
    config = validate_pack_set.PACK_TYPE_CONFIGS.get(pack_type)
    if not config:
        return {}
    manifest_path = root / config["manifest"]
    if not manifest_path.exists():
        return {}
    try:
        payload = json.loads(manifest_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    return payload if isinstance(payload, Mapping) else {}


def _manifest_id(manifest: Mapping[str, Any], *, fallback: Any = None) -> str:
    for field in ["pack_id", "queue_id", "provider_id", "report_id"]:
        value = manifest.get(field)
        if isinstance(value, str) and value:
            return value
    return str(fallback or "unknown")


def _manifest_version(manifest: Mapping[str, Any]) -> str:
    for field in ["pack_version", "queue_version", "provider_version", "report_version", "schema_version"]:
        value = manifest.get(field)
        if isinstance(value, str) and value:
            return value
    return "unknown"


def _record_counts(manifest: Mapping[str, Any]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for key, value in manifest.items():
        if key.endswith("_files") and isinstance(value, list):
            counts[key] = len(value)
        elif key in {"queue_entries", "decision_files", "contribution_item_files"} and isinstance(value, list):
            counts[key] = len(value)
    return counts


def _ai_record_counts() -> dict[str, int]:
    if not AI_OUTPUT_EXAMPLES.exists():
        return {}
    try:
        payload = json.loads(AI_OUTPUT_EXAMPLES.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return {}
    examples = payload.get("examples", [])
    return {"typed_ai_output_examples": len(examples)} if isinstance(examples, list) else {}


def _validator_id_for_type(pack_type: str) -> str:
    return {
        "source_pack": "source_pack_validator_v0",
        "evidence_pack": "evidence_pack_validator_v0",
        "index_pack": "index_pack_validator_v0",
        "contribution_pack": "contribution_pack_validator_v0",
        "master_index_review_queue": "master_index_review_queue_validator_v0",
        "unknown": "pack_import_validator_aggregator_v0",
    }.get(pack_type, "pack_import_validator_aggregator_v0")


def _report_id(
    results: Sequence[Mapping[str, Any]],
    specs: Sequence[Mapping[str, Any]],
    *,
    strict: bool,
    include_errors: Sequence[str],
) -> str:
    seed = json.dumps(
        {
            "results": results,
            "inputs": [
                {"root": spec.get("display_root"), "pack_type": spec.get("pack_type"), "kind": spec.get("root_kind")}
                for spec in specs
            ],
            "strict": strict,
            "errors": list(include_errors),
        },
        sort_keys=True,
    )
    digest = hashlib.sha256(seed.encode("utf-8")).hexdigest()[:16]
    return f"pack-import-report:validate-only:{digest}"


def _sanitize_mapping(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {key: _sanitize_mapping(child) for key, child in value.items()}
    if isinstance(value, list):
        return [_sanitize_mapping(child) for child in value]
    if isinstance(value, str):
        return _sanitize_text(value)
    return value


def _sanitize_text(value: str) -> str:
    sanitized = PRIVATE_PATH_RE.sub("<redacted-local-path>", value)
    sanitized = SECRET_VALUE_RE.sub("<redacted-secret>", sanitized)
    return sanitized


def _safe_path(path: Path | None) -> str:
    if path is None:
        return ""
    resolved = path.resolve()
    try:
        return resolved.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return "<explicit-local-path>"


def _excerpt(value: str | None) -> str:
    if not value:
        return ""
    sanitized = _sanitize_text(value.strip())
    if len(sanitized) <= EXCERPT_MAX_CHARS:
        return sanitized
    return sanitized[:EXCERPT_MAX_CHARS] + "...[truncated]"


def _resolve(path: Path) -> Path:
    return path if path.is_absolute() else (REPO_ROOT / path).resolve()


def _output_path_policy_error(path: Path) -> str:
    try:
        relative = path.resolve().relative_to(REPO_ROOT)
    except ValueError:
        return ""
    relative_text = relative.as_posix()
    for root in sorted(FORBIDDEN_OUTPUT_REPO_ROOTS, key=len, reverse=True):
        if relative_text == root or relative_text.startswith(f"{root}/"):
            return f"--output is under a forbidden repo root: {root}"
    return ""


def _emit(payload: Mapping[str, Any], *, json_output: bool, output: TextIO) -> None:
    if json_output:
        output.write(json.dumps(payload, indent=2, sort_keys=True) + "\n")
    else:
        output.write(_format_plain(payload))


def _format_plain(payload: Mapping[str, Any]) -> str:
    if payload.get("mode") == "list_examples":
        lines = [
            "Validate-Only Pack Import examples",
            f"status: {'valid' if payload.get('ok') else 'invalid'}",
            f"strict: {payload.get('strict')}",
        ]
        for example in payload.get("examples", []):
            lines.append(f"- {example['pack_type']}: {example['root']} ({example['root_kind']})")
        for key in [
            "network_performed",
            "mutation_performed",
            "import_performed",
            "staging_performed",
            "indexing_performed",
            "upload_performed",
            "master_index_mutation_performed",
            "runtime_mutation_performed",
        ]:
            lines.append(f"{key}: {payload.get(key)}")
        for error in payload.get("errors", []):
            lines.append(f"error: {error}")
        return "\n".join(lines) + "\n"

    if "report_kind" not in payload:
        return json.dumps(payload, indent=2, sort_keys=True) + "\n"

    summary = payload.get("validation_summary", {})
    lines = [
        "Validate-Only Pack Import",
        f"report_status: {payload.get('report_status')}",
        f"report_id: {payload.get('report_id')}",
        f"mode: {payload.get('mode')}",
        "summary: "
        f"total={summary.get('total', 0)} "
        f"passed={summary.get('passed', 0)} "
        f"failed={summary.get('failed', 0)} "
        f"unavailable={summary.get('unavailable', 0)} "
        f"unknown_type={summary.get('unknown_type', 0)}",
    ]
    for result in payload.get("pack_results", []):
        lines.append(f"- {result['pack_type']}: {result['pack_root']} -> {result['validation_status']}")
    mutation = payload.get("mutation_summary", {})
    for field in HARD_FALSE_FIELDS:
        lines.append(f"{field}: {mutation.get(field)}")
    lines.append(f"next_action: {payload.get('next_actions', [{}])[0].get('action')}")
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
