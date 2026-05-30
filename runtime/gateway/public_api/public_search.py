from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any, Mapping, Protocol, Sequence
from urllib.parse import quote

from runtime.engine.index import IndexRecord
from runtime.engine.interfaces.public import QueryPlanRequest
from runtime.engine.interfaces.service import QueryPlannerService
from runtime.gateway.public_api.resolution_boundary import PublicApiResponse
from runtime.source.registry import SourceRecordNotFoundError, SourceRegistry


SCHEMA_VERSION = "0.1.0"
SEARCH_RESPONSE_CONTRACT_ID = "eureka_public_search_response_v0"
ERROR_RESPONSE_CONTRACT_ID = "eureka_public_search_error_response_v0"
RESULT_CARD_CONTRACT_ID = "eureka_public_search_result_card_v0"
MODE = "local_index_only"
ARCHIVE_ORG_METADATA_CANDIDATES = "archive_org_metadata_candidates"
ALLOWED_SOURCE_POLICIES = frozenset({MODE, ARCHIVE_ORG_METADATA_CANDIDATES})
MAX_QUERY_LENGTH = 160
DEFAULT_RESULT_LIMIT = 10
MAX_RESULT_LIMIT = 25
MAX_INCLUDE_ITEMS = 8

ALLOWED_PROFILES = frozenset(
    {"standard_web", "lite_html", "text", "api_client", "snapshot", "native_client"}
)
ALLOWED_INCLUDES = frozenset(
    {
        "actions",
        "compatibility",
        "evidence",
        "gaps",
        "limitations",
        "query_plan",
        "source_summary",
        "source_summaries",
        "evidence_summaries",
        "compatibility_summaries",
        "absence_summary",
    }
)
SEARCH_QUERY_PARAMETERS = frozenset(
    {
        "q",
        "limit",
        "offset",
        "cursor",
        "profile",
        "mode",
        "include",
        "source_policy",
    }
)
SOURCE_QUERY_PARAMETERS = frozenset(
    {
        "status",
        "family",
        "role",
        "surface",
        "coverage_depth",
        "capability",
        "connector_mode",
    }
)
LOCAL_PATH_PARAMETERS = frozenset(
    {
        "index_path",
        "store_root",
        "run_store_root",
        "task_store_root",
        "memory_store_root",
        "local_path",
        "path",
        "file_path",
        "directory",
        "root",
    }
)
URL_OR_NETWORK_PARAMETERS = frozenset(
    {"url", "fetch_url", "crawl_url", "source_url", "network", "arbitrary_source"}
)
DOWNLOAD_PARAMETERS = frozenset({"download"})
INSTALL_PARAMETERS = frozenset({"install", "execute"})
UPLOAD_PARAMETERS = frozenset({"upload", "user_file"})
CREDENTIAL_PARAMETERS = frozenset({"source_credentials", "auth_token", "api_key"})
LIVE_PROBE_PARAMETERS = frozenset({"live_probe", "live_source"})
FORBIDDEN_PARAMETERS = (
    LOCAL_PATH_PARAMETERS
    | URL_OR_NETWORK_PARAMETERS
    | DOWNLOAD_PARAMETERS
    | INSTALL_PARAMETERS
    | UPLOAD_PARAMETERS
    | CREDENTIAL_PARAMETERS
    | LIVE_PROBE_PARAMETERS
)


@dataclass(frozen=True)
class PublicSearchRequest:
    raw_query: str
    normalized_query: str
    limit: int = DEFAULT_RESULT_LIMIT
    profile: str = "standard_web"
    mode: str = MODE
    includes: tuple[str, ...] = ()
    source_policy: str = MODE
    offset: int = 0
    cursor: str | None = None


class ArchiveOrgMetadataCandidateProvider(Protocol):
    def search_metadata_candidates(self, query: str, limit: int) -> Mapping[str, Any]:
        ...


class CandidateIndexSearchProvider(Protocol):
    def search_candidates(self, query: str, limit: int) -> Mapping[str, Any]:
        ...


class PublicSearchPublicApi:
    def __init__(
        self,
        *,
        index_records: tuple[IndexRecord, ...],
        source_registry: SourceRegistry,
        query_planner: QueryPlannerService,
        index_status: str = "controlled_local_index_only",
        index_document_count: int | None = None,
        archive_org_metadata_candidates: ArchiveOrgMetadataCandidateProvider | None = None,
        candidate_index_search: CandidateIndexSearchProvider | None = None,
        default_source_policy: str = MODE,
    ) -> None:
        self._index_records = tuple(index_records)
        self._source_registry = source_registry
        self._query_planner = query_planner
        self._index_status = index_status
        self._index_document_count = index_document_count if index_document_count is not None else len(index_records)
        self._archive_org_metadata_candidates = archive_org_metadata_candidates
        self._candidate_index_search = candidate_index_search
        if default_source_policy not in ALLOWED_SOURCE_POLICIES:
            raise ValueError(f"unsupported default source policy: {default_source_policy}")
        self._default_source_policy = default_source_policy

    def search(
        self,
        query: Mapping[str, Sequence[str]],
        *,
        default_profile: str = "api_client",
    ) -> PublicApiResponse:
        request_or_error = validate_public_search_query(
            query,
            default_profile=default_profile,
            default_source_policy=self._default_source_policy,
        )
        if isinstance(request_or_error, PublicApiResponse):
            return request_or_error
        request = request_or_error
        terms = _query_terms(request.normalized_query)
        matches = tuple(
            record
            for record in self._index_records
            if _record_matches_query(record, terms, request.normalized_query)
        )
        limited = tuple(sorted(matches, key=_record_sort_key)[: request.limit])
        cards = [
            public_result_card_from_index_record(record, terms, self._source_registry)
            for record in limited
        ]
        archive_candidate_result = _archive_org_candidate_search_result(
            self._archive_org_metadata_candidates,
            request,
            terms,
        )
        archive_candidate_cards = _archive_org_candidate_cards(archive_candidate_result, terms)
        candidate_index_result = _candidate_index_search_result(
            self._candidate_index_search,
            request,
            terms,
        )
        candidate_index_cards = _candidate_index_candidate_cards(candidate_index_result, terms)
        body = _search_success_envelope(
            request,
            cards,
            checked_sources=_checked_sources(limited, self._source_registry),
            plan=_plan_to_public_dict(self._query_planner, request.normalized_query),
            archive_candidate_result=archive_candidate_result,
            archive_candidate_cards=archive_candidate_cards,
            candidate_index_result=candidate_index_result,
            candidate_index_cards=candidate_index_cards,
        )
        body["index_status"] = self._index_status
        body["index_document_count"] = self._index_document_count
        return PublicApiResponse(status_code=200, body=body)

    def query_plan(
        self,
        query: Mapping[str, Sequence[str]],
        *,
        default_profile: str = "api_client",
    ) -> PublicApiResponse:
        request_or_error = validate_public_search_query(
            query,
            default_profile=default_profile,
            allowed_parameters=SEARCH_QUERY_PARAMETERS,
            default_source_policy=self._default_source_policy,
        )
        if isinstance(request_or_error, PublicApiResponse):
            return request_or_error
        request = request_or_error
        task = self._query_planner.plan_query(QueryPlanRequest.from_parts(request.normalized_query))
        return PublicApiResponse(
            status_code=200,
            body={
                "ok": True,
                "schema_version": SCHEMA_VERSION,
                "contract_id": "eureka_public_search_query_plan_v0",
                "mode": MODE,
                "query": _query_block(request, interpreted_task_kind=task.task_kind),
                "query_plan": task.to_dict(),
                "generated_by": _generated_by("public_search_query_plan_runtime_v0"),
                "warnings": _global_warnings(),
                "limitations": _global_limitations(),
                "no_live_probe": True,
            },
        )

    def status(self, query: Mapping[str, Sequence[str]] | None = None) -> PublicApiResponse:
        forbidden = _forbidden_parameter_error(query or {})
        if forbidden is not None:
            return forbidden
        source_count = len(self._source_registry.records)
        return PublicApiResponse(
            status_code=200,
            body={
                "ok": True,
                "schema_version": SCHEMA_VERSION,
                "contract_id": "eureka_public_search_status_v0",
                "mode": MODE,
                "public_search": {
                    "implemented": True,
                    "implementation_scope": "local_prototype_backend",
                    "hosted_public_deployment": False,
                    "mode": MODE,
                    "live_probes_enabled": False,
                    "archive_org_metadata_candidate_search_available": self._archive_org_metadata_candidates is not None,
                    "archive_org_metadata_candidate_search_default": self._default_source_policy == ARCHIVE_ORG_METADATA_CANDIDATES,
                    "downloads_enabled": False,
                    "installs_enabled": False,
                    "uploads_enabled": False,
                    "local_paths_enabled": False,
                    "telemetry_enabled": False,
                    "production_ready": False,
                },
                "public_search_implemented": True,
                "hosted_search_implemented": False,
                "local_runtime_available": True,
                "live_probes_enabled": False,
                "archive_org_metadata_candidate_search_available": self._archive_org_metadata_candidates is not None,
                "archive_org_metadata_candidate_search_default": self._default_source_policy == ARCHIVE_ORG_METADATA_CANDIDATES,
                "downloads_enabled": False,
                "uploads_enabled": False,
                "installs_enabled": False,
                "local_paths_enabled": False,
                "arbitrary_url_fetch_enabled": False,
                "telemetry_enabled": False,
                "account_required": False,
                "max_query_length": MAX_QUERY_LENGTH,
                "default_limit": DEFAULT_RESULT_LIMIT,
                "max_limit": MAX_RESULT_LIMIT,
                "index_status": self._index_status,
                "index_document_count": self._index_document_count,
                "source_status_summary": {
                    "source_count": source_count,
                    "live_enabled": False,
                },
                "source_count": source_count,
                "contracts": {
                    "search_api": "public_search_api_contract_v0",
                    "result_card": "public_search_result_card_contract_v0",
                    "safety": "public_search_safety_abuse_guard_v0",
                },
                "warnings": _global_warnings(),
                "limitations": _global_limitations(),
            },
        )

    def list_sources(self, query: Mapping[str, Sequence[str]]) -> PublicApiResponse:
        forbidden = _forbidden_parameter_error(query)
        if forbidden is not None:
            return forbidden
        unexpected = sorted(
            name for name in query if name not in SOURCE_QUERY_PARAMETERS and name not in FORBIDDEN_PARAMETERS
        )
        if unexpected:
            return public_search_error_response(
                400,
                code="bad_request",
                message=f"Unsupported source query parameter '{unexpected[0]}'.",
                parameter=unexpected[0],
            )
        records = self._source_registry.list_records(
            status=_optional_value(query, "status"),
            source_family=_optional_value(query, "family"),
            role=_optional_value(query, "role"),
            surface=_optional_value(query, "surface"),
            coverage_depth=_optional_value(query, "coverage_depth"),
            capability=_optional_value(query, "capability"),
            connector_mode=_optional_value(query, "connector_mode"),
        )
        return PublicApiResponse(
            status_code=200,
            body=_sources_envelope(
                [_source_public_summary(record, checked_as="static_summary") for record in records],
            ),
        )

    def get_source(
        self,
        source_id: str,
        query: Mapping[str, Sequence[str]] | None = None,
    ) -> PublicApiResponse:
        forbidden = _forbidden_parameter_error(query or {})
        if forbidden is not None:
            return forbidden
        normalized_source_id = source_id.strip()
        if not normalized_source_id:
            return public_search_error_response(
                400,
                code="bad_request",
                message="Provide a non-empty source_id path segment.",
                parameter="source_id",
            )
        try:
            record = self._source_registry.get_record(normalized_source_id)
        except SourceRecordNotFoundError:
            return public_search_error_response(
                404,
                code="not_found",
                message=f"Unknown source_id '{normalized_source_id}'.",
                parameter="source_id",
            )
        return PublicApiResponse(
            status_code=200,
            body=_sources_envelope(
                [_source_public_summary(record, checked_as="static_summary")],
                selected_source_id=record.source_id,
            ),
        )


def validate_public_search_query(
    query: Mapping[str, Sequence[str]],
    *,
    default_profile: str = "api_client",
    allowed_parameters: frozenset[str] = SEARCH_QUERY_PARAMETERS,
    default_source_policy: str = MODE,
) -> PublicSearchRequest | PublicApiResponse:
    forbidden = _forbidden_parameter_error(query)
    if forbidden is not None:
        return forbidden

    unexpected = sorted(
        name for name in query if name not in allowed_parameters and name not in FORBIDDEN_PARAMETERS
    )
    if unexpected:
        return public_search_error_response(
            400,
            code="bad_request",
            message=f"Unsupported public search parameter '{unexpected[0]}'.",
            parameter=unexpected[0],
        )

    raw_query = _optional_value(query, "q")
    if raw_query is None:
        return public_search_error_response(
            400,
            code="query_required",
            message="Provide a non-empty q query parameter.",
            parameter="q",
        )
    normalized_query = raw_query.strip()
    if not normalized_query:
        return public_search_error_response(
            400,
            code="query_required",
            message="Provide a non-empty q query parameter.",
            parameter="q",
        )
    if len(normalized_query) > MAX_QUERY_LENGTH:
        return public_search_error_response(
            400,
            code="query_too_long",
            message=f"q must be at most {MAX_QUERY_LENGTH} characters.",
            parameter="q",
        )

    limit_or_error = _parse_limit(query)
    if isinstance(limit_or_error, PublicApiResponse):
        return limit_or_error
    limit = limit_or_error

    profile = _optional_value(query, "profile") or default_profile
    if profile not in ALLOWED_PROFILES:
        return public_search_error_response(
            400,
            code="unsupported_profile",
            message=f"Unsupported public search profile '{profile}'.",
            parameter="profile",
        )

    mode = _optional_value(query, "mode") or MODE
    if mode != MODE:
        code = "live_probes_disabled" if "live" in mode.casefold() else "unsupported_mode"
        return public_search_error_response(
            400,
            code=code,
            message="Public search v0 only supports local_index_only mode.",
            parameter="mode",
        )

    source_policy = _optional_value(query, "source_policy") or default_source_policy
    if source_policy not in ALLOWED_SOURCE_POLICIES:
        return public_search_error_response(
            400,
            code="unsupported_mode",
            message=(
                "Public search supports local_index_only or "
                "archive_org_metadata_candidates source_policy."
            ),
            parameter="source_policy",
        )

    includes = _include_values(query)
    if len(includes) > MAX_INCLUDE_ITEMS:
        return public_search_error_response(
            400,
            code="unsupported_include",
            message=f"include accepts at most {MAX_INCLUDE_ITEMS} values.",
            parameter="include",
        )
    unsupported_includes = sorted(set(includes) - ALLOWED_INCLUDES)
    if unsupported_includes:
        return public_search_error_response(
            400,
            code="unsupported_include",
            message=f"Unsupported include value '{unsupported_includes[0]}'.",
            parameter="include",
        )

    offset = _parse_offset(query)
    if isinstance(offset, PublicApiResponse):
        return offset

    return PublicSearchRequest(
        raw_query=raw_query,
        normalized_query=normalized_query,
        limit=limit,
        profile=profile,
        mode=mode,
        includes=tuple(includes),
        source_policy=source_policy,
        offset=offset,
        cursor=_optional_value(query, "cursor"),
    )


def public_search_error_response(
    status_code: int,
    *,
    code: str,
    message: str,
    parameter: str | None = None,
    capability_required: str | None = None,
) -> PublicApiResponse:
    return PublicApiResponse(
        status_code=status_code,
        body={
            "ok": False,
            "schema_version": SCHEMA_VERSION,
            "contract_id": ERROR_RESPONSE_CONTRACT_ID,
            "error": {
                "code": code,
                "message": message,
                "status": status_code,
                "retryable": code in {"rate_limited", "timeout"},
                "capability_required": capability_required,
                "parameter": parameter,
                "docs": "docs/reference/PUBLIC_SEARCH_API_CONTRACT.md",
                "severity": "blocked" if status_code in {400, 403} else "error",
                "remediation": (
                    "Remove the unsafe or unsupported request parameter and retry "
                    "with local_index_only mode."
                ),
                "public_safe": True,
            },
            "warnings": _global_warnings(),
            "limits": {
                "query_length_limit": MAX_QUERY_LENGTH,
                "max_result_limit": MAX_RESULT_LIMIT,
            },
            "mode": MODE,
            "limitations": _global_limitations(),
            "request_limits": _request_limits(),
        },
    )


def public_result_card_from_index_record(
    record: IndexRecord,
    matched_terms: Sequence[str],
    source_registry: SourceRegistry,
) -> dict[str, Any]:
    source = _source_for_record(record, source_registry)
    compatibility = _compatibility_block(record)
    evidence = _evidence_block(record)
    identity = _identity_block(record)
    warnings = _card_warnings(record)
    limitations = _card_limitations(record)
    result_lane = record.primary_lane or (record.result_lanes[0] if record.result_lanes else "other")
    public_target_ref = record.target_ref or record.index_record_id
    card = {
        "schema_version": SCHEMA_VERSION,
        "contract_id": RESULT_CARD_CONTRACT_ID,
        "stability": _card_stability(),
        "result_id": record.index_record_id,
        "title": record.label,
        "subtitle": record.summary,
        "summary": record.summary,
        "record_kind": record.record_kind,
        "matched_query_terms": [
            term for term in matched_terms if term in record.search_text().casefold()
        ],
        "why_matched": _why_matched(record, matched_terms),
        "why_ranked": [record.usefulness_summary] if record.usefulness_summary else [],
        "result_lane": result_lane,
        "user_cost": _user_cost(record),
        "source": source,
        "identity": identity,
        "evidence": evidence,
        "compatibility": compatibility,
        "parent_lineage": _parent_lineage(record),
        "member": _member_block(record),
        "representation": _representation_block(record),
        "actions": _actions_block(record),
        "rights": _rights_block(record),
        "risk": _risk_block(record),
        "warnings": warnings,
        "limitations": limitations,
        "gaps": [],
        "links": _links_block(record),
        "debug": None,
        # Compact aliases retained for P26 response clients.
        "source_id": source["source_id"],
        "source_family": source["source_family"],
        "public_target_ref": public_target_ref,
        "target_ref": public_target_ref,
        "resolved_resource_id": record.resolved_resource_id,
    }
    return card


def _archive_org_candidate_search_result(
    provider: ArchiveOrgMetadataCandidateProvider | None,
    request: PublicSearchRequest,
    terms: Sequence[str],
) -> dict[str, Any] | None:
    del terms
    if request.source_policy != ARCHIVE_ORG_METADATA_CANDIDATES:
        return None
    if provider is None:
        return {
            "schema_version": "archive_org_metadata_candidate_search.v0",
            "status": "unavailable",
            "query": request.normalized_query,
            "source_id": "internet_archive_metadata",
            "source_family": "internet_archive",
            "candidate_count": 0,
            "candidates": [],
            "total_http_requests": 0,
            "live_call_performed": False,
            "metadata_request_performed": False,
            "source_probe_executed": False,
            "raw_response_committed": False,
            "download_performed": False,
            "upload_performed": False,
            "extraction_executed": False,
            "accepted_truth": False,
            "review_required": True,
            "failure_reason": "archive_org_metadata_candidate_provider_unavailable",
            "warnings": [
                "Archive.org metadata candidate search is not configured for this public-search API instance."
            ],
            "limitations": [
                "archive_org_metadata_candidate_provider_unavailable",
                "candidate_not_reviewed_truth",
                "no_download",
                "no_auto_promotion",
            ],
        }
    return dict(provider.search_metadata_candidates(request.normalized_query, request.limit))


def _candidate_index_search_result(
    provider: CandidateIndexSearchProvider | None,
    request: PublicSearchRequest,
    terms: Sequence[str],
) -> dict[str, Any] | None:
    del terms
    if provider is None:
        return None
    result = dict(provider.search_candidates(request.normalized_query, request.limit))
    result.setdefault("schema_version", "candidate_search_result.v0")
    result.setdefault("accepted_truth", False)
    result.setdefault("review_required", True)
    result.setdefault("public_mutation_enabled", False)
    result.setdefault("reviewed_index_mutated", False)
    result.setdefault("master_index_mutated", False)
    return result


def _archive_org_candidate_cards(
    result: Mapping[str, Any] | None,
    terms: Sequence[str],
) -> list[dict[str, Any]]:
    if not result or result.get("status") != "succeeded":
        return []
    cards: list[dict[str, Any]] = []
    for candidate in result.get("candidates", []) or []:
        if isinstance(candidate, Mapping):
            cards.append(_archive_org_candidate_card(candidate, terms))
    return cards


def _candidate_index_candidate_cards(
    result: Mapping[str, Any] | None,
    terms: Sequence[str],
) -> list[dict[str, Any]]:
    if not result:
        return []
    cards: list[dict[str, Any]] = []
    for candidate in result.get("results", []) or []:
        if isinstance(candidate, Mapping):
            cards.append(_candidate_index_candidate_card(candidate, terms))
    return cards


def _candidate_index_candidate_card(
    candidate: Mapping[str, Any],
    matched_terms: Sequence[str],
) -> dict[str, Any]:
    title = str(candidate.get("title") or candidate.get("candidate_id") or "Candidate index result")
    summary = str(candidate.get("description") or "Stored candidate; review required before use.")
    candidate_id = str(candidate.get("candidate_id") or "")
    source_family = str(candidate.get("source_family") or "candidate_index")
    locator = candidate.get("source_locator") if isinstance(candidate.get("source_locator"), Mapping) else {}
    target_ref = candidate_id or str(locator.get("url") or "")
    text = f"{title} {summary} {target_ref}".casefold()
    matched = [term for term in matched_terms if term in text]
    source = {
        "source_id": "candidate_index",
        "source_family": source_family,
        "source_label": "Local candidate index",
        "source_status": "local_candidate_memory",
        "posture": "candidate_only",
        "coverage_depth": "local_candidate_index",
        "trust_lane": "candidate_only",
        "source_lane": "candidate_index",
        "checked_as": "candidate_index_search",
        "domain_pack": str(candidate.get("domain_id") or ""),
        "limitations": [
            "candidate_not_reviewed_truth",
            "local_candidate_memory",
            "no_download",
            "no_extraction",
            "no_auto_promotion",
        ],
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "contract_id": RESULT_CARD_CONTRACT_ID,
        "stability": _card_stability(),
        "result_id": candidate_id or target_ref,
        "title": title,
        "subtitle": summary,
        "summary": summary,
        "record_kind": "candidate_index_record",
        "matched_query_terms": matched,
        "why_matched": [f"matched term: {term}" for term in matched[:6]]
        or ["Stored candidate matched the query."],
        "why_ranked": ["Local candidate index match; candidate requires review."],
        "result_lane": "candidate_index",
        "user_cost": {
            "score": 2,
            "label": "low",
            "reasons": ["candidate_index_memory", "review_required"],
            "explanation": "Stored candidate memory; review required before promotion.",
        },
        "source": source,
        "identity": {
            "public_target_ref": target_ref,
            "target_ref": target_ref,
            "resolved_resource_id": None,
            "object_id": candidate_id,
            "release_or_state_id": None,
            "representation_id": None,
            "member_target_ref": None,
            "native_source_id": candidate_id,
            "identity_status": "candidate",
            "notes": ["Candidate index identity still requires Eureka review."],
        },
        "evidence": {
            "evidence_count": 1,
            "summaries": [
                {
                    "evidence_id": f"{candidate_id}:candidate_index",
                    "evidence_kind": "candidate_index_summary",
                    "source_id": "candidate_index",
                    "locator": None,
                    "snippet": summary[:280],
                    "confidence": "unknown",
                }
            ],
            "provenance_notes": ["public-safe local candidate summary only"],
            "missing_evidence": [],
        },
        "compatibility": {
            "status": "unknown",
            "target_platforms": [],
            "architecture": "unknown",
            "evidence_summaries": [],
            "confidence": "unknown",
            "caveats": [],
            "unknowns": ["Candidate index memory does not establish compatibility."],
        },
        "parent_lineage": [],
        "member": None,
        "representation": None,
        "actions": {
            "allowed": [
                _action("inspect", "allowed", "Inspect candidate summary metadata."),
                _action("view_source", "allowed", "View governed source summary metadata."),
                _action("view_provenance", "allowed", "View public-safe candidate provenance."),
            ],
            "blocked": [
                _action("download", "blocked", "Downloads are disabled by Public Search Safety / Abuse Guard v0."),
                _action("install_handoff", "blocked", "Installer handoff is disabled in v0."),
                _action("execute", "blocked", "Execution is disabled in v0."),
                _action("upload", "blocked", "Uploads and private source submission are disabled in v0."),
                _action("accept", "blocked", "Public candidate acceptance is disabled."),
                _action("promote", "blocked", "Candidate promotion requires a separate review workflow."),
            ],
            "future_gated": [
                _action("review_candidate", "future_gated", "Promotion requires a future review workflow action."),
            ],
        },
        "rights": {
            "rights_status": "unknown",
            "distribution_allowed": "unknown",
            "notes": ["Candidate memory does not grant Eureka distribution permission."],
        },
        "risk": {
            "executable_risk": "unknown",
            "malware_scan_status": "not_scanned",
            "warnings": [
                {
                    "warning_type": "candidate_not_reviewed_truth",
                    "message": "Candidate memory requires review before promotion.",
                    "severity": "info",
                }
            ],
        },
        "warnings": [
            _warning("candidate_not_reviewed_truth", "Candidate requires review before promotion.", "info"),
        ],
        "limitations": sorted(
            set(candidate.get("limitations") or [])
            | {
                "candidate_not_reviewed_truth",
                "local_candidate_memory",
                "no_download",
                "no_install",
                "no_execute",
                "no_upload",
                "no_extraction",
                "no_auto_promotion",
            }
        ),
        "source_locator": dict(locator),
        "accepted_truth": False,
        "review_required": True,
    }


def _archive_org_candidate_card(
    candidate: Mapping[str, Any],
    matched_terms: Sequence[str],
) -> dict[str, Any]:
    title = str(candidate.get("candidate_title") or candidate.get("identifier") or "Archive.org metadata candidate")
    summary = str(candidate.get("candidate_summary") or "Archive.org metadata candidate; review required before use.")
    identifier = str(candidate.get("identifier") or "")
    target_ref = f"archive.org:item:{identifier}" if identifier else str(candidate.get("candidate_id") or "")
    source = {
        "source_id": "internet_archive_metadata",
        "source_family": "internet_archive",
        "source_label": "Internet Archive metadata search",
        "source_status": "live_metadata_candidate_source",
        "posture": "candidate_only",
        "coverage_depth": "archive_org_metadata_search",
        "trust_lane": "candidate_only",
        "source_lane": "metadata_source",
        "checked_as": "archive_org_metadata_candidate_search",
        "query_intent": str(candidate.get("query_intent") or ""),
        "domain_pack": str(candidate.get("domain_pack") or ""),
        "limitations": [
            "metadata_only",
            "candidate_not_reviewed_truth",
            "no_download",
            "no_auto_promotion",
        ],
    }
    warnings = [
        _warning(
            "archive_org_metadata_candidate",
            "Archive.org metadata candidate requires review before promotion.",
            "info",
        ),
        _warning("no_download", "Downloads are disabled in public search v0.", "caution"),
        _warning("no_rights_clearance", "No rights clearance is claimed.", "caution"),
        _warning("no_malware_scan", "Executable-like material was not scanned.", "warning"),
    ]
    limitations = sorted(
        set(candidate.get("limitations") or [])
        | {
            "archive_org_metadata_only",
            "candidate_not_reviewed_truth",
            "external_metadata_source",
            "no_download",
            "no_install",
            "no_execute",
            "no_upload",
            "no_extraction",
            "no_auto_promotion",
            "no_rights_clearance",
            "no_malware_scan",
            "not_production_ranking",
        }
    )
    text = f"{title} {summary} {identifier}".casefold()
    matched = [term for term in matched_terms if term in text]
    return {
        "schema_version": SCHEMA_VERSION,
        "contract_id": RESULT_CARD_CONTRACT_ID,
        "stability": _card_stability(),
        "result_id": str(candidate.get("candidate_id") or target_ref),
        "title": title,
        "subtitle": summary,
        "summary": summary,
        "record_kind": "archive_org_metadata_candidate",
        "matched_query_terms": matched,
        "why_matched": [f"matched term: {term}" for term in matched[:6]]
        or ["Archive.org metadata search returned this candidate."],
        "why_ranked": [
            "Archive.org metadata search order; candidate requires review.",
            *(
                [f"query plan intent: {candidate.get('query_intent')}"]
                if candidate.get("query_intent")
                else []
            ),
            *(
                [f"domain pack: {candidate.get('domain_pack')}"]
                if candidate.get("domain_pack")
                else []
            ),
        ],
        "result_lane": "source_candidates",
        "user_cost": {
            "score": 3,
            "label": "medium",
            "reasons": ["external_metadata_candidate", "review_required"],
            "explanation": "Metadata candidate from Archive.org; review required before promotion.",
        },
        "source": source,
        "identity": {
            "public_target_ref": target_ref,
            "target_ref": target_ref,
            "resolved_resource_id": None,
            "object_id": identifier,
            "release_or_state_id": str(candidate.get("date") or "") or None,
            "representation_id": None,
            "member_target_ref": None,
            "native_source_id": identifier,
            "identity_status": "candidate",
            "notes": ["Archive.org identifier is public metadata; identity still requires Eureka review."],
        },
        "evidence": {
            "evidence_count": 1,
            "summaries": [
                {
                    "evidence_id": f"{candidate.get('candidate_id')}:archive_org_metadata",
                    "evidence_kind": "archive_org_metadata_search_summary",
                    "source_id": "internet_archive_metadata",
                    "locator": None,
                    "snippet": summary[:280],
                    "confidence": "unknown",
                }
            ],
            "provenance_notes": ["public-safe Archive.org metadata summary only"],
            "missing_evidence": [],
        },
        "compatibility": {
            "status": "unknown",
            "target_platforms": [],
            "architecture": "unknown",
            "evidence_summaries": [],
            "confidence": "unknown",
            "caveats": [],
            "unknowns": ["Archive.org metadata does not establish compatibility."],
        },
        "parent_lineage": [],
        "member": None,
        "representation": None,
        "actions": {
            "allowed": [
                _action("inspect", "allowed", "Inspect public metadata for this candidate."),
                _action("view_source", "allowed", "View governed source summary metadata."),
                _action("view_provenance", "allowed", "View public-safe metadata provenance."),
            ],
            "blocked": [
                _action("download", "blocked", "Downloads are disabled by Public Search Safety / Abuse Guard v0."),
                _action("install_handoff", "blocked", "Installer handoff is disabled in v0."),
                _action("execute", "blocked", "Execution is disabled in v0."),
                _action("upload", "blocked", "Uploads and private source submission are disabled in v0."),
            ],
            "future_gated": [
                _action("review_candidate", "future_gated", "Promotion requires a future review workflow action."),
                _action("download_member", "future_gated", "Member downloads require a future rights and safety policy."),
            ],
        },
        "rights": {
            "rights_status": "unknown",
            "distribution_allowed": "unknown",
            "notes": ["Archive.org metadata does not grant Eureka distribution permission."],
        },
        "risk": {
            "executable_risk": "unknown",
            "malware_scan_status": "not_scanned",
            "warnings": [
                {
                    "warning_type": "no_malware_scan",
                    "message": "No malware scan or executable safety claim is made.",
                    "severity": "warning",
                }
            ],
        },
        "warnings": warnings,
        "limitations": limitations,
        "gaps": [{"gap_type": "review_required", "message": "Candidate has not been reviewed or promoted."}],
        "links": {
            "inspect": None,
            "source": "/api/v1/sources",
            "evidence": None,
            "absence": None,
            "archive_org_details": _archive_org_details_url(candidate),
        },
        "debug": None,
        "source_id": source["source_id"],
        "source_family": source["source_family"],
        "public_target_ref": target_ref,
        "target_ref": target_ref,
        "resolved_resource_id": None,
    }


def _search_success_envelope(
    request: PublicSearchRequest,
    results: list[dict[str, Any]],
    *,
    checked_sources: list[dict[str, Any]],
    plan: dict[str, Any] | None,
    archive_candidate_result: Mapping[str, Any] | None = None,
    archive_candidate_cards: list[dict[str, Any]] | None = None,
    candidate_index_result: Mapping[str, Any] | None = None,
    candidate_index_cards: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    candidate_cards = list(archive_candidate_cards or []) + list(candidate_index_cards or [])
    gaps: list[dict[str, Any]] = []
    absence_summary: dict[str, Any] | None = {
        "status": "none",
        "message": "At least one controlled local-index result matched.",
        "searched_scope": "controlled local index",
        "next_actions": [],
    }
    if request.source_policy == ARCHIVE_ORG_METADATA_CANDIDATES:
        checked_sources = list(checked_sources)
        checked_sources.append(_archive_org_checked_source(archive_candidate_result))
    if candidate_index_result is not None:
        checked_sources = list(checked_sources)
        checked_sources.append(_candidate_index_checked_source(candidate_index_result))
    if not results:
        gaps.append(
            {
                "gap_type": "bounded_absence",
                "message": "No controlled local-index records matched this query.",
                "source_id": None,
                "next_action": "Refine the query or wait for a future source expansion pack.",
            }
        )
        absence_summary = {
            "status": "bounded_absence",
            "message": "No controlled local-index records matched this query.",
            "searched_scope": "controlled local index only",
            "next_actions": [
                "try a narrower query",
                "review source coverage",
                "do not infer global absence from this local prototype result",
            ],
        }
    if candidate_cards:
        gaps.append(
            {
                "gap_type": "candidate_results_available",
                "message": "Candidate results are available; review is required before promotion.",
                "source_id": "candidate_index_or_source_action",
                "next_action": "review candidate results",
            }
        )
        if not results:
            absence_summary = {
                "status": "candidate_results_only",
                "message": (
                    "No reviewed local-index records matched, but candidate "
                    "results were found for review."
                ),
                "searched_scope": "controlled local index plus candidate search lanes",
                "next_actions": [
                    "review candidate results",
                    "promote useful reviewed records only after manual review",
                    "do not infer reviewed truth from candidate metadata",
                ],
            }

    query = _query_block(
        request,
        interpreted_task_kind=plan.get("task_kind") if isinstance(plan, Mapping) else None,
    )
    if request.cursor:
        query["notices"].append("cursor is accepted as a future pagination hint but unused in v0.")
    if request.offset:
        query["notices"].append("offset is accepted as experimental and unused in this v0 prototype.")

    return {
        "ok": True,
        "schema_version": SCHEMA_VERSION,
        "contract_id": SEARCH_RESPONSE_CONTRACT_ID,
        "mode": MODE,
        "source_policy": request.source_policy,
        "query": query,
        "limits": {
            "result_limit": request.limit,
            "query_length_limit": MAX_QUERY_LENGTH,
        },
        "result_count": len(results),
        "results": results,
        "candidate_result_count": len(candidate_cards),
        "candidate_results": candidate_cards,
        "archive_org_metadata_candidate_search": _candidate_search_summary(archive_candidate_result),
        "candidate_index_search": _candidate_index_search_summary(candidate_index_result),
        "checked_sources": checked_sources,
        "checked": checked_sources,
        "gaps": gaps,
        "warnings": _global_warnings(request.source_policy) + _candidate_warnings(archive_candidate_result),
        "limitations": _global_limitations() + _candidate_limitations(archive_candidate_result),
        "absence_summary": absence_summary,
        "absence": _absence_report_from_summary(absence_summary, checked_sources, gaps),
        "source_status": _source_status_from_checked_sources(checked_sources),
        "timing": {
            "budget_ms": 5000,
            "elapsed_ms": None,
            "timed_out": False,
        },
        "request_limits": _request_limits(),
        "next_actions": _next_actions_for_response(absence_summary),
        "live_probes_enabled": False,
        "archive_org_metadata_candidate_search_enabled": request.source_policy == ARCHIVE_ORG_METADATA_CANDIDATES,
        "candidate_index_search_enabled": candidate_index_result is not None,
        "archive_org_metadata_external_call_performed": bool(
            (archive_candidate_result or {}).get("live_call_performed", False)
        ),
        "downloads_enabled": False,
        "uploads_enabled": False,
        "installs_enabled": False,
        "local_paths_enabled": False,
        "arbitrary_url_fetch_enabled": False,
        "telemetry_enabled": False,
        "generated_by": _generated_by("local_public_search_runtime_v0"),
        "stability": {
            "stable_draft": [
                "ok",
                "schema_version",
                "contract_id",
                "mode",
                "query.raw",
                "query.normalized",
                "limits",
                "results",
            ],
            "experimental": [
                "checked_sources",
                "checked",
                "absence_summary",
                "absence",
                "links",
                "timing.elapsed_ms",
            ],
            "volatile": ["generated_by", "query.notices"],
            "future": ["debug"],
        },
        "links": {
            "html": "/search?q=" + quote(request.normalized_query, safe=""),
            "sources": "/api/v1/sources",
            "status": "/api/v1/status",
        },
        "debug": None,
    }


def _sources_envelope(
    sources: list[dict[str, Any]],
    *,
    selected_source_id: str | None = None,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "ok": True,
        "schema_version": SCHEMA_VERSION,
        "contract_id": "eureka_public_search_sources_v0",
        "mode": MODE,
        "source_count": len(sources),
        "sources": sources,
        "warnings": _global_warnings(),
        "limitations": _global_limitations(),
    }
    if selected_source_id is not None:
        payload["selected_source_id"] = selected_source_id
    return payload


def _forbidden_parameter_error(query: Mapping[str, Sequence[str]]) -> PublicApiResponse | None:
    present = {name for name, values in query.items() if _has_present_value(values)}
    if not present:
        return None
    for group, code, message in (
        (
            LOCAL_PATH_PARAMETERS,
            "local_paths_forbidden",
            "Public search does not accept caller-provided local paths or roots.",
        ),
        (
            DOWNLOAD_PARAMETERS,
            "downloads_disabled",
            "Public search v0 does not expose downloads.",
        ),
        (
            INSTALL_PARAMETERS,
            "installs_disabled",
            "Public search v0 does not expose installs or execution.",
        ),
        (
            UPLOAD_PARAMETERS,
            "uploads_disabled",
            "Public search v0 does not accept uploads or user files.",
        ),
        (
            LIVE_PROBE_PARAMETERS,
            "live_probes_disabled",
            "Public search v0 does not allow live probes or live source fanout.",
        ),
        (
            CREDENTIAL_PARAMETERS,
            "forbidden_parameter",
            "Public search does not accept credentials or API keys.",
        ),
        (
            URL_OR_NETWORK_PARAMETERS,
            "forbidden_parameter",
            "Public search v0 does not accept arbitrary URLs or network source controls.",
        ),
    ):
        matched = sorted(present & group)
        if matched:
            return public_search_error_response(
                400,
                code=code,
                message=message,
                parameter=matched[0],
            )
    return None


def _parse_limit(query: Mapping[str, Sequence[str]]) -> int | PublicApiResponse:
    raw = _optional_value(query, "limit")
    if raw is None:
        return DEFAULT_RESULT_LIMIT
    try:
        value = int(raw)
    except ValueError:
        return public_search_error_response(
            400,
            code="bad_request",
            message="limit must be an integer.",
            parameter="limit",
        )
    if value < 1:
        return public_search_error_response(
            400,
            code="bad_request",
            message="limit must be at least 1.",
            parameter="limit",
        )
    if value > MAX_RESULT_LIMIT:
        return public_search_error_response(
            400,
            code="limit_too_large",
            message=f"limit must be at most {MAX_RESULT_LIMIT}.",
            parameter="limit",
        )
    return value


def _parse_offset(query: Mapping[str, Sequence[str]]) -> int | PublicApiResponse:
    raw = _optional_value(query, "offset")
    if raw is None:
        return 0
    try:
        value = int(raw)
    except ValueError:
        return public_search_error_response(
            400,
            code="bad_request",
            message="offset must be an integer.",
            parameter="offset",
        )
    if value < 0:
        return public_search_error_response(
            400,
            code="bad_request",
            message="offset must be non-negative.",
            parameter="offset",
        )
    return value


def _include_values(query: Mapping[str, Sequence[str]]) -> list[str]:
    values: list[str] = []
    for raw in query.get("include", ()):
        for item in str(raw).split(","):
            normalized = item.strip()
            if normalized:
                values.append(normalized)
    return values


def _optional_value(query: Mapping[str, Sequence[str]], name: str) -> str | None:
    values = query.get(name)
    if not values:
        return None
    raw = str(values[0]).strip()
    return raw or None


def _has_present_value(values: Sequence[str]) -> bool:
    return bool(values) and any(str(value).strip() for value in values)


def _query_terms(query: str) -> tuple[str, ...]:
    return tuple(
        token
        for token in re.split(r"[^a-z0-9.]+", query.casefold())
        if token
    ) or (query.casefold(),)


def _record_matches_query(record: IndexRecord, terms: Sequence[str], query: str) -> bool:
    text = record.search_text().casefold()
    if query in text:
        return True
    return all(term in text for term in terms)


def _record_sort_key(record: IndexRecord) -> tuple[int, int, str, str]:
    lane_priority = {
        "best_direct_answer": 0,
        "installable_or_usable_now": 1,
        "inside_bundles": 2,
        "preservation": 3,
        "community": 4,
        "documentation": 5,
        "mentions_or_traces": 6,
        "absence_or_next_steps": 7,
        "still_searching": 8,
        "other": 9,
    }
    lane = record.primary_lane or (record.result_lanes[0] if record.result_lanes else "other")
    return (
        record.user_cost_score if record.user_cost_score is not None else 9,
        lane_priority.get(lane, 9),
        record.label.casefold(),
        record.index_record_id,
    )


def _query_block(
    request: PublicSearchRequest,
    *,
    interpreted_task_kind: str | None,
) -> dict[str, Any]:
    notices = [
        "local_index_only: searched controlled repo-owned/demo index records."
    ]
    if request.source_policy == ARCHIVE_ORG_METADATA_CANDIDATES:
        notices.append(
            "archive_org_metadata_candidates: also queried Archive.org metadata for review-only candidates."
        )
    return {
        "raw": request.raw_query,
        "normalized": request.normalized_query,
        "source_policy": request.source_policy,
        "interpreted_task_kind": interpreted_task_kind,
        "notices": notices,
    }


def _generated_by(component: str) -> dict[str, Any]:
    return {
        "component": component,
        "contract": "public_search_api_contract_v0",
        "runtime_mode": MODE,
        "notices": [
            "local/prototype runtime only",
            "not hosted public deployment",
            "not production API stability",
        ],
    }


def _plan_to_public_dict(
    query_planner: QueryPlannerService,
    query: str,
) -> dict[str, Any] | None:
    try:
        return query_planner.plan_query(QueryPlanRequest.from_parts(query)).to_dict()
    except ValueError:
        return None


def _checked_sources(
    records: Sequence[IndexRecord],
    source_registry: SourceRegistry,
) -> list[dict[str, Any]]:
    seen: set[str] = set()
    checked: list[dict[str, Any]] = []
    for record in records:
        source_id = record.source_id
        if not source_id or source_id in seen:
            continue
        seen.add(source_id)
        try:
            source_record = source_registry.get_record(source_id)
        except SourceRecordNotFoundError:
            checked.append(
                {
                    "source_id": source_id,
                    "source_family": record.source_family or "unknown",
                    "coverage_depth": "unknown",
                    "status": "unknown",
                    "posture": "unknown",
                    "checked_as": "local_index",
                    "limitations": ["source_registry_record_missing", "local_index_only"],
                }
            )
            continue
        checked.append(_checked_source_from_record(source_record))
    if checked:
        return checked
    return [
        _checked_source_from_record(record, checked_as="not_checked")
        for record in tuple(source_registry.records)[:5]
    ]


def _checked_source_from_record(record: Any, *, checked_as: str = "local_index") -> dict[str, Any]:
    return {
        "source_id": record.source_id,
        "source_family": record.source_family,
        "coverage_depth": record.coverage.coverage_depth,
        "status": record.status,
        "posture": record.trust_lane,
        "checked_as": checked_as,
        "limitations": _source_limitations(record),
    }


def _archive_org_checked_source(result: Mapping[str, Any] | None) -> dict[str, Any]:
    status = str((result or {}).get("status") or "not_requested")
    checked_as = "archive_org_metadata_candidate_search"
    if status in {"unavailable", "failed"}:
        checked_as = f"{checked_as}_{status}"
    return {
        "source_id": "internet_archive_metadata",
        "source_family": "internet_archive",
        "source_label": "Internet Archive metadata search",
        "coverage_depth": "archive_org_metadata_search",
        "status": status,
        "posture": "candidate_only",
        "checked_as": checked_as,
        "limitations": [
            "metadata_only",
            "candidate_not_reviewed_truth",
            "no_download",
            "no_auto_promotion",
        ],
        "capabilities_summary": ["metadata_search"],
        "connector_mode": "metadata_only_http",
        "live_access_mode": "metadata_candidate_search",
    }


def _candidate_index_checked_source(result: Mapping[str, Any] | None) -> dict[str, Any]:
    status = "available" if result is not None else "not_requested"
    return {
        "source_id": "candidate_index",
        "source_family": "candidate_index",
        "source_label": "Local candidate index",
        "coverage_depth": "local_candidate_memory",
        "status": status,
        "posture": "candidate_only",
        "checked_as": "candidate_index_search",
        "limitations": [
            "candidate_not_reviewed_truth",
            "local_candidate_memory",
            "no_download",
            "no_extraction",
            "no_auto_promotion",
        ],
        "capabilities_summary": ["candidate_search"],
        "connector_mode": "local_read_only",
        "live_access_mode": "none",
    }


def _candidate_search_summary(result: Mapping[str, Any] | None) -> dict[str, Any]:
    if not result:
        return {
            "enabled": False,
            "status": "not_requested",
            "candidate_count": 0,
            "total_http_requests": 0,
            "live_call_performed": False,
            "raw_response_committed": False,
            "download_performed": False,
            "accepted_truth": False,
        }
    return {
        "enabled": True,
        "status": str(result.get("status") or "unknown"),
        "query": str(result.get("query") or ""),
        "source_query": str(result.get("source_query") or result.get("query") or ""),
        "query_plan": dict(result.get("query_plan") or {}),
        "candidate_count": int(result.get("candidate_count", 0) or 0),
        "suppressed_candidate_count": int(result.get("suppressed_candidate_count", 0) or 0),
        "candidate_suppressions_applied": list(result.get("candidate_suppressions_applied") or []),
        "total_http_requests": int(result.get("total_http_requests", 0) or 0),
        "live_call_performed": bool(result.get("live_call_performed", False)),
        "metadata_request_performed": bool(result.get("metadata_request_performed", False)),
        "source_probe_executed": bool(result.get("source_probe_executed", False)),
        "cache_hit": bool(result.get("cache_hit", False)),
        "raw_response_committed": bool(result.get("raw_response_committed", False)),
        "download_performed": bool(result.get("download_performed", False)),
        "upload_performed": bool(result.get("upload_performed", False)),
        "extraction_executed": bool(result.get("extraction_executed", False)),
        "accepted_truth": bool(result.get("accepted_truth", False)),
        "review_required": bool(result.get("review_required", True)),
        "failure_reason": result.get("failure_reason"),
        "limitations": list(result.get("limitations") or []),
    }


def _candidate_index_search_summary(result: Mapping[str, Any] | None) -> dict[str, Any]:
    if not result:
        return {
            "enabled": False,
            "status": "not_requested",
            "result_count": 0,
            "accepted_truth": False,
            "public_mutation_enabled": False,
            "reviewed_index_mutated": False,
            "master_index_mutated": False,
        }
    return {
        "enabled": True,
        "status": "succeeded",
        "query": str(result.get("query") or ""),
        "result_count": int(result.get("result_count", 0) or 0),
        "accepted_truth": bool(result.get("accepted_truth", False)),
        "review_required": bool(result.get("review_required", True)),
        "public_mutation_enabled": bool(result.get("public_mutation_enabled", False)),
        "reviewed_index_mutated": bool(result.get("reviewed_index_mutated", False)),
        "master_index_mutated": bool(result.get("master_index_mutated", False)),
    }


def _candidate_warnings(result: Mapping[str, Any] | None) -> list[dict[str, str]]:
    if not result:
        return []
    warnings = []
    for item in result.get("warnings", []) or []:
        warnings.append(_warning("archive_org_metadata_candidate_search", str(item), "info"))
    if result.get("status") == "failed":
        warnings.append(
            _warning(
                "archive_org_metadata_candidate_search_failed",
                "Archive.org metadata candidate search failed for this request.",
                "warning",
            )
        )
    return warnings


def _candidate_limitations(result: Mapping[str, Any] | None) -> list[str]:
    if not result:
        return []
    return [str(item) for item in result.get("limitations", []) or [] if str(item)]


def _archive_org_details_url(candidate: Mapping[str, Any]) -> str | None:
    locator = candidate.get("source_locator")
    if not isinstance(locator, Mapping):
        return None
    url = locator.get("url")
    if not isinstance(url, str):
        return None
    if not url.startswith("https://archive.org/details/"):
        return None
    return url


def _source_for_record(record: IndexRecord, source_registry: SourceRegistry) -> dict[str, Any]:
    if record.source_id:
        try:
            source_record = source_registry.get_record(record.source_id)
        except SourceRecordNotFoundError:
            return {
                "source_id": record.source_id,
                "source_family": record.source_family or "unknown",
                "source_label": record.source_label,
                "source_status": "unknown",
                "posture": "unknown",
                "coverage_depth": "unknown",
                "trust_lane": None,
                "source_lane": None,
                "checked_as": "local_index",
                "limitations": ["source_registry_record_missing", "local_index_only"],
            }
        return _source_public_summary(source_record, checked_as="local_index")
    return {
        "source_id": "unknown-source",
        "source_family": record.source_family or "unknown",
        "source_label": record.source_label,
        "source_status": "unknown",
        "posture": "unknown",
        "coverage_depth": "unknown",
        "trust_lane": None,
        "source_lane": None,
        "checked_as": "local_index",
        "limitations": ["source_identity_missing", "local_index_only"],
    }


def _source_public_summary(record: Any, *, checked_as: str) -> dict[str, Any]:
    return {
        "source_id": record.source_id,
        "source_family": record.source_family,
        "source_label": record.name,
        "source_status": record.status,
        "posture": record.trust_lane,
        "coverage_depth": record.coverage.coverage_depth,
        "trust_lane": record.trust_lane,
        "source_lane": record.authority_class,
        "checked_as": checked_as,
        "limitations": _source_limitations(record),
        "capabilities_summary": list(record.capabilities.enabled_capabilities()),
        "connector_mode": record.coverage.connector_mode,
        "live_access_mode": record.live_access.mode,
    }


def _source_limitations(record: Any) -> list[str]:
    limitations = ["local_index_only"]
    limitations.extend(record.coverage.current_limitations)
    if not record.capabilities.live_supported:
        limitations.append("no_live_probe")
    if record.status in {"placeholder", "future", "local_private_future", "live_deferred"}:
        limitations.append("not_runtime_backed")
    return sorted(set(limitations))


def _identity_block(record: IndexRecord) -> dict[str, Any]:
    public_target_ref = record.target_ref or record.index_record_id
    identity_status = "unknown"
    if record.record_kind == "synthetic_member":
        identity_status = "synthetic_member"
    elif record.record_kind in {"member", "representation", "state_or_release", "resolved_object"}:
        identity_status = "candidate" if record.record_kind != "resolved_object" else "exact"
    elif record.record_kind == "evidence":
        identity_status = "candidate"
    elif record.record_kind == "source_record":
        identity_status = "unknown"
    if record.member_kind in {"article", "article_segment", "page_range", "document_section"}:
        identity_status = "article_segment"
    return {
        "public_target_ref": public_target_ref,
        "target_ref": public_target_ref,
        "resolved_resource_id": record.resolved_resource_id,
        "object_id": record.subject_key,
        "release_or_state_id": record.version_or_state,
        "representation_id": record.representation_id,
        "member_target_ref": public_target_ref if record.member_path else None,
        "native_source_id": record.source_id,
        "identity_status": identity_status,
        "notes": ["public-safe target reference only; no private local path is exposed"],
    }


def _evidence_block(record: IndexRecord) -> dict[str, Any]:
    summaries = [
        {
            "evidence_id": f"{record.index_record_id}:evidence:{index}",
            "evidence_kind": "local_index_summary",
            "source_id": record.source_id or "unknown-source",
            "locator": None,
            "snippet": item[:280],
            "confidence": "unknown",
        }
        for index, item in enumerate(record.evidence)
    ]
    return {
        "evidence_count": len(summaries),
        "summaries": summaries,
        "provenance_notes": ["public-safe evidence summaries only"],
        "missing_evidence": [] if summaries else ["no public evidence summary attached to this index record"],
    }


def _compatibility_block(record: IndexRecord) -> dict[str, Any]:
    evidence = tuple(record.compatibility_evidence)
    summaries = [
        {
            "evidence_id": item.get("evidence_id"),
            "evidence_kind": str(item.get("evidence_kind") or "compatibility_summary"),
            "source_id": str(item.get("source_id") or record.source_id or "unknown-source"),
            "locator": _safe_locator(item.get("locator")),
            "snippet": _compatibility_snippet(item),
            "confidence": item.get("confidence") if item.get("confidence") in {"high", "medium", "low", "unknown"} else "unknown",
        }
        for item in evidence
        if isinstance(item, Mapping)
    ]
    target_platforms = sorted(
        {
            str(platform.get("name") or platform.get("marketing_alias"))
            for item in evidence
            if isinstance(item, Mapping)
            for platform in (_mapping_or_empty(item.get("platform")),)
            if platform.get("name") or platform.get("marketing_alias")
        }
    )
    architectures = sorted(
        {
            str(item.get("architecture"))
            for item in evidence
            if isinstance(item, Mapping) and item.get("architecture")
        }
    )
    status = "unknown"
    claim_types = {
        str(item.get("claim_type"))
        for item in evidence
        if isinstance(item, Mapping) and item.get("claim_type")
    }
    if "does_not_work_on" in claim_types:
        status = "unsupported"
    elif claim_types & {"supports_platform", "driver_for_hardware", "requires"}:
        status = "partial"
    elif claim_types:
        status = "candidate"
    return {
        "status": status,
        "target_platforms": target_platforms,
        "architecture": ", ".join(architectures) if architectures else "unknown",
        "evidence_summaries": summaries,
        "confidence": _compatibility_confidence(evidence),
        "caveats": ["fixture-backed compatibility evidence only"] if summaries else [],
        "unknowns": [] if summaries else ["no compatibility evidence attached"],
    }


def _compatibility_confidence(evidence: Sequence[Mapping[str, Any]]) -> str:
    confidences = {
        str(item.get("confidence"))
        for item in evidence
        if isinstance(item, Mapping) and item.get("confidence")
    }
    if "high" in confidences:
        return "high"
    if "medium" in confidences:
        return "medium"
    if "low" in confidences:
        return "low"
    return "unknown"


def _compatibility_snippet(item: Mapping[str, Any]) -> str | None:
    value = item.get("evidence_text")
    if isinstance(value, str) and value:
        return value[:280]
    claim = item.get("claim_type")
    evidence_kind = item.get("evidence_kind")
    if claim or evidence_kind:
        return " ".join(str(part) for part in (claim, evidence_kind) if part)
    return None


def _safe_locator(value: Any) -> str | None:
    if not isinstance(value, str) or not value:
        return None
    normalized = value.replace("\\", "/")
    if normalized.startswith(("C:/", "D:/", "/Users/", "/home/", "/tmp/", "runtime/", "contracts/")):
        return None
    if "://" in normalized:
        return None
    return normalized[:180]


def _user_cost(record: IndexRecord) -> dict[str, Any]:
    score = record.user_cost_score if record.user_cost_score is not None else 9
    label = "unknown"
    if score <= 1:
        label = "very_low"
    elif score <= 2:
        label = "low"
    elif score <= 5:
        label = "medium"
    elif score <= 8:
        label = "high"
    reasons = list(record.user_cost_reasons) or ["compatibility_unknown"]
    return {
        "score": score,
        "label": label,
        "reasons": reasons,
        "explanation": record.usefulness_summary or f"user cost {score}",
    }


def _parent_lineage(record: IndexRecord) -> list[dict[str, str]]:
    if not record.parent_target_ref:
        return []
    return [
        {
            "target_ref": record.parent_target_ref,
            "label": record.parent_object_label or record.parent_target_ref,
            "relationship": "parent",
        }
    ]


def _member_block(record: IndexRecord) -> dict[str, Any] | None:
    if not record.member_path:
        return None
    return {
        "member_path": record.member_path,
        "member_label": record.label,
        "member_kind": record.member_kind or record.record_kind,
        "media_type": record.media_type or "unknown",
        "byte_length": record.size_bytes,
        "sha256": record.content_hash if _looks_sha256(record.content_hash) else None,
        "parent_target_ref": record.parent_target_ref or record.target_ref or "",
        "parent_label": record.parent_object_label or record.parent_target_ref or "parent bundle",
        "parent_lineage": _parent_lineage(record),
    }


def _representation_block(record: IndexRecord) -> dict[str, Any] | None:
    if not record.representation_id:
        return None
    return {
        "representation_id": record.representation_id,
        "representation_kind": "bounded_fixture_representation",
        "media_type": record.media_type or "unknown",
        "file_name": _basename(record.member_path) if record.member_path else None,
        "size": record.size_bytes,
        "checksum": record.content_hash,
        "access_path_kind": "server_owned_fixture_or_recorded_summary",
        "limitations": ["no_download", "no_install", "local_index_only"],
    }


def _actions_block(record: IndexRecord) -> dict[str, Any]:
    allowed = [
        _action("inspect", "allowed", "Inspect public metadata for this result."),
        _action("view_source", "allowed", "View governed source summary metadata."),
        _action("view_provenance", "allowed", "View public-safe evidence summaries."),
    ]
    if record.summary or record.member_path:
        allowed.append(_action("read", "allowed", "Read public-safe text summary fields only."))
    blocked = [
        _action("download", "blocked", "Downloads are disabled by Public Search Safety / Abuse Guard v0."),
        _action("install_handoff", "blocked", "Installer handoff is disabled in v0."),
        _action("execute", "blocked", "Execution is disabled in v0."),
        _action("upload", "blocked", "Uploads and private source submission are disabled in v0."),
    ]
    future = [
        _action("download_member", "future_gated", "Member downloads require a future rights and safety policy."),
        _action("package_manager_handoff", "future_gated", "Package manager handoff is future only."),
        _action("submit_private_source", "future_gated", "Private source contribution requires future policy."),
    ]
    return {
        "allowed": allowed,
        "blocked": blocked,
        "future_gated": future,
    }


def _action(action_id: str, status: str, reason: str) -> dict[str, Any]:
    return {
        "action_id": action_id,
        "status": status,
        "reason": reason,
        "policy_reference": "docs/reference/ACTION_DOWNLOAD_INSTALL_POLICY.md",
        "requires_confirmation": False if status == "allowed" else None,
        "requires_future_policy": status in {"blocked", "future_gated"},
    }


def _rights_block(record: IndexRecord) -> dict[str, Any]:
    return {
        "rights_status": "public_metadata_only" if record.record_kind == "source_record" else "unknown",
        "distribution_allowed": "unknown",
        "notes": [
            "No rights clearance is claimed.",
            "Public search v0 exposes metadata and summaries only.",
        ],
    }


def _risk_block(record: IndexRecord) -> dict[str, Any]:
    executable_like = _looks_executable_like(record)
    return {
        "executable_risk": "executable_unknown" if executable_like else "metadata_only",
        "malware_scan_status": "not_scanned" if executable_like else "not_applicable",
        "warnings": [
            {
                "warning_type": "no_malware_scan",
                "message": "No malware scan or executable safety claim is made.",
                "severity": "caution" if executable_like else "info",
            }
        ],
    }


def _looks_executable_like(record: IndexRecord) -> bool:
    haystack = " ".join(
        item
        for item in (record.label, record.summary, record.member_path, " ".join(record.action_hints))
        if isinstance(item, str)
    ).casefold()
    return any(token in haystack for token in (".exe", ".msi", "installer", "execute", "utility"))


def _card_warnings(record: IndexRecord) -> list[dict[str, str]]:
    warnings = [
        _warning("local_index_only", "Result came from controlled local index records only.", "info"),
        _warning("no_live_probe", "No live external source probe was performed.", "info"),
        _warning("no_download", "Downloads are disabled in public search v0.", "caution"),
        _warning("no_install", "Installs and execution are disabled in public search v0.", "caution"),
        _warning("no_rights_clearance", "No rights clearance is claimed.", "caution"),
    ]
    if _looks_executable_like(record):
        warnings.append(_warning("no_malware_scan", "Executable-like material was not scanned.", "warning"))
    return warnings


def _warning(warning_type: str, message: str, severity: str) -> dict[str, str]:
    return {
        "warning_type": warning_type,
        "message": message,
        "severity": severity,
    }


def _card_limitations(record: IndexRecord) -> list[str]:
    limitations = {
        "source_coverage_limited",
        "compatibility_evidence_limited",
        "no_live_probe",
        "no_download",
        "no_install",
        "no_execute",
        "no_upload",
        "no_malware_scan",
        "no_rights_clearance",
        "external_baseline_pending",
        "local_index_only",
        "not_production_ranking",
    }
    if record.source_id in {
        "synthetic-fixtures",
        "local-bundle-fixtures",
        "internet-archive-recorded-fixtures",
        "github-releases-recorded-fixtures",
        "article-scan-recorded-fixtures",
        "manual-document-recorded-fixtures",
        "package-registry-recorded-fixtures",
        "review-description-recorded-fixtures",
        "software-heritage-recorded-fixtures",
        "sourceforge-recorded-fixtures",
        "wayback-memento-recorded-fixtures",
    }:
        limitations.add("fixture_backed")
    if record.record_kind == "source_record":
        limitations.add("static_summary_only")
    return sorted(limitations)


def _links_block(record: IndexRecord) -> dict[str, str | None]:
    target_ref = record.target_ref
    return {
        "inspect": "/?target_ref=" + quote(target_ref, safe="") if target_ref else None,
        "source": "/api/v1/source/" + quote(record.source_id, safe="") if record.source_id else None,
        "evidence": None,
        "absence": "/absence/search?q=" + quote(record.label, safe=""),
    }


def _why_matched(record: IndexRecord, terms: Sequence[str]) -> list[str]:
    text = record.search_text().casefold()
    matched = [term for term in terms if term in text]
    if not matched:
        return ["query matched controlled local-index text"]
    return [f"matched term: {term}" for term in matched[:6]]


def _card_stability() -> dict[str, list[str]]:
    return {
        "stable_draft": [
            "result_id",
            "title",
            "record_kind",
            "result_lane",
            "user_cost.score",
            "source.source_id",
            "source.source_family",
            "identity.public_target_ref",
            "actions.allowed.status",
            "actions.blocked.status",
            "warnings",
            "limitations",
        ],
        "experimental": [
            "why_matched",
            "why_ranked",
            "compatibility.confidence",
            "member",
            "representation",
        ],
        "volatile": ["matched_query_terms"],
        "internal": [],
        "future": ["debug"],
    }


def _global_warnings(source_policy: str = MODE) -> list[dict[str, str]]:
    search_scope = (
        "Public search runtime searches controlled local index records and Archive.org metadata-only candidates."
        if source_policy == ARCHIVE_ORG_METADATA_CANDIDATES
        else "Public search runtime searches controlled local index records only."
    )
    return [
        {
            "warning_type": "local_index_only",
            "message": search_scope,
        },
        {
            "warning_type": "not_hosted_public_deployment",
            "message": "This is a local/prototype backend runtime, not hosted public deployment.",
        },
    ]


def _global_limitations() -> list[str]:
    return [
        "local_index_only",
        "no_live_probe",
        "no_download",
        "no_install",
        "no_upload",
        "no_local_path_search",
        "no_telemetry",
        "not_production",
    ]


def _request_limits() -> dict[str, int]:
    return {
        "max_query_length": MAX_QUERY_LENGTH,
        "default_limit": DEFAULT_RESULT_LIMIT,
        "max_limit": MAX_RESULT_LIMIT,
        "timeout_ms": 5000,
    }


def _absence_report_from_summary(
    summary: Mapping[str, Any] | None,
    checked_sources: Sequence[Mapping[str, Any]],
    gaps: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    if not summary or summary.get("status") == "none":
        status = "unknown"
    else:
        status = "no_verified_result"
    return {
        "absence_status": status,
        "query_fingerprint": None,
        "sources_checked": [
            str(source.get("source_id"))
            for source in checked_sources
            if source.get("source_id")
        ],
        "near_misses": [],
        "gaps": [
            str(gap.get("gap_type") or gap.get("message"))
            for gap in gaps
            if gap.get("gap_type") or gap.get("message")
        ],
        "next_actions": list(_next_actions_for_response(summary)),
        "limitations": _global_limitations(),
        "privacy_classification": "public",
    }


def _source_status_from_checked_sources(
    checked_sources: Sequence[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    statuses: list[dict[str, Any]] = []
    for source in checked_sources:
        raw_status = str(source.get("status") or "placeholder")
        status = "placeholder"
        if raw_status in {"active_fixture", "fixture"}:
            status = "active_fixture"
        elif raw_status in {"active_recorded_fixture", "recorded_fixture"}:
            status = "active_recorded_fixture"
        elif raw_status in {"succeeded", "zero_results"}:
            status = "metadata_candidate_source"
        elif raw_status in {"failed", "rate_limited", "unavailable"}:
            status = "metadata_candidate_source_limited"
        elif raw_status in {"live_disabled", "live_deferred"}:
            status = "live_disabled"
        elif raw_status == "local_private_future":
            status = "local_private_future"
        elif raw_status == "available" and source.get("source_id") == "candidate_index":
            status = "local_candidate_memory"
        statuses.append(
            {
                "source_id": str(source.get("source_id") or "unknown-source"),
                "source_family": str(source.get("source_family") or "unknown"),
                "label": str(source.get("source_label") or source.get("source_id") or "Unknown source"),
                "status": status,
                "coverage_depth": str(source.get("coverage_depth") or "unknown"),
                "live_supported": False,
                "live_enabled": False,
                "network_required": source.get("source_id") == "internet_archive_metadata",
                "last_checked": None,
                "last_synced": None,
                "limitations": list(source.get("limitations") or ["local_index_only"]),
                "next_coverage_step": "future source coverage review",
                "public_safe": True,
                "health": None,
            }
        )
    return statuses


def _next_actions_for_response(summary: Mapping[str, Any] | None) -> list[str]:
    if not summary:
        return []
    actions = summary.get("next_actions")
    if isinstance(actions, list):
        return [str(action) for action in actions]
    return []


def _mapping_or_empty(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _basename(value: str | None) -> str | None:
    if not value:
        return None
    return value.replace("\\", "/").rsplit("/", 1)[-1]


def _looks_sha256(value: str | None) -> bool:
    return bool(isinstance(value, str) and re.fullmatch(r"[a-f0-9]{64}", value))
