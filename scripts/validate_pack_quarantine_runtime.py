#!/usr/bin/env python3
"""Validate I-BUNDLE-01 pack quarantine runtime artifacts offline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any, Mapping, Sequence

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.extraction.guards import FORBIDDEN_IMPORT_RE  # noqa: E402
from runtime.local_foundry import (  # noqa: E402
    contribution_review,
    pack_fixity,
    pack_import_preview,
    pack_quarantine,
    pack_signature,
)


CONTRACTS = (
    "contracts/packs/pack_quarantine_request.v0.json",
    "contracts/packs/pack_quarantine_result.v0.json",
    "control/schemas/audits/packs/pack_fixity_report.v0.json",
    "contracts/packs/pack_signature_envelope.v0.json",
    "control/schemas/audits/packs/pack_signature_verification_report.v0.json",
    "control/schemas/previews/packs/pack_import_preview.v0.json",
    "contracts/packs/contribution_review_seed.v0.json",
    "control/schemas/previews/packs/pack_trust_revocation_preview.v0.json",
)
POLICIES = (
    "control/inventory/packs/pack_quarantine_policy.json",
    "control/inventory/packs/pack_quarantine_input_policy.json",
    "control/inventory/packs/pack_quarantine_output_policy.json",
    "control/inventory/packs/pack_quarantine_path_policy.json",
    "control/inventory/packs/pack_quarantine_truth_policy.json",
    "control/inventory/packs/pack_fixity_verification_policy.json",
    "control/inventory/packs/pack_signature_verification_policy.json",
    "control/inventory/packs/pack_import_preview_policy.json",
    "control/inventory/packs/contribution_review_seed_policy.json",
    "control/inventory/packs/pack_trust_revocation_policy.json",
)
EXAMPLES = (
    "examples/pack_quarantine/minimal_quarantine_request_v0.json",
    "examples/pack_quarantine/evidence_pack_quarantine_request_v0.json",
    "examples/pack_quarantine/source_pack_quarantine_request_v0.json",
    "examples/pack_quarantine/contribution_pack_quarantine_request_v0.json",
    "examples/pack_quarantine/policy_blocked_quarantine_request_v0.json",
    "examples/pack_quarantine/results/minimal_quarantine_result_v0.json",
    "examples/pack_quarantine/results/evidence_pack_quarantine_result_v0.json",
    "examples/pack_quarantine/results/source_pack_quarantine_result_v0.json",
    "examples/pack_quarantine/results/contribution_pack_quarantine_result_v0.json",
    "examples/pack_quarantine/results/policy_blocked_quarantine_result_v0.json",
    "examples/pack_quarantine/fixity/pack_fixity_report_v0.json",
    "examples/pack_quarantine/signatures/unsigned_pack_signature_envelope_v0.json",
    "examples/pack_quarantine/signatures/placeholder_signature_envelope_v0.json",
    "examples/pack_quarantine/signatures/malformed_signature_envelope_v0.json",
    "examples/pack_quarantine/signatures/signature_verification_report_v0.json",
    "examples/pack_quarantine/import_preview/evidence_pack_import_preview_v0.json",
    "examples/pack_quarantine/import_preview/source_pack_import_preview_v0.json",
    "examples/pack_quarantine/import_preview/contribution_pack_import_preview_v0.json",
    "examples/pack_quarantine/import_preview/policy_blocked_pack_import_preview_v0.json",
    "examples/pack_quarantine/review_seeds/contribution_review_seed_v0.json",
    "examples/pack_quarantine/review_seeds/pack_requires_more_evidence_review_seed_v0.json",
    "examples/pack_quarantine/review_seeds/pack_policy_blocked_review_seed_v0.json",
    "examples/pack_quarantine/trust/pack_trust_preview_v0.json",
    "examples/pack_quarantine/trust/pack_revocation_preview_v0.json",
)
PYTHON_FILES = (
    "runtime/local_foundry/pack_quarantine.py",
    "runtime/local_foundry/pack_fixity.py",
    "runtime/local_foundry/pack_signature.py",
    "runtime/local_foundry/pack_import_preview.py",
    "runtime/local_foundry/contribution_review.py",
    "scripts/quarantine_local_pack.py",
    "scripts/verify_local_pack_fixity.py",
    "scripts/preview_pack_import.py",
    "scripts/validate_pack_quarantine_runtime.py",
    "scripts/summarize_pack_quarantine.py",
)
DOCS = (
    "docs/reference/PACK_QUARANTINE_RUNTIME.md",
    "docs/reference/PACK_FIXITY_REPORT_CONTRACT.md",
    "docs/reference/PACK_SIGNATURE_ENVELOPE_CONTRACT.md",
    "docs/reference/PACK_IMPORT_PREVIEW_CONTRACT.md",
    "docs/reference/CONTRIBUTION_REVIEW_SEED_CONTRACT.md",
    "docs/architecture/PACK_QUARANTINE_MODEL.md",
    "docs/architecture/PACK_TRUST_MODEL.md",
    "docs/operations/PACK_QUARANTINE_REVIEW.md",
    "docs/operations/PACK_SIGNATURE_AND_FIXITY_POLICY.md",
    "docs/operations/CONTRIBUTION_REVIEW_POLICY.md",
    "docs/operations/PACK_IMPORT_PREVIEW_NO_IMPORT_POLICY.md",
)
AUDIT_DIR = Path("control/audits/i-bundle-01-pack-quarantine-contribution-review-v0")
AUDIT_FILES = (
    "README.md",
    "i_bundle_01_report.json",
    "pack_quarantine_summary.md",
    "pack_fixity_verification_report.md",
    "pack_signature_verification_report.md",
    "pack_import_preview_report.md",
    "contribution_review_seed_report.md",
    "pack_trust_revocation_preview.md",
    "pack_import_no_mutation_report.md",
    "j0_readiness_recommendation.md",
    "validation.md",
    "generated/sample_pack_quarantine_result.json",
    "generated/sample_pack_fixity_report.json",
    "generated/sample_pack_signature_verification_report.json",
    "generated/sample_pack_import_preview.json",
    "generated/sample_contribution_review_seed.json",
    "generated/sample_pack_quarantine_summary.md",
)


def validate_repo(root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    for rel in CONTRACTS + POLICIES + EXAMPLES:
        payload = load_required_json(root / rel, errors)
        if payload:
            validate_payload_semantics(rel, payload, errors)
    validate_policy_values(root, errors)
    validate_required_files(root, DOCS + tuple((AUDIT_DIR / item).as_posix() for item in AUDIT_FILES), errors)
    validate_audit_report(root, errors)
    validate_imports(root, errors)
    validate_scripts(root, errors)
    validate_no_private_roots(root, errors)
    return {
        "schema_version": "pack_quarantine_runtime_validation.v0",
        "task": "I-BUNDLE-01",
        "status": "valid" if not errors else "invalid",
        "offline_default": True,
        "pack_import_enabled": False,
        "real_signing_enabled": False,
        "errors": sorted(dict.fromkeys(errors)),
    }


def validate_payload_semantics(rel: str, payload: Mapping[str, Any], errors: list[str]) -> None:
    schema = payload.get("schema_version")
    if schema == pack_quarantine.RESULT_SCHEMA_VERSION:
        errors.extend(f"{rel}: {error}" for error in pack_quarantine.validate_pack_quarantine_result(payload))
    elif schema == pack_fixity.SCHEMA_VERSION:
        errors.extend(f"{rel}: {error}" for error in pack_fixity.validate_pack_fixity_report(payload))
    elif schema == pack_signature.ENVELOPE_SCHEMA_VERSION:
        errors.extend(f"{rel}: {error}" for error in pack_signature.validate_signature_envelope(payload))
    elif schema == pack_signature.REPORT_SCHEMA_VERSION:
        errors.extend(f"{rel}: {error}" for error in pack_signature.validate_signature_verification_report(payload))
    elif schema == pack_import_preview.SCHEMA_VERSION:
        errors.extend(f"{rel}: {error}" for error in pack_import_preview.validate_pack_import_preview(payload))
    elif schema == contribution_review.REVIEW_SEED_SCHEMA_VERSION:
        errors.extend(f"{rel}: {error}" for error in contribution_review.validate_contribution_review_seed(payload))
    elif schema == contribution_review.TRUST_PREVIEW_SCHEMA_VERSION:
        errors.extend(f"{rel}: {error}" for error in contribution_review.validate_pack_trust_preview(payload))
    errors.extend(f"{rel}: {error}" for error in pack_quarantine.detect_pack_quarantine_truth_boundary_violations(payload))
    text = json.dumps(payload, sort_keys=True).casefold()
    if "-----begin" in text:
        errors.append(f"{rel}: private key block is forbidden")
    if '"private_key_used": true' in text or '"real_signature_created": true' in text:
        errors.append(f"{rel}: private key or real signature use must remain false")
    for forbidden in ("accepted pack claim", "pack import completed"):
        if forbidden in text:
            errors.append(f"{rel}: forbidden text present: {forbidden}")


def validate_policy_values(root: Path, errors: list[str]) -> None:
    quarantine = load_required_json(root / "control/inventory/packs/pack_quarantine_policy.json", errors)
    for key in ("import_enabled", "submission_enabled", "publication_enabled", "acceptance_enabled", "hosted_upload_enabled"):
        if quarantine.get(key) is not False:
            errors.append(f"pack_quarantine_policy.{key} must be false")
    signature = load_required_json(root / "control/inventory/packs/pack_signature_verification_policy.json", errors)
    for key in ("private_keys_allowed", "real_signing_allowed", "real_signature_verification_current"):
        if signature.get(key) is not False:
            errors.append(f"pack_signature_verification_policy.{key} must be false")
    truth = load_required_json(root / "control/inventory/packs/pack_quarantine_truth_policy.json", errors)
    for key, value in truth.items():
        if key == "schema_version":
            continue
        if value is not False:
            errors.append(f"pack_quarantine_truth_policy.{key} must be false")
    path_policy = load_required_json(root / "control/inventory/packs/pack_quarantine_path_policy.json", errors)
    for forbidden in ("site/dist/", "data/public_index/", "runtime/", "contracts/"):
        if forbidden not in path_policy.get("forbidden_output_roots", []):
            errors.append(f"pack_quarantine_path_policy must forbid {forbidden}")


def validate_audit_report(root: Path, errors: list[str]) -> None:
    report = load_required_json(root / AUDIT_DIR / "i_bundle_01_report.json", errors)
    if not report:
        return
    scope = report.get("quarantine_scope", {})
    for key in ("quarantine_only", "fixity_verification_enabled", "signature_envelope_validation_enabled", "import_preview_enabled"):
        if scope.get(key) is not True:
            errors.append(f"audit report quarantine_scope.{key} must be true")
    for key in ("real_signing_enabled", "private_keys_allowed", "pack_import_enabled", "pack_submission_enabled", "hosted_upload_enabled", "pack_acceptance_enabled"):
        if scope.get(key) is not False:
            errors.append(f"audit report quarantine_scope.{key} must be false")
    validate_payload_semantics("audit report", report, errors)


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
            errors.append(f"runtime pack quarantine module must not execute processes: {rel}")


def validate_scripts(root: Path, errors: list[str]) -> None:
    commands = (
        [sys.executable, "scripts/quarantine_local_pack.py", "--input", "examples/pack_exports/evidence_pack_export_v0.json", "--check", "--json"],
        [sys.executable, "scripts/verify_local_pack_fixity.py", "--input", "examples/pack_exports/evidence_pack_export_v0.json", "--check", "--json"],
        [sys.executable, "scripts/preview_pack_import.py", "--input", "examples/pack_quarantine/results/evidence_pack_quarantine_result_v0.json", "--check", "--json"],
        [sys.executable, "scripts/summarize_pack_quarantine.py", "--input", "examples/pack_quarantine/results", "--check", "--json"],
    )
    for command in commands:
        result = subprocess.run(command, cwd=root, capture_output=True, text=True, timeout=120, check=False)
        if result.returncode != 0:
            errors.append(f"script failed: {' '.join(command)} :: {result.stdout} {result.stderr}")
    for output in ("site/dist/quarantine.json", "data/public_index/quarantine.json", "runtime/quarantine.json"):
        result = subprocess.run(
            [sys.executable, "scripts/quarantine_local_pack.py", "--input", "examples/pack_exports/evidence_pack_export_v0.json", "--output", output],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=120,
            check=False,
        )
        combined = result.stdout + result.stderr
        if result.returncode == 0 or "refusing forbidden output root" not in combined:
            errors.append(f"quarantine script must reject forbidden output: {output}")


def validate_required_files(root: Path, paths: Sequence[str], errors: list[str]) -> None:
    for rel in paths:
        if not (root / rel).is_file():
            errors.append(f"missing required file: {rel}")


def validate_no_private_roots(root: Path, errors: list[str]) -> None:
    for rel in (".aide.local", ".local/eureka", ".cache/eureka"):
        if (root / rel).exists():
            errors.append(f"local private root must not exist: {rel}")


def load_required_json(path: Path, errors: list[str]) -> dict[str, Any]:
    if not path.is_file():
        errors.append(f"missing JSON: {rel(path)}")
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"invalid JSON: {rel(path)}: {exc}")
        return {}
    if not isinstance(payload, dict):
        errors.append(f"JSON must be an object: {rel(path)}")
        return {}
    return payload


def rel(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    result = validate_repo(REPO_ROOT)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True))
    else:
        print("Pack quarantine runtime validation")
        print(f"status: {result['status']}")
        for error in result["errors"]:
            print(f"ERROR: {error}")
    return 0 if result["status"] == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
