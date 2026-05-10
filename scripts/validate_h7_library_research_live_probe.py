#!/usr/bin/env python3
"""Validate H7 library/research live-probe framework without live calls."""

from __future__ import annotations

import argparse
import importlib
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile
from collections.abc import Mapping, Sequence
from typing import Any, TextIO

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.connectors.h7_library_research.live_probe_common import (  # noqa: E402
    H7_SOURCE_IDS,
    SOURCE_CONFIGS,
    detect_h7_library_research_live_probe_product_boundary_violations,
    detect_h7_library_research_live_probe_truth_boundary_violations,
    load_h7_library_research_live_probe_policy_bundle,
    validate_h7_source_approval,
)

EXPECTED_SOURCES = H7_SOURCE_IDS
CONTRACTS = (
    "contracts/connectors/h7_library_research_live_probe_request.v0.json",
    "contracts/connectors/h7_library_research_live_probe_result.v0.json",
    "contracts/connectors/h7_library_research_live_probe_output_bundle.v0.json",
    "contracts/connectors/h7_library_research_connector_health_summary.v0.json",
)
POLICIES = (
    "control/inventory/connectors/h7_library_research_live_probe_policy.json",
    "control/inventory/connectors/h7_library_research_live_probe_allowed_requests.json",
    "control/inventory/connectors/h7_library_research_live_probe_endpoint_policy.json",
    "control/inventory/connectors/h7_library_research_live_probe_rate_limit_policy.json",
    "control/inventory/connectors/h7_library_research_live_probe_cache_policy.json",
    "control/inventory/connectors/h7_library_research_live_probe_kill_switch_policy.json",
    "control/inventory/connectors/h7_library_research_live_probe_output_policy.json",
    "control/inventory/connectors/h7_library_research_live_probe_path_policy.json",
    "control/inventory/connectors/h7_library_research_live_probe_review_policy.json",
    "control/inventory/connectors/h7_library_research_live_probe_truth_policy.json",
    "control/inventory/connectors/h7_library_research_live_probe_no_harvest_download_policy.json",
    "control/inventory/connectors/h7_library_research_live_probe_restricted_source_policy.json",
)
DOCS = (
    "docs/reference/H7_LIBRARY_RESEARCH_LIVE_PROBE.md",
    "docs/reference/H7_LIBRARY_RESEARCH_LIVE_PROBE_RESULT.md",
    "docs/reference/H7_LIBRARY_RESEARCH_CONNECTOR_HEALTH_SUMMARY.md",
    "docs/architecture/H7_LIBRARY_RESEARCH_LIVE_PROBE_MODEL.md",
    "docs/operations/H7_LIBRARY_RESEARCH_LIVE_PROBE_APPROVAL_GATES.md",
    "docs/operations/H7_LIBRARY_RESEARCH_LIVE_PROBE_REVIEW.md",
    "docs/operations/H7_LIBRARY_RESEARCH_LIVE_PROBE_BLOCKED_MODE.md",
    "docs/operations/H7_LIBRARY_RESEARCH_LIVE_PROBE_NO_HARVEST_DOWNLOAD_POLICY.md",
    "docs/operations/H7_LIBRARY_RESEARCH_LIVE_PROBE_RESTRICTED_SOURCE_POLICY.md",
)
AUDIT_DIR = Path("control/audits/h7-bundle-03-library-research-live-probes-v0")
AUDIT_FILES = (
    "README.md",
    "h7_bundle_03_report.json",
    "live_probe_policy_review.md",
    "live_probe_execution_report.md",
    "bibliographic_identity_candidate_preview.md",
    "research_work_identity_candidate_preview.md",
    "dataset_identity_candidate_preview.md",
    "cultural_object_identity_candidate_preview.md",
    "patent_identity_candidate_preview.md",
    "citation_relation_candidate_preview.md",
    "access_rights_availability_candidate_preview.md",
    "source_cache_candidate_preview.md",
    "evidence_candidate_preview.md",
    "review_queue_seed_preview.md",
    "connector_health_summary.md",
    "no_harvest_download_report.md",
    "restricted_source_policy_report.md",
    "h7_live_probe_blocked_or_completed_summary.md",
    "validation.md",
    "generated/sample_h7_live_probe_result.json",
    "generated/sample_h7_bibliographic_identity_candidate_from_probe.json",
    "generated/sample_h7_research_work_identity_candidate_from_probe.json",
    "generated/sample_h7_dataset_identity_candidate_from_probe.json",
    "generated/sample_h7_cultural_object_identity_candidate_from_probe.json",
    "generated/sample_h7_patent_identity_candidate_from_probe.json",
    "generated/sample_h7_citation_relation_candidate_from_probe.json",
    "generated/sample_h7_access_rights_availability_candidate_from_probe.json",
    "generated/sample_h7_source_cache_candidate_from_probe.json",
    "generated/sample_h7_evidence_candidate_preview_from_probe.json",
    "generated/sample_h7_review_queue_seed_from_probe.json",
    "generated/sample_h7_connector_health_summary.json",
    "generated/sample_h7_live_probe_summary.md",
)
PYTHON_FILES = tuple(
    ["runtime/connectors/h7_library_research/live_probe_common.py"]
    + [f"runtime/connectors/h7_library_research/live_probe_{source_id}.py" for source_id in EXPECTED_SOURCES]
    + [
        "scripts/run_h7_library_research_live_probe.py",
        "scripts/validate_h7_library_research_live_probe.py",
        "scripts/summarize_h7_library_research_live_probe_outputs.py",
    ]
)
BANNED_IMPORT_RE = re.compile(
    r"^\s*(?:from|import)\s+"
    r"(requests|httpx|aiohttp|socket|ftplib|smtplib|webbrowser|selenium|playwright|openai|anthropic)\b",
    re.MULTILINE,
)
CLIENT_CALL_RE = re.compile(r"(?<![\"'])\b(requests|httpx|aiohttp|openai|anthropic)\.")
SECRET_KEY_RE = re.compile(r'"[^"]*(api[_-]?key|api[_-]?token|access[_-]?token|auth[_-]?token|client_secret|password|private_key|cookie)[^"]*"\s*:', re.IGNORECASE)
FORBIDDEN_TRUE_KEYS = {
    "live_probe_result_is_public_truth",
    "normalized_record_is_public_truth",
    "bibliographic_identity_candidate_is_truth",
    "research_work_candidate_is_truth",
    "dataset_identity_candidate_is_truth",
    "cultural_object_candidate_is_truth",
    "patent_identity_candidate_is_truth",
    "citation_relation_candidate_is_truth",
    "access_metadata_is_rights_truth",
    "open_access_metadata_is_rights_clearance",
    "accepted_bibliographic_truth",
    "accepted_research_work_truth",
    "accepted_dataset_truth",
    "accepted_cultural_object_truth",
    "accepted_patent_truth",
    "accepted_citation_truth",
    "accepted_access_rights_truth",
    "accepted_source_truth",
    "accepted_evidence_truth",
    "accepted_candidate_truth",
    "accepted_public_record",
    "source_cache_candidate_is_accepted_source",
    "evidence_candidate_preview_is_accepted_evidence",
    "review_seed_is_review_decision",
    "public_index_mutated",
    "master_index_mutated",
    "rights_clearance_claimed",
    "open_access_truth_claimed",
    "privacy_safety_claimed",
    "malware_safety_claimed",
    "verified_availability_claimed",
    "production_readiness_claimed",
    "changed_public_search_behavior",
    "enabled_live_probes",
    "enabled_source_sync",
    "enabled_harvesting",
    "enabled_downloads",
    "enabled_crawling",
    "enabled_scraping",
    "restricted_source_enabled",
    "source_sync_enabled",
    "public_query_fanout_enabled",
    "oai_pmh_harvest_enabled",
    "api_query_enabled",
    "full_text_fetch_enabled",
    "pdf_download_enabled",
    "book_scan_download_enabled",
    "article_download_enabled",
    "dataset_download_enabled",
    "patent_document_download_enabled",
    "iiif_manifest_fetch_enabled",
    "media_download_enabled",
    "scraping_enabled",
    "crawling_enabled",
    "browser_automation_enabled",
    "bypass_or_automation_enabled",
}


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    result = validate_repo(REPO_ROOT)
    if args.json:
        print(json.dumps(result, indent=2, sort_keys=True), file=stdout)
    else:
        print("H7 library/research live probe validation", file=stdout)
        print(f"status: {result['status']}", file=stdout)
        print(f"errors: {len(result['errors'])}", file=stdout)
        for error in result["errors"]:
            print(f"- {error}", file=stdout)
    return 0 if result["status"] == "valid" else 1


def validate_repo(root: Path = REPO_ROOT) -> dict[str, Any]:
    errors: list[str] = []
    payloads: dict[str, dict[str, Any]] = {}
    for rel in CONTRACTS + POLICIES:
        payload = load_json_object(root / rel, errors)
        if payload is not None:
            payloads[rel] = payload
    for rel in DOCS + PYTHON_FILES:
        if not (root / rel).is_file():
            errors.append(f"missing required file: {rel}")
    for name in AUDIT_FILES:
        if not (root / AUDIT_DIR / name).is_file():
            errors.append(f"missing audit file: {(AUDIT_DIR / name).as_posix()}")
    validate_policies(payloads, errors)
    validate_examples(root, errors)
    validate_runtime_imports(errors)
    validate_python_safety(root, errors)
    validate_cli_offline(root, errors)
    validate_generated_outputs(root, errors)
    validate_no_private_roots(root, errors)
    return {
        "schema_version": "h7_library_research_live_probe_validation.v0",
        "status": "valid" if not errors else "invalid",
        "task": "H7-BUNDLE-03",
        "offline_default": True,
        "network_calls_made": False,
        "harvest_query_fetch_download_used": False,
        "restricted_source_access_used": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "errors": errors,
    }


def validate_policies(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    live = payloads.get(POLICIES[0], {})
    for key in (
        "live_probe_default_enabled",
        "source_sync_enabled",
        "public_query_fanout_enabled",
        "oai_pmh_harvest_enabled",
        "api_query_enabled",
        "full_text_fetch_enabled",
        "pdf_download_enabled",
        "book_scan_download_enabled",
        "article_download_enabled",
        "dataset_download_enabled",
        "patent_document_download_enabled",
        "iiif_manifest_fetch_enabled",
        "media_download_enabled",
        "scraping_enabled",
        "crawling_enabled",
        "browser_automation_enabled",
        "restricted_source_enabled",
        "bypass_or_automation_enabled",
    ):
        if live.get(key) is not False:
            errors.append(f"global policy {key} must be false")
    allowed = payloads.get(POLICIES[1], {})
    sources = allowed.get("sources", [])
    if sorted(item.get("source_id") for item in sources if isinstance(item, Mapping)) != sorted(EXPECTED_SOURCES):
        errors.append("allowed requests policy must list all H7 sources")
    bundle = load_h7_library_research_live_probe_policy_bundle(REPO_ROOT)
    for item in sources:
        if not isinstance(item, Mapping):
            errors.append("allowed request source entry must be object")
            continue
        source_id = str(item.get("source_id"))
        if item.get("approval_status") != "not_approved_for_live_access":
            errors.append(f"{source_id}: approval_status must remain not_approved_for_live_access")
        if item.get("allowed_request_keys") not in ([], None):
            errors.append(f"{source_id}: allowed_request_keys must stay empty without approval")
        for key in ("live_access_approved", "metadata_probe_approved"):
            if item.get(key) is not False:
                errors.append(f"{source_id}: {key} must be false")
        for key in (
            "source_sync_approved",
            "oai_pmh_harvest_approved",
            "api_query_approved",
            "full_text_fetch_approved",
            "pdf_download_approved",
            "book_scan_download_approved",
            "article_download_approved",
            "dataset_download_approved",
            "patent_document_download_approved",
            "iiif_manifest_fetch_approved",
            "media_download_approved",
            "scraping_approved",
            "crawling_approved",
            "browser_automation_approved",
            "restricted_rights_sensitive_source_approved",
            "bypass_or_access_control_automation_approved",
            "public_query_fanout_approved",
        ):
            if item.get(key) is not False:
                errors.append(f"{source_id}: {key} must be false")
        request_key = str((item.get("planned_request_keys") or [""])[0])
        approval = validate_h7_source_approval(source_id, request_key, bundle)
        if approval["approved"]:
            errors.append(f"{source_id}: live approval unexpectedly passes")
    truth = payloads.get(POLICIES[9], {})
    for key in FORBIDDEN_TRUE_KEYS:
        if truth.get(key) is True:
            errors.append(f"truth policy {key} must be false")
    output = payloads.get(POLICIES[6], {})
    for key in (
        "oai_pmh_harvest_result",
        "api_query_sync_result",
        "full_text_payload",
        "pdf_payload",
        "book_scan_payload",
        "article_payload",
        "dataset_payload",
        "patent_document_payload",
        "iiif_payload",
        "media_payload",
        "scraping_output",
        "crawling_output",
        "restricted_source_access_output",
        "accepted_bibliographic_truth",
        "accepted_research_work_truth",
        "accepted_dataset_truth",
        "accepted_cultural_object_truth",
        "accepted_patent_truth",
        "accepted_citation_truth",
        "accepted_access_rights_truth",
        "accepted_source_truth",
        "accepted_evidence_truth",
        "accepted_candidate_truth",
        "accepted_public_record",
        "public_index_mutation",
        "master_index_mutation",
        "rights_clearance",
        "open_access_truth",
        "privacy_safety",
        "malware_safety",
        "verified_availability",
        "production_readiness_claim",
    ):
        if key not in output.get("forbidden_outputs", []):
            errors.append(f"output policy must forbid {key}")


def validate_examples(root: Path, errors: list[str]) -> None:
    prompt_sources = ("openalex", "crossref", "datacite", "open_library", "arxiv", "pubmed", "google_patents")
    for source_id in prompt_sources:
        request_path = root / "examples/connectors/h7_library_research/live_probe" / f"approved_{source_id}_probe_request_v0.json"
        result_path = root / "examples/connectors/h7_library_research/live_probe_results" / f"{source_id}_live_probe_result_example_v0.json"
        for path in (request_path, result_path):
            payload = load_json_object(path, errors)
            if payload is not None:
                validate_no_forbidden_claims(path.as_posix(), payload, errors)
    for rel in (
        "examples/connectors/h7_library_research/live_probe/blocked_live_probe_request_v0.json",
        "examples/connectors/h7_library_research/live_probe_results/blocked_live_probe_result_v0.json",
        "examples/connectors/h7_library_research/live_probe_outputs/source_cache_candidate_from_h7_probe_v0.json",
        "examples/connectors/h7_library_research/live_probe_outputs/evidence_candidate_preview_from_h7_probe_v0.json",
        "examples/connectors/h7_library_research/live_probe_outputs/review_queue_seed_from_h7_probe_v0.json",
        "examples/connectors/h7_library_research/live_probe_outputs/connector_health_from_h7_probe_v0.json",
        "examples/connectors/h7_library_research/live_probe_outputs/bibliographic_identity_candidate_from_h7_probe_v0.json",
        "examples/connectors/h7_library_research/live_probe_outputs/research_work_identity_candidate_from_h7_probe_v0.json",
        "examples/connectors/h7_library_research/live_probe_outputs/dataset_identity_candidate_from_h7_probe_v0.json",
        "examples/connectors/h7_library_research/live_probe_outputs/cultural_object_identity_candidate_from_h7_probe_v0.json",
        "examples/connectors/h7_library_research/live_probe_outputs/patent_identity_candidate_from_h7_probe_v0.json",
        "examples/connectors/h7_library_research/live_probe_outputs/citation_relation_candidate_from_h7_probe_v0.json",
        "examples/connectors/h7_library_research/live_probe_outputs/access_rights_availability_candidate_from_h7_probe_v0.json",
    ):
        payload = load_json_object(root / rel, errors)
        if payload is not None:
            validate_no_forbidden_claims(rel, payload, errors)


def validate_runtime_imports(errors: list[str]) -> None:
    try:
        importlib.import_module("runtime.connectors.h7_library_research.live_probe_common")
        for source_id in EXPECTED_SOURCES:
            importlib.import_module(f"runtime.connectors.h7_library_research.live_probe_{source_id}")
        importlib.import_module("scripts.run_h7_library_research_live_probe")
        importlib.import_module("scripts.summarize_h7_library_research_live_probe_outputs")
    except Exception as exc:  # noqa: BLE001
        errors.append(f"runtime/script import failed: {exc}")


def validate_python_safety(root: Path, errors: list[str]) -> None:
    for rel in PYTHON_FILES:
        path = root / rel
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        if BANNED_IMPORT_RE.search(text):
            errors.append(f"forbidden network/provider/browser import in {rel}")
        if CLIENT_CALL_RE.search(text):
            errors.append(f"forbidden client/provider call in {rel}")


def validate_cli_offline(root: Path, errors: list[str]) -> None:
    run = subprocess.run(
        [sys.executable, "scripts/run_h7_library_research_live_probe.py", "--source-id", "openalex", "--request-key", "example_work_metadata", "--check", "--json"],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if run.returncode != 0:
        errors.append(f"live probe CLI offline check failed: {run.stdout} {run.stderr}")
    summary = subprocess.run(
        [sys.executable, "scripts/summarize_h7_library_research_live_probe_outputs.py", "--input", "examples/connectors/h7_library_research/live_probe_results", "--check", "--json"],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if summary.returncode != 0:
        errors.append(f"live probe summary check failed: {summary.stdout} {summary.stderr}")
    forbidden = subprocess.run(
        [sys.executable, "scripts/run_h7_library_research_live_probe.py", "--source-id", "openalex", "--request-key", "example_work_metadata", "--output", "site/dist/probe.json", "--json"],
        cwd=root,
        text=True,
        capture_output=True,
        check=False,
    )
    if forbidden.returncode == 0:
        errors.append("live probe CLI should refuse site/dist output")
    with tempfile.TemporaryDirectory() as tempdir:
        output = Path(tempdir) / "probe.json"
        write = subprocess.run(
            [sys.executable, "scripts/run_h7_library_research_live_probe.py", "--source-id", "openalex", "--request-key", "example_work_metadata", "--output", str(output), "--json"],
            cwd=root,
            text=True,
            capture_output=True,
            check=False,
        )
        if write.returncode != 0 or not output.is_file():
            errors.append(f"live probe CLI explicit temp output failed: {write.stdout} {write.stderr}")


def validate_generated_outputs(root: Path, errors: list[str]) -> None:
    for rel in (
        "control/audits/h7-bundle-03-library-research-live-probes-v0/generated/sample_h7_live_probe_result.json",
        "control/audits/h7-bundle-03-library-research-live-probes-v0/generated/sample_h7_connector_health_summary.json",
    ):
        payload = load_json_object(root / rel, errors)
        if payload is not None:
            validate_no_forbidden_claims(rel, payload, errors)
            errors.extend(f"{rel}: {item}" for item in detect_h7_library_research_live_probe_truth_boundary_violations(payload))
            errors.extend(f"{rel}: {item}" for item in detect_h7_library_research_live_probe_product_boundary_violations(payload))


def validate_no_forbidden_claims(label: str, value: object, errors: list[str]) -> None:
    if isinstance(value, Mapping):
        for key, item in value.items():
            if key in FORBIDDEN_TRUE_KEYS and item is True:
                errors.append(f"{label}: forbidden true claim {key}")
            if key in {"credential", "credentials", "cookie", "cookies", "api_key", "api_token", "access_token", "auth_token", "password", "private_key"}:
                errors.append(f"{label}: secret-like field {key}")
            if key in {"full_text_payload", "pdf_payload", "book_scan_payload", "article_payload", "dataset_payload", "patent_document_payload", "iiif_payload", "media_payload", "ocr_payload", "scraping_output", "crawling_output"}:
                errors.append(f"{label}: forbidden payload field {key}")
            validate_no_forbidden_claims(label, item, errors)
    elif isinstance(value, list):
        for item in value:
            validate_no_forbidden_claims(label, item, errors)


def validate_no_private_roots(root: Path, errors: list[str]) -> None:
    for rel in (".aide.local", ".local/eureka", ".cache/eureka"):
        if (root / rel).exists():
            errors.append(f"local private root exists: {rel}")


def load_json_object(path: Path, errors: list[str]) -> dict[str, Any] | None:
    if not path.is_file():
        errors.append(f"missing required JSON file: {path.relative_to(REPO_ROOT).as_posix() if path.is_relative_to(REPO_ROOT) else path.as_posix()}")
        return None
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        errors.append(f"invalid JSON {path}: {exc}")
        return None
    if not isinstance(payload, dict):
        errors.append(f"JSON file must contain object: {path}")
        return None
    text = path.read_text(encoding="utf-8")
    if SECRET_KEY_RE.search(text):
        errors.append(f"secret-like key in JSON file: {path}")
    return payload


if __name__ == "__main__":
    raise SystemExit(main())
