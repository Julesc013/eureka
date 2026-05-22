#!/usr/bin/env python3
"""Audit the Track B local foundry spine without live source access."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Iterable


DEFAULT_MATRIX_PATH = Path("control/inventory/track_b_completion_matrix.json")
DEFAULT_REPORT_PATH = Path("control/audits/track-b-23-integration-audit-v0/track_b_23_report.json")

BANNED_IMPORT_RE = re.compile(
    r"^\s*(?:from|import)\s+"
    r"(requests|urllib|http|socket|ftplib|smtplib|webbrowser|selenium|playwright|openai)\b",
    re.MULTILINE,
)

FORBIDDEN_ROOTS = [
    "site/dist",
    "site/dist/data/public_index",
    ".aide.local",
    ".local/eureka",
    ".cache/eureka",
]

TRUTH_TRUE_FORBIDDEN_FRAGMENTS = [
    "accepted",
    "accepts_",
    "public_truth",
    "source_truth",
    "creates_public_record",
    "mutate",
    "mutated",
    "rights_clearance",
    "malware_safety",
    "verified_installability",
    "exhaustive_global_search",
    "production_readiness",
    "automatic_merge",
    "automatic_promotion",
]

PRODUCT_TRUE_FORBIDDEN_KEYS = {
    "changed_product_behavior",
    "changed_public_search_behavior",
    "changed_public_routes",
    "changed_generated_site_artifacts",
    "regenerated_site_dist",
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
    "enabled_network_access",
    "enabled_api_calls",
    "enabled_model_provider_calls",
    "enabled_pack_import_runtime",
    "enabled_pack_submission_runtime",
    "enabled_hosted_upload_runtime",
    "enabled_review_runtime",
    "enabled_hosted_review_runtime",
    "created_native_projects",
    "created_local_private_state",
    "mutated_public_index",
    "mutated_master_index",
    "claimed_rights_clearance",
    "claimed_malware_safety",
    "claimed_verified_installability",
    "claimed_exhaustive_global_search",
    "claimed_production_readiness",
}


class AuditError(Exception):
    """Raised for invalid audit inputs."""


def repo_root_from_cwd() -> Path:
    return Path.cwd()


def relpath(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


def load_json_file(path: Path) -> tuple[Any | None, str | None]:
    try:
        return json.loads(path.read_text(encoding="utf-8")), None
    except Exception as exc:  # noqa: BLE001 - surfaced as deterministic audit text.
        return None, str(exc)


def load_matrix(root: Path, matrix_path: Path | None = None) -> tuple[dict[str, Any] | None, list[str]]:
    path = root / (matrix_path or DEFAULT_MATRIX_PATH)
    if not path.exists():
        return None, [f"missing matrix: {relpath(path, root)}"]
    data, error = load_json_file(path)
    if error:
        return None, [f"invalid matrix JSON: {relpath(path, root)}: {error}"]
    if not isinstance(data, dict):
        return None, [f"matrix is not an object: {relpath(path, root)}"]
    return data, []


def iter_task_paths(task: dict[str, Any]) -> Iterable[str]:
    keys = [
        "artifact_paths",
        "contract_paths",
        "policy_paths",
        "runtime_paths",
        "script_paths",
        "validator_paths",
        "test_paths",
        "example_paths",
        "audit_paths",
    ]
    for key in keys:
        for value in task.get(key, []) or []:
            if isinstance(value, str):
                yield value


def iter_all_paths(matrix: dict[str, Any]) -> Iterable[str]:
    for task in matrix.get("tasks", []) or []:
        if isinstance(task, dict):
            yield from iter_task_paths(task)
    for key in [
        "contract_families",
        "runtime_families",
        "validator_families",
        "policy_families",
        "example_families",
        "audit_packs",
    ]:
        for value in matrix.get(key, []) or []:
            if isinstance(value, str):
                yield value
            elif isinstance(value, dict):
                for nested in value.values():
                    if isinstance(nested, str):
                        yield nested
                    elif isinstance(nested, list):
                        for item in nested:
                            if isinstance(item, str):
                                yield item


def expand_spec(root: Path, spec: str) -> list[Path]:
    if any(ch in spec for ch in "*?[]"):
        return sorted(root.glob(spec.replace("\\", "/")))
    return [root / spec]


def check_expected_paths(root: Path, matrix: dict[str, Any]) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    warnings: list[str] = []
    seen: set[str] = set()
    for spec in sorted(set(iter_all_paths(matrix))):
        if spec in seen:
            continue
        seen.add(spec)
        expanded = expand_spec(root, spec)
        if not expanded or not any(path.exists() for path in expanded):
            errors.append(f"missing expected path: {spec}")
        elif spec.endswith("/"):
            warnings.append(f"path has trailing slash but exists: {spec}")
    return errors, warnings


def json_specs(matrix: dict[str, Any]) -> list[str]:
    specs = []
    for spec in sorted(set(iter_all_paths(matrix))):
        if spec.endswith(".json") or spec.endswith(".jsonl") or "*.json" in spec:
            specs.append(spec)
    specs.append(DEFAULT_MATRIX_PATH.as_posix())
    return sorted(set(specs))


def check_json_syntax(root: Path, matrix: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for spec in json_specs(matrix):
        for path in expand_spec(root, spec):
            if not path.exists() or path.suffix != ".json":
                continue
            _, error = load_json_file(path)
            if error:
                errors.append(f"invalid JSON: {relpath(path, root)}: {error}")
    return errors


def report_paths(root: Path, matrix: dict[str, Any]) -> list[Path]:
    paths: list[Path] = []
    for task in matrix.get("tasks", []) or []:
        if not isinstance(task, dict):
            continue
        for spec in task.get("audit_paths", []) or []:
            if not isinstance(spec, str):
                continue
            base = root / spec
            if base.is_dir():
                paths.extend(sorted(base.glob("*_report.json")))
                paths.extend(sorted(base.glob("track_b_*_report.json")))
            elif base.name.endswith("_report.json"):
                paths.append(base)
    return sorted(set(paths))


def iter_boundary_dicts(data: Any) -> Iterable[tuple[str, dict[str, Any]]]:
    if isinstance(data, dict):
        for key, value in data.items():
            if key in {"truth_boundary", "product_boundary", "runtime_scope"} and isinstance(value, dict):
                yield key, value
            yield from iter_boundary_dicts(value)
    elif isinstance(data, list):
        for item in data:
            yield from iter_boundary_dicts(item)


def truth_key_is_forbidden(key: str) -> bool:
    return any(fragment in key for fragment in TRUTH_TRUE_FORBIDDEN_FRAGMENTS)


def product_key_is_forbidden(key: str) -> bool:
    if key in PRODUCT_TRUE_FORBIDDEN_KEYS:
        return True
    if key.startswith("claimed_") or key.startswith("mutated_") or key.startswith("changed_"):
        return True
    return False


def check_boundaries(root: Path, matrix: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for path in report_paths(root, matrix):
        if not path.exists():
            continue
        data, error = load_json_file(path)
        if error:
            errors.append(f"cannot read boundary report: {relpath(path, root)}: {error}")
            continue
        for boundary_name, boundary in iter_boundary_dicts(data):
            for key, value in boundary.items():
                if value is not True:
                    continue
                if boundary_name == "truth_boundary" and truth_key_is_forbidden(key):
                    errors.append(f"truth boundary violation: {relpath(path, root)} {key}=true")
                if boundary_name in {"product_boundary", "runtime_scope"} and product_key_is_forbidden(key):
                    errors.append(f"product boundary violation: {relpath(path, root)} {key}=true")
    return errors


def check_banned_imports(root: Path, matrix: dict[str, Any]) -> list[str]:
    findings: list[str] = []
    specs: set[str] = {"scripts/audit_track_b_integration.py"}
    for task in matrix.get("tasks", []) or []:
        if not isinstance(task, dict):
            continue
        for key in ("runtime_paths", "script_paths", "validator_paths"):
            for spec in task.get(key, []) or []:
                if isinstance(spec, str) and (spec.endswith(".py") or "*.py" in spec):
                    specs.add(spec)
    for spec in sorted(specs):
        for path in expand_spec(root, spec):
            if not path.exists() or path.suffix != ".py":
                continue
            text = path.read_text(encoding="utf-8")
            for match in BANNED_IMPORT_RE.finditer(text):
                findings.append(f"forbidden import in {relpath(path, root)}: {match.group(1)}")
    return findings


def git_status_for_roots(root: Path, roots: list[str]) -> list[str]:
    try:
        result = subprocess.run(
            ["git", "status", "--short", "--", *roots],
            cwd=root,
            check=False,
            capture_output=True,
            text=True,
            timeout=15,
        )
    except Exception:
        return []
    if result.returncode != 0:
        return []
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def check_forbidden_roots(root: Path, strict_presence: bool = False) -> list[str]:
    errors: list[str] = []
    if strict_presence:
        for spec in FORBIDDEN_ROOTS:
            path = root / spec
            if path.exists():
                errors.append(f"forbidden output root exists: {spec}")
        return errors
    for line in git_status_for_roots(root, FORBIDDEN_ROOTS):
        errors.append(f"forbidden output root changed: {line}")
    return errors


def summarize_task(task: dict[str, Any], root: Path) -> dict[str, Any]:
    missing = []
    for spec in iter_task_paths(task):
        expanded = expand_spec(root, spec)
        if not expanded or not any(path.exists() for path in expanded):
            missing.append(spec)
    status = "pass" if not missing else "fail"
    if task.get("known_warnings"):
        status = "warn" if status == "pass" else status
    return {
        "task_id": task.get("task_id"),
        "label": task.get("label"),
        "status": status,
        "missing_paths": missing,
        "known_warnings": task.get("known_warnings", []),
        "product_boundary_preserved": task.get("product_boundary_preserved") is True,
        "truth_boundary_preserved": task.get("truth_boundary_preserved") is True,
    }


def audit_repo(
    root: Path,
    matrix_path: Path | None = None,
    strict_forbidden_roots: bool = False,
) -> dict[str, Any]:
    root = root.resolve()
    matrix, matrix_errors = load_matrix(root, matrix_path)
    errors: list[str] = list(matrix_errors)
    warnings: list[str] = []
    task_results: list[dict[str, Any]] = []
    if matrix is None:
        return build_result(root, None, task_results, errors, warnings)

    path_errors, path_warnings = check_expected_paths(root, matrix)
    errors.extend(path_errors)
    warnings.extend(path_warnings)
    errors.extend(check_json_syntax(root, matrix))
    errors.extend(check_boundaries(root, matrix))
    errors.extend(check_banned_imports(root, matrix))
    errors.extend(check_forbidden_roots(root, strict_forbidden_roots))

    for task in matrix.get("tasks", []) or []:
        if isinstance(task, dict):
            task_results.append(summarize_task(task, root))

    for task_result in task_results:
        if task_result["status"] == "warn":
            warnings.extend(
                f"{task_result['task_id']} warning: {warning}"
                for warning in task_result.get("known_warnings", [])
            )

    return build_result(root, matrix, task_results, errors, warnings)


def build_result(
    root: Path,
    matrix: dict[str, Any] | None,
    task_results: list[dict[str, Any]],
    errors: list[str],
    warnings: list[str],
) -> dict[str, Any]:
    errors = sorted(set(errors))
    warnings = sorted(set(warnings))
    status = "pass" if not errors and not warnings else "pass_with_warnings" if not errors else "partial"
    track_status = "complete_enough_for_first_connector_approval" if not errors else "needs_remediation"
    first_connector = "READY_FOR_IA_APPROVAL_PROMPT" if not errors and not warnings else "READY_WITH_WARNINGS" if not errors else "NEEDS_REMEDIATION"
    exit_decision = "PASS" if status == "pass" else "PASS_WITH_WARNINGS" if status == "pass_with_warnings" else "PARTIAL"
    audited_tasks = [task.get("task_id") for task in task_results if task.get("task_id")]
    return {
        "schema_version": "track_b_23_report.v0",
        "status": status,
        "track": "B",
        "task": "TRACK-B-23",
        "track_status": track_status,
        "audited_tasks": audited_tasks,
        "contract_families": (matrix or {}).get("contract_families", []),
        "runtime_families": (matrix or {}).get("runtime_families", []),
        "validators": (matrix or {}).get("validator_families", []),
        "audit_packs": (matrix or {}).get("audit_packs", []),
        "gate_results": {
            "expected_paths_exist": not any("missing expected path" in error for error in errors),
            "json_syntax_valid": not any("invalid JSON" in error for error in errors),
            "truth_boundary_preserved": not any("truth boundary violation" in error for error in errors),
            "product_boundary_preserved": not any("product boundary violation" in error for error in errors),
            "forbidden_roots_unchanged": not any("forbidden output root" in error for error in errors),
            "banned_runtime_imports_absent": not any("forbidden import" in error for error in errors),
        },
        "task_results": task_results,
        "warnings": warnings,
        "critical_blockers": errors,
        "deferred_work": (matrix or {}).get("deferred_work", []),
        "known_gaps": (matrix or {}).get("known_gaps", []),
        "first_connector_readiness": first_connector,
        "truth_boundary": {
            "accepted_public_truth_created": False,
            "accepted_evidence_truth_created": False,
            "accepted_candidate_truth_created": False,
            "source_truth_accepted": False,
            "public_index_mutated": False,
            "master_index_mutated": False,
            "rights_clearance_claimed": False,
            "malware_safety_claimed": False,
            "verified_installability_claimed": False,
            "exhaustive_global_search_claimed": False,
            "automatic_merge_or_promotion_claimed": False,
        },
        "product_boundary": {
            "changed_product_behavior": False,
            "changed_public_search_behavior": False,
            "changed_public_routes": False,
            "changed_generated_site_artifacts": False,
            "regenerated_site_dist": False,
            "enabled_hosting": False,
            "enabled_live_probes": False,
            "enabled_source_sync": False,
            "enabled_source_connectors": False,
            "enabled_downloads": False,
            "enabled_installers": False,
            "enabled_execution": False,
            "enabled_uploads": False,
            "enabled_accounts": False,
            "enabled_telemetry": False,
            "enabled_pack_import_runtime": False,
            "enabled_pack_submission_runtime": False,
            "enabled_hosted_upload_runtime": False,
            "enabled_review_runtime": False,
            "enabled_hosted_review_runtime": False,
            "enabled_model_provider_calls": False,
            "created_native_projects": False,
            "created_local_private_state": False,
            "mutated_public_index": False,
            "mutated_master_index": False,
        },
        "exit_gate_decision": exit_decision,
        "next_task": "IA-01 - Internet Archive metadata connector approval decision",
        "notes": [
            "Audit script is read-only unless --json-output is provided.",
            "Existing site/dist and site/dist/data/public_index roots are checked for git changes, not mere historical presence.",
        ],
    }


def print_list(matrix: dict[str, Any]) -> None:
    print("Track B integration audit tasks")
    for task in matrix.get("tasks", []) or []:
        if not isinstance(task, dict):
            continue
        print(f"- {task.get('task_id')}: {task.get('label')}")


def print_summary(result: dict[str, Any]) -> None:
    print("Track B integration audit")
    print(f"status: {result['status']}")
    print(f"track_status: {result['track_status']}")
    print(f"exit_gate_decision: {result['exit_gate_decision']}")
    print(f"first_connector_readiness: {result['first_connector_readiness']}")
    print(f"audited_tasks: {len(result['audited_tasks'])}")
    print(f"warnings: {len(result['warnings'])}")
    print(f"critical_blockers: {len(result['critical_blockers'])}")
    for warning in result["warnings"][:10]:
        print(f"WARN: {warning}")
    for blocker in result["critical_blockers"][:10]:
        print(f"FAIL: {blocker}")


def assert_output_path_allowed(root: Path, path: Path) -> None:
    resolved = path.resolve()
    try:
        rel = resolved.relative_to(root.resolve()).as_posix()
    except ValueError:
        rel = resolved.as_posix()
    forbidden_prefixes = [
        "site/dist/",
        "site/dist/data/public_index/",
        "runtime/",
        "contracts/",
        ".aide.local/",
        ".local/eureka/",
        ".cache/eureka/",
    ]
    if any(rel == prefix.rstrip("/") or rel.startswith(prefix) for prefix in forbidden_prefixes):
        raise AuditError(f"refusing forbidden output path: {rel}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Return nonzero on audit errors.")
    parser.add_argument("--json-output", help="Write deterministic JSON report to an explicit path.")
    parser.add_argument("--list", action="store_true", help="List audited Track B tasks.")
    parser.add_argument("--matrix", default=DEFAULT_MATRIX_PATH.as_posix(), help="Matrix path relative to repo root.")
    args = parser.parse_args(argv)

    root = repo_root_from_cwd()
    matrix_path = Path(args.matrix)
    matrix, matrix_errors = load_matrix(root, matrix_path)
    if args.list:
        if matrix is None:
            for error in matrix_errors:
                print(f"FAIL: {error}")
            return 1
        print_list(matrix)
        return 0

    result = audit_repo(root, matrix_path)
    print_summary(result)

    if args.json_output:
        output_path = root / args.json_output
        try:
            assert_output_path_allowed(root, output_path)
        except AuditError as exc:
            print(f"FAIL: {exc}", file=sys.stderr)
            return 2
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    if args.check and result["critical_blockers"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
