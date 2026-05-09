#!/usr/bin/env python3
"""Validate G-BUNDLE-02 ranking shadow runtime artifacts offline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.extraction.guards import FORBIDDEN_IMPORT_RE, detect_truth_or_product_violations, load_json  # noqa: E402


CONTRACTS = (
    "contracts/query/ranking_shadow_result.v0.json",
    "contracts/query/ranking_factor.v0.json",
    "contracts/query/ranking_input_bundle.v0.json",
    "contracts/query/ranking_output_bundle.v0.json",
    "contracts/query/identity_merge_shadow.v0.json",
    "contracts/query/dedup_shadow_result.v0.json",
    "contracts/query/search_quality_query_set.v0.json",
    "contracts/query/search_quality_regression_report.v0.json",
    "contracts/query/public_ranking_gate.v0.json",
)
POLICIES = (
    "control/inventory/search_quality/ranking_shadow_policy.json",
    "control/inventory/search_quality/ranking_factor_policy.json",
    "control/inventory/search_quality/identity_merge_shadow_policy.json",
    "control/inventory/search_quality/dedup_shadow_policy.json",
    "control/inventory/search_quality/search_quality_query_set_policy.json",
    "control/inventory/search_quality/search_quality_regression_policy.json",
    "control/inventory/search_quality/public_ranking_gate_policy.json",
    "control/inventory/search_quality/ranking_output_policy.json",
    "control/inventory/search_quality/ranking_path_policy.json",
    "control/inventory/search_quality/ranking_truth_policy.json",
)
EXAMPLES = (
    "examples/search_quality/ranking/input_bundle_software_v0.json",
    "examples/search_quality/ranking/input_bundle_extraction_gap_v0.json",
    "examples/search_quality/ranking/ranking_shadow_result_v0.json",
    "examples/search_quality/ranking/ranking_output_bundle_v0.json",
    "examples/search_quality/ranking/policy_blocked_ranking_shadow_v0.json",
    "examples/search_quality/identity/identity_merge_shadow_v0.json",
    "examples/search_quality/identity/dedup_shadow_result_v0.json",
    "examples/search_quality/identity/conflict_preserved_identity_shadow_v0.json",
    "examples/search_quality/identity/policy_blocked_identity_shadow_v0.json",
    "examples/search_quality/query_sets/minimal_search_quality_query_set_v0.json",
    "examples/search_quality/query_sets/software_compatibility_query_set_v0.json",
    "examples/search_quality/query_sets/extraction_gap_query_set_v0.json",
    "examples/search_quality/query_sets/known_absence_query_set_v0.json",
    "examples/search_quality/regression/minimal_regression_report_v0.json",
    "examples/search_quality/regression/software_quality_regression_report_v0.json",
    "examples/search_quality/regression/extraction_gap_regression_report_v0.json",
    "examples/search_quality/regression/policy_blocked_regression_report_v0.json",
    "examples/search_quality/public_ranking_gate/public_ranking_gate_blocked_v0.json",
    "examples/search_quality/public_ranking_gate/public_ranking_gate_ready_future_v0.json",
)
PYTHON_FILES = (
    "runtime/search_quality/ranking_shadow.py",
    "runtime/search_quality/ranking_factors.py",
    "runtime/search_quality/identity_shadow.py",
    "runtime/search_quality/dedup_shadow.py",
    "runtime/search_quality/quality_harness.py",
    "runtime/search_quality/public_ranking_gate.py",
    "scripts/run_ranking_shadow.py",
    "scripts/run_search_quality_regression.py",
    "scripts/summarize_ranking_shadow.py",
    "scripts/validate_ranking_shadow_runtime.py",
)
AUDIT_DIR = Path("control/audits/g-bundle-02-ranking-shadow-quality-harness-v0")
AUDIT_FILES = (
    "README.md",
    "g_bundle_02_report.json",
    "ranking_shadow_runtime_summary.md",
    "ranking_factor_summary.md",
    "identity_merge_dedup_shadow_report.md",
    "search_quality_regression_report.md",
    "public_ranking_gate_report.md",
    "public_ranking_no_change_report.md",
    "next_phase_recommendation.md",
    "validation.md",
    "generated/sample_ranking_shadow_result.json",
    "generated/sample_ranking_output_bundle.json",
    "generated/sample_identity_merge_shadow.json",
    "generated/sample_search_quality_regression_report.json",
    "generated/sample_public_ranking_gate.json",
    "generated/sample_ranking_summary.md",
)


def validate_repo(root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    for rel in CONTRACTS + POLICIES + EXAMPLES:
        payload = load_required_json(root / rel, errors)
        if payload:
            errors.extend(f"{rel}: {error}" for error in detect_truth_or_product_violations(payload))
            validate_semantics(rel, payload, errors)
    validate_policy_values(root, errors)
    validate_imports(root, errors)
    validate_scripts(root, errors)
    validate_audit(root, errors)
    validate_no_private_roots(root, errors)
    return {
        "schema_version": "ranking_shadow_runtime_validation.v0",
        "task": "G-BUNDLE-02",
        "status": "valid" if not errors else "invalid",
        "offline_default": True,
        "errors": errors,
    }


def validate_policy_values(root: Path, errors: list[str]) -> None:
    shadow = load_required_json(root / "control/inventory/search_quality/ranking_shadow_policy.json", errors)
    for key in ("public_ranking_mutation_allowed", "public_search_mutation_allowed", "public_index_mutation_allowed", "master_index_mutation_allowed", "accepted_truth_creation_allowed"):
        if shadow.get(key) is not False:
            errors.append(f"ranking shadow policy {key} must be false")
    gate = load_required_json(root / "control/inventory/search_quality/public_ranking_gate_policy.json", errors)
    if gate.get("public_ranking_blocked_current") is not True:
        errors.append("public ranking must remain blocked current")
    truth = load_required_json(root / "control/inventory/search_quality/ranking_truth_policy.json", errors)
    for key, value in truth.items():
        if key in {"schema_version", "policy_id"}:
            continue
        if value is not False:
            errors.append(f"ranking truth policy {key} must be false")


def validate_semantics(rel: str, payload: Mapping[str, Any], errors: list[str]) -> None:
    if rel.startswith("contracts/"):
        return
    schema = payload.get("schema_version")
    if schema == "public_ranking_gate.v0" and payload.get("gate_status") not in {"blocked_current", "ready_for_review_future"}:
        errors.append(f"{rel}: public ranking gate must be blocked/current or future-review only")
    if schema == "identity_merge_shadow.v0":
        if payload.get("merge_allowed_current") is not False or payload.get("automatic_merge_allowed") is not False:
            errors.append(f"{rel}: identity merge must remain disabled")
    if schema == "dedup_shadow_result.v0":
        for key in ("merge_allowed_current", "delete_allowed_current", "automatic_dedup_allowed"):
            if payload.get(key) is not False:
                errors.append(f"{rel}: {key} must be false")
    if schema == "search_quality_regression_report.v0":
        text = json.dumps(payload, sort_keys=True).casefold()
        for term in ("beats_google", "beats_internet_archive", "production_search_quality"):
            if f'"{term}": true' in text:
                errors.append(f"{rel}: forbidden quality claim {term}")


def validate_imports(root: Path, errors: list[str]) -> None:
    for rel in PYTHON_FILES:
        path = root / rel
        if not path.is_file():
            errors.append(f"missing Python file: {rel}")
            continue
        text = path.read_text(encoding="utf-8")
        for match in FORBIDDEN_IMPORT_RE.finditer(text):
            errors.append(f"forbidden import in {rel}: {match.group(1)}")
        if rel.startswith("runtime/") and re.search(r"\bexec\s*\(|\beval\s*\(|subprocess\.(?:run|Popen|call)", text):
            errors.append(f"runtime ranking module must not execute processes: {rel}")


def validate_scripts(root: Path, errors: list[str]) -> None:
    commands = (
        [sys.executable, "scripts/run_ranking_shadow.py", "--input", "examples/search_quality/ranking/input_bundle_software_v0.json", "--check", "--json"],
        [sys.executable, "scripts/run_search_quality_regression.py", "--query-set", "examples/search_quality/query_sets/minimal_search_quality_query_set_v0.json", "--check", "--json"],
        [sys.executable, "scripts/summarize_ranking_shadow.py", "--input", "examples/search_quality/ranking", "--check", "--json"],
    )
    for command in commands:
        result = subprocess.run(command, cwd=root, capture_output=True, text=True, timeout=120, check=False)
        if result.returncode != 0:
            errors.append(f"script failed: {' '.join(command)} :: {result.stdout} {result.stderr}")
    forbidden = subprocess.run(
        [sys.executable, "scripts/run_ranking_shadow.py", "--input", "examples/search_quality/ranking/input_bundle_software_v0.json", "--output", "site/dist/ranking.json"],
        cwd=root,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    if forbidden.returncode == 0 or "refusing forbidden output root" not in forbidden.stdout:
        errors.append("ranking script must reject site/dist output")
    public = subprocess.run(
        [sys.executable, "scripts/run_search_quality_regression.py", "--query-set", "examples/search_quality/query_sets/minimal_search_quality_query_set_v0.json", "--output", "data/public_index/ranking.json"],
        cwd=root,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    if public.returncode == 0 or "refusing forbidden output root" not in public.stdout:
        errors.append("regression script must reject data/public_index output")


def validate_audit(root: Path, errors: list[str]) -> None:
    for rel in AUDIT_FILES:
        path = root / AUDIT_DIR / rel
        if not path.is_file():
            errors.append(f"missing audit file: {(AUDIT_DIR / rel).as_posix()}")
            continue
        if rel.endswith(".json"):
            payload = load_required_json(path, errors)
            errors.extend(f"{rel}: {error}" for error in detect_truth_or_product_violations(payload))


def validate_no_private_roots(root: Path, errors: list[str]) -> None:
    for rel in (".aide.local", ".local/eureka", ".cache/eureka"):
        if (root / rel).exists():
            errors.append(f"local private root must not exist: {rel}")


def load_required_json(path: Path, errors: list[str]) -> dict[str, Any]:
    if not path.is_file():
        errors.append(f"missing JSON: {rel(path)}")
        return {}
    try:
        return load_json(path)
    except Exception as exc:  # noqa: BLE001
        errors.append(f"invalid JSON: {rel(path)}: {exc}")
        return {}


def rel(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    result = validate_repo(REPO_ROOT)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print("Ranking shadow runtime validation", file=stdout)
        print(f"status: {result['status']}", file=stdout)
        for error in result["errors"]:
            print(f"ERROR: {error}", file=stdout)
    return 0 if result["status"] == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
