#!/usr/bin/env python3
"""Validate F-BUNDLE-02 extraction search integration artifacts offline."""

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
    "contracts/extraction/extraction_search_integration.v0.json",
    "contracts/extraction/extraction_search_gap.v0.json",
    "contracts/extraction/extraction_review_seed.v0.json",
    "contracts/extraction/extraction_workunit_seed.v0.json",
    "contracts/control_schemas/audits/extraction/extraction_usefulness_report.v0.json",
)
POLICIES = (
    "control/inventory/extraction/extraction_search_integration_policy.json",
    "control/inventory/extraction/extraction_search_gap_policy.json",
    "control/inventory/extraction/extraction_review_seed_policy.json",
    "control/inventory/extraction/extraction_workunit_seed_policy.json",
    "control/inventory/extraction/extraction_candidate_effect_policy.json",
    "control/inventory/extraction/extraction_search_output_policy.json",
    "control/inventory/extraction/extraction_search_truth_policy.json",
    "control/inventory/extraction/extraction_to_track_g_handoff_policy.json",
)
EXAMPLES = (
    "examples/extraction/search_integration/manifest_member_search_gap_v0.json",
    "examples/extraction/search_integration/hidden_driver_member_search_gap_v0.json",
    "examples/extraction/search_integration/article_inside_scan_gap_future_v0.json",
    "examples/extraction/search_integration/policy_blocked_search_gap_v0.json",
    "examples/extraction/review_seeds/member_candidate_review_seed_v0.json",
    "examples/extraction/review_seeds/manifest_candidate_review_seed_v0.json",
    "examples/extraction/review_seeds/source_locator_review_seed_v0.json",
    "examples/extraction/review_seeds/policy_blocked_review_seed_v0.json",
    "examples/extraction/workunit_seeds/deepen_container_workunit_seed_v0.json",
    "examples/extraction/workunit_seeds/verify_manifest_workunit_seed_v0.json",
    "examples/extraction/workunit_seeds/check_member_relevance_workunit_seed_v0.json",
    "examples/extraction/workunit_seeds/policy_blocked_workunit_seed_v0.json",
    "examples/extraction/usefulness/extraction_usefulness_report_v0.json",
    "examples/extraction/usefulness/extraction_quality_delta_preview_v0.json",
    "examples/extraction/usefulness/extraction_to_track_g_handoff_v0.json",
)
PYTHON_FILES = (
    "runtime/extraction/search_integration.py",
    "runtime/extraction/review_bridge.py",
    "runtime/extraction/workunit_seeds.py",
    "runtime/extraction/usefulness.py",
    "scripts/integrate_extraction_candidates.py",
    "scripts/summarize_extraction_search_gaps.py",
    "scripts/validate_extraction_search_integration.py",
)
AUDIT_DIR = Path("control/audits/f-bundle-02-extraction-candidate-search-integration-v0")
AUDIT_FILES = (
    "README.md",
    "f_bundle_02_report.json",
    "extraction_search_integration_report.md",
    "extraction_search_gap_report.md",
    "extraction_review_seed_report.md",
    "extraction_workunit_seed_report.md",
    "extraction_usefulness_report.md",
    "extraction_safety_quality_audit.md",
    "track_g_readiness_recommendation.md",
    "validation.md",
    "generated/sample_extraction_search_integration.json",
    "generated/sample_extraction_search_gap.json",
    "generated/sample_extraction_review_seed.json",
    "generated/sample_extraction_workunit_seed.json",
    "generated/sample_extraction_usefulness_report.json",
    "generated/sample_extraction_summary.md",
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
        "schema_version": "extraction_search_integration_validation.v0",
        "task": "F-BUNDLE-02",
        "status": "valid" if not errors else "invalid",
        "offline_default": True,
        "errors": errors,
    }


def validate_policy_values(root: Path, errors: list[str]) -> None:
    policy = load_required_json(root / "control/inventory/extraction/extraction_search_integration_policy.json", errors)
    for key in (
        "public_search_mutation_allowed",
        "public_index_mutation_allowed",
        "master_index_mutation_allowed",
        "candidate_store_mutation_allowed",
        "evidence_ledger_mutation_allowed",
        "review_queue_mutation_allowed",
    ):
        if policy.get(key) is not False:
            errors.append(f"search integration policy {key} must be false")
    truth = load_required_json(root / "control/inventory/extraction/extraction_search_truth_policy.json", errors)
    for key, value in truth.items():
        if key in {"schema_version", "policy_id"}:
            continue
        if value is not False:
            errors.append(f"search truth policy {key} must be false")


def validate_artifact_semantics(rel: str, payload: Mapping[str, Any], errors: list[str]) -> None:
    if payload.get("schema_version") == "extraction_review_seed.v0":
        if payload.get("truth_boundary", {}).get("review_seed_is_review_decision") is not False:
            errors.append(f"{rel}: review seed must not be a review decision")
    if payload.get("schema_version") == "extraction_workunit_seed.v0":
        if payload.get("workunit_seed_executes_work") is not False:
            errors.append(f"{rel}: workunit seed must not execute work")
    if payload.get("schema_version") == "extraction_usefulness_report.v0":
        if payload.get("truth_boundary", {}).get("production_quality_claimed") is not False:
            errors.append(f"{rel}: usefulness report must not claim production quality")


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
            errors.append(f"runtime extraction integration module must not execute processes: {rel}")


def validate_scripts(root: Path, errors: list[str]) -> None:
    commands = (
        [sys.executable, "scripts/integrate_extraction_candidates.py", "--input", "examples/extraction/results", "--check", "--json"],
        [sys.executable, "scripts/summarize_extraction_search_gaps.py", "--input", "examples/extraction/search_integration", "--check", "--json"],
    )
    for command in commands:
        result = subprocess.run(command, cwd=root, capture_output=True, text=True, timeout=120, check=False)
        if result.returncode != 0:
            errors.append(f"script failed: {' '.join(command)} :: {result.stdout} {result.stderr}")
    forbidden = subprocess.run(
        [sys.executable, "scripts/integrate_extraction_candidates.py", "--input", "examples/extraction/results", "--output", "site/dist/extraction.json"],
        cwd=root,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    if forbidden.returncode == 0 or "refusing forbidden output root" not in forbidden.stdout:
        errors.append("integration script must reject site/dist output")
    public = subprocess.run(
        [sys.executable, "scripts/summarize_extraction_search_gaps.py", "--input", "examples/extraction/search_integration", "--output", "site/dist/data/public_index/extraction.json"],
        cwd=root,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    if public.returncode == 0 or "refusing forbidden output root" not in public.stdout:
        errors.append("search gap summary script must reject site/dist/data/public_index output")


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
        print("Extraction search integration validation", file=stdout)
        print(f"status: {result['status']}", file=stdout)
        for error in result["errors"]:
            print(f"ERROR: {error}", file=stdout)
    return 0 if result["status"] == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
