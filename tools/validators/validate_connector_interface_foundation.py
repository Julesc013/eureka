#!/usr/bin/env python3
"""Validate H0-BUNDLE-02 connector-interface artifacts offline."""

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

from runtime.connectors.core.connector_interface import (  # noqa: E402
    detect_connector_product_boundary_violations,
    detect_connector_truth_boundary_violations,
)
from runtime.connectors.core.output_envelope import validate_connector_output_envelope  # noqa: E402
from runtime.connectors.core.policy_evaluator import evaluate_connector_policy  # noqa: E402


CONTRACTS = (
    "contracts/connectors/source_connector_interface.v0.json",
    "contracts/connectors/source_connector_capability.v0.json",
    "contracts/schema/control/fixtures/connectors/source_connector_fixture_replay.v0.json",
    "contracts/connectors/source_connector_output_envelope.v0.json",
    "contracts/connectors/live_probe_request.v0.json",
    "contracts/connectors/live_probe_result.v0.json",
    "contracts/connectors/connector_policy_evaluation.v0.json",
    "contracts/connectors/connector_family.v0.json",
)
INVENTORIES = (
    "control/inventory/connectors/connector_family_registry.json",
    "control/inventory/connectors/connector_interface_policy.json",
    "control/inventory/connectors/connector_capability_policy.json",
    "control/inventory/connectors/connector_fixture_replay_policy.json",
    "control/inventory/connectors/connector_output_envelope_policy.json",
    "control/inventory/connectors/live_probe_envelope_policy.json",
    "control/inventory/connectors/connector_policy_evaluation_policy.json",
    "control/inventory/connectors/connector_no_live_call_policy.json",
)
FAMILY_EXAMPLES = (
    "examples/connectors/core/families/api_json_connector_family_v0.json",
    "examples/connectors/core/families/package_registry_connector_family_v0.json",
    "examples/connectors/core/families/warc_cdx_connector_family_v0.json",
    "examples/connectors/core/families/html_catalog_connector_family_v0.json",
    "examples/connectors/core/families/oai_pmh_connector_family_v0.json",
    "examples/connectors/core/families/iiif_connector_family_v0.json",
    "examples/connectors/core/families/local_source_connector_family_v0.json",
    "examples/connectors/core/families/policy_blocked_connector_family_v0.json",
)
FIXTURE_REPLAY_EXAMPLES = (
    "examples/connectors/core/fixture_replay/minimal_fixture_replay_request_v0.json",
    "examples/connectors/core/fixture_replay/ia_fixture_replay_request_v0.json",
    "examples/connectors/core/fixture_replay/package_registry_fixture_replay_request_v0.json",
    "examples/connectors/core/fixture_replay/policy_blocked_fixture_replay_request_v0.json",
    "examples/connectors/core/fixture_replay/minimal_fixture_replay_result_v0.json",
    "examples/connectors/core/fixture_replay/ia_fixture_replay_result_v0.json",
    "examples/connectors/core/fixture_replay/policy_blocked_fixture_replay_result_v0.json",
)
LIVE_PROBE_EXAMPLES = (
    "examples/connectors/core/live_probe/minimal_live_probe_request_v0.json",
    "examples/connectors/core/live_probe/policy_blocked_live_probe_request_v0.json",
    "examples/connectors/core/live_probe/live_probe_envelope_blocked_result_v0.json",
)
OUTPUT_ENVELOPE_EXAMPLES = (
    "examples/connectors/core/output_envelopes/minimal_connector_output_envelope_v0.json",
    "examples/connectors/core/output_envelopes/source_cache_candidate_output_envelope_v0.json",
    "examples/connectors/core/output_envelopes/evidence_candidate_output_envelope_v0.json",
    "examples/connectors/core/output_envelopes/policy_blocked_output_envelope_v0.json",
)
DOCS = (
    "docs/reference/SOURCE_CONNECTOR_INTERFACE.md",
    "docs/reference/CONNECTOR_FIXTURE_REPLAY_CONTRACT.md",
    "docs/reference/LIVE_PROBE_ENVELOPE_CONTRACT.md",
    "docs/reference/CONNECTOR_POLICY_EVALUATION_CONTRACT.md",
    "docs/architecture/CONNECTOR_INTERFACE_MODEL.md",
    "docs/architecture/CONNECTOR_FIXTURE_REPLAY_MODEL.md",
    "docs/operations/CONNECTOR_POLICY_EVALUATION.md",
    "docs/operations/CONNECTOR_NO_LIVE_CALL_POLICY.md",
)
AUDIT_FILES = (
    "control/audits/h0-bundle-02-connector-interface-replay-v0/README.md",
    "control/audits/h0-bundle-02-connector-interface-replay-v0/h0_bundle_02_report.json",
    "control/audits/h0-bundle-02-connector-interface-replay-v0/connector_interface_summary.md",
    "control/audits/h0-bundle-02-connector-interface-replay-v0/connector_family_registry_summary.md",
    "control/audits/h0-bundle-02-connector-interface-replay-v0/fixture_replay_report.md",
    "control/audits/h0-bundle-02-connector-interface-replay-v0/live_probe_envelope_report.md",
    "control/audits/h0-bundle-02-connector-interface-replay-v0/connector_policy_evaluation_report.md",
    "control/audits/h0-bundle-02-connector-interface-replay-v0/no_live_call_report.md",
    "control/audits/h0-bundle-02-connector-interface-replay-v0/validation.md",
    "control/audits/h0-bundle-02-connector-interface-replay-v0/generated/sample_connector_family_summary.json",
    "control/audits/h0-bundle-02-connector-interface-replay-v0/generated/sample_connector_family_summary.md",
    "control/audits/h0-bundle-02-connector-interface-replay-v0/generated/sample_fixture_replay_result.json",
    "control/audits/h0-bundle-02-connector-interface-replay-v0/generated/sample_policy_evaluation_result.json",
    "control/audits/h0-bundle-02-connector-interface-replay-v0/generated/sample_live_probe_blocked_result.json",
)
PYTHON_SCAN_PATHS = (
    "runtime/connectors/core/connector_interface.py",
    "runtime/connectors/core/fixture_replay.py",
    "runtime/connectors/core/live_probe_envelope.py",
    "runtime/connectors/core/policy_evaluator.py",
    "runtime/connectors/core/output_envelope.py",
    "scripts/run_connector_fixture_replay.py",
    "scripts/evaluate_connector_policy.py",
    "scripts/summarize_connector_families.py",
    "scripts/validate_connector_interface_foundation.py",
)
BANNED_IMPORT_RE = re.compile(
    r"^\s*(?:from|import)\s+"
    r"(requests|httpx|aiohttp|socket|ftplib|smtplib|webbrowser|selenium|playwright|openai|anthropic)\b",
    re.MULTILINE,
)
FORBIDDEN_TERMS = (
    "\"accepted_source_truth\": true",
    "\"accepted_evidence_truth\": true",
    "\"accepted_candidate_truth\": true",
    "\"accepted_public_truth\": true",
    "\"public_index_mutated\": true",
    "\"master_index_mutated\": true",
    "\"downloaded_file\": true",
    "\"executed_artifact\": true",
    "\"rights_clearance_claimed\": true",
    "\"malware_safety_claimed\": true",
    "\"verified_installability_claimed\": true",
)
KNOWN_SOURCE_FAMILIES = {
    "archive_metadata",
    "web_archive",
    "package_registry",
    "os_package_archive",
    "code_source_release_host",
    "vendor_update_driver",
    "vendor_update_driver_firmware",
    "web_archive_news_event",
    "library_cultural_research",
    "manuals_docs_standards",
    "media_music_image_video_map",
    "games_emulation_software_identity",
    "storefront_app_store",
    "retro_community_archive",
    "local_private_user_supplied",
    "restricted_source_manifest_only",
    "source_discovery_scorecard",
    "source_discovery_and_scorecards",
}
FORBIDDEN_DEFAULT_OPERATIONS = {
    "arbitrary_url_fetch",
    "unbounded_search",
    "broad_crawl",
    "scrape_html_without_policy",
    "bypass_access_controls",
    "bypass_captcha",
    "use_credentials_without_policy",
    "download_binary",
    "fetch_item_file_payload",
    "run_installer",
    "execute_downloaded_artifact",
    "upload_to_hosted_backend",
    "mutate_public_index",
    "mutate_master_index",
    "accept_evidence_truth",
    "accept_public_truth",
}


def validate_repo(root: Path = REPO_ROOT) -> dict[str, Any]:
    root = root.resolve()
    errors: list[str] = []
    json_files = (
        CONTRACTS
        + INVENTORIES
        + FAMILY_EXAMPLES
        + FIXTURE_REPLAY_EXAMPLES
        + LIVE_PROBE_EXAMPLES
        + OUTPUT_ENVELOPE_EXAMPLES
        + ("control/audits/h0-bundle-02-connector-interface-replay-v0/h0_bundle_02_report.json",)
    )
    payloads = {rel: load_json_object(root / rel, errors) for rel in json_files}
    validate_required_files(root, errors)
    validate_family_registry(payloads, errors)
    validate_capability_and_policy(payloads, errors)
    validate_examples(payloads, errors)
    validate_audit_report(payloads, errors)
    validate_runtime_imports(root, errors)
    validate_scripts(root, errors)
    validate_no_private_roots(root, errors)
    return {
        "schema_version": "connector_interface_foundation_validation.v0",
        "status": "valid" if not errors else "invalid",
        "task": "H0-BUNDLE-02",
        "offline_default": True,
        "errors": errors,
    }


def validate_required_files(root: Path, errors: list[str]) -> None:
    for rel in CONTRACTS + INVENTORIES + FAMILY_EXAMPLES + FIXTURE_REPLAY_EXAMPLES + LIVE_PROBE_EXAMPLES + OUTPUT_ENVELOPE_EXAMPLES + DOCS + AUDIT_FILES:
        if not (root / rel).is_file():
            errors.append(f"missing required file: {rel}")


def validate_family_registry(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    registry = payloads.get("control/inventory/connectors/connector_family_registry.json", {})
    families = registry.get("families", [])
    required = {"api_json", "package_registry", "oai_pmh", "iiif", "warc_cdx", "html_catalog", "rss_atom_sitemap", "directory_listing", "storefront", "local_source", "review_text", "restricted_manifest_only"}
    family_ids = {str(item.get("family_id")) for item in families if isinstance(item, Mapping)}
    missing = sorted(required - family_ids)
    if missing:
        errors.append(f"connector family registry missing families: {', '.join(missing)}")
    for family in families:
        if not isinstance(family, Mapping):
            errors.append("connector family entries must be objects")
            continue
        validate_family(family, f"connector_family_registry.{family.get('family_id')}", errors)


def validate_family(family: Mapping[str, Any], label: str, errors: list[str]) -> None:
    required = {
        "schema_version",
        "family_id",
        "source_families_supported",
        "typical_input_shapes",
        "typical_output_shapes",
        "current_default_access",
        "live_access_default",
        "fixture_replay_required",
        "policy_gates_required",
        "forbidden_default_operations",
        "no_goals",
    }
    missing = sorted(required - set(family))
    if missing:
        errors.append(f"{label} missing fields: {', '.join(missing)}")
    if family.get("schema_version") != "connector_family.v0":
        errors.append(f"{label} schema_version must be connector_family.v0")
    if family.get("live_access_default") is not False:
        errors.append(f"{label} live_access_default must be false")
    if family.get("fixture_replay_required") is not True:
        errors.append(f"{label} fixture_replay_required must be true")
    if "download_binary" in _strings(family.get("typical_output_shapes")):
        errors.append(f"{label} must not list download_binary as output")
    for source_family in _strings(family.get("source_families_supported")):
        if source_family not in KNOWN_SOURCE_FAMILIES:
            errors.append(f"{label} unknown source_family: {source_family}")
    allowed_default = set(_strings(family.get("allowed_default_operations")))
    overlap = sorted(allowed_default & FORBIDDEN_DEFAULT_OPERATIONS)
    if overlap:
        errors.append(f"{label} forbidden operations allowed by default: {', '.join(overlap)}")
    validate_boundaries(family, label, errors)


def validate_capability_and_policy(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    capability_policy = payloads.get("control/inventory/connectors/connector_capability_policy.json", {})
    if capability_policy.get("capability_is_permission") is not False:
        errors.append("connector_capability_policy.capability_is_permission must be false")
    interface_policy = payloads.get("control/inventory/connectors/connector_interface_policy.json", {})
    if interface_policy.get("supported_operation_declarations_grant_permission") is not False:
        errors.append("supported operation declarations must not grant permission")
    no_live = payloads.get("control/inventory/connectors/connector_no_live_call_policy.json", {})
    for key in (
        "h0_bundle_02_enables_live_source_calls",
        "h0_bundle_02_enables_live_probes",
        "h0_bundle_02_enables_source_sync",
        "connector_interface_grants_permission",
        "fixture_replay_grants_permission",
        "live_probe_envelope_grants_permission",
        "policy_evaluation_executes_connector",
        "network_calls_made",
    ):
        if no_live.get(key) is not False:
            errors.append(f"connector_no_live_call_policy.{key} must be false")
    output = payloads.get("control/inventory/connectors/connector_output_envelope_policy.json", {})
    for item in ("accepted_source_truth", "accepted_evidence_truth", "public_index_mutation", "master_index_mutation", "downloaded_file", "executed_artifact"):
        if item not in _strings(output.get("forbidden_output_types")):
            errors.append(f"connector_output_envelope_policy must forbid {item}")
    operation_request = {"connector_id": "test", "source_id": "test", "requested_operation": "download_binary"}
    decision = evaluate_connector_policy(operation_request, {"connector_policy_evaluation_policy": payloads.get("control/inventory/connectors/connector_policy_evaluation_policy.json", {})})
    if decision.get("decision") != "blocked_by_forbidden_operation":
        errors.append("policy evaluator must block download_binary")


def validate_examples(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    for rel in FAMILY_EXAMPLES:
        validate_family(payloads.get(rel, {}), rel, errors)
    for rel in FIXTURE_REPLAY_EXAMPLES + LIVE_PROBE_EXAMPLES + OUTPUT_ENVELOPE_EXAMPLES:
        payload = payloads.get(rel, {})
        validate_boundaries(payload, rel, errors)
        if rel.endswith("fixture_replay_result_v0.json"):
            if payload.get("no_network_used") is not True or payload.get("no_live_source_used") is not True:
                errors.append(f"{rel} must be no-network fixture replay")
        if rel.endswith("live_probe_envelope_blocked_result_v0.json"):
            if payload.get("result_status") != "blocked" or payload.get("network_used") is not False:
                errors.append(f"{rel} must be blocked with network_used false")
        if "output_envelopes" in rel:
            try:
                validate_connector_output_envelope(payload, {})
            except Exception as exc:  # noqa: BLE001
                errors.append(f"{rel} invalid output envelope: {exc}")


def validate_audit_report(payloads: Mapping[str, Mapping[str, Any]], errors: list[str]) -> None:
    report = payloads.get("control/audits/h0-bundle-02-connector-interface-replay-v0/h0_bundle_02_report.json", {})
    if not report:
        return
    if report.get("schema_version") != "h0_bundle_02_report.v0":
        errors.append("h0 bundle 02 report schema_version mismatch")
    scope = report.get("connector_scope", {})
    if isinstance(scope, Mapping):
        for key in ("new_live_connector_added", "live_access_enabled", "source_sync_enabled", "network_calls_made"):
            if scope.get(key) is not False:
                errors.append(f"h0 bundle 02 report connector_scope.{key} must be false")
    validate_boundaries(report, "h0_bundle_02_report", errors)


def validate_runtime_imports(root: Path, errors: list[str]) -> None:
    for rel in PYTHON_SCAN_PATHS:
        path = root / rel
        if not path.is_file():
            errors.append(f"missing Python file: {rel}")
            continue
        text = path.read_text(encoding="utf-8")
        for match in BANNED_IMPORT_RE.finditer(text):
            errors.append(f"forbidden import in {rel}: {match.group(1)}")
        if ("url" + "open(") in text or (".Re" + "quest(") in text:
            errors.append(f"runtime/script must not perform live calls in H0-BUNDLE-02: {rel}")


def validate_scripts(root: Path, errors: list[str]) -> None:
    commands = (
        [sys.executable, "scripts/summarize_connector_families.py", "--input", "examples/connectors/core/families", "--check"],
        [sys.executable, "scripts/run_connector_fixture_replay.py", "--request", "examples/connectors/core/fixture_replay/minimal_fixture_replay_request_v0.json", "--check"],
        [sys.executable, "scripts/evaluate_connector_policy.py", "--request", "examples/connectors/core/live_probe/policy_blocked_live_probe_request_v0.json", "--check"],
    )
    for command in commands:
        result = subprocess.run(command, cwd=root, check=False, capture_output=True, text=True, timeout=120)
        if result.returncode != 0:
            errors.append(f"script failed: {' '.join(command)} :: {result.stdout} {result.stderr}")


def validate_no_private_roots(root: Path, errors: list[str]) -> None:
    for rel in (".aide.local", ".local/eureka", ".cache/eureka"):
        if (root / rel).exists():
            errors.append(f"local private root must not be created: {rel}")


def validate_boundaries(payload: Mapping[str, Any], label: str, errors: list[str]) -> None:
    errors.extend(f"{label}: {error}" for error in detect_connector_truth_boundary_violations(payload, None))
    errors.extend(f"{label}: {error}" for error in detect_connector_product_boundary_violations(payload, None))
    text = json.dumps(payload, sort_keys=True)
    for term in FORBIDDEN_TERMS:
        if term in text:
            errors.append(f"{label}: forbidden true term present: {term}")


def load_json_object(path: Path, errors: list[str]) -> Mapping[str, Any]:
    if not path.is_file():
        errors.append(f"missing JSON: {rel(path)}")
        return {}
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception as exc:  # noqa: BLE001
        errors.append(f"invalid JSON: {rel(path)}: {exc}")
        return {}
    if not isinstance(payload, Mapping):
        errors.append(f"JSON must be an object: {rel(path)}")
        return {}
    return payload


def _strings(value: Any) -> list[str]:
    if isinstance(value, list):
        return [str(item) for item in value if item not in (None, "")]
    if value in (None, ""):
        return []
    return [str(value)]


def rel(path: Path) -> str:
    try:
        return path.relative_to(REPO_ROOT).as_posix()
    except ValueError:
        return path.as_posix()


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)
    report = validate_repo(REPO_ROOT)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True), file=stdout)
    else:
        print(f"status: {report['status']}", file=stdout)
        for error in report["errors"]:
            print(f"ERROR: {error}", file=stdout)
    return 0 if report["status"] == "valid" else 1


if __name__ == "__main__":
    raise SystemExit(main())
