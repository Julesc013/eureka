#!/usr/bin/env python3
"""Validate the local pack builder runtime artifacts."""

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

from runtime.local_foundry import pack_builder


POLICY_FILES = [
    "control/inventory/packs/pack_builder_runtime_policy.json",
    "control/inventory/packs/pack_builder_input_policy.json",
    "control/inventory/packs/pack_builder_output_policy.json",
    "control/inventory/packs/pack_builder_type_policy.json",
    "control/inventory/packs/pack_builder_path_policy.json",
    "control/inventory/packs/pack_builder_review_policy.json",
    "control/inventory/packs/pack_builder_truth_policy.json",
]

PACK_BUILDER_EXAMPLES = [
    "examples/pack_builder/source_pack_draft_case_v0.json",
    "examples/pack_builder/evidence_pack_draft_case_v0.json",
    "examples/pack_builder/contribution_pack_draft_case_v0.json",
    "examples/pack_builder/review_pack_draft_case_v0.json",
    "examples/pack_builder/index_pack_preview_case_v0.json",
    "examples/pack_builder/policy_blocked_pack_build_case_v0.json",
]

PACK_DRAFT_EXAMPLES = [
    "examples/pack_drafts/source_pack_draft_v0.json",
    "examples/pack_drafts/evidence_pack_draft_v0.json",
    "examples/pack_drafts/contribution_pack_draft_v0.json",
    "examples/pack_drafts/review_pack_draft_v0.json",
    "examples/pack_drafts/index_pack_preview_v0.json",
    "examples/pack_drafts/policy_blocked_pack_draft_v0.json",
]

DOC_FILES = [
    "docs/reference/PACK_BUILDER_RUNTIME.md",
    "docs/architecture/PACK_BUILDER_MODEL.md",
    "docs/operations/PACK_BUILDER_REVIEW.md",
]

AUDIT_FILES = [
    "control/audits/track-b-21-pack-builder-runtime-v0/README.md",
    "control/audits/track-b-21-pack-builder-runtime-v0/track_b_21_report.json",
    "control/audits/track-b-21-pack-builder-runtime-v0/validation.md",
    "control/audits/track-b-21-pack-builder-runtime-v0/generated/sample_pack_draft.json",
    "control/audits/track-b-21-pack-builder-runtime-v0/generated/sample_pack_builder_report.json",
    "control/audits/track-b-21-pack-builder-runtime-v0/generated/sample_pack_builder_summary.md",
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
    errors.extend(_validate_pack_builder_examples())
    errors.extend(_validate_pack_draft_examples())
    errors.extend(_validate_generated_artifacts())
    errors.extend(_validate_script_commands())
    errors.extend(_validate_forbidden_output_roots())
    errors.extend(_validate_no_banned_imports())

    if errors:
        for error in sorted(dict.fromkeys(errors)):
            print(f"FAIL: {error}")
        return 1
    print("PASS: local pack builder runtime artifacts validate")
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
        "build_pack_draft",
        "validate_pack_builder_request",
        "validate_pack_draft",
        "summarize_pack_draft",
        "classify_pack_type",
        "classify_pack_inputs",
        "detect_pack_truth_boundary_violations",
        "detect_pack_product_boundary_violations",
        "detect_forbidden_pack_input",
        "build_pack_builder_result",
        "summarize_pack_builder_result",
    ]
    errors = []
    for name in required:
        if not hasattr(pack_builder, name):
            errors.append(f"runtime missing function: {name}")
    return errors


def _validate_policy_contents() -> list[str]:
    errors: list[str] = []
    runtime_policy = _load_json("control/inventory/packs/pack_builder_runtime_policy.json")
    path_policy = _load_json("control/inventory/packs/pack_builder_path_policy.json")
    review_policy = _load_json("control/inventory/packs/pack_builder_review_policy.json")
    truth_policy = _load_json("control/inventory/packs/pack_builder_truth_policy.json")
    output_policy = _load_json("control/inventory/packs/pack_builder_output_policy.json")
    type_policy = _load_json("control/inventory/packs/pack_builder_type_policy.json")

    for field in (
        "pack_import_enabled",
        "pack_submission_enabled",
        "pack_acceptance_enabled",
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
    for field in pack_builder.TRUTH_BOUNDARY_FALSE_FIELDS:
        if truth_policy.get(field) is not False:
            errors.append(f"truth policy must keep {field} false")
    for forbidden_output in pack_builder.FORBIDDEN_OUTPUT_TYPES:
        if forbidden_output not in output_policy.get("forbidden_output_types", []):
            errors.append(f"output policy missing forbidden output: {forbidden_output}")
    if "site/dist/" not in path_policy.get("forbidden_output_roots", []):
        errors.append("path policy must forbid site/dist/")
    if "runtime/" not in path_policy.get("forbidden_output_roots", []):
        errors.append("path policy must forbid runtime/")
    if "site/dist/data/public_index/" not in path_policy.get("forbidden_output_roots", []):
        errors.append("path policy must forbid site/dist/data/public_index/")
    for current_type in pack_builder.CURRENT_PACK_TYPES:
        if current_type not in type_policy.get("current_pack_types", []):
            errors.append(f"type policy missing current pack type: {current_type}")
    return errors


def _validate_pack_builder_examples() -> list[str]:
    errors: list[str] = []
    errors.extend(_validate_required_files(PACK_BUILDER_EXAMPLES))
    for path in PACK_BUILDER_EXAMPLES:
        if not (REPO_ROOT / path).is_file():
            continue
        payload = _load_json(path)
        errors.extend(f"{path}: {error}" for error in pack_builder.validate_pack_builder_request(payload))
    return errors


def _validate_pack_draft_examples() -> list[str]:
    errors: list[str] = []
    errors.extend(_validate_required_files(PACK_DRAFT_EXAMPLES))
    for path in PACK_DRAFT_EXAMPLES:
        if not (REPO_ROOT / path).is_file():
            continue
        payload = _load_json(path)
        errors.extend(f"{path}: {error}" for error in pack_builder.validate_pack_draft(payload))
    return errors


def _validate_generated_artifacts() -> list[str]:
    errors: list[str] = []
    pack_path = REPO_ROOT / "control/audits/track-b-21-pack-builder-runtime-v0/generated/sample_pack_draft.json"
    result_path = REPO_ROOT / "control/audits/track-b-21-pack-builder-runtime-v0/generated/sample_pack_builder_report.json"
    if pack_path.is_file():
        errors.extend(f"generated sample pack: {error}" for error in pack_builder.validate_pack_draft(_load_json(str(pack_path.relative_to(REPO_ROOT)))))
    if result_path.is_file():
        result = _load_json(str(result_path.relative_to(REPO_ROOT)))
        if result.get("schema_version") != pack_builder.RESULT_SCHEMA_VERSION:
            errors.append("generated sample report has unexpected schema_version")
        if isinstance(result.get("pack_draft"), dict):
            errors.extend(f"generated sample report pack: {error}" for error in pack_builder.validate_pack_draft(result["pack_draft"]))
        else:
            errors.append("generated sample report missing pack_draft")
    return errors


def _validate_script_commands() -> list[str]:
    commands = [
        [
            sys.executable,
            "scripts/build_local_pack.py",
            "--pack-type",
            "evidence_pack_draft",
            "--input",
            "examples/evidence_ledger_records/metadata_claim_record_v0.json",
            "--check",
        ],
        [
            sys.executable,
            "scripts/summarize_local_pack.py",
            "--input",
            "examples/pack_drafts",
            "--check",
        ],
    ]
    errors: list[str] = []
    for command in commands:
        completed = subprocess.run(command, cwd=REPO_ROOT, text=True, capture_output=True)
        if completed.returncode != 0:
            errors.append(f"script command failed: {' '.join(command)} :: {completed.stderr.strip() or completed.stdout.strip()}")
    return errors


def _validate_forbidden_output_roots() -> list[str]:
    errors: list[str] = []
    for output in ("site/dist/pack.json", "runtime/pack.json", "site/dist/data/public_index/pack.json"):
        command = [
            sys.executable,
            "scripts/build_local_pack.py",
            "--pack-type",
            "evidence_pack_draft",
            "--input",
            "examples/evidence_ledger_records/metadata_claim_record_v0.json",
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
        "runtime/local_foundry/pack_builder.py",
        "scripts/build_local_pack.py",
        "scripts/summarize_local_pack.py",
        "scripts/validate_pack_builder_runtime.py",
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
