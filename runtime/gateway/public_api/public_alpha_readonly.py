from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping, Sequence

from runtime.gateway.public_api.resolution_boundary import PublicApiResponse
from runtime.relay.snapshot_relay import project_relay_response
from runtime.snapshots.relay_foundation import CREATED_AT, stable_id


MODE = "reviewed_snapshot_read_only"
SCHEMA_VERSION = "public_alpha_readonly.v0"
MAX_QUERY_LENGTH = 160
DEFAULT_LIMIT = 10
MAX_LIMIT = 10

ALLOWED_QUERY_PARAMETERS = frozenset({"q", "limit"})
FORBIDDEN_QUERY_PARAMETERS = frozenset(
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
        "url",
        "fetch_url",
        "crawl_url",
        "source_url",
        "network",
        "arbitrary_source",
        "download",
        "install",
        "execute",
        "upload",
        "user_file",
        "source_credentials",
        "auth_token",
        "api_key",
        "live_probe",
        "live_source",
    }
)
NON_CLAIMS = (
    "not_production",
    "not_public_launch",
    "not_live_source_search",
    "not_download_service",
    "not_extraction_service",
    "limited_reviewed_snapshot",
)


@dataclass(frozen=True)
class PublicAlphaReadOnlyApi:
    snapshot_build_result: Mapping[str, Any]
    relay_build_result: Mapping[str, Any]

    def status(self, query: Mapping[str, Sequence[str]] | None = None) -> PublicApiResponse:
        forbidden = _forbidden_query_response(query or {})
        if forbidden is not None:
            return forbidden
        return PublicApiResponse(
            status_code=200,
            body={
                **self._base_envelope("eureka_public_alpha_readonly_status_v0"),
                "status": "ready_read_only_local",
                "public_alpha_readonly_implemented": True,
                "local_runtime_available": True,
            },
        )

    def search(self, query: Mapping[str, Sequence[str]]) -> PublicApiResponse:
        forbidden = _forbidden_query_response(query)
        if forbidden is not None:
            return forbidden
        unexpected = sorted(name for name in query if name not in ALLOWED_QUERY_PARAMETERS)
        if unexpected:
            return _error_response(
                400,
                code="bad_request",
                message=f"Unsupported public alpha parameter '{unexpected[0]}'.",
                parameter=unexpected[0],
            )

        raw_query = _optional_value(query, "q")
        if raw_query is None or not raw_query.strip():
            return _error_response(
                400,
                code="query_required",
                message="Provide a non-empty q query parameter.",
                parameter="q",
            )
        normalized_query = " ".join(raw_query.split())
        if len(normalized_query) > MAX_QUERY_LENGTH:
            return _error_response(
                400,
                code="query_too_long",
                message=f"q must be at most {MAX_QUERY_LENGTH} characters.",
                parameter="q",
            )
        limit_or_error = _parse_limit(query)
        if isinstance(limit_or_error, PublicApiResponse):
            return limit_or_error

        results = self._matching_records(normalized_query)[:limit_or_error]
        query_response = self._query_response(normalized_query, results)
        body = {
            **self._base_envelope("eureka_public_alpha_readonly_search_v0"),
            "query": {
                "raw": raw_query,
                "normalized": normalized_query,
            },
            "limit": limit_or_error,
            "result_count": len(results),
            "results": results,
            "relay_query_response": query_response,
            "relay_projection": project_relay_response(query_response, "public_api_read_only"),
            "object_pages": [self._object_packet(record, status_code=None) for record in results],
            "source_summaries": self._source_summaries_for_records(results),
            "evidence_summaries": self._evidence_summaries_for_records(results),
            "absence_summaries": [] if results else self._absence_summaries(),
            "known_needs": [] if results else self._need_summaries(),
            "links": {
                "status": "/api/v1/alpha/status",
                "html": "/alpha?q=" + normalized_query.replace(" ", "+"),
                "needs": "/api/v1/alpha/needs",
            },
        }
        return PublicApiResponse(status_code=200, body=body)

    def object(self, object_id: str, query: Mapping[str, Sequence[str]] | None = None) -> PublicApiResponse:
        forbidden = _forbidden_query_response(query or {})
        if forbidden is not None:
            return forbidden
        normalized = object_id.strip()
        if not normalized:
            return _error_response(
                400,
                code="object_id_required",
                message="Provide a non-empty object identifier.",
                parameter="object_id",
            )
        for record in self._records():
            if normalized in {str(record.get("object_id")), str(record.get("record_id"))}:
                return PublicApiResponse(status_code=200, body=self._object_packet(record))
        return _error_response(
            404,
            code="not_found",
            message=f"Unknown reviewed snapshot object '{normalized}'.",
            parameter="object_id",
        )

    def source_summary(
        self,
        summary_id: str,
        query: Mapping[str, Sequence[str]] | None = None,
    ) -> PublicApiResponse:
        return self._summary_response(
            summary_id,
            self._source_summaries(),
            "source_summary",
            "eureka_public_alpha_readonly_source_summary_v0",
            query,
        )

    def evidence_summary(
        self,
        summary_id: str,
        query: Mapping[str, Sequence[str]] | None = None,
    ) -> PublicApiResponse:
        return self._summary_response(
            summary_id,
            self._evidence_summaries(),
            "evidence_summary",
            "eureka_public_alpha_readonly_evidence_summary_v0",
            query,
        )

    def absence_summary(
        self,
        summary_id: str,
        query: Mapping[str, Sequence[str]] | None = None,
    ) -> PublicApiResponse:
        return self._summary_response(
            summary_id,
            self._absence_summaries(),
            "absence_summary",
            "eureka_public_alpha_readonly_absence_summary_v0",
            query,
        )

    def known_needs(self, query: Mapping[str, Sequence[str]] | None = None) -> PublicApiResponse:
        forbidden = _forbidden_query_response(query or {})
        if forbidden is not None:
            return forbidden
        needs = self._need_summaries()
        return PublicApiResponse(
            status_code=200,
            body={
                **self._base_envelope("eureka_public_alpha_readonly_known_needs_v0"),
                "need_count": len(needs),
                "known_needs": needs,
            },
        )

    def _base_envelope(self, contract_id: str) -> dict[str, Any]:
        envelope = self.snapshot_build_result["envelope"]
        manifest = self.snapshot_build_result["manifest"]
        relay_manifest = self.relay_build_result["relay_manifest"]
        relay_index = self.relay_build_result["relay_record_index"]
        return {
            "ok": True,
            "schema_version": SCHEMA_VERSION,
            "contract_id": contract_id,
            "mode": MODE,
            "read_only": True,
            "reviewed_index_only": True,
            "snapshot_backed": True,
            "relay_backed": True,
            "created_at": CREATED_AT,
            "snapshot": {
                "snapshot_id": envelope["snapshot_id"],
                "snapshot_version": envelope["snapshot_version"],
                "record_count": manifest["record_count"],
                "source_summary_count": manifest["source_summary_count"],
                "evidence_summary_count": manifest["evidence_summary_count"],
                "absence_summary_count": manifest["absence_summary_count"],
                "known_need_count": manifest["known_need_count"],
                "integrity_manifest_ref": envelope["integrity_manifest_ref"],
                "capability_profile_ref": envelope["capability_profile_ref"],
            },
            "relay": {
                "relay_id": relay_manifest["relay_id"],
                "relay_record_index_id": relay_index["relay_record_index_id"],
                "record_count": relay_index["record_count"],
                "supported_projection_profiles": relay_manifest["supported_projection_profiles"],
            },
            "capability_profile": self.snapshot_build_result["capability_profile"],
            "limitations": [
                "reviewed snapshot records only",
                "fixture-sized alpha corpus",
                "absence means not present in the current reviewed snapshot",
            ],
            "non_claims": list(NON_CLAIMS),
            **_unsafe_false_flags(),
        }

    def _object_packet(
        self,
        record: Mapping[str, Any],
        *,
        status_code: int | None = 200,
    ) -> dict[str, Any]:
        del status_code
        source_summaries = self._summaries_by_ref(
            self._source_summaries(),
            "summary_id",
            _string_list(record.get("source_summary_refs")),
        )
        evidence_summaries = self._summaries_by_ref(
            self._evidence_summaries(),
            "summary_id",
            _string_list(record.get("evidence_summary_refs")),
        )
        return {
            **self._base_envelope("eureka_public_alpha_readonly_object_packet_v0"),
            "record": dict(record),
            "source_summaries": source_summaries,
            "evidence_summaries": evidence_summaries,
            "actions": {
                "allowed": ["view", "cite"],
                "blocked": ["download", "install", "execute", "upload", "live_probe"],
            },
            "links": {
                "html": "/alpha/object?id=" + str(record.get("object_id")),
                "api": "/api/v1/alpha/object/" + str(record.get("object_id")),
            },
        }

    def _summary_response(
        self,
        summary_id: str,
        summaries: Sequence[Mapping[str, Any]],
        field_name: str,
        contract_id: str,
        query: Mapping[str, Sequence[str]] | None,
    ) -> PublicApiResponse:
        forbidden = _forbidden_query_response(query or {})
        if forbidden is not None:
            return forbidden
        normalized = summary_id.strip()
        if not normalized:
            return _error_response(
                400,
                code=f"{field_name}_id_required",
                message=f"Provide a non-empty {field_name} identifier.",
                parameter="summary_id",
            )
        for summary in summaries:
            if summary.get("summary_id") == normalized:
                return PublicApiResponse(
                    status_code=200,
                    body={
                        **self._base_envelope(contract_id),
                        field_name: dict(summary),
                    },
                )
        return _error_response(
            404,
            code="not_found",
            message=f"Unknown public alpha {field_name} '{normalized}'.",
            parameter="summary_id",
        )

    def _query_response(self, query: str, results: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
        return {
            "schema_version": "relay_query_response.v0",
            "record_type": "relay_query_response",
            "query_response_id": stable_id(
                "public_alpha_relay_query_response",
                query,
                [record.get("record_id") for record in results],
            ),
            "created_at": CREATED_AT,
            "query": query,
            "read_only": True,
            "result_count": len(results),
            "results": [dict(record) for record in results],
            "mutation_enabled": False,
            "live_source_actions_enabled": False,
            "download_enabled": False,
            "extraction_enabled": False,
            "limitations": ["read-only query over reviewed public alpha snapshot records"],
        }

    def _matching_records(self, query: str) -> list[dict[str, Any]]:
        terms = _query_terms(query)
        if not terms:
            return []
        matches: list[dict[str, Any]] = []
        for record in self._records():
            text = _record_text(record)
            if all(term in text for term in terms):
                matches.append(dict(record))
        return matches

    def _records(self) -> list[Mapping[str, Any]]:
        record_set = self.snapshot_build_result["record_set"]
        return [record for record in record_set.get("records", []) if isinstance(record, Mapping)]

    def _source_summaries(self) -> list[Mapping[str, Any]]:
        return _mapping_list(self.snapshot_build_result.get("source_summaries"))

    def _evidence_summaries(self) -> list[Mapping[str, Any]]:
        return _mapping_list(self.snapshot_build_result.get("evidence_summaries"))

    def _absence_summaries(self) -> list[Mapping[str, Any]]:
        return _mapping_list(self.snapshot_build_result.get("absence_summaries"))

    def _need_summaries(self) -> list[Mapping[str, Any]]:
        return _mapping_list(self.snapshot_build_result.get("need_summaries"))

    def _source_summaries_for_records(self, records: Sequence[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
        refs = {ref for record in records for ref in _string_list(record.get("source_summary_refs"))}
        return self._summaries_by_ref(self._source_summaries(), "summary_id", refs)

    def _evidence_summaries_for_records(self, records: Sequence[Mapping[str, Any]]) -> list[Mapping[str, Any]]:
        refs = {ref for record in records for ref in _string_list(record.get("evidence_summary_refs"))}
        return self._summaries_by_ref(self._evidence_summaries(), "summary_id", refs)

    @staticmethod
    def _summaries_by_ref(
        summaries: Sequence[Mapping[str, Any]],
        key: str,
        refs: Sequence[str] | set[str],
    ) -> list[Mapping[str, Any]]:
        ref_set = set(refs)
        return [dict(summary) for summary in summaries if str(summary.get(key)) in ref_set]


def _parse_limit(query: Mapping[str, Sequence[str]]) -> int | PublicApiResponse:
    raw = _optional_value(query, "limit")
    if raw is None:
        return DEFAULT_LIMIT
    try:
        value = int(raw)
    except ValueError:
        return _error_response(
            400,
            code="bad_request",
            message="limit must be an integer.",
            parameter="limit",
        )
    if value < 1:
        return _error_response(
            400,
            code="bad_request",
            message="limit must be at least 1.",
            parameter="limit",
        )
    if value > MAX_LIMIT:
        return _error_response(
            400,
            code="limit_too_large",
            message=f"limit must be at most {MAX_LIMIT}.",
            parameter="limit",
        )
    return value


def _forbidden_query_response(query: Mapping[str, Sequence[str]]) -> PublicApiResponse | None:
    forbidden = [
        name
        for name in sorted(FORBIDDEN_QUERY_PARAMETERS)
        if query.get(name) and str(query[name][0]).strip()
    ]
    if not forbidden:
        return None
    first = forbidden[0]
    if first in {"live_probe", "live_source"}:
        code = "live_probes_disabled"
    elif first in {"download"}:
        code = "downloads_disabled"
    elif first in {"install", "execute"}:
        code = "installs_disabled"
    elif first in {"upload", "user_file"}:
        code = "uploads_disabled"
    elif first in {"index_path", "store_root", "run_store_root", "task_store_root", "memory_store_root", "local_path", "path", "file_path", "directory", "root"}:
        code = "local_paths_forbidden"
    else:
        code = "forbidden_parameter"
    return _error_response(
        400,
        code=code,
        message="Public alpha read-only routes reject live, local path, credential, mutation, and transfer controls.",
        parameter=first,
        extra={"blocked_parameters": forbidden},
    )


def _error_response(
    status_code: int,
    *,
    code: str,
    message: str,
    parameter: str | None = None,
    extra: Mapping[str, Any] | None = None,
) -> PublicApiResponse:
    return PublicApiResponse(
        status_code=status_code,
        body={
            "ok": False,
            "schema_version": SCHEMA_VERSION,
            "contract_id": "eureka_public_alpha_readonly_error_v0",
            "mode": MODE,
            "error": {
                "code": code,
                "message": message,
                "status": status_code,
                "parameter": parameter,
                "retryable": False,
                "public_safe": True,
            },
            "non_claims": list(NON_CLAIMS),
            **_unsafe_false_flags(),
            **dict(extra or {}),
        },
    )


def _unsafe_false_flags() -> dict[str, bool]:
    return {
        "mutation_enabled": False,
        "live_source_actions_enabled": False,
        "download_enabled": False,
        "upload_enabled": False,
        "install_enabled": False,
        "execution_enabled": False,
        "extraction_enabled": False,
        "model_provider_enabled": False,
        "deployment_performed": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
        "master_index_mutated": False,
        "data_public_index_mutated": False,
    }


def _optional_value(query: Mapping[str, Sequence[str]], name: str) -> str | None:
    values = query.get(name)
    if not values:
        return None
    value = str(values[0]).strip()
    return value or None


def _query_terms(query: str) -> list[str]:
    return [term for term in query.casefold().split() if term]


def _record_text(record: Mapping[str, Any]) -> str:
    parts = [
        record.get("record_id"),
        record.get("object_id"),
        record.get("title"),
        record.get("domain_id"),
        record.get("result_kind"),
        record.get("reviewed_status"),
        " ".join(_string_list(record.get("limitations"))),
    ]
    return " ".join(str(part) for part in parts if part).casefold()


def _mapping_list(value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, list):
        return []
    return [item for item in value if isinstance(item, Mapping)]


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, list):
        return []
    return [str(item) for item in value if isinstance(item, str) and item]
