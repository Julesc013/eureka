#!/usr/bin/env python3
"""Validate G-BUNDLE-01 search explanation runtime artifacts offline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any, Mapping, Sequence, TextIO


REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.extraction.guards import FORBIDDEN_IMPORT_RE, detect_truth_or_product_violations, load_json  # noqa: E402


CONTRACTS = (
    "contracts/query/search_result_explanation.v0.json",
    "contracts/query/near_miss_explanation.v0.json",
    "contracts/query/known_absence_record.v0.json",
    "contracts/query/search_gap_explanation.v0.json",
    "contracts/query/explanation_input_bundle.v0.json",
    "contracts/control_schemas/previews/query/explanation_output_bundle.v0.json",
)
POLICIES = (
    "control/inventory/search_quality/search_explanation_policy.json",
    "control/inventory/search_quality/near_miss_policy.json",
    "control/inventory/search_quality/known_absence_policy.json",
    "control/inventory/search_quality/search_gap_explanation_policy.json",
    "control/inventory/search_quality/explanation_output_policy.json",
    "control/inventory/search_quality/explanation_path_policy.json",
    "control/inventory/search_quality/explanation_truth_policy.json",
    "control/inventory/search_quality/explanation_review_policy.json",
)
EXAMPLES = (
    "examples/search_quality/explanations/exact_candidate_explanation_v0.json",
    "examples/search_quality/explanations/source_cache_supported_explanation_v0.json",
    "examples/search_quality/explanations/evidence_supported_explanation_v0.json",
    "examples/search_quality/explanations/extraction_member_explanation_v0.json",
    "examples/search_quality/explanations/policy_blocked_explanation_v0.json",
    "examples/search_quality/near_misses/wrong_version_near_miss_v0.json",
    "examples/search_quality/near_misses/wrong_platform_near_miss_v0.json",
    "examples/search_quality/near_misses/source_only_near_miss_v0.json",
    "examples/search_quality/near_misses/extraction_gap_near_miss_v0.json",
    "examples/search_quality/known_absence/no_reviewed_result_absence_v0.json",
    "examples/search_quality/known_absence/source_gap_absence_v0.json",
    "examples/search_quality/known_absence/extraction_needed_absence_v0.json",
    "examples/search_quality/known_absence/policy_blocked_absence_v0.json",
    "examples/search_quality/input_bundles/software_search_explanation_bundle_v0.json",
    "examples/search_quality/input_bundles/extraction_gap_explanation_bundle_v0.json",
    "examples/search_quality/output_bundles/software_search_explanation_output_v0.json",
    "examples/search_quality/output_bundles/known_absence_output_v0.json",
)
PYTHON_FILES = (
    "runtime/search_quality/__init__.py",
    "runtime/search_quality/explanation.py",
    "runtime/search_quality/near_miss.py",
    "runtime/search_quality/known_absence.py",
    "runtime/search_quality/gap_explanation.py",
    "runtime/search_quality/explanation_summary.py",
    "scripts/explain_search_fixture.py",
    "scripts/summarize_search_explanations.py",
    "scripts/validate_search_explanation_runtime.py",
)
AUDIT_DIR = Path("control/audits/g-bundle-01-result-explanations-absence-v0")
AUDIT_FILES = (
    "README.md",
    "g_bundle_01_report.json",
    "search_explanation_runtime_summary.md",
    "near_miss_explanation_report.md",
    "known_absence_report.md",
    "extraction_gap_explanation_report.md",
    "explanation_no_ranking_change_report.md",
    "g_bundle_02_readiness.md",
    "validation.md",
    "generated/sample_search_result_explanation.json",
    "generated/sample_near_miss_explanation.json",
    "generated/sample_known_absence_record.json",
    "generated/sample_explanation_output_bundle.json",
    "generated/sample_explanation_summary.md",
)


def validate_repo(root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    for rel in CONTRACTS + POLICIES + EXAMPLES:
        payload = load_required_json(root / rel, errors)
        if payload:
            errors.extend(f"{rel}: {error}" for error in detect_truth_or_product_violations(payload))
            validate_artifact_semantics(rel, payload, errors)
    validate_policy_values(root, errors)
    validate_imports(root, errors)
    validate_scripts(root, errors)
    validate_audit(root, errors)
    validate_no_private_roots(root, errors)
    return {
        "schema_version": "search_explanation_runtime_validation.v0",
        "task": "G-BUNDLE-01",
        "status": "valid" if not errors else "invalid",
        "offline_default": True,
        "errors": errors,
    }


def validate_policy_values(root: Path, errors: list[str]) -> None:
    explanation = load_required_json(root / "control/inventory/search_quality/search_explanation_policy.json", errors)
    for key in (
        "public_ranking_mutation_allowed",
        "public_search_mutation_allowed",
        "accepted_truth_creation_allowed",
        "source_acceptance_allowed",
        "evidence_acceptance_allowed",
        "candidate_acceptance_allowed",
    ):
        if explanation.get(key) is not False:
            errors.append(f"search explanation policy {key} must be false")
    absence = load_required_json(root / "control/inventory/search_quality/known_absence_policy.json", errors)
    if absence.get("global_absence_claim_allowed") is not False:
        errors.append("known absence global absence claims must be disabled")
    if absence.get("exhaustive_web_search_claim_allowed") is not False:
        errors.append("known absence exhaustive web claims must be disabled")
    truth = load_required_json(root / "control/inventory/search_quality/explanation_truth_policy.json", errors)
    for key, value in truth.items():
        if key in {"schema_version", "policy_id"}:
            continue
        if value is not False:
            errors.append(f"explanation truth policy {key} must be false")


def validate_artifact_semantics(rel: str, payload: Mapping[str, Any], errors: list[str]) -> None:
    schema = payload.get("schema_version")
    if schema == "known_absence_record.v0":
        no_claims = payload.get("no_claims", {})
        if no_claims.get("global_absence_claimed") is not False:
            errors.append(f"{rel}: known absence must not claim global absence")
        if no_claims.get("exhaustive_web_search_claimed") is not False:
            errors.append(f"{rel}: known absence must not claim exhaustive web search")
    if schema == "near_miss_explanation.v0":
        if payload.get("suggested_workunit_seed_future", {}).get("created") is not False:
            errors.append(f"{rel}: near miss must not execute or create WorkUnit")
    if schema in {"search_result_explanation.v0", "explanation_output_bundle.v0"}:
        truth = payload.get("truth_boundary", {})
        for key in ("explanation_mutates_ranking", "explanation_mutates_public_search", "explanation_accepts_evidence", "explanation_accepts_candidate"):
            if truth.get(key) is not False:
                errors.append(f"{rel}: {key} must be false")


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
            errors.append(f"runtime search-quality module must not execute processes: {rel}")


def validate_scripts(root: Path, errors: list[str]) -> None:
    commands = (
        [sys.executable, "scripts/explain_search_fixture.py", "--input", "examples/search_quality/input_bundles/software_search_explanation_bundle_v0.json", "--check", "--json"],
        [sys.executable, "scripts/summarize_search_explanations.py", "--input", "examples/search_quality", "--check", "--json"],
    )
    for command in commands:
        result = subprocess.run(command, cwd=root, capture_output=True, text=True, timeout=120, check=False)
        if result.returncode != 0:
            errors.append(f"script failed: {' '.join(command)} :: {result.stdout} {result.stderr}")
    forbidden = subprocess.run(
        [sys.executable, "scripts/explain_search_fixture.py", "--input", "examples/search_quality/input_bundles/software_search_explanation_bundle_v0.json", "--output", "site/dist/explanation.json"],
        cwd=root,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    if forbidden.returncode == 0 or "refusing forbidden output root" not in forbidden.stdout:
        errors.append("explanation script must reject site/dist output")
    public = subprocess.run(
        [sys.executable, "scripts/summarize_search_explanations.py", "--input", "examples/search_quality", "--output", "site/dist/data/public_index/explanation.json"],
        cwd=root,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    if public.returncode == 0 or "refusing forbidden output root" not in public.stdout:
        errors.append("summary script must reject site/dist/data/public_index output")


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
        print("Search explanation runtime validation", file=stdout)
        print(f"status: {result['status']}", file=stdout)
        for error in result["errors"]:
            print(f"ERROR: {error}", file=stdout)
    return 0 if result["status"] == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
