from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from runtime.engine.index import LocalIndexNotFoundError, LocalIndexSchemaError
from runtime.engine.interfaces.public import (
    LocalIndexBuildRequest,
    LocalIndexBuildResult,
    LocalIndexQueryRequest,
    LocalIndexQueryResult,
    LocalIndexStatusRequest,
    LocalIndexStatusResult,
)
from runtime.engine.interfaces.service import LocalIndexService
from runtime.gateway.public_api.resolution_boundary import PublicApiResponse


class LocalIndexPublicApi:
    def __init__(self, index_service: LocalIndexService) -> None:
        self._index_service = index_service

    def build_index(self, request: LocalIndexBuildRequest) -> PublicApiResponse:
        try:
            result = self._index_service.build_index(request)
        except ValueError as error:
            return PublicApiResponse(
                status_code=400,
                body=local_index_error_envelope(
                    code="invalid_index_build_request",
                    message=str(error),
                    index_path=request.index_path,
                ),
            )
        return PublicApiResponse(
            status_code=200,
            body=local_index_build_to_public_envelope(result),
        )

    def get_index_status(self, request: LocalIndexStatusRequest) -> PublicApiResponse:
        try:
            result = self._index_service.get_index_status(request)
        except LocalIndexNotFoundError:
            return PublicApiResponse(
                status_code=404,
                body=local_index_error_envelope(
                    code="local_index_not_found",
                    message=f"Local index '{request.index_path}' was not found.",
                    index_path=request.index_path,
                ),
            )
        except (LocalIndexSchemaError, ValueError) as error:
            return PublicApiResponse(
                status_code=400,
                body=local_index_error_envelope(
                    code="invalid_local_index",
                    message=str(error),
                    index_path=request.index_path,
                ),
            )
        return PublicApiResponse(
            status_code=200,
            body=local_index_status_to_public_envelope(result),
        )

    def query_index(self, request: LocalIndexQueryRequest) -> PublicApiResponse:
        try:
            result = self._index_service.query_index(request)
        except LocalIndexNotFoundError:
            return PublicApiResponse(
                status_code=404,
                body=local_index_error_envelope(
                    code="local_index_not_found",
                    message=f"Local index '{request.index_path}' was not found.",
                    index_path=request.index_path,
                    query=request.query,
                ),
            )
        except (LocalIndexSchemaError, ValueError) as error:
            return PublicApiResponse(
                status_code=400,
                body=local_index_error_envelope(
                    code="invalid_local_index_query",
                    message=str(error),
                    index_path=request.index_path,
                    query=request.query,
                ),
            )
        return PublicApiResponse(
            status_code=200,
            body=local_index_query_to_public_envelope(result),
        )


def local_index_build_to_public_envelope(result: LocalIndexBuildResult) -> dict[str, Any]:
    envelope: dict[str, Any] = {
        "status": result.status,
        "index": result.metadata.to_dict(),
    }
    if result.notices:
        envelope["notices"] = [notice.to_dict() for notice in result.notices]
    return envelope


def local_index_status_to_public_envelope(result: LocalIndexStatusResult) -> dict[str, Any]:
    envelope: dict[str, Any] = {
        "status": result.status,
        "index": result.metadata.to_dict(),
    }
    if result.notices:
        envelope["notices"] = [notice.to_dict() for notice in result.notices]
    return envelope


def local_index_query_to_public_envelope(result: LocalIndexQueryResult) -> dict[str, Any]:
    envelope: dict[str, Any] = {
        "status": result.status,
        "query": result.query,
        "result_count": len(result.results),
        "results": [item.to_dict() for item in result.results],
        "index": result.metadata.to_dict(),
    }
    if result.notices:
        envelope["notices"] = [notice.to_dict() for notice in result.notices]
    return envelope


def local_index_error_envelope(
    *,
    code: str,
    message: str,
    index_path: str | None = None,
    query: str | None = None,
) -> dict[str, Any]:
    envelope: dict[str, Any] = {
        "status": "blocked",
        "index": _bootstrap_index_metadata(index_path),
        "results": [],
    }
    if query is not None:
        envelope["query"] = query
        envelope["result_count"] = 0
    envelope["notices"] = [
        {
            "code": code,
            "severity": "warning",
            "message": message,
        }
    ]
    return envelope


def _bootstrap_index_metadata(index_path: str | None) -> dict[str, Any]:
    return {
        "index_path_kind": "bootstrap_local_path",
        "index_path": index_path,
        "fts_mode": "fallback_like",
        "record_count": 0,
        "record_kind_counts": {},
    }
