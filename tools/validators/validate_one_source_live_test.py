#!/usr/bin/env python3
"""Validate the R0-09 one-source PyPI metadata live-test gate."""

from __future__ import annotations

import argparse
import ast
import json
import sys
import tempfile
from pathlib import Path
from typing import Any, Mapping, Sequence, TextIO

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.run_one_source_live_test import run_one_source_live_test
from runtime.review_queue import ReviewDecisionKind
from runtime.source_observation.sources import pypi_json_metadata


POLICY_PATHS = (
    "control/policies/r0_one_source_live_test_policy.json",
    "control/policies/r0_pypi_metadata_source_policy.json",
)
CONTRACT_PATHS = (
    "contracts/runtime/live_metadata_test_request.v0.json",
    "contracts/runtime/live_metadata_test_result.v0.json",
)
SOURCE_MODULE = Path("runtime/source_observation/sources/pypi_json_metadata.py")
GENERATED_RESULT = Path("control/audits/r0-09-one-source-live-test-v0/generated/sample_live_test_output.json")
BANNED_IMPORT_ROOTS = {
    "requests",
    "httpx",
    "aiohttp",
    "subprocess",
    "socket",
    "webbrowser",
    "selenium",
    "playwright",
    "openai",
    "anthropic",
    "runtime.connectors",
    "runtime.local_foundry",
}
FORBIDDEN_PAYLOAD_TERMS = (
    "truth_boundary",
    "product_boundary",
    "quality_delta",
    "next_phase",
    "integration_audit",
    "review_seed",
    "source_truth",
    "evidence_truth",
)


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", default=str(REPO_ROOT))
    parser.add_argument("--require-live", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    result = validate(Path(args.repo_root).resolve(), require_live=args.require_live)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print("R0-09 one-source live test validation", file=stdout)
        print(f"status: {result['status']}", file=stdout)
        for error in result["errors"]:
            print(f"ERROR: {error}", file=stdout)
        for warning in result["warnings"]:
            print(f"WARN: {warning}", file=stdout)
    return 0 if result["status"] == "pass" else 1


def validate(root: Path = REPO_ROOT, *, require_live: bool = False) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    validate_json_inputs(root, errors)
    validate_policies(root, errors)
    validate_static_source(root, errors)
    dry_run = run_dry_run_check(errors)
    mocked_live = run_mocked_live_check(errors)
    generated_live = validate_generated_live_result(root, errors, warnings, require_live=require_live)
    status = "pass" if not errors else "fail"
    return {
        "schema_version": "one_source_live_test_validation.v0",
        "task": "R0-09",
        "status": status,
        "errors": errors,
        "warnings": warnings,
        "dry_run_status": dry_run.get("status"),
        "mocked_live_status": mocked_live.get("status"),
        "generated_live_status": generated_live.get("status"),
        "source_id": "pypi_json_metadata",
        "package_name": "sampleproject",
        "request_count_max": 1,
        "download_count": 0,
        "install_execution_count": 0,
        "source_sync_used": False,
        "site_dist_mutated": False,
        "master_index_mutated": False,
        "model_provider_used": False,
        "f0_should_remain_blocked": True,
        "dev_to_main_should_remain_blocked": True,
    }


def validate_json_inputs(root: Path, errors: list[str]) -> None:
    for rel in POLICY_PATHS + CONTRACT_PATHS:
        path = root / rel
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except FileNotFoundError:
            errors.append(f"missing JSON file: {rel}")
            continue
        except json.JSONDecodeError as exc:
            errors.append(f"invalid JSON file: {rel}: {exc}")
            continue
        if not isinstance(payload, Mapping):
            errors.append(f"JSON root must be an object: {rel}")
        text = json.dumps(payload, sort_keys=True).lower()
        for term in FORBIDDEN_PAYLOAD_TERMS:
            if term in text:
                errors.append(f"forbidden payload term in {rel}: {term}")


def validate_policies(root: Path, errors: list[str]) -> None:
    try:
        gate = json.loads((root / POLICY_PATHS[0]).read_text(encoding="utf-8"))
        source = json.loads((root / POLICY_PATHS[1]).read_text(encoding="utf-8"))
    except (FileNotFoundError, json.JSONDecodeError):
        return
    if gate.get("live_test_default_enabled") is not False:
        errors.append("live test policy must default to disabled")
    if gate.get("live_requires_explicit_flag") is not True:
        errors.append("live test policy must require explicit live flag")
    if gate.get("max_requests_per_run") != 1:
        errors.append("live test policy must allow only one request")
    for key in ("package_downloads_enabled", "dependency_resolution_enabled", "install_execution_enabled", "source_sync_enabled", "site_dist_writes_enabled", "master_index_writes_enabled"):
        if gate.get(key) is not False:
            errors.append(f"live test policy must keep {key}=false")
    if source.get("approved_package_names") != ["sampleproject"]:
        errors.append("PyPI source policy must approve only sampleproject")
    if source.get("download_urls_must_not_be_fetched") is not True:
        errors.append("PyPI source policy must forbid fetching download URLs")
    if source.get("max_requests_per_run") != 1:
        errors.append("PyPI source policy must allow only one request")


def validate_static_source(root: Path, errors: list[str]) -> None:
    path = root / SOURCE_MODULE
    if not path.is_file():
        errors.append(f"missing source module: {SOURCE_MODULE.as_posix()}")
        return
    text = path.read_text(encoding="utf-8")
    lower = text.lower()
    for term in FORBIDDEN_PAYLOAD_TERMS:
        if term in lower:
            errors.append(f"forbidden term in source module: {term}")
    if "runtime.connectors" in lower or "runtime.local_foundry" in lower:
        errors.append("source module must not depend on legacy runtime modules")
    if "download_url" in lower or "download_url" + "s" in lower:
        errors.append("source module must not fetch package file URL fields")
    try:
        tree = ast.parse(text, filename=str(path))
    except SyntaxError as exc:
        errors.append(f"source module is not parseable: {exc}")
        return
    for node in ast.walk(tree):
        imported: list[str] = []
        if isinstance(node, ast.Import):
            imported.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            imported.append(node.module)
        for name in imported:
            if any(name == banned or name.startswith(banned + ".") for banned in BANNED_IMPORT_ROOTS):
                errors.append(f"forbidden import in source module: {name}")


def run_dry_run_check(errors: list[str]) -> dict[str, Any]:
    original_urlopen = pypi_json_metadata.urllib.request.urlopen

    def fail_urlopen(*_args: Any, **_kwargs: Any) -> None:
        raise AssertionError("dry-run must not call network")

    pypi_json_metadata.urllib.request.urlopen = fail_urlopen
    try:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = run_one_source_live_test(
                package_name="sampleproject",
                source_cache_db=root / "source.sqlite",
                evidence_db=root / "evidence.sqlite",
                review_db=root / "review.sqlite",
                public_index_db=root / "public.sqlite",
                live=False,
            )
    finally:
        pypi_json_metadata.urllib.request.urlopen = original_urlopen
    validate_result_payload(result, errors, expect_live=False, expected_search_hits=1)
    return result


def run_mocked_live_check(errors: list[str]) -> dict[str, Any]:
    calls: list[Any] = []
    original_urlopen = pypi_json_metadata.urllib.request.urlopen

    class FakeResponse:
        status = 200

        def __enter__(self) -> "FakeResponse":
            return self

        def __exit__(self, *_args: Any) -> None:
            return None

        def read(self) -> bytes:
            return json.dumps(_sample_pypi_payload()).encode("utf-8")

        def getcode(self) -> int:
            return 200

    def fake_urlopen(request: Any, timeout: int) -> FakeResponse:
        calls.append((request, timeout))
        return FakeResponse()

    pypi_json_metadata.urllib.request.urlopen = fake_urlopen
    try:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            result = run_one_source_live_test(
                package_name="sampleproject",
                source_cache_db=root / "source.sqlite",
                evidence_db=root / "evidence.sqlite",
                review_db=root / "review.sqlite",
                public_index_db=root / "public.sqlite",
                live=True,
                decision_kind=ReviewDecisionKind.ACCEPT,
            )
    finally:
        pypi_json_metadata.urllib.request.urlopen = original_urlopen
    if len(calls) != 1:
        errors.append(f"mocked live path performed {len(calls)} requests")
    validate_result_payload(result, errors, expect_live=True, expected_search_hits=1)
    return result


def validate_generated_live_result(root: Path, errors: list[str], warnings: list[str], *, require_live: bool) -> dict[str, Any]:
    path = root / GENERATED_RESULT
    if not path.is_file():
        message = f"generated live result is missing: {GENERATED_RESULT.as_posix()}"
        if require_live:
            errors.append(message)
        else:
            warnings.append(message)
        return {}
    try:
        result = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(f"generated live result is invalid JSON: {exc}")
        return {}
    validate_result_payload(
        result,
        errors,
        expect_live=bool(result.get("live_requested")),
        expected_search_hits=1 if result.get("review_decision", {}).get("decision_kind") == "accept" else 0,
    )
    if require_live and result.get("network_used") is not True:
        errors.append("required live result did not use the network")
    return result


def validate_result_payload(result: Mapping[str, Any], errors: list[str], *, expect_live: bool, expected_search_hits: int) -> None:
    if result.get("source_id") != "pypi_json_metadata":
        errors.append("result source_id must be pypi_json_metadata")
    if result.get("package_name") != "sampleproject":
        errors.append("result package_name must be sampleproject")
    if result.get("request_count", 0) > 1:
        errors.append("result request_count must be at most one")
    if result.get("download_count") != 0:
        errors.append("result must not record downloads")
    if result.get("install_execution_count") != 0:
        errors.append("result must not record install or execution")
    if result.get("source_sync_used") is not False:
        errors.append("result must not record source sync")
    if result.get("site_dist_mutated") is not False:
        errors.append("result must not mutate site/dist")
    if result.get("master_index_mutated") is not False:
        errors.append("result must not mutate a master index")
    if expect_live:
        if result.get("live_requested") is not True:
            errors.append("live result must record live_requested=true")
        if result.get("network_used") is not True:
            errors.append("live result must record network_used=true")
        if result.get("request_count") != 1:
            errors.append("live result must record exactly one request")
    else:
        if result.get("network_used") is not False:
            errors.append("dry-run result must not use network")
    for key in ("source_cache_entry_created", "evidence_candidate_created", "review_item_created", "review_decision_recorded", "public_index_rebuilt"):
        if result.get(key) is not True:
            errors.append(f"result must set {key}=true")
    if result.get("search_hit_count", 0) < expected_search_hits:
        errors.append("result search hit count is lower than expected")
    if result.get("absence_hit_count") != 0:
        errors.append("absence query must return no hits")
    serialized = json.dumps(result, sort_keys=True).lower()
    for term in FORBIDDEN_PAYLOAD_TERMS:
        if term in serialized:
            errors.append(f"forbidden payload term in result: {term}")


def _sample_pypi_payload() -> dict[str, Any]:
    return {
        "info": {
            "name": "sampleproject",
            "version": "4.0.0",
            "summary": "A sample Python project",
            "project_urls": {
                "Homepage": "https://github.com/pypa/sampleproject"
            },
        },
        "releases": {
            "4.0.0": [
                {
                    "filename": "sampleproject-4.0.0.tar.gz",
                    "url": "https://files.pythonhosted.org/packages/sampleproject-4.0.0.tar.gz"
                }
            ]
        },
        "urls": [
            {
                "filename": "sampleproject-4.0.0-py3-none-any.whl",
                "url": "https://files.pythonhosted.org/packages/sampleproject-4.0.0-py3-none-any.whl"
            }
        ],
    }


if __name__ == "__main__":
    raise SystemExit(main())
