#!/usr/bin/env python3
"""Validate the local pack export runtime artifacts."""

from __future__ import annotations

import ast
import json
from pathlib import Path
import subprocess
import sys
from typing import Any

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local.foundry import pack_export


POLICY_FILES = [
    "control/inventory/packs/pack_export_runtime_policy.json",
    "control/inventory/packs/pack_export_input_policy.json",
    "control/inventory/packs/pack_export_output_policy.json",
    "control/inventory/packs/pack_export_format_policy.json",
    "control/inventory/packs/pack_export_path_policy.json",
    "control/inventory/packs/pack_export_review_policy.json",
    "control/inventory/packs/pack_export_truth_policy.json",
    "control/inventory/packs/pack_export_fixity_policy.json",
]

PACK_EXPORT_EXAMPLES = [
    "examples/packs/exports/source_pack_export_v0.json",
    "examples/packs/exports/evidence_pack_export_v0.json",
    "examples/packs/exports/contribution_pack_export_v0.json",
    "examples/packs/exports/review_pack_export_v0.json",
    "examples/packs/exports/index_pack_preview_export_v0.json",
    "examples/packs/exports/policy_blocked_pack_export_v0.json",
]

DOC_FILES = [
    "docs/reference/PACK_EXPORT_RUNTIME.md",
    "docs/architecture/PACK_EXPORT_MODEL.md",
    "docs/operations/PACK_EXPORT_REVIEW.md",
]

AUDIT_FILES = [
    "control/audits/track-b-22-pack-export-runtime-v0/README.md",
    "control/audits/track-b-22-pack-export-runtime-v0/track_b_22_report.json",
    "control/audits/track-b-22-pack-export-runtime-v0/validation.md",
    "control/audits/track-b-22-pack-export-runtime-v0/generated/sample_pack_export.json",
    "control/audits/track-b-22-pack-export-runtime-v0/generated/sample_pack_export_report.json",
    "control/audits/track-b-22-pack-export-runtime-v0/generated/sample_pack_export_summary.md",
]

BANNED_IMPORTS = {
    "requests",
    "urllib",
    "http",
    "socket",
    "ftplib",
    "smtplib",
    "webbrowser",
    "selenium",
    "playwright",
    "openai",
}


def main() -> int:
    errors: list[str] = []
    errors.extend(_validate_json_files(POLICY_FILES))
    errors.extend(_validate_required_files(DOC_FILES + AUDIT_FILES))
    errors.extend(_validate_runtime_imports())
    errors.extend(_validate_policy_contents())
    errors.extend(_validate_pack_export_examples())
    errors.extend(_validate_generated_artifacts())
    errors.extend(_validate_script_commands())
    errors.extend(_validate_forbidden_output_roots())
    errors.extend(_validate_no_banned_imports())

    if errors:
        for error in sorted(dict.fromkeys(errors)):
            print(f"FAIL: {error}")
        return 1
    print("PASS: local pack export runtime artifacts validate")
    return 0


def _validate_required_files(paths: list[str]) -> list[str]:
    return [f"missing required file: {path}" for path in paths if not (REPO_ROOT / path).is_file()]


def _validate_json_files(paths: list[str]) -> list[str]:
    errors: list[str] = []
    for path in paths:
        file_path = REPO_ROOT / path
        if not file_path.is_file():
            errors.append(f"missing policy JSON: {path}")
            continue
        try:
            json.loads(file_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"invalid JSON {path}: {exc}")
    return errors


def _validate_runtime_imports() -> list[str]:
    required = [
        "build_pack_export",
        "validate_pack_export_request",
        "validate_pack_export",
        "summarize_pack_export",
        "classify_export_pack_type",
        "compute_pack_fixity",
        "build_export_manifest",
        "detect_pack_export_truth_boundary_violations",
        "detect_pack_export_product_boundary_violations",
        "detect_forbidden_export_input",
        "build_pack_export_result",
    ]
    return [f"runtime missing function: {name}" for name in required if not hasattr(pack_export, name)]


def _validate_policy_contents() -> list[str]:
    errors: list[str] = []
    runtime_policy = _load_json("control/inventory/packs/pack_export_runtime_policy.json")
    path_policy = _load_json("control/inventory/packs/pack_export_path_policy.json")
    review_policy = _load_json("control/inventory/packs/pack_export_review_policy.json")
    truth_policy = _load_json("control/inventory/packs/pack_export_truth_policy.json")
    output_policy = _load_json("control/inventory/packs/pack_export_output_policy.json")
    format_policy = _load_json("control/inventory/packs/pack_export_format_policy.json")
    fixity_policy = _load_json("control/inventory/packs/pack_export_fixity_policy.json")

    for field in (
        "pack_import_enabled",
        "pack_submission_enabled",
        "hosted_upload_enabled",
        "pack_acceptance_enabled",
        "real_signing_enabled",
        "public_index_mutation_enabled",
        "master_index_mutation_enabled",
    ):
        if runtime_policy.get("runtime_scope", {}).get(field) is not False:
            errors.append(f"runtime policy must keep runtime_scope.{field} false")
    for field in (
        "automatic_pack_import_allowed",
        "automatic_pack_submission_allowed",
        "automatic_pack_acceptance_allowed",
        "automatic_evidence_acceptance_allowed",
        "automatic_public_index_mutation_allowed",
        "automatic_master_index_mutation_allowed",
    ):
        if review_policy.get(field) is not False:
            errors.append(f"review policy must keep {field} false")
    for field in pack_export.TRUTH_BOUNDARY_FALSE_FIELDS:
        if truth_policy.get(field) is not False:
            errors.append(f"truth policy must keep {field} false")
    for forbidden_output in pack_export.FORBIDDEN_OUTPUT_TYPES:
        if forbidden_output not in output_policy.get("forbidden_output_types", []):
            errors.append(f"output policy missing forbidden output: {forbidden_output}")
    for forbidden_root in ("site/dist/", "runtime/", "site/dist/data/public_index/"):
        if forbidden_root not in path_policy.get("forbidden_output_roots", []):
            errors.append(f"path policy must forbid {forbidden_root}")
    for current_format in pack_export.ALLOWED_FORMATS:
        if current_format not in format_policy.get("current_allowed_formats", []):
            errors.append(f"format policy missing current format: {current_format}")
    if fixity_policy.get("allowed_hash_algorithms") != ["sha256"]:
        errors.append("fixity policy must allow only sha256")
    for field in ("real_signing_enabled", "no_private_keys_allowed"):
        expected = False if field == "real_signing_enabled" else True
        if fixity_policy.get(field) is not expected:
            errors.append(f"fixity policy has unexpected {field}")
    return errors


def _validate_pack_export_examples() -> list[str]:
    errors: list[str] = []
    errors.extend(_validate_required_files(PACK_EXPORT_EXAMPLES))
    for path in PACK_EXPORT_EXAMPLES:
        if not (REPO_ROOT / path).is_file():
            continue
        payload = _load_json(path)
        errors.extend(f"{path}: {error}" for error in pack_export.validate_pack_export(payload))
    return errors


def _validate_generated_artifacts() -> list[str]:
    errors: list[str] = []
    export_path = REPO_ROOT / "control/audits/track-b-22-pack-export-runtime-v0/generated/sample_pack_export.json"
    result_path = REPO_ROOT / "control/audits/track-b-22-pack-export-runtime-v0/generated/sample_pack_export_report.json"
    if export_path.is_file():
        errors.extend(f"generated sample export: {error}" for error in pack_export.validate_pack_export(_load_json(str(export_path.relative_to(REPO_ROOT)))))
    if result_path.is_file():
        result = _load_json(str(result_path.relative_to(REPO_ROOT)))
        if result.get("schema_version") != pack_export.RESULT_SCHEMA_VERSION:
            errors.append("generated sample report has unexpected schema_version")
        if isinstance(result.get("pack_export"), dict):
            errors.extend(f"generated sample report export: {error}" for error in pack_export.validate_pack_export(result["pack_export"]))
        else:
            errors.append("generated sample report missing pack_export")
    return errors


def _validate_script_commands() -> list[str]:
    command = [
        sys.executable,
        "scripts/export_local_pack.py",
        "--input",
        "examples/packs/drafts/evidence_pack_draft_v0.json",
        "--check",
    ]
    completed = subprocess.run(command, cwd=REPO_ROOT, text=True, capture_output=True)
    if completed.returncode != 0:
        return [f"script command failed: {' '.join(command)} :: {completed.stderr.strip() or completed.stdout.strip()}"]
    return []


def _validate_forbidden_output_roots() -> list[str]:
    errors: list[str] = []
    for output in ("site/dist/export.json", "runtime/export.json", "site/dist/data/public_index/export.json"):
        command = [
            sys.executable,
            "scripts/export_local_pack.py",
            "--input",
            "examples/packs/drafts/evidence_pack_draft_v0.json",
            "--output",
            output,
        ]
        completed = subprocess.run(command, cwd=REPO_ROOT, text=True, capture_output=True)
        if completed.returncode == 0:
            errors.append(f"forbidden output root was not rejected: {output}")
    return errors


def _validate_no_banned_imports() -> list[str]:
    errors: list[str] = []
    for path in (
        "runtime/local/foundry/pack_export.py",
        "scripts/export_local_pack.py",
        "scripts/validate_pack_export_runtime.py",
    ):
        file_path = REPO_ROOT / path
        if not file_path.is_file():
            errors.append(f"missing import-scan target: {path}")
            continue
        tree = ast.parse(file_path.read_text(encoding="utf-8"))
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    root = alias.name.split(".")[0]
                    if root in BANNED_IMPORTS:
                        errors.append(f"{path} imports forbidden module: {alias.name}")
            elif isinstance(node, ast.ImportFrom):
                root = (node.module or "").split(".")[0]
                if root in BANNED_IMPORTS:
                    errors.append(f"{path} imports forbidden module: {node.module}")
    return errors


def _load_json(path: str) -> dict[str, Any]:
    payload = json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"expected JSON object: {path}")
    return payload


if __name__ == "__main__":
    raise SystemExit(main())
