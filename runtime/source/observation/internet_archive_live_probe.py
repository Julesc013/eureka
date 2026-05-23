"""IA-02 bounded live Internet Archive metadata probe runtime."""

from __future__ import annotations

import hashlib
import json
import re
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable, Mapping

from runtime.source.observation.internet_archive_live_transport import (
    IALiveTransport,
    IALiveTransportPolicy,
    IALiveTransportResponse,
    response_json,
)
from runtime.source.observation.internet_archive_metadata import FORBIDDEN_SIDE_EFFECT_FLAGS
from runtime.source.observation.internet_archive_normalization import normalize_ia_metadata_fixture


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_POLICY_PATH = REPO_ROOT / "control" / "policies" / "ia_live_probe_policy.json"
IA_BASE_URL = "https://archive.org"
SAFE_IDENTIFIER_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")


def load_live_probe_policy(path: str | Path = DEFAULT_POLICY_PATH) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def build_metadata_search_request(policy: Mapping[str, Any], query: str, rows: int | None = None) -> dict[str, Any]:
    requested_rows = int(rows if rows is not None else policy.get("metadata_search_rows_max", 1))
    max_rows = int(policy.get("metadata_search_rows_max", 1))
    if requested_rows < 0 or requested_rows > max_rows:
        raise ValueError("metadata search row cap exceeded")
    params = [
        ("q", query),
        ("fl[]", "identifier"),
        ("fl[]", "title"),
        ("fl[]", "mediatype"),
        ("fl[]", "collection"),
        ("fl[]", "creator"),
        ("fl[]", "date"),
        ("fl[]", "description"),
        ("rows", str(requested_rows)),
        ("page", "1"),
        ("output", "json"),
    ]
    query_string = urllib.parse.urlencode(params)
    return {
        "request_id": "ia02_metadata_search",
        "endpoint_class": "metadata_search_small",
        "method": "GET",
        "url": f"{IA_BASE_URL}/advancedsearch.php?{query_string}",
        "query_or_identifier": query,
        "rows": requested_rows,
        "metadata_only": True,
    }


def build_item_metadata_request(policy: Mapping[str, Any], identifier: str) -> dict[str, Any]:
    _ = policy
    if not SAFE_IDENTIFIER_RE.match(identifier):
        raise ValueError("IA identifier is not exact-safe for IA-02")
    encoded_identifier = urllib.parse.quote(identifier, safe="")
    return {
        "request_id": "ia02_item_metadata",
        "endpoint_class": "item_metadata_read",
        "method": "GET",
        "url": f"{IA_BASE_URL}/metadata/{encoded_identifier}",
        "query_or_identifier": identifier,
        "rows": 0,
        "metadata_only": True,
    }


def run_live_metadata_probe(
    policy: Mapping[str, Any],
    *,
    approve_live: bool = False,
    dry_run: bool = False,
    query: str | None = None,
    identifier: str | None = None,
    rows: int | None = None,
    max_requests: int | None = None,
    client_label: str = "",
    contact: str = "",
    kill_switch_enabled: bool = True,
    transport_factory: Callable[[IALiveTransportPolicy], IALiveTransport] | None = None,
) -> dict[str, Any]:
    if not dry_run and not approve_live:
        raise RuntimeError("--approve-live is required for IA-02 network access")
    _validate_live_policy(policy)
    query_text = query or str(policy.get("default_query", "sampleproject"))
    requested_rows = int(rows if rows is not None else policy.get("metadata_search_rows_max", 1))
    request_cap = int(max_requests if max_requests is not None else policy.get("total_http_requests_max", 2))
    _enforce_caps(policy, requested_rows, request_cap)

    request_plan = [build_metadata_search_request(policy, query_text, requested_rows)]
    if identifier:
        request_plan.append(build_item_metadata_request(policy, identifier))
    if dry_run:
        summary = _base_summary(
            policy=policy,
            query=query_text,
            request_plan=request_plan,
            approved_live=False,
            dry_run=True,
            client_label=client_label,
            contact=contact,
        )
        boundary = build_live_probe_boundary_report(
            approved_live=False,
            dry_run=True,
            total_http_requests=0,
            live_source_call_performed=False,
            source_probe_executed=False,
            raw_response_committed=False,
        )
        return _report(
            policy=policy,
            request_plan=request_plan,
            summary=summary,
            normalized_preview=[],
            boundary_report=boundary,
            dry_run=True,
        )

    if not client_label.strip():
        raise RuntimeError("HTTP client label is required for approved IA-02 live probe")
    if not contact.strip():
        raise RuntimeError("contact is required for approved IA-02 live probe")

    transport_policy = IALiveTransportPolicy(
        allowed_domains=tuple(str(item) for item in policy.get("allowed_domains", [])),
        total_http_requests_max=request_cap,
        timeout_seconds_max=int(policy.get("timeout_seconds_max", 10)),
        retry_attempts_max=int(policy.get("retry_attempts_max", 1)),
        honor_retry_after=bool(policy.get("honor_retry_after", True)),
    )
    transport = transport_factory(transport_policy) if transport_factory else IALiveTransport(transport_policy)
    responses: list[IALiveTransportResponse] = []
    normalized_records: list[Mapping[str, Any]] = []
    search_docs: list[Mapping[str, Any]] = []
    rate_limited = False
    failed_reason = ""

    search_response = transport.get_json(
        url=request_plan[0]["url"],
        endpoint_class="metadata_search_small",
        client_label=client_label,
        contact=contact,
        timeout_seconds=int(policy.get("timeout_seconds_max", 10)),
        kill_switch_enabled=kill_switch_enabled,
    )
    responses.append(search_response)
    if search_response.rate_limited:
        rate_limited = True
        normalized_records.append(_normalize_retry_after(search_response, query_text).to_dict())
    elif search_response.status_code == 0:
        failed_reason = str(search_response.transport_error or "transport_error")
    elif search_response.status_code < 200 or search_response.status_code >= 300:
        failed_reason = f"http_status_{search_response.status_code}"
    else:
        search_json = response_json(search_response)
        search_docs = _extract_search_docs(search_json, requested_rows)
        normalized_records.append(_normalize_search(search_json, query_text, requested_rows).to_dict())
        returned_identifier = identifier or _first_identifier(search_docs)
        if returned_identifier and transport.request_count < request_cap:
            item_request = build_item_metadata_request(policy, returned_identifier)
            request_plan.append(item_request)
            item_response = transport.get_json(
                url=item_request["url"],
                endpoint_class="item_metadata_read",
                client_label=client_label,
                contact=contact,
                timeout_seconds=int(policy.get("timeout_seconds_max", 10)),
                kill_switch_enabled=kill_switch_enabled,
            )
            responses.append(item_response)
            if item_response.rate_limited:
                rate_limited = True
                normalized_records.append(_normalize_retry_after(item_response, query_text).to_dict())
            elif item_response.status_code == 0:
                failed_reason = str(item_response.transport_error or "transport_error")
            elif item_response.status_code < 200 or item_response.status_code >= 300:
                failed_reason = f"http_status_{item_response.status_code}"
            else:
                item_json = response_json(item_response)
                normalized_records.append(_normalize_item_metadata(item_json, returned_identifier).to_dict())

    redacted_preview = [_redact_normalized_record(record) for record in normalized_records]
    summary = _live_summary(
        policy=policy,
        query=query_text,
        request_plan=request_plan,
        responses=responses,
        normalized_preview=redacted_preview,
        client_label=client_label,
        contact=contact,
        requested_rows=requested_rows,
        returned_rows=len(search_docs),
        rate_limited=rate_limited,
        failed_reason=failed_reason,
    )
    boundary = build_live_probe_boundary_report(
        approved_live=True,
        dry_run=False,
        total_http_requests=len(responses),
        live_source_call_performed=bool(responses),
        source_probe_executed=bool(responses),
        raw_response_committed=False,
    )
    return _report(
        policy=policy,
        request_plan=request_plan,
        summary=summary,
        normalized_preview=redacted_preview,
        boundary_report=boundary,
        dry_run=False,
    )


def normalize_live_probe_result(report: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    return [dict(item) for item in report.get("normalized_preview", []) or []]


def redact_live_probe_result(report: Mapping[str, Any]) -> dict[str, Any]:
    return dict(report.get("redacted_summary", {}) or {})


def build_live_probe_boundary_report(
    *,
    approved_live: bool,
    dry_run: bool,
    total_http_requests: int,
    live_source_call_performed: bool,
    source_probe_executed: bool,
    raw_response_committed: bool,
) -> dict[str, Any]:
    flags = {key: False for key in FORBIDDEN_SIDE_EFFECT_FLAGS}
    flags["live_source_call_performed"] = live_source_call_performed
    flags["source_probe_executed"] = source_probe_executed
    violations: list[str] = []
    if raw_response_committed:
        violations.append("raw_response_committed")
    for key in (
        "source_cache_write_performed",
        "evidence_ledger_write_performed",
        "candidate_index_mutated",
        "reviewed_index_mutated",
        "master_index_mutated",
        "download_performed",
        "upload_performed",
        "model_provider_used",
        "deployment_performed",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    ):
        if flags[key]:
            violations.append(key)
    return {
        "schema_version": "ia_live_probe_boundary_report.v0",
        "task": "IA-02",
        "approved_live": approved_live,
        "dry_run": dry_run,
        "passed": not violations,
        "violations": violations,
        "total_http_requests": total_http_requests,
        "raw_response_committed": raw_response_committed,
        "downloads_enabled": False,
        "uploads_enabled": False,
        "write_apis_enabled": False,
        "public_search_fanout_enabled": False,
        "disallowed_host_accessed": False,
        **flags,
    }


def _validate_live_policy(policy: Mapping[str, Any]) -> None:
    if policy.get("schema_version") != "ia_live_probe_policy.v0":
        raise ValueError("IA-02 live probe policy missing or invalid")
    if policy.get("live_calls_require_approve_live_flag") is not True:
        raise ValueError("IA-02 live probe policy must require approval")
    if policy.get("raw_response_commit_forbidden") is not True:
        raise ValueError("IA-02 policy must forbid raw response commits")
    for key in (
        "downloads_enabled",
        "uploads_enabled",
        "write_apis_enabled",
        "public_search_fanout_enabled",
        "source_cache_writes_enabled",
        "evidence_ledger_writes_enabled",
        "candidate_index_mutation_enabled",
        "reviewed_index_mutation_enabled",
        "master_index_mutation_enabled",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    ):
        if policy.get(key) is not False:
            raise ValueError(f"IA-02 policy must keep {key} false")


def _enforce_caps(policy: Mapping[str, Any], rows: int, max_requests: int) -> None:
    if rows > int(policy.get("metadata_search_rows_max", 1)):
        raise ValueError("metadata search row cap exceeded")
    if max_requests > int(policy.get("total_http_requests_max", 2)):
        raise ValueError("total_http_requests_max exceeded")
    if max_requests < 1:
        raise ValueError("max_requests must be positive")


def _normalize_search(payload: Mapping[str, Any], query: str, rows: int) -> Any:
    return normalize_ia_metadata_fixture(
        {
            "fixture_id": "live_metadata_search_small",
            "fixture_class": "metadata_search_small",
            "endpoint_class": "metadata_search_small",
            "request": {"query": query, "rows": rows},
            "payload": payload,
        }
    )


def _normalize_item_metadata(payload: Mapping[str, Any], identifier: str) -> Any:
    body = dict(payload)
    metadata = dict(body.get("metadata", {}) or {})
    metadata.setdefault("identifier", identifier)
    body["metadata"] = metadata
    return normalize_ia_metadata_fixture(
        {
            "fixture_id": "live_item_metadata",
            "fixture_class": "item_metadata_read",
            "endpoint_class": "item_metadata_read",
            "request": {"identifier": identifier},
            "payload": body,
        }
    )


def _normalize_retry_after(response: IALiveTransportResponse, query: str) -> Any:
    return normalize_ia_metadata_fixture(
        {
            "fixture_id": "live_retry_after",
            "fixture_class": "retry_after_429",
            "endpoint_class": response.endpoint_class,
            "headers": {"Retry-After": str(response.retry_after_seconds or "")},
            "request": {"query": query},
            "payload": {},
        }
    )


def _extract_search_docs(payload: Mapping[str, Any], rows: int) -> list[Mapping[str, Any]]:
    response = payload.get("response", {}) or {}
    docs = response.get("docs", []) if isinstance(response, Mapping) else []
    return [dict(item) for item in docs[:rows] if isinstance(item, Mapping)]


def _first_identifier(docs: list[Mapping[str, Any]]) -> str:
    if not docs:
        return ""
    identifier = str(docs[0].get("identifier", ""))
    return identifier if SAFE_IDENTIFIER_RE.match(identifier) else ""


def _base_summary(
    *,
    policy: Mapping[str, Any],
    query: str,
    request_plan: list[Mapping[str, Any]],
    approved_live: bool,
    dry_run: bool,
    client_label: str,
    contact: str,
) -> dict[str, Any]:
    return {
        "schema_version": "ia_live_probe_redacted_summary.v0",
        "task": "IA-02",
        "probe_status": "dry_run" if dry_run else "planned",
        "approved_live": approved_live,
        "dry_run": dry_run,
        "request_timestamp_utc": _utc_now(),
        "query": query,
        "query_hash": _hash_text(query),
        "endpoint_classes_attempted": [str(item.get("endpoint_class", "")) for item in request_plan],
        "total_http_requests": 0,
        "policy_max_requests": int(policy.get("total_http_requests_max", 2)),
        "metadata_search_rows_requested": int(policy.get("metadata_search_rows_max", 1)),
        "metadata_search_rows_returned": 0,
        "identifier_count": 0,
        "identifier_hashes": [],
        "normalized_preview_count": 0,
        "client_label_present": bool(str(client_label).strip()),
        "contact_present": bool(str(contact).strip()),
        "http_responses": [],
        "raw_response_committed": False,
    }


def _live_summary(
    *,
    policy: Mapping[str, Any],
    query: str,
    request_plan: list[Mapping[str, Any]],
    responses: list[IALiveTransportResponse],
    normalized_preview: list[Mapping[str, Any]],
    client_label: str,
    contact: str,
    requested_rows: int,
    returned_rows: int,
    rate_limited: bool,
    failed_reason: str,
) -> dict[str, Any]:
    identifier_hashes = [
        str(item.get("item_identifier_hash", ""))
        for item in normalized_preview
        if str(item.get("item_identifier_hash", ""))
    ]
    if failed_reason:
        status = "failed"
    elif rate_limited:
        status = "rate_limited"
    elif returned_rows == 0:
        status = "zero_results"
    else:
        status = "succeeded"
    summary = _base_summary(
        policy=policy,
        query=query,
        request_plan=request_plan,
        approved_live=True,
        dry_run=False,
        client_label=client_label,
        contact=contact,
    )
    summary.update(
        {
            "probe_status": status,
            "failure_reason": failed_reason,
            "endpoint_classes_attempted": [response.endpoint_class for response in responses],
            "total_http_requests": len(responses),
            "metadata_search_rows_requested": requested_rows,
            "metadata_search_rows_returned": returned_rows,
            "identifier_count": len(identifier_hashes),
            "identifier_hashes": identifier_hashes,
            "normalized_preview_count": len(normalized_preview),
            "live_probe_rate_limited": rate_limited,
            "http_responses": [response.metadata() for response in responses],
        }
    )
    return summary


def _redact_normalized_record(record: Mapping[str, Any]) -> dict[str, Any]:
    identifier = str(record.get("item_identifier", ""))
    return {
        "schema_version": "ia_live_normalized_preview.v0",
        "source_id": str(record.get("source_id", "internet_archive_metadata")),
        "observation_id": str(record.get("observation_id", "")),
        "fixture_id": str(record.get("fixture_id", "")),
        "observation_kind": str(record.get("observation_kind", "")),
        "item_identifier_hash": _hash_text(identifier) if identifier else "",
        "title_candidate_present": bool(record.get("title_candidate")),
        "mediatype_candidate": str(record.get("mediatype_candidate", "")),
        "collection_candidate_count": len(record.get("collection_candidates", []) or []),
        "creator_candidate_present": bool(record.get("creator_candidate")),
        "date_candidate_present": bool(record.get("date_candidate")),
        "description_candidate_present": bool(record.get("description_candidate")),
        "file_metadata_candidate_count": len(record.get("file_metadata_candidates", []) or []),
        "checksum_candidate_count": len(record.get("checksum_candidates", []) or []),
        "limitations": list(record.get("limitations", []) or []),
        "risk_flags": list(record.get("risk_flags", []) or []),
        "rights_flags": list(record.get("rights_flags", []) or []),
        "confidence": float(record.get("confidence", 0.0)),
        "review_required": bool(record.get("review_required", True)),
        "accepted_truth": bool(record.get("accepted_truth", False)),
        "download_performed": bool(record.get("download_performed", False)),
        "source_cache_write_performed": bool(record.get("source_cache_write_performed", False)),
        "evidence_ledger_write_performed": bool(record.get("evidence_ledger_write_performed", False)),
        "index_mutation_performed": bool(record.get("index_mutation_performed", False)),
        "candidate_index_mutated": False,
        "reviewed_index_mutated": False,
        "master_index_mutated": False,
    }


def _report(
    *,
    policy: Mapping[str, Any],
    request_plan: list[Mapping[str, Any]],
    summary: Mapping[str, Any],
    normalized_preview: list[Mapping[str, Any]],
    boundary_report: Mapping[str, Any],
    dry_run: bool,
) -> dict[str, Any]:
    return {
        "schema_version": "ia_live_probe_report.v0",
        "task": "IA-02",
        "dry_run": dry_run,
        "policy_id": str(policy.get("schema_version", "")),
        "request_plan": [_redact_request_plan_item(item) for item in request_plan],
        "redacted_summary": dict(summary),
        "normalized_preview": [dict(item) for item in normalized_preview],
        "boundary_report": dict(boundary_report),
    }


def _redact_request_plan_item(item: Mapping[str, Any]) -> dict[str, Any]:
    url = str(item.get("url", ""))
    parsed = urllib.parse.urlparse(url)
    path = parsed.path
    if path.startswith("/metadata/"):
        path = "/metadata/<redacted-identifier>"
    return {
        "request_id": str(item.get("request_id", "")),
        "endpoint_class": str(item.get("endpoint_class", "")),
        "method": str(item.get("method", "GET")),
        "url": urllib.parse.urlunparse((parsed.scheme, parsed.netloc, path, "", "<redacted-query>", "")),
        "query_or_identifier_hash": _hash_text(str(item.get("query_or_identifier", ""))),
        "rows": int(item.get("rows", 0)),
        "metadata_only": bool(item.get("metadata_only", True)),
    }


def _hash_text(value: str) -> str:
    return hashlib.sha256(str(value).encode("utf-8")).hexdigest()[:16]


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
