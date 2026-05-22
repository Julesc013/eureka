#!/usr/bin/env python3
"""Validate the R0-04 source observation seam."""

from __future__ import annotations

import argparse
import ast
import json
import re
import sys
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.demo_source_observation_seam import build_demo_result


RUNTIME_ROOT = Path("runtime/source_observation")
CONTRACT_PATHS = (
    "contracts/domain/source_record.v0.json",
    "contracts/domain/source_policy.v0.json",
    "contracts/runtime/metadata_request.v0.json",
    "contracts/runtime/metadata_response.v0.json",
    "contracts/runtime/source_observation.v0.json",
    "contracts/runtime/normalized_observation.v0.json",
    "contracts/runtime/evidence_candidate.v0.json",
    "contracts/runtime/review_item.v0.json",
    "contracts/runtime/connector_health.v0.json",
)
FORBIDDEN_TERMS = tuple(
    [f"H{index}" for index in range(15)]
    + [
        "BUNDLE",
        "IA-BUNDLE",
        "F-BUNDLE",
        "G-BUNDLE",
        "MVP",
        "LOCAL-MVP",
        "AIDE",
        "prompt",
        "agent",
        "human_obs",
        "fixture_only",
        "preview_only",
        "truth_boundary",
        "product_boundary",
        "review_seed",
        "next_phase",
        "quality_delta",
        "integration_audit",
    ]
)
BANNED_IMPORT_ROOTS = {
    "requests",
    "httpx",
    "aiohttp",
    "urllib.request",
    "subprocess",
    "socket",
    "webbrowser",
    "selenium",
    "playwright",
    "openai",
    "anthropic",
    "runtime.connectors",
}


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    root = Path(args.repo_root).resolve()
    result = validate_seam(root)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print("R0-04 source observation seam validation", file=stdout)
        print(f"status: {result['status']}", file=stdout)
        for error in result["errors"]:
            print(f"ERROR: {error}", file=stdout)
        for warning in result["warnings"]:
            print(f"WARN: {warning}", file=stdout)
    return 0 if result["status"] in {"pass", "pass_with_warnings"} else 1


def validate_seam(root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    if not (root / RUNTIME_ROOT).is_dir():
        errors.append("runtime/source_observation package is missing")

    forbidden_vocabulary_found = scan_forbidden_vocabulary(root, errors)
    h_series_dependencies = scan_h_series_dependencies(root, errors)
    network_dependencies = scan_banned_imports(root, errors)
    validate_contracts(root, errors)
    demo = validate_demo_payload(errors)
    validate_r0_prerequisites(root, warnings)

    status = "pass"
    if warnings:
        status = "pass_with_warnings"
    if errors:
        status = "fail"
    return {
        "schema_version": "source_observation_seam_validation.v0",
        "status": status,
        "errors": errors,
        "warnings": warnings,
        "runtime_package": RUNTIME_ROOT.as_posix(),
        "contract_count": len(CONTRACT_PATHS),
        "forbidden_vocabulary_found": forbidden_vocabulary_found,
        "h_series_dependencies": h_series_dependencies,
        "network_dependencies": network_dependencies,
        "demo_keys": sorted(demo.keys()),
        "durable_writes_enabled": False,
        "public_index_writes_enabled": False,
        "f0_should_remain_blocked": True,
        "dev_to_main_should_remain_blocked": True,
    }


def scan_forbidden_vocabulary(root: Path, errors: list[str]) -> int:
    count = 0
    for path in sorted((root / RUNTIME_ROOT).glob("*.py")):
        text = path.read_text(encoding="utf-8")
        for term in FORBIDDEN_TERMS:
            if re.search(re.escape(term), text, re.IGNORECASE):
                errors.append(f"forbidden vocabulary in {path.relative_to(root).as_posix()}: {term}")
                count += 1
    return count


def scan_h_series_dependencies(root: Path, errors: list[str]) -> int:
    count = 0
    for path in sorted((root / RUNTIME_ROOT).glob("*.py")):
        text = path.read_text(encoding="utf-8").lower()
        if "runtime.connectors" in text or re.search(r"\bh(?:[0-9]|1[0-4])[_\.-]", text):
            errors.append(f"legacy phase dependency in {path.relative_to(root).as_posix()}")
            count += 1
    return count


def scan_banned_imports(root: Path, errors: list[str]) -> int:
    count = 0
    for path in sorted((root / RUNTIME_ROOT).glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
        for node in ast.walk(tree):
            imported: list[str] = []
            if isinstance(node, ast.Import):
                imported.extend(alias.name for alias in node.names)
            elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
                imported.append(node.module)
            for name in imported:
                if any(name == banned or name.startswith(banned + ".") for banned in BANNED_IMPORT_ROOTS):
                    errors.append(f"forbidden import in {path.relative_to(root).as_posix()}: {name}")
                    count += 1
    return count


def validate_contracts(root: Path, errors: list[str]) -> None:
    for rel in CONTRACT_PATHS:
        path = root / rel
        if not path.is_file():
            errors.append(f"missing contract: {rel}")
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"contract is not valid JSON: {rel}: {exc}")
            continue
        if not isinstance(payload, Mapping):
            errors.append(f"contract root must be an object: {rel}")
        text = json.dumps(payload, sort_keys=True)
        for term in FORBIDDEN_TERMS:
            if re.search(re.escape(term), text, re.IGNORECASE):
                errors.append(f"forbidden vocabulary in contract {rel}: {term}")


def validate_demo_payload(errors: list[str]) -> dict[str, Any]:
    demo = build_demo_result()
    serialized = json.dumps(demo, sort_keys=True)
    for key in ("source_observation", "normalized_observation", "evidence_candidate", "review_item"):
        if key not in demo:
            errors.append(f"demo missing {key}")
    for term in ("truth_boundary", "product_boundary"):
        if term in serialized:
            errors.append(f"demo output contains reserved field {term}")
    if demo.get("evidence_candidate", {}).get("accepted") is not False:
        errors.append("evidence candidate must not be accepted")
    if demo.get("review_item", {}).get("review_status") not in {"candidate", "needs_review"}:
        errors.append("review item must remain pre-decision")
    if demo.get("writes_enabled", {}).get("durable_store") is not False:
        errors.append("demo must not enable durable writes")
    if demo.get("writes_enabled", {}).get("public_index") is not False:
        errors.append("demo must not enable public index writes")
    return demo


def validate_r0_prerequisites(root: Path, warnings: list[str]) -> None:
    final_taxonomy = root / "control/inventory/r0_03b_2_final_contract_taxonomy.json"
    try:
        payload = json.loads(final_taxonomy.read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        warnings.append("R0-03B-2 final contract taxonomy could not be read")
        return
    if payload.get("contracts_clean_enough_for_r0_04") is not True:
        warnings.append("R0-03B-2 records remaining contract taxonomy debt")


if __name__ == "__main__":
    raise SystemExit(main())
