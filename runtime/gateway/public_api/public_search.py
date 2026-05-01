from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any, Mapping, Sequence
from urllib.parse import quote

from runtime.engine.index import IndexRecord
from runtime.engine.interfaces.public import QueryPlanRequest
from runtime.engine.interfaces.service import QueryPlannerService
from runtime.gateway.public_api.resolution_boundary import PublicApiResponse
from runtime.source_registry import SourceRecordNotFoundError, SourceRegistry


SCHEMA_VERSION = "0.1.0"
SEARCH_RESPONSE_CONTRACT_ID = "eureka_public_search_response_v0"
ERROR_RESPONSE_CONTRACT_ID = "eureka_public_search_error_response_v0"
RESULT_CARD_CONTRACT_ID = "eureka_public_search_result_card_v0"
MODE = "local_index_only"
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


class PublicSearchPublicApi:
    def __init__(
        self,
        *,
        index_records: tuple[IndexRecord, ...],
        source_registry: SourceRegistry,
        query_planner: QueryPlannerService,
        index_status: str = "controlled_local_index_only",
        index_document_count: int | None = None,
    ) -> None:
        self._index_records = tuple(index_records)
        self._source_registry = source_registry
        self._query_planner = query_planner
        self._index_status = index_status
        self._index_document_count = index_document_count if index_document_count is not None else len(index_records)

    def search(
        self,
        query: Mapping[str, Sequence[str]],
        *,
        default_profile: str = "api_client",
    ) -> PublicApiResponse:
        request_or_error = validate_public_search_query(
            query,
            default_profile=default_profile,
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
        body = _search_success_envelope(
            request,
            cards,
            checked_sources=_checked_sources(limited, self._source_registry),
            plan=_plan_to_public_dict(self._query_planner, request.normalized_query),
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

    source_policy = _optional_value(query, "source_policy") or MODE
    if source_policy != MODE:
        return public_search_error_response(
            400,
            code="unsupported_mode",
            message="Public search v0 only supports local_index_only source_policy.",
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


def _search_success_envelope(
    request: PublicSearchRequest,
    results: list[dict[str, Any]],
    *,
    checked_sources: list[dict[str, Any]],
    plan: dict[str, Any] | None,
) -> dict[str, Any]:
    gaps: list[dict[str, Any]] = []
    absence_summary: dict[str, Any] | None = {
        "status": "none",
        "message": "At least one controlled local-index result matched.",
        "searched_scope": "controlled local index",
        "next_actions": [],
    }
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
        "query": query,
        "limits": {
            "result_limit": request.limit,
            "query_length_limit": MAX_QUERY_LENGTH,
        },
        "result_count": len(results),
        "results": results,
        "checked_sources": checked_sources,
        "checked": checked_sources,
        "gaps": gaps,
        "warnings": _global_warnings(),
        "limitations": _global_limitations(),
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
    return {
        "raw": request.raw_query,
        "normalized": request.normalized_query,
        "interpreted_task_kind": interpreted_task_kind,
        "notices": [
            "local_index_only: searched controlled repo-owned/demo index records only.",
        ],
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


def _global_warnings() -> list[dict[str, str]]:
    return [
        {
            "warning_type": "local_index_only",
            "message": "Public search runtime searches controlled local index records only.",
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
        elif raw_status in {"live_disabled", "live_deferred"}:
            status = "live_disabled"
        elif raw_status == "local_private_future":
            status = "local_private_future"
        statuses.append(
            {
                "source_id": str(source.get("source_id") or "unknown-source"),
                "source_family": str(source.get("source_family") or "unknown"),
                "label": str(source.get("source_label") or source.get("source_id") or "Unknown source"),
                "status": status,
                "coverage_depth": str(source.get("coverage_depth") or "unknown"),
                "live_supported": False,
                "live_enabled": False,
                "network_required": False,
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
