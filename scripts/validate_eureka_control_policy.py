from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.preview_eureka_changelog import parse_commit_message

POLICY_FILES = {
    "commit": ".aide/policies/commit-message-standard.yaml",
    "workunit": ".aide/policies/workunit-recovery-policy.yaml",
    "documentation": ".aide/policies/documentation-quality-policy.yaml",
    "source_comment": ".aide/policies/source-comment-policy.yaml",
}
DOC_FILES = [
    "docs/operations/COMMIT_AND_CHANGELOG_STANDARD.md",
    "docs/operations/WORKUNIT_RECOVERY_POLICY.md",
    "docs/operations/DOCUMENTATION_QUALITY_STANDARD.md",
    "docs/operations/SOURCE_COMMENT_STANDARD.md",
]
SCRIPTS = [
    "scripts/validate_eureka_control_policy.py",
    "scripts/preview_eureka_changelog.py",
]
TESTS = [
    "tests/operations/test_eureka_control_policy.py",
    "tests/operations/test_eureka_changelog_preview.py",
]
SAMPLE_VALID = "examples/commit_messages/valid_structured_commit.txt"
SAMPLE_INVALID_MISSING_WHY = "examples/commit_messages/invalid_missing_why.txt"
SAMPLE_WARN = "examples/commit_messages/valid_warn_only_commit.txt"
AUDIT_REPORT = "control/audits/eureka-ctrl-01-control-standards-v0/eureka_ctrl_01_report.json"

ALLOWED_TYPES = {
    "feat", "fix", "docs", "test", "refactor", "chore", "contracts", "runtime", "surface", "eval",
    "audit", "ops", "native", "site", "aide", "security", "revert",
}
REQUIRED_HEADINGS = [
    "## Summary",
    "## Why",
    "## Changed",
    "## Validation",
    "## Changelog",
    "## Risks",
    "## Follow-up",
]
REQUIRED_TRAILERS = [
    "AIDE-Task",
    "AIDE-Result",
    "AIDE-Scope",
    "AIDE-Change-Class",
    "AIDE-Quality-Gate",
    "AIDE-WorkUnit",
]
CHANGELOG_GROUPS = [
    "Added",
    "Changed",
    "Fixed",
    "Removed",
    "Deprecated",
    "Security",
    "Tests",
    "Docs",
    "Internal",
    "Risks",
    "Follow-up",
]
WORKUNIT_RECOVERY_REQUIRED = [
    "dirty_tree",
    "missing_dependency",
    "stale_status",
    "failed_validation",
    "out_of_order_task",
    "repeated_prompt",
]
STOP_CONDITIONS = [
    "destructive ambiguity",
    "missing external credentials",
    "legal/licensing decision",
    "manual observation requirement",
    "irreversible action without explicit approval",
    "private-data exposure risk",
    "unsafe network/source action",
    "production deployment or hosting mutation without explicit approval",
]
NON_STOP_CONDITIONS = [
    "duplicate prompt",
    "repeated task",
    "stale status file",
    "out-of-order prompt",
    "partial previous task",
    "missing optional generated artifact",
    "known WARN-only AIDE warning",
]
STALE_CLAIM_CHECKS = [
    "hosted backend active",
    "live probes enabled",
    "source sync enabled",
    "source connectors active",
    "downloads/installers/execution enabled",
    "uploads/accounts/telemetry enabled",
    "rights clearance",
    "malware safety",
    "verified installability",
    "exhaustive global search",
    "automatic merge/dedup/promotion",
    "master-index mutation",
    "native project creation",
]
PRODUCT_BOUNDARY_FIELDS = [
    "changed_product_behavior",
    "changed_public_routes",
    "changed_generated_site_artifacts",
    "enabled_hosting",
    "enabled_live_probes",
    "enabled_source_sync",
    "enabled_source_connectors",
    "enabled_downloads",
    "enabled_installers",
    "enabled_execution",
    "enabled_uploads",
    "enabled_accounts",
    "enabled_telemetry",
    "enabled_node_runtime",
    "enabled_pack_import_runtime",
    "enabled_review_runtime",
    "created_native_projects",
    "mutated_master_index",
]

SUBJECT_RE = re.compile(r"^(?P<type>[a-z]+)\((?P<scope>[A-Za-z0-9_.-]+)\): (?P<summary>.+)$")


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate Eureka control policy files and examples.")
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--json", action="store_true", help="Emit JSON report.")
    args = parser.parse_args(list(argv) if argv is not None else None)

    report = validate_control_policy(Path(args.repo_root))
    output = stdout or sys.stdout
    if args.json:
        output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
    else:
        output.write(format_report(report))
    return 0 if report["status"] == "valid" else 1


def validate_control_policy(repo_root: Path = REPO_ROOT) -> dict[str, Any]:
    root = repo_root.resolve()
    errors: list[str] = []
    warnings: list[str] = []

    policies = {name: load_jsonish(root / path, errors) for name, path in POLICY_FILES.items()}
    for path in [*POLICY_FILES.values(), *DOC_FILES, *SCRIPTS, *TESTS, SAMPLE_VALID, SAMPLE_INVALID_MISSING_WHY, SAMPLE_WARN]:
        require_path(root, path, errors)

    if isinstance(policies.get("commit"), Mapping):
        validate_commit_policy(policies["commit"], errors)
    if isinstance(policies.get("workunit"), Mapping):
        validate_workunit_policy(policies["workunit"], errors)
    if isinstance(policies.get("documentation"), Mapping):
        validate_documentation_policy(policies["documentation"], errors)
    if isinstance(policies.get("source_comment"), Mapping):
        validate_source_comment_policy(policies["source_comment"], errors)

    valid_sample = (root / SAMPLE_VALID).read_text(encoding="utf-8") if (root / SAMPLE_VALID).is_file() else ""
    invalid_sample = (root / SAMPLE_INVALID_MISSING_WHY).read_text(encoding="utf-8") if (root / SAMPLE_INVALID_MISSING_WHY).is_file() else ""
    warn_sample = (root / SAMPLE_WARN).read_text(encoding="utf-8") if (root / SAMPLE_WARN).is_file() else ""
    if valid_sample:
        errors.extend(f"valid sample: {error}" for error in validate_commit_message(valid_sample))
    if warn_sample:
        errors.extend(f"warn sample: {error}" for error in validate_commit_message(warn_sample))
    if invalid_sample and not any("missing required heading ## Why" in error for error in validate_commit_message(invalid_sample)):
        errors.append("invalid_missing_why sample must fail for missing ## Why")

    report_path = root / AUDIT_REPORT
    if report_path.is_file():
        audit = load_jsonish(report_path, errors)
        if isinstance(audit, Mapping):
            boundary = audit.get("product_boundary")
            if not isinstance(boundary, Mapping):
                errors.append("audit report product_boundary must be an object")
            else:
                for field in PRODUCT_BOUNDARY_FIELDS:
                    if boundary.get(field) is not False:
                        errors.append(f"audit report product_boundary.{field} must be false")
    else:
        warnings.append(f"{AUDIT_REPORT}: audit report not present yet")

    errors = sorted(set(errors))
    return {
        "schema_version": "eureka_control_policy_validation.v0",
        "status": "valid" if not errors else "invalid",
        "errors": errors,
        "warnings": sorted(set(warnings)),
        "policy_files": sorted(POLICY_FILES.values()),
        "doc_files": sorted(DOC_FILES),
        "sample_commit_files": sorted([SAMPLE_VALID, SAMPLE_INVALID_MISSING_WHY, SAMPLE_WARN]),
    }


def validate_commit_policy(policy: Mapping[str, Any], errors: list[str]) -> None:
    allowed = set(string_items(mapping(policy.get("subject")).get("allowed_types")))
    missing_types = ALLOWED_TYPES - allowed
    if missing_types:
        errors.append(f"commit policy missing allowed types {sorted(missing_types)}")
    headings = string_items(mapping(policy.get("body")).get("required_headings"))
    for heading in REQUIRED_HEADINGS:
        if heading not in headings:
            errors.append(f"commit policy missing required heading {heading}")
    groups = string_items(mapping(policy.get("changelog")).get("groups"))
    for group in CHANGELOG_GROUPS:
        if group not in groups:
            errors.append(f"commit policy missing changelog group {group}")
    required_trailers = mapping(mapping(policy.get("trailers")).get("required"))
    for trailer in REQUIRED_TRAILERS:
        if trailer not in required_trailers:
            errors.append(f"commit policy missing required trailer {trailer}")
    if "PASS_WITH_WARNINGS" not in string_items(required_trailers.get("AIDE-Result")):
        errors.append("commit policy must allow PASS_WITH_WARNINGS")


def validate_workunit_policy(policy: Mapping[str, Any], errors: list[str]) -> None:
    idempotency = mapping(policy.get("idempotency"))
    duplicate = mapping(idempotency.get("duplicate_behavior"))
    for key in ("if_complete", "if_partial", "if_conflicting"):
        if key not in duplicate:
            errors.append(f"workunit policy missing duplicate behavior {key}")
    recovery = mapping(policy.get("recovery"))
    for key in WORKUNIT_RECOVERY_REQUIRED:
        if key not in recovery:
            errors.append(f"workunit policy missing recovery behavior {key}")
    for condition in STOP_CONDITIONS:
        if condition not in string_items(policy.get("stop_conditions")):
            errors.append(f"workunit policy missing stop condition {condition}")
    for condition in NON_STOP_CONDITIONS:
        if condition not in string_items(policy.get("non_stop_conditions")):
            errors.append(f"workunit policy missing non-stop condition {condition}")
    if len(string_items(policy.get("recovery_loop"))) < 8:
        errors.append("workunit policy recovery_loop must list the full inspect/classify/reconcile/resume/validate/evidence/commit/review loop")


def validate_documentation_policy(policy: Mapping[str, Any], errors: list[str]) -> None:
    for phrase in ("accurate", "source-grounded", "compact", "non-bloated"):
        if phrase not in string_items(policy.get("required_qualities")):
            errors.append(f"documentation policy missing quality {phrase}")
    anti_bloat = " ".join(string_items(policy.get("anti_bloat_rules"))).lower()
    for phrase in ("full chat history", "project-history dumps", "canonical docs"):
        if phrase not in anti_bloat:
            errors.append(f"documentation policy missing anti-bloat phrase {phrase}")
    for claim in STALE_CLAIM_CHECKS:
        if claim not in string_items(policy.get("stale_claim_checks")):
            errors.append(f"documentation policy missing stale-claim check {claim}")


def validate_source_comment_policy(policy: Mapping[str, Any], errors: list[str]) -> None:
    principle = str(policy.get("principle", "")).lower()
    for phrase in ("why", "invariants", "side effects", "failure modes", "not add comments that merely restate syntax"):
        if phrase not in principle:
            errors.append(f"source-comment policy missing why-first principle phrase {phrase}")
    if not mapping(policy.get("explanation_density_bands")):
        errors.append("source-comment policy missing advisory density bands")
    enforcement = mapping(policy.get("enforcement"))
    if enforcement.get("hard_fail_existing_code") is not False:
        errors.append("source-comment policy must not hard-fail existing code")


def validate_commit_message(message: str) -> list[str]:
    errors: list[str] = []
    normalized = message.replace("\r\n", "\n").strip()
    lines = normalized.split("\n") if normalized else []
    subject = lines[0].strip() if lines else ""
    match = SUBJECT_RE.match(subject)
    if not match:
        errors.append("invalid subject line")
    else:
        if match.group("type") not in ALLOWED_TYPES:
            errors.append(f"invalid subject type {match.group('type')}")
        if len(subject) > 72:
            errors.append("subject exceeds 72 characters")
        if subject.endswith("."):
            errors.append("subject must not end with a period")
    for heading in REQUIRED_HEADINGS:
        if heading not in normalized:
            errors.append(f"missing required heading {heading}")
    parsed = parse_commit_message(message)
    trailers = parsed["trailers"]
    for trailer in REQUIRED_TRAILERS:
        if trailer not in trailers:
            errors.append(f"missing required trailer {trailer}")
    if not parsed["changelog"]:
        errors.append("missing parseable changelog groups")
    return sorted(errors)


def load_jsonish(path: Path, errors: list[str]) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"{rel(path)}: file not found")
    except json.JSONDecodeError as exc:
        errors.append(f"{rel(path)}: expected JSON-compatible YAML at line {exc.lineno}: {exc.msg}")
    return None


def require_path(root: Path, relative: str, errors: list[str]) -> None:
    if not (root / relative).exists():
        errors.append(f"{relative}: required path missing")


def mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def string_items(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [item for item in value if isinstance(item, str)]


def rel(path: Path) -> str:
    try:
        return path.resolve().relative_to(REPO_ROOT.resolve()).as_posix()
    except ValueError:
        return str(path)


def format_report(report: Mapping[str, Any]) -> str:
    lines = [
        f"validate_eureka_control_policy: {report['status']}",
        f"schema_version: {report['schema_version']}",
        f"policy_files: {len(report['policy_files'])}",
        f"doc_files: {len(report['doc_files'])}",
        f"sample_commit_files: {len(report['sample_commit_files'])}",
    ]
    if report.get("warnings"):
        lines.append("warnings:")
        lines.extend(f"- {warning}" for warning in report["warnings"])
    if report.get("errors"):
        lines.append("errors:")
        lines.extend(f"- {error}" for error in report["errors"])
    return "\n".join(lines) + "\n"


if __name__ == "__main__":
    raise SystemExit(main())
