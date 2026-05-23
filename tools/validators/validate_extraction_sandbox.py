#!/usr/bin/env python3
"""Validate F-BUNDLE-01 fixture extraction sandbox artifacts offline."""

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


AUDIT_DIR = Path("control/audits/f-bundle-01-extraction-sandbox-tier0-2-v0")
CONTRACTS = (
    "contracts/extraction/extraction_sandbox.v0.json",
    "contracts/extraction/extraction_target.v0.json",
    "contracts/extraction/extraction_policy.v0.json",
    "contracts/extraction/extraction_result.v0.json",
    "contracts/extraction/extraction_member.v0.json",
    "contracts/schema/control/previews/extraction/extraction_manifest_candidate.v0.json",
    "contracts/schema/control/previews/extraction/extraction_candidate_effect.v0.json",
    "contracts/schema/control/audits/extraction/extraction_safety_report.v0.json",
)
POLICIES = (
    "control/inventory/extraction/extraction_sandbox_policy.json",
    "control/inventory/extraction/extraction_resource_limit_policy.json",
    "control/inventory/extraction/extraction_container_type_policy.json",
    "control/inventory/extraction/extraction_path_safety_policy.json",
    "control/inventory/extraction/extraction_archive_bomb_policy.json",
    "control/inventory/extraction/extraction_tier_policy.json",
    "control/inventory/extraction/extraction_output_policy.json",
    "control/inventory/extraction/extraction_truth_policy.json",
    "control/inventory/extraction/extraction_review_policy.json",
)
FIXTURES = ("zip_basic", "zip_manifest", "tar_basic", "path_traversal_blocked", "archive_bomb_blocked")
TARGETS = tuple(f"examples/extraction/targets/{name}_target_v0.json" for name in FIXTURES)
RESULTS = (
    "examples/extraction/results/zip_basic_tier0_result_v0.json",
    "examples/extraction/results/zip_basic_tier1_result_v0.json",
    "examples/extraction/results/zip_manifest_tier2_result_v0.json",
    "examples/extraction/results/tar_basic_tier1_result_v0.json",
    "examples/extraction/results/path_traversal_blocked_result_v0.json",
    "examples/extraction/results/archive_bomb_blocked_result_v0.json",
)
CANDIDATE_EFFECTS = (
    "examples/extraction/candidate_effects/zip_manifest_candidate_effect_v0.json",
    "examples/extraction/candidate_effects/member_listing_candidate_effect_v0.json",
    "examples/extraction/candidate_effects/policy_blocked_candidate_effect_v0.json",
)
RUNTIME_AND_SCRIPTS = (
    "runtime/extraction/sandbox.py",
    "runtime/extraction/container_detect.py",
    "runtime/extraction/tier0_outer_metadata.py",
    "runtime/extraction/tier1_member_listing.py",
    "runtime/extraction/tier2_manifest_extract.py",
    "runtime/extraction/guards.py",
    "runtime/extraction/candidate_effects.py",
    "runtime/extraction/summaries.py",
    "scripts/run_fixture_extraction.py",
    "scripts/summarize_extraction_results.py",
    "scripts/validate_extraction_sandbox.py",
)
AUDIT_FILES = (
    "README.md",
    "f_bundle_01_report.json",
    "extraction_sandbox_summary.md",
    "extraction_fixture_summary.md",
    "tier0_outer_metadata_report.md",
    "tier1_member_listing_report.md",
    "tier2_manifest_extraction_report.md",
    "extraction_safety_report.md",
    "candidate_effects_preview.md",
    "f_bundle_02_readiness.md",
    "validation.md",
    "generated/sample_tier0_result.json",
    "generated/sample_tier1_result.json",
    "generated/sample_tier2_result.json",
    "generated/sample_candidate_effect.json",
    "generated/sample_extraction_summary.md",
)


def validate_repo(root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    for rel in CONTRACTS + POLICIES:
        load_required_json(root / rel, errors)
    validate_policy_values(root, errors)
    validate_fixtures(root, errors)
    validate_outputs(root, errors)
    validate_audit(root, errors)
    validate_imports(root, errors)
    validate_scripts(root, errors)
    validate_no_private_roots(root, errors)
    return {
        "schema_version": "extraction_sandbox_validation.v0",
        "task": "F-BUNDLE-01",
        "status": "valid" if not errors else "invalid",
        "offline_default": True,
        "errors": errors,
    }


def validate_policy_values(root: Path, errors: list[str]) -> None:
    sandbox = load_required_json(root / "control/inventory/extraction/extraction_sandbox_policy.json", errors)
    required_false = (
        "private_file_access_allowed",
        "arbitrary_path_access_allowed",
        "network_allowed",
        "execution_allowed",
        "installer_execution_allowed",
        "live_source_access_allowed",
    )
    for key in required_false:
        if sandbox.get(key) is not False:
            errors.append(f"extraction sandbox policy {key} must be false")
    truth = load_required_json(root / "control/inventory/extraction/extraction_truth_policy.json", errors)
    for key, value in truth.items():
        if key.endswith("_is_truth") or key.endswith("_is_accepted_evidence") or key.endswith("_is_accepted_candidate") or key.endswith("_mutate_public_index") or key.endswith("_mutate_master_index"):
            if value is not False:
                errors.append(f"truth policy {key} must be false")


def validate_fixtures(root: Path, errors: list[str]) -> None:
    for name in FIXTURES:
        fixture_root = root / "examples" / "extraction" / "fixtures" / name
        for file_name in ("build_fixture.py", "README.md"):
            if not (fixture_root / file_name).is_file():
                errors.append(f"missing fixture file: {fixture_root / file_name}")
    for rel in TARGETS:
        load_required_json(root / rel, errors)


def validate_outputs(root: Path, errors: list[str]) -> None:
    for rel in RESULTS + CANDIDATE_EFFECTS:
        payload = load_required_json(root / rel, errors)
        errors.extend(f"{rel}: {error}" for error in detect_truth_or_product_violations(payload))
    blocked_path = load_required_json(root / "examples/extraction/results/path_traversal_blocked_result_v0.json", errors)
    if blocked_path.get("extraction_status") != "blocked_path_traversal":
        errors.append("path traversal result must be blocked_path_traversal")
    bomb = load_required_json(root / "examples/extraction/results/archive_bomb_blocked_result_v0.json", errors)
    if bomb.get("extraction_status") != "blocked_archive_bomb_risk":
        errors.append("archive bomb result must be blocked_archive_bomb_risk")


def validate_audit(root: Path, errors: list[str]) -> None:
    for rel in AUDIT_FILES:
        path = root / AUDIT_DIR / rel
        if not path.is_file():
            errors.append(f"missing audit file: {(AUDIT_DIR / rel).as_posix()}")
            continue
        if rel.endswith(".json"):
            payload = load_required_json(path, errors)
            errors.extend(f"{rel}: {error}" for error in detect_truth_or_product_violations(payload))


def validate_imports(root: Path, errors: list[str]) -> None:
    for rel in RUNTIME_AND_SCRIPTS:
        path = root / rel
        if not path.is_file():
            errors.append(f"missing Python file: {rel}")
            continue
        text = path.read_text(encoding="utf-8")
        for match in FORBIDDEN_IMPORT_RE.finditer(text):
            errors.append(f"forbidden import in {rel}: {match.group(1)}")
        if re.search(r"\bexec\s*\(|\beval\s*\(|subprocess\.(?:run|Popen|call)", text) and rel.startswith("runtime/"):
            errors.append(f"runtime extraction module must not execute processes: {rel}")


def validate_scripts(root: Path, errors: list[str]) -> None:
    commands = (
        [sys.executable, "scripts/run_fixture_extraction.py", "--target", "examples/extraction/targets/zip_manifest_target_v0.json", "--tiers", "0,1,2", "--check", "--json"],
        [sys.executable, "scripts/run_fixture_extraction.py", "--target", "examples/extraction/targets/path_traversal_blocked_target_v0.json", "--tiers", "0,1", "--check", "--json"],
        [sys.executable, "scripts/run_fixture_extraction.py", "--target", "examples/extraction/targets/archive_bomb_blocked_target_v0.json", "--tiers", "0,1", "--check", "--json"],
        [sys.executable, "scripts/summarize_extraction_results.py", "--input", "examples/extraction/results", "--check", "--json"],
    )
    for command in commands:
        result = subprocess.run(command, cwd=root, capture_output=True, text=True, timeout=120, check=False)
        if result.returncode != 0:
            errors.append(f"script failed: {' '.join(command)} :: {result.stdout} {result.stderr}")
    forbidden_output = subprocess.run(
        [sys.executable, "scripts/run_fixture_extraction.py", "--target", "examples/extraction/targets/zip_manifest_target_v0.json", "--output", "site/dist/extraction.json"],
        cwd=root,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    if forbidden_output.returncode == 0 or "refusing forbidden output root" not in forbidden_output.stdout:
        errors.append("runner must reject site/dist output")
    forbidden_public = subprocess.run(
        [sys.executable, "scripts/summarize_extraction_results.py", "--input", "examples/extraction/results", "--output", "site/dist/data/public_index/extraction.json"],
        cwd=root,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    if forbidden_public.returncode == 0 or "refusing forbidden output root" not in forbidden_public.stdout:
        errors.append("summary script must reject site/dist/data/public_index output")
    private = subprocess.run(
        [sys.executable, "scripts/run_fixture_extraction.py", "--fixture", "C:/Users/private/archive.zip", "--check"],
        cwd=root,
        capture_output=True,
        text=True,
        timeout=120,
        check=False,
    )
    if private.returncode == 0:
        errors.append("runner must reject private-looking input paths")


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
        print("Extraction sandbox validation", file=stdout)
        print(f"status: {result['status']}", file=stdout)
        for error in result["errors"]:
            print(f"ERROR: {error}", file=stdout)
    return 0 if result["status"] == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
