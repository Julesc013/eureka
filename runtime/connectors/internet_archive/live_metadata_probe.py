"""Fail-closed Internet Archive metadata live-probe helpers.

The module can perform one approved metadata endpoint request, but only after
committed policy gates explicitly approve that exact identifier and endpoint.
Pending policy produces a blocked result without network access.
"""

from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time
from typing import Any, Mapping
import urllib.error
import urllib.request

from runtime.connectors.internet_archive.metadata_normalizer import (
    map_normalized_to_source_cache_candidate,
    normalize_ia_metadata,
    preview_evidence_candidates,
)


SOURCE_ID = "internet_archive"
CONNECTOR_ID = "internet_archive_metadata_connector"
METADATA_ENDPOINT_TEMPLATE = "https://archive.org/metadata/{identifier}"

POLICY_PATHS = {
    "source_policy": "control/inventory/connectors/internet_archive_source_policy.json",
    "endpoint_policy": "control/inventory/connectors/internet_archive_endpoint_policy.json",
    "rate_limit_policy": "control/inventory/connectors/internet_archive_rate_limit_policy.json",
    "cache_policy": "control/inventory/connectors/internet_archive_cache_policy.json",
    "kill_switch_policy": "control/inventory/connectors/internet_archive_kill_switch_policy.json",
    "live_probe_policy": "control/inventory/connectors/internet_archive_live_probe_policy.json",
    "allowed_identifier_policy": "control/inventory/connectors/internet_archive_live_probe_allowed_identifiers.json",
    "output_policy": "control/inventory/connectors/internet_archive_live_probe_output_policy.json",
    "path_policy": "control/inventory/connectors/internet_archive_live_probe_path_policy.json",
    "review_policy": "control/inventory/connectors/internet_archive_live_probe_review_policy.json",
    "truth_policy": "control/inventory/connectors/internet_archive_live_probe_truth_policy.json",
    "normalization_policy": "control/inventory/connectors/internet_archive_normalization_policy.json",
    "source_cache_mapping_policy": "control/inventory/connectors/internet_archive_source_cache_mapping_policy.json",
    "evidence_mapping_policy": "control/inventory/connectors/internet_archive_evidence_mapping_policy.json",
}

FORBIDDEN_TRUE_KEYS = {
    "accepted_as_public_truth",
    "accepted_candidate_truth",
    "accepted_evidence",
    "accepted_evidence_truth",
    "accepted_public_record",
    "accepted_public_truth",
    "download_permission_granted",
    "downloaded_file",
    "enabled_accounts",
    "enabled_downloads",
    "enabled_hosting",
    "enabled_live_public_fanout",
    "enabled_source_sync",
    "enabled_telemetry",
    "enabled_uploads",
    "evidence_candidate_preview_is_accepted_evidence",
    "evidence_preview_is_accepted_evidence",
    "file_download_approved",
    "file_fetch_approved",
    "item_file_payload",
    "live_probe_can_claim_malware_safety",
    "live_probe_can_claim_rights_clearance",
    "live_probe_can_claim_verified_installability",
    "live_probe_can_mutate_master_index",
    "live_probe_can_mutate_public_index",
    "live_probe_result_is_accepted_evidence",
    "live_probe_result_is_truth",
    "malware_safety_claimed",
    "master_index_mutated",
    "mutated_master_index",
    "mutated_public_index",
    "public_index_mutated",
    "review_queue_seed_is_review_decision",
    "review_seed_is_review_decision",
    "rights_clearance_claimed",
    "source_cache_candidate_is_accepted_source",
    "verified_installability_claimed",
}


class LiveProbeBlocked(RuntimeError):
    """Raised when policy blocks the live metadata probe before network use."""

    def __init__(self, result: Mapping[str, Any]):
        super().__init__("IA metadata live probe blocked by committed policy")
        self.result = dict(result)


def load_policy_bundle(repo_root: str | Path) -> dict[str, Any]:
    root = Path(repo_root)
    bundle: dict[str, Any] = {}
    for key, rel_path in POLICY_PATHS.items():
        path = root / rel_path
        with path.open("r", encoding="utf-8") as handle:
            bundle[key] = json.load(handle)
    return bundle


def validate_live_probe_policy(policy_bundle: Mapping[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []
    source = _mapping(policy_bundle.get("source_policy"))
    endpoint = _mapping(policy_bundle.get("endpoint_policy"))
    rate = _mapping(policy_bundle.get("rate_limit_policy"))
    cache = _mapping(policy_bundle.get("cache_policy"))
    kill = _mapping(policy_bundle.get("kill_switch_policy"))
    live = _mapping(policy_bundle.get("live_probe_policy"))

    _require_true(source.get("live_access_approved"), "source_policy.live_access_approved", reasons)
    _require_true(source.get("metadata_probe_approved"), "source_policy.metadata_probe_approved", reasons)
    _require_false(source.get("file_download_approved"), "source_policy.file_download_approved", reasons)
    _require_false(source.get("item_file_fetch_approved"), "source_policy.item_file_fetch_approved", reasons)
    _require_false(source.get("scraping_approved"), "source_policy.scraping_approved", reasons)
    _require_false(source.get("public_query_fanout_approved"), "source_policy.public_query_fanout_approved", reasons)

    _require_true(live.get("live_probe_enabled"), "live_probe_policy.live_probe_enabled", reasons)
    if live.get("approval_status") not in {"approved", "approved_for_single_identifier_metadata_read"}:
        reasons.append("live_probe_policy.approval_status is not approved")
    if live.get("live_probe_scope") != "single_identifier_metadata_read":
        reasons.append("live_probe_policy.live_probe_scope must be single_identifier_metadata_read")

    templates = live.get("allowed_endpoint_templates")
    if not isinstance(templates, list) or templates != [METADATA_ENDPOINT_TEMPLATE]:
        reasons.append("live_probe_policy.allowed_endpoint_templates must contain only the metadata endpoint")
    if live.get("allowed_http_methods") != ["GET"]:
        reasons.append("live_probe_policy.allowed_http_methods must be exactly ['GET']")
    if endpoint.get("current_allowed_endpoint_behavior") not in {"approved_metadata_read_only", "single_identifier_metadata_read"}:
        reasons.append("endpoint_policy current behavior does not approve metadata read only")
    if endpoint.get("current_network_calls_allowed") is not True:
        reasons.append("endpoint_policy.current_network_calls_allowed must be true")
    forbidden_endpoint = endpoint.get("forbidden_current")
    if isinstance(forbidden_endpoint, Mapping):
        for key in ("downloads", "file_fetches", "item_file_downloads", "unbounded_search", "scraping", "crawling", "public_query_live_fanout"):
            _require_true(forbidden_endpoint.get(key), f"endpoint_policy.forbidden_current.{key}", reasons)

    omission_approved = live.get("user_agent_contact_omission_approved") is True
    if not omission_approved:
        if _is_pending(rate.get("proposed_user_agent")):
            reasons.append("rate_limit_policy.proposed_user_agent is pending")
        if _is_pending(rate.get("contact_email")):
            reasons.append("rate_limit_policy.contact_email is pending")
    timeout = rate.get("timeout_seconds")
    if not isinstance(timeout, (int, float)) or timeout <= 0:
        reasons.append("rate_limit_policy.timeout_seconds must be a positive number")
    budget = rate.get("max_requests_per_minute")
    if not isinstance(budget, (int, float)) or budget <= 0:
        reasons.append("rate_limit_policy.max_requests_per_minute must be a positive number")
    if _is_pending(rate.get("retry_policy")):
        reasons.append("rate_limit_policy.retry_policy is pending")
    cache_ttl = cache.get("cache_ttl")
    no_cache = cache.get("no_cache_decision_approved") is True
    if _is_pending(cache_ttl) and not no_cache:
        reasons.append("cache_policy.cache_ttl or no-cache decision must be approved")

    kill_allows = kill.get("default_enabled") is True or kill.get("allow_one_probe") is True
    if not kill_allows:
        reasons.append("kill_switch_policy does not allow this one probe")
    if kill.get("failure_mode") != "fail_closed":
        reasons.append("kill_switch_policy.failure_mode must be fail_closed")

    return {
        "approved": not reasons,
        "blocked_reasons": reasons,
        "metadata_endpoint": METADATA_ENDPOINT_TEMPLATE,
        "request_limit": 1,
    }


def validate_identifier_allowed(identifier: str, allowed_identifier_policy: Mapping[str, Any]) -> dict[str, Any]:
    reasons: list[str] = []
    if not _identifier_is_safe(identifier):
        reasons.append("identifier contains characters outside the approved safe set")
    approved = allowed_identifier_policy.get("approved_identifiers")
    if not isinstance(approved, list):
        reasons.append("approved_identifiers must be a list")
        approved = []
    if allowed_identifier_policy.get("approval_status") not in {"approved", "approved_for_single_identifier_metadata_read"}:
        reasons.append("allowed identifier policy is not approved")
    if identifier not in approved:
        reasons.append(f"identifier is not approved: {identifier}")
    if allowed_identifier_policy.get("max_identifiers_current") != 1:
        reasons.append("max_identifiers_current must be 1")
    if allowed_identifier_policy.get("max_identifiers_per_run") != 1:
        reasons.append("max_identifiers_per_run must be 1")
    return {"approved": not reasons, "blocked_reasons": reasons}


def build_metadata_url(identifier: str) -> str:
    if not _identifier_is_safe(identifier):
        raise ValueError("identifier contains characters outside the approved safe set")
    return METADATA_ENDPOINT_TEMPLATE.format(identifier=identifier)


def fetch_ia_metadata_once(identifier: str, policy_bundle: Mapping[str, Any]) -> tuple[dict[str, Any], dict[str, Any]]:
    policy_result = validate_live_probe_policy(policy_bundle)
    identifier_result = validate_identifier_allowed(identifier, _mapping(policy_bundle.get("allowed_identifier_policy")))
    blocked_reasons = policy_result["blocked_reasons"] + identifier_result["blocked_reasons"]
    if blocked_reasons:
        raise LiveProbeBlocked(build_blocked_live_probe_result(identifier, policy_bundle, blocked_reasons))

    url = build_metadata_url(identifier)
    rate = _mapping(policy_bundle.get("rate_limit_policy"))
    timeout = float(rate["timeout_seconds"])
    user_agent = str(rate.get("proposed_user_agent"))
    request = urllib.request.Request(url, headers={"User-Agent": user_agent}, method="GET")
    start = time.monotonic()
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            final_url = response.geturl()
            if not str(final_url).startswith("https://archive.org/metadata/"):
                raise LiveProbeBlocked(build_blocked_live_probe_result(identifier, policy_bundle, [f"forbidden redirect target: {final_url}"]))
            raw = response.read()
            duration_ms = round((time.monotonic() - start) * 1000, 3)
            payload = json.loads(raw.decode("utf-8"))
            if not isinstance(payload, dict):
                raise ValueError("IA metadata response must be a JSON object")
            metadata = {
                "url": url,
                "final_url": str(final_url),
                "status": getattr(response, "status", None),
                "content_type": response.headers.get("Content-Type", ""),
                "duration_ms": duration_ms,
                "response_sha256": hashlib.sha256(raw).hexdigest(),
                "fetched_at_utc": _now_utc(),
                "request_count": 1,
            }
            return payload, metadata
    except urllib.error.URLError as exc:
        raise RuntimeError(f"IA metadata request failed: {exc}") from exc


def build_live_probe_result(
    identifier: str,
    response_payload: Mapping[str, Any],
    response_metadata: Mapping[str, Any],
    policy_bundle: Mapping[str, Any],
) -> dict[str, Any]:
    result = {
        "schema_version": "internet_archive_live_probe_result.v0",
        "probe_id": _probe_id(identifier),
        "source_id": SOURCE_ID,
        "connector_id": CONNECTOR_ID,
        "identifier": identifier,
        "endpoint": build_metadata_url(identifier),
        "result_status": "completed",
        "attempted": True,
        "blocked_by_policy": False,
        "blocked_reasons": [],
        "request_count": 1,
        "network_used": True,
        "http_method": "GET",
        "response_metadata": dict(response_metadata),
        "response_payload": dict(response_payload),
        "source_observation_only": True,
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(network_allowed_for_probe=True),
        "notes": [
            "One approved metadata endpoint response is a source observation only.",
            "No file download, item file fetch, scraping, source sync, public-index mutation, or master-index mutation occurred.",
        ],
    }
    _raise_on_live_probe_boundary_errors(result)
    return result


def build_blocked_live_probe_result(
    identifier: str | None,
    policy_bundle: Mapping[str, Any],
    blocked_reasons: list[str],
) -> dict[str, Any]:
    endpoint = METADATA_ENDPOINT_TEMPLATE if not identifier else build_metadata_url(identifier)
    return {
        "schema_version": "internet_archive_live_probe_result.v0",
        "probe_id": _probe_id(identifier or "not_selected"),
        "source_id": SOURCE_ID,
        "connector_id": CONNECTOR_ID,
        "identifier": identifier,
        "endpoint": endpoint,
        "result_status": "blocked",
        "attempted": False,
        "blocked_by_policy": True,
        "blocked_reasons": blocked_reasons,
        "request_count": 0,
        "network_used": False,
        "http_method": "GET",
        "response_metadata": None,
        "response_payload": None,
        "source_observation_only": True,
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(network_allowed_for_probe=False),
        "notes": [
            "No external call was made because committed policy did not approve the probe.",
            "Operator approval is required before IA-BUNDLE-02 can perform a live metadata read.",
        ],
    }


def normalize_live_probe_result(live_probe_result: Mapping[str, Any], normalization_policy: Mapping[str, Any]) -> dict[str, Any]:
    if live_probe_result.get("result_status") != "completed":
        raise LiveProbeBlocked(dict(live_probe_result))
    payload = _mapping(live_probe_result.get("response_payload"))
    metadata = _mapping(payload.get("metadata"))
    fixture_like = {
        "source_id": SOURCE_ID,
        "connector_id": CONNECTOR_ID,
        "fixture_kind": "live_probe_metadata_response",
        "fixture_status": "live_probe_observation",
        "live_call_used": False,
        "network_used": False,
        "external_api_used": False,
        "raw_metadata": {
            "metadata": metadata,
            "files": payload.get("files", []),
        },
        "limitations": [
            "normalized from a bounded live metadata probe",
            "live response is a source observation, not truth",
        ],
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(network_allowed_for_probe=False),
    }
    record = normalize_ia_metadata(fixture_like, policy=normalization_policy)
    record["source_observation_origin"] = "ia_bundle_02_live_probe"
    record["live_probe_result_ref"] = live_probe_result.get("probe_id")
    record["notes"] = [
        "Normalized from an IA-BUNDLE-02 live metadata probe result.",
        "No file download, item file fetch, scraping, public-index mutation, or master-index mutation occurred.",
    ]
    _raise_on_live_probe_boundary_errors(record)
    return record


def map_live_probe_to_source_cache_candidate(
    normalized_record: Mapping[str, Any],
    mapping_policy: Mapping[str, Any],
) -> dict[str, Any]:
    candidate = map_normalized_to_source_cache_candidate(normalized_record, policy=mapping_policy)
    candidate["schema_version"] = "internet_archive_live_probe_source_cache_candidate_preview.v0"
    candidate["mapping_status"] = "live_probe_preview_only"
    candidate["source_observation_origin"] = "ia_bundle_02_live_probe"
    candidate["source_cache_runtime_mutated"] = False
    candidate["accepted_source_truth"] = False
    _raise_on_live_probe_boundary_errors(candidate)
    return candidate


def preview_live_probe_evidence_candidates(
    normalized_record: Mapping[str, Any],
    evidence_policy: Mapping[str, Any],
) -> dict[str, Any]:
    preview = preview_evidence_candidates(normalized_record, policy=evidence_policy)
    preview["schema_version"] = "internet_archive_live_probe_evidence_candidate_preview.v0"
    preview["source_observation_origin"] = "ia_bundle_02_live_probe"
    preview["evidence_ledger_runtime_mutated"] = False
    preview["accepted_evidence"] = False
    _raise_on_live_probe_boundary_errors(preview)
    return preview


def build_review_queue_seed_preview(
    live_probe_result: Mapping[str, Any],
    source_cache_candidate: Mapping[str, Any],
    evidence_preview: Mapping[str, Any],
    review_policy: Mapping[str, Any],
) -> dict[str, Any]:
    identifier = str(live_probe_result.get("identifier") or "unknown")
    seed = {
        "schema_version": "internet_archive_live_probe_review_queue_seed_preview.v0",
        "seed_id": f"review_seed.internet_archive.{_short_hash(identifier)}.v0",
        "source_id": SOURCE_ID,
        "connector_id": CONNECTOR_ID,
        "identifier": live_probe_result.get("identifier"),
        "review_subject_type": "internet_archive_metadata_live_probe",
        "review_subject_ref": live_probe_result.get("probe_id"),
        "review_required": True,
        "review_queue_runtime_mutated": False,
        "review_seed_is_review_decision": False,
        "source_cache_candidate_ref": source_cache_candidate.get("candidate_id"),
        "evidence_preview_ref": evidence_preview.get("evidence_preview_id"),
        "required_reviews": {
            "source_cache_persistence": review_policy.get("review_required_before_source_cache_persistence") is True,
            "evidence_acceptance": review_policy.get("review_required_before_evidence_acceptance") is True,
            "candidate_acceptance": review_policy.get("review_required_before_candidate_acceptance") is True,
            "public_index_use": review_policy.get("review_required_before_public_index_use") is True,
            "master_index": review_policy.get("review_required_before_master_index") is True,
        },
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(network_allowed_for_probe=False),
        "notes": [
            "Review queue seed preview only; no review queue runtime write occurred.",
            "A seed is not a review decision.",
        ],
    }
    _raise_on_live_probe_boundary_errors(seed)
    return seed


def build_not_created_preview(kind: str, live_probe_result: Mapping[str, Any]) -> dict[str, Any]:
    preview = {
        "schema_version": f"internet_archive_live_probe_{kind}.not_created.v0",
        "status": "not_created_blocked_by_policy",
        "kind": kind,
        "identifier": live_probe_result.get("identifier"),
        "live_probe_result_ref": live_probe_result.get("probe_id"),
        "blocked_reasons": list(live_probe_result.get("blocked_reasons") or []),
        "accepted_source_truth": False,
        "accepted_evidence": False,
        "review_seed_is_review_decision": False,
        "runtime_mutated": False,
        "truth_boundary": _truth_boundary(),
        "product_boundary": _product_boundary(network_allowed_for_probe=False),
    }
    _raise_on_live_probe_boundary_errors(preview)
    return preview


def summarize_live_probe_result(result: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "identifier": result.get("identifier"),
        "result_status": result.get("result_status"),
        "attempted": result.get("attempted") is True,
        "blocked_by_policy": result.get("blocked_by_policy") is True,
        "request_count": result.get("request_count", 0),
        "network_used": result.get("network_used") is True,
        "blocked_reasons": list(result.get("blocked_reasons") or []),
        "public_index_mutated": False,
        "master_index_mutated": False,
    }


def detect_live_probe_truth_boundary_violations(result: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    return [f"truth boundary violation: {path}=true" for path, key, value in _iter_key_values(result) if key in FORBIDDEN_TRUE_KEYS and value is True]


def detect_live_probe_product_boundary_violations(result: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> list[str]:
    return [f"product boundary violation: {path}=true" for path, key, value in _iter_key_values(result) if key in FORBIDDEN_TRUE_KEYS and value is True]


def _raise_on_live_probe_boundary_errors(result: Mapping[str, Any]) -> None:
    errors = detect_live_probe_truth_boundary_violations(result) + detect_live_probe_product_boundary_violations(result)
    if errors:
        raise ValueError("; ".join(errors))


def _truth_boundary() -> dict[str, bool]:
    return {
        "live_probe_result_is_truth": False,
        "live_probe_result_is_accepted_evidence": False,
        "source_cache_candidate_is_accepted_source": False,
        "evidence_candidate_preview_is_accepted_evidence": False,
        "review_queue_seed_is_review_decision": False,
        "live_probe_can_mutate_public_index": False,
        "live_probe_can_mutate_master_index": False,
        "live_probe_can_claim_rights_clearance": False,
        "live_probe_can_claim_malware_safety": False,
        "live_probe_can_claim_verified_installability": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "rights_clearance_claimed": False,
        "malware_safety_claimed": False,
        "verified_installability_claimed": False,
    }


def _product_boundary(network_allowed_for_probe: bool) -> dict[str, bool]:
    return {
        "changed_public_search_behavior": False,
        "enabled_hosting": False,
        "enabled_live_public_fanout": False,
        "enabled_source_sync": False,
        "enabled_downloads": False,
        "enabled_uploads": False,
        "enabled_accounts": False,
        "enabled_telemetry": False,
        "mutated_public_index": False,
        "mutated_master_index": False,
        "metadata_endpoint_only": True,
        "single_identifier_only": True,
        "network_allowed_for_this_probe": network_allowed_for_probe,
    }


def _probe_id(identifier: str) -> str:
    return f"ia_live_probe.{_short_hash(identifier)}.v0"


def _short_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:12]


def _now_utc() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def _identifier_is_safe(identifier: str) -> bool:
    if not isinstance(identifier, str) or not identifier:
        return False
    allowed = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._-")
    return all(char in allowed for char in identifier)


def _is_pending(value: Any) -> bool:
    return value in {None, "", "pending", "pending_operator_approval"}


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _require_true(value: Any, label: str, reasons: list[str]) -> None:
    if value is not True:
        reasons.append(f"{label} must be true")


def _require_false(value: Any, label: str, reasons: list[str]) -> None:
    if value is not False:
        reasons.append(f"{label} must be false")


def _iter_key_values(value: Any, prefix: str = ""):
    if isinstance(value, Mapping):
        for key, nested in value.items():
            key_text = str(key)
            path = f"{prefix}.{key_text}" if prefix else key_text
            yield path, key_text, nested
            yield from _iter_key_values(nested, path)
    elif isinstance(value, list):
        for index, nested in enumerate(value):
            yield from _iter_key_values(nested, f"{prefix}[{index}]")
