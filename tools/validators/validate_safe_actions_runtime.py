#!/usr/bin/env python3
"""Validate J0 safe action manifests, policies, examples, scripts, and audits."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
from typing import Any, Mapping, Sequence

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.actions import action_manifest, action_policy, blocked_action  # noqa: E402
from runtime.actions.acquisition_manifest import validate_acquisition_manifest  # noqa: E402
from runtime.actions.citation_bundle import validate_citation_bundle  # noqa: E402
from runtime.actions.compare_manifest import validate_compare_action_manifest  # noqa: E402
from runtime.actions.export_manifest import validate_export_manifest  # noqa: E402
from runtime.actions.preservation_manifest import validate_preservation_manifest  # noqa: E402


CONTRACTS = (
    "contracts/control_schemas/policies/actions/action_taxonomy.v0.json",
    "contracts/actions/action_policy.v0.json",
    "contracts/actions/action_manifest.v0.json",
    "contracts/control_schemas/previews/actions/action_result_preview.v0.json",
    "contracts/actions/acquisition_manifest.v0.json",
    "contracts/control_schemas/policies/actions/citation_bundle.v0.json",
    "contracts/actions/export_manifest.v0.json",
    "contracts/actions/preservation_manifest.v0.json",
    "contracts/control_schemas/audits/actions/blocked_action_report.v0.json",
    "contracts/actions/compare_action_manifest.v0.json",
)
POLICIES = (
    "control/inventory/actions/action_taxonomy_policy.json",
    "control/inventory/actions/safe_action_policy.json",
    "control/inventory/actions/action_output_policy.json",
    "control/inventory/actions/action_path_policy.json",
    "control/inventory/actions/action_truth_policy.json",
    "control/inventory/actions/acquisition_manifest_policy.json",
    "control/inventory/actions/citation_bundle_policy.json",
    "control/inventory/actions/export_manifest_policy.json",
    "control/inventory/actions/preservation_manifest_policy.json",
    "control/inventory/actions/blocked_action_policy.json",
    "control/inventory/actions/future_risky_action_policy.json",
)
EXAMPLES = tuple(path.as_posix() for path in sorted((REPO_ROOT / "examples/actions").rglob("*.json")))
PYTHON_FILES = (
    "runtime/actions/__init__.py",
    "runtime/actions/action_policy.py",
    "runtime/actions/action_manifest.py",
    "runtime/actions/acquisition_manifest.py",
    "runtime/actions/citation_bundle.py",
    "runtime/actions/export_manifest.py",
    "runtime/actions/preservation_manifest.py",
    "runtime/actions/compare_manifest.py",
    "runtime/actions/blocked_action.py",
    "runtime/actions/summaries.py",
    "scripts/build_action_manifest.py",
    "scripts/build_citation_bundle.py",
    "scripts/build_export_manifest.py",
    "scripts/build_acquisition_manifest.py",
    "scripts/validate_safe_actions_runtime.py",
    "scripts/summarize_action_manifests.py",
)
DOCS = (
    "docs/reference/ACTION_TAXONOMY_CONTRACT.md",
    "docs/reference/ACTION_MANIFEST_CONTRACT.md",
    "docs/reference/ACQUISITION_MANIFEST_CONTRACT.md",
    "docs/reference/CITATION_BUNDLE_CONTRACT.md",
    "docs/reference/EXPORT_MANIFEST_CONTRACT.md",
    "docs/reference/PRESERVATION_MANIFEST_CONTRACT.md",
    "docs/reference/BLOCKED_ACTION_REPORT_CONTRACT.md",
    "docs/architecture/SAFE_ACTION_MODEL.md",
    "docs/architecture/ACTION_POLICY_MODEL.md",
    "docs/operations/SAFE_ACTION_REVIEW.md",
    "docs/operations/ACQUISITION_MANIFEST_NO_DOWNLOAD_POLICY.md",
    "docs/operations/CITATION_AND_EXPORT_POLICY.md",
    "docs/operations/FUTURE_RISKY_ACTIONS_POLICY.md",
)
AUDIT_DIR = Path("control/audits/j0-bundle-01-safe-actions-manifests-v0")
AUDIT_FILES = (
    "README.md",
    "j0_bundle_01_report.json",
    "action_taxonomy_summary.md",
    "safe_action_manifest_report.md",
    "acquisition_manifest_report.md",
    "citation_export_manifest_report.md",
    "preservation_manifest_report.md",
    "blocked_action_report.md",
    "future_risky_action_boundary.md",
    "d_bundle_01_readiness_recommendation.md",
    "validation.md",
    "generated/sample_action_manifest.json",
    "generated/sample_acquisition_manifest.json",
    "generated/sample_citation_bundle.json",
    "generated/sample_export_manifest.json",
    "generated/sample_preservation_manifest.json",
    "generated/sample_blocked_action_report.json",
    "generated/sample_action_summary.md",
)
FORBIDDEN_IMPORT_RE = re.compile(
    r"^\s*(?:from|import)\s+(requests|httpx|aiohttp|socket|ftplib|smtplib|webbrowser|selenium|playwright|openai|anthropic)\b",
    re.MULTILINE,
)


def validate_repo(root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    for rel in CONTRACTS + POLICIES:
        load_required_json(root / rel, errors)
    policy = action_policy.load_action_policy(root)
    validate_policy_values(policy, errors)
    for rel in EXAMPLES:
        path = Path(rel)
        if path.is_absolute():
            payload = load_required_json(path, errors)
            display = path.relative_to(root).as_posix()
        else:
            payload = load_required_json(root / rel, errors)
            display = rel
        if payload:
            validate_payload(display, payload, policy, errors)
    validate_required_files(root, PYTHON_FILES + DOCS + tuple((AUDIT_DIR / item).as_posix() for item in AUDIT_FILES), errors)
    validate_audit_report(root, errors)
    validate_imports(root, errors)
    validate_scripts(root, errors)
    validate_no_private_roots(root, errors)
    return {
        "schema_version": "safe_actions_runtime_validation.v0",
        "task": "J0-BUNDLE-01",
        "status": "valid" if not errors else "invalid",
        "safe_manifests_enabled": True,
        "download_enabled": False,
        "mirror_enabled": False,
        "install_enabled": False,
        "execute_enabled": False,
        "emulate_enabled": False,
        "errors": sorted(dict.fromkeys(errors)),
    }


def validate_payload(rel: str, payload: Mapping[str, Any], policy: Mapping[str, Any], errors: list[str]) -> None:
    schema = payload.get("schema_version")
    if schema == "action_manifest.v0":
        errors.extend(f"{rel}: {error}" for error in action_manifest.validate_action_manifest(payload, policy))
    elif schema == "acquisition_manifest.v0":
        errors.extend(f"{rel}: {error}" for error in validate_acquisition_manifest(payload, policy))
    elif schema == "citation_bundle.v0":
        errors.extend(f"{rel}: {error}" for error in validate_citation_bundle(payload, policy))
    elif schema == "export_manifest.v0":
        errors.extend(f"{rel}: {error}" for error in validate_export_manifest(payload, policy))
    elif schema == "preservation_manifest.v0":
        errors.extend(f"{rel}: {error}" for error in validate_preservation_manifest(payload, policy))
    elif schema == "blocked_action_report.v0":
        errors.extend(f"{rel}: {error}" for error in blocked_action.validate_blocked_action_report(payload, policy))
    elif schema == "compare_action_manifest.v0":
        errors.extend(f"{rel}: {error}" for error in validate_compare_action_manifest(payload, policy))
    errors.extend(f"{rel}: {error}" for error in action_policy.detect_action_boundary_violations(payload))
    text = json.dumps(payload, sort_keys=True).casefold()
    for forbidden in (
        "rights are cleared",
        "malware-safe",
        "safe to execute",
        "installability verified",
        "download completed",
        "mirrored file",
        "public index mutated",
        "master index mutated",
    ):
        if forbidden in text:
            errors.append(f"{rel}: forbidden claim present: {forbidden}")


def validate_policy_values(policy: Mapping[str, Any], errors: list[str]) -> None:
    safe = set(policy.get("safe_actions", []))
    risky = set(policy.get("risky_actions", []))
    if not action_policy.SAFE_ACTIONS.issubset(safe):
        errors.append("safe action policy missing required current safe actions")
    if not action_policy.RISKY_ACTIONS.issubset(risky):
        errors.append("safe action policy missing required future risky actions")
    truth = policy.get("action_truth_policy", {})
    for key, value in truth.items():
        if key == "schema_version":
            continue
        if value is not False:
            errors.append(f"action_truth_policy.{key} must be false")
    for key in ("download_enabled", "mirror_enabled", "install_enabled", "execute_enabled", "emulate_enabled"):
        if policy.get("safe_action_policy", {}).get(key) is not False:
            errors.append(f"safe_action_policy.{key} must be false")


def validate_audit_report(root: Path, errors: list[str]) -> None:
    report = load_required_json(root / AUDIT_DIR / "j0_bundle_01_report.json", errors)
    if not report:
        return
    scope = report.get("action_scope", {})
    for key in ("safe_action_manifests_enabled", "view_enabled", "inspect_enabled", "compare_enabled", "cite_enabled", "export_manifest_enabled", "acquisition_manifest_enabled", "preservation_manifest_enabled"):
        if scope.get(key) is not True:
            errors.append(f"audit report action_scope.{key} must be true")
    for key in ("download_enabled", "mirror_enabled", "install_enabled", "execute_enabled", "emulate_enabled"):
        if scope.get(key) is not False:
            errors.append(f"audit report action_scope.{key} must be false")
    validate_payload("audit report", report, action_policy.load_action_policy(root), errors)


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
            errors.append(f"runtime action module must not execute processes: {rel}")


def validate_scripts(root: Path, errors: list[str]) -> None:
    commands = (
        [sys.executable, "scripts/build_action_manifest.py", "--action", "view", "--subject", "examples/actions/manifests/view_action_manifest_v0.json", "--check", "--json"],
        [sys.executable, "scripts/build_acquisition_manifest.py", "--subject", "examples/actions/acquisition/acquisition_manifest_metadata_only_v0.json", "--check", "--json"],
        [sys.executable, "scripts/build_citation_bundle.py", "--subject", "examples/actions/citation/citation_bundle_object_v0.json", "--check", "--json"],
        [sys.executable, "scripts/build_export_manifest.py", "--subject", "examples/actions/export/export_manifest_object_v0.json", "--check", "--json"],
        [sys.executable, "scripts/summarize_action_manifests.py", "--input", "examples/actions", "--check", "--json"],
    )
    for command in commands:
        result = subprocess.run(command, cwd=root, capture_output=True, text=True, timeout=120, check=False)
        if result.returncode != 0:
            errors.append(f"script failed: {' '.join(command)} :: {result.stdout} {result.stderr}")
    forbidden_outputs = (
        ("scripts/build_action_manifest.py", ["--action", "view", "--subject", "examples/actions/manifests/view_action_manifest_v0.json", "--output"]),
        ("scripts/build_export_manifest.py", ["--subject", "examples/actions/export/export_manifest_object_v0.json", "--output"]),
    )
    for script, base_args in forbidden_outputs:
        for output in ("site/dist/action.json", "site/dist/data/public_index/action.json", "download/action.json", "runtime/action.json"):
            command = [sys.executable, script, *base_args, output]
            result = subprocess.run(command, cwd=root, capture_output=True, text=True, timeout=120, check=False)
            combined = result.stdout + result.stderr
            if result.returncode == 0 or "refusing forbidden output root" not in combined:
                errors.append(f"{script} must reject forbidden output: {output}")


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
        print("Safe actions runtime validation")
        print(f"status: {result['status']}")
        for error in result["errors"]:
            print(f"ERROR: {error}")
    return 0 if result["status"] == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
