"""Archive.org metadata-only candidate search for public-search previews."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
import re
import urllib.parse
from typing import Any, Callable, Mapping

from runtime.search.query_plan import archive_org_metadata_query, plan_query_to_source_actions
from runtime.source.observation.internet_archive_live_transport import (
    IALiveTransport,
    IALiveTransportPolicy,
    response_json,
)


ARCHIVE_ORG_BASE_URL = "https://archive.org"
SOURCE_ID = "internet_archive_metadata"
SOURCE_FAMILY = "internet_archive"
SCHEMA_VERSION = "archive_org_metadata_candidate_search.v0"
DEFAULT_ROWS = 5
MAX_ROWS = 10
DEFAULT_TIMEOUT_SECONDS = 5
CLIENT_LABEL = "EurekaPublicAlphaArchiveOrgMetadataCandidates/0"
CONTACT = "local-public-alpha-operator"


@dataclass(frozen=True)
class ArchiveOrgMetadataCandidateProvider:
    """Small, fail-closed Archive.org metadata search client.

    This intentionally performs only Archive.org item-search metadata calls.
    It does not fetch files, follow arbitrary URLs, persist raw responses,
    mutate indexes, or promote candidates to reviewed truth.
    """

    rows: int = DEFAULT_ROWS
    timeout_seconds: int = DEFAULT_TIMEOUT_SECONDS
    transport_factory: Callable[[IALiveTransportPolicy], IALiveTransport] | None = None
    client_label: str = CLIENT_LABEL
    contact: str = CONTACT

    def __post_init__(self) -> None:
        object.__setattr__(self, "_cache", {})

    def search_metadata_candidates(self, query: str, limit: int = DEFAULT_ROWS) -> dict[str, Any]:
        normalized_query = _normalize_query(query)
        if not normalized_query:
            return _empty_result("blocked", "empty_query", query="")
        query_plan = plan_query_to_source_actions(normalized_query)
        source_query = archive_org_metadata_query(query_plan)
        rows = _bounded_rows(limit, self.rows)
        cache_key = (normalized_query, source_query, rows)
        cache = getattr(self, "_cache")
        if cache_key in cache:
            cached = _clone_json(cache[cache_key])
            cached["cache_hit"] = True
            cached["total_http_requests"] = 0
            cached["live_call_performed"] = False
            cached["metadata_request_performed"] = False
            cached["source_probe_executed"] = False
            return cached

        request_url = build_archive_org_metadata_search_url(source_query, rows)
        policy = IALiveTransportPolicy(
            allowed_domains=("archive.org",),
            total_http_requests_max=1,
            timeout_seconds_max=self.timeout_seconds,
            retry_attempts_max=1,
            honor_retry_after=True,
        )
        transport = self.transport_factory(policy) if self.transport_factory else IALiveTransport(policy)
        try:
            response = transport.get_json(
                url=request_url,
                endpoint_class="archive_org_metadata_search",
                client_label=self.client_label,
                contact=self.contact,
                timeout_seconds=self.timeout_seconds,
                kill_switch_enabled=True,
            )
        except Exception as exc:  # pragma: no cover - defensive live boundary
            return _failure_result(normalized_query, "transport_exception", type(exc).__name__)

        payload = response_json(response)
        if response.rate_limited:
            return _failure_result(
                normalized_query,
                "rate_limited",
                "retry_after",
                http_status=response.status_code,
                retry_after_seconds=response.retry_after_seconds,
            )
        if response.status_code == 0:
            return _failure_result(normalized_query, "transport_error", response.transport_error)
        if response.status_code < 200 or response.status_code >= 300:
            return _failure_result(
                normalized_query,
                "http_error",
                f"http_status_{response.status_code}",
                http_status=response.status_code,
            )
        if payload.get("error"):
            return _failure_result(normalized_query, "archive_org_error", str(payload.get("error")))

        candidate_result = _candidate_records(
            normalized_query,
            payload,
            rows,
            query_plan=query_plan,
        )
        candidates = candidate_result["candidates"]
        result = {
            "schema_version": SCHEMA_VERSION,
            "status": "succeeded",
            "query": normalized_query,
            "source_query": source_query,
            "query_plan": _public_query_plan_summary(query_plan),
            "source_id": SOURCE_ID,
            "source_family": SOURCE_FAMILY,
            "source_label": "Internet Archive metadata search",
            "endpoint_class": "archive_org_metadata_search",
            "candidate_count": len(candidates),
            "suppressed_candidate_count": candidate_result["suppressed_candidate_count"],
            "candidate_suppressions_applied": candidate_result["candidate_suppressions_applied"],
            "candidates": candidates,
            "total_http_requests": 1,
            "live_call_performed": True,
            "metadata_request_performed": True,
            "source_probe_executed": False,
            "cache_hit": False,
            "raw_response_committed": False,
            "download_performed": False,
            "upload_performed": False,
            "extraction_executed": False,
            "accepted_truth": False,
            "review_required": True,
            "limitations": _limitations(),
            "warnings": _warnings(),
            "http_status": response.status_code,
            "response_metadata": response.metadata(),
        }
        cache[cache_key] = _clone_json(result)
        return result


def build_archive_org_metadata_search_url(query: str, rows: int) -> str:
    params = [
        ("q", query),
        ("fl[]", "identifier"),
        ("fl[]", "title"),
        ("fl[]", "mediatype"),
        ("fl[]", "collection"),
        ("fl[]", "creator"),
        ("fl[]", "date"),
        ("fl[]", "description"),
        ("rows", str(_bounded_rows(rows, MAX_ROWS))),
        ("page", "1"),
        ("output", "json"),
    ]
    return f"{ARCHIVE_ORG_BASE_URL}/advancedsearch.php?{urllib.parse.urlencode(params)}"


def _candidate_records(
    query: str,
    payload: Mapping[str, Any],
    rows: int,
    *,
    query_plan: Mapping[str, Any],
) -> dict[str, Any]:
    response = payload.get("response", {})
    docs = response.get("docs", []) if isinstance(response, Mapping) else []
    candidates: list[dict[str, Any]] = []
    suppressions = [
        item
        for item in query_plan.get("candidate_suppressions", [])
        if isinstance(item, Mapping)
    ]
    suppressed_count = 0
    applied: set[str] = set()
    for index, item in enumerate(docs[:rows] if isinstance(docs, list) else []):
        if not isinstance(item, Mapping):
            continue
        suppression_id = _candidate_suppression_id(item, suppressions)
        if suppression_id:
            suppressed_count += 1
            applied.add(suppression_id)
            continue
        identifier = _text(item.get("identifier"))
        if not identifier:
            continue
        title = _text(item.get("title")) or identifier
        candidate = {
            "schema_version": "archive_org_metadata_candidate.v0",
            "candidate_id": _candidate_id(query, identifier, title),
            "candidate_status": "needs_review",
            "candidate_type": "archive_org_item_metadata_candidate",
            "candidate_title": title,
            "candidate_summary": _summary(item),
            "identifier": identifier,
            "mediatype": _text(item.get("mediatype")),
            "collection": _text_list(item.get("collection")),
            "creator": _text_or_list(item.get("creator")),
            "date": _text_or_list(item.get("date")),
            "source_locator": {
                "locator_kind": "archive_org_details_page",
                "url": f"{ARCHIVE_ORG_BASE_URL}/details/{urllib.parse.quote(identifier, safe='')}",
            },
            "rank": index + 1,
            "source_id": SOURCE_ID,
            "source_family": SOURCE_FAMILY,
            "source_label": "Internet Archive metadata search",
            "query_plan_ref": query_plan.get("plan_id"),
            "query_intent": query_plan.get("intent"),
            "domain_pack": query_plan.get("domain_pack"),
            "accepted_truth": False,
            "review_required": True,
            "raw_response_committed": False,
            "download_performed": False,
            "upload_performed": False,
            "extraction_executed": False,
            "limitations": _limitations(),
            "warnings": _warnings(),
        }
        candidates.append(candidate)
    return {
        "candidates": candidates,
        "suppressed_candidate_count": suppressed_count,
        "candidate_suppressions_applied": sorted(applied),
    }


def _empty_result(status: str, reason: str, *, query: str) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "query": query,
        "source_id": SOURCE_ID,
        "source_family": SOURCE_FAMILY,
        "candidate_count": 0,
        "candidates": [],
        "total_http_requests": 0,
        "live_call_performed": False,
        "metadata_request_performed": False,
        "source_probe_executed": False,
        "cache_hit": False,
        "raw_response_committed": False,
        "download_performed": False,
        "upload_performed": False,
        "extraction_executed": False,
        "accepted_truth": False,
        "review_required": True,
        "failure_reason": reason,
        "limitations": _limitations(),
        "warnings": _warnings(),
    }


def _failure_result(
    query: str,
    reason: str,
    detail: str,
    *,
    http_status: int = 0,
    retry_after_seconds: int | None = None,
) -> dict[str, Any]:
    result = _empty_result("failed", reason, query=query)
    result.update(
        {
            "failure_detail": detail,
            "http_status": http_status,
            "retry_after_seconds": retry_after_seconds,
            "metadata_request_performed": True,
        }
    )
    return result


def _public_query_plan_summary(query_plan: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "schema_version": "query_to_source_action_plan_summary.v0",
        "plan_id": str(query_plan.get("plan_id") or ""),
        "planner_id": str(query_plan.get("planner_id") or ""),
        "intent": str(query_plan.get("intent") or ""),
        "intent_confidence": str(query_plan.get("intent_confidence") or ""),
        "domain_pack": str(query_plan.get("domain_pack") or ""),
        "source_families": [str(item) for item in query_plan.get("source_families", []) or []],
        "archive_org_metadata_query": archive_org_metadata_query(query_plan),
        "candidate_suppressions": [
            {
                "suppression_id": str(item.get("suppression_id") or ""),
                "terms": [str(term) for term in item.get("terms", []) or []],
                "reason": str(item.get("reason") or ""),
            }
            for item in query_plan.get("candidate_suppressions", []) or []
            if isinstance(item, Mapping)
        ],
        "candidate_lane_expectations": [
            dict(item)
            for item in query_plan.get("candidate_lane_expectations", []) or []
            if isinstance(item, Mapping)
        ],
        "explanation": dict(query_plan.get("explanation") or {}),
        "accepted_truth": False,
        "review_required": True,
        "download_performed": False,
        "extraction_executed": False,
        "model_provider_used": False,
        "index_mutation_performed": False,
    }


def _candidate_suppression_id(
    item: Mapping[str, Any],
    suppressions: list[Mapping[str, Any]],
) -> str:
    haystack = " ".join(
        part
        for part in (
            _text(item.get("identifier")),
            _text(item.get("title")),
            _text_or_list(item.get("description")),
            _text(item.get("mediatype")),
            " ".join(_text_list(item.get("collection"))),
        )
        if part
    ).casefold()
    for suppression in suppressions:
        for term in suppression.get("terms", []) or []:
            if _contains_suppression_term(haystack, str(term)):
                return str(suppression.get("suppression_id") or "candidate_suppressed")
    return ""


def _contains_suppression_term(haystack: str, term: str) -> bool:
    normalized = term.casefold().strip()
    if not normalized:
        return False
    if re.fullmatch(r"[a-z0-9.]+", normalized):
        return re.search(rf"\b{re.escape(normalized)}\b", haystack) is not None
    return normalized in haystack


def _bounded_rows(*values: int) -> int:
    positive_values = [int(value) for value in values if int(value) > 0]
    if not positive_values:
        return 1
    rows = min(positive_values)
    return max(1, min(rows, MAX_ROWS))


def _normalize_query(query: str) -> str:
    return " ".join(str(query or "").split())[:160]


def _candidate_id(query: str, identifier: str, title: str) -> str:
    digest = hashlib.sha256(f"{query}\0{identifier}\0{title}".encode("utf-8")).hexdigest()[:16]
    return f"ia-meta-candidate:{digest}"


def _summary(item: Mapping[str, Any]) -> str:
    description = _text_or_list(item.get("description"))
    if description:
        return description[:320]
    mediatype = _text(item.get("mediatype"))
    date = _text_or_list(item.get("date"))
    parts = [part for part in (mediatype, date) if part]
    if parts:
        return "Archive.org metadata candidate: " + ", ".join(parts)
    return "Archive.org metadata candidate; review required before use."


def _text(value: Any) -> str:
    if isinstance(value, str):
        return " ".join(value.split())[:500]
    if isinstance(value, (int, float)):
        return str(value)
    return ""


def _text_or_list(value: Any) -> str:
    if isinstance(value, list):
        return ", ".join(_text(item) for item in value if _text(item))[:500]
    return _text(value)


def _text_list(value: Any) -> list[str]:
    if isinstance(value, list):
        return [_text(item) for item in value if _text(item)]
    text = _text(value)
    return [text] if text else []


def _limitations() -> list[str]:
    return [
        "archive_org_metadata_only",
        "candidate_not_reviewed_truth",
        "no_download",
        "no_extraction",
        "no_install",
        "no_raw_response_commit",
        "no_auto_promotion",
        "no_rights_clearance",
        "no_malware_scan",
    ]


def _warnings() -> list[str]:
    return [
        "Archive.org metadata candidates require review before promotion.",
        "Metadata search does not grant download, install, execution, rights, or safety permission.",
    ]


def _clone_json(value: Mapping[str, Any]) -> dict[str, Any]:
    return {
        str(key): _clone_value(item)
        for key, item in value.items()
    }


def _clone_value(value: Any) -> Any:
    if isinstance(value, Mapping):
        return _clone_json(value)
    if isinstance(value, list):
        return [_clone_value(item) for item in value]
    return value
