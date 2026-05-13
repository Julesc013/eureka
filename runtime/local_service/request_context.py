"""Request context construction for the read-only local service."""

from dataclasses import dataclass
from typing import Mapping
from urllib.parse import parse_qs, unquote, urlsplit

from .validation import validate_host_allowed, validate_no_mutation_route, validate_query_params


@dataclass(frozen=True)
class LocalRequestContext:
    method: str
    path: str
    query: str
    params: Mapping[str, list[str]]
    client_host: str
    warnings: tuple[str, ...] = ()
    limitations: tuple[str, ...] = (
        "local reviewed index only",
        "read-only service",
        "no live source inspection",
    )


def build_request_context(method: str, path: str, query: str | Mapping[str, object] | None, client_host: str) -> LocalRequestContext:
    split = urlsplit(str(path or "/"))
    request_path = unquote(split.path or "/")
    query_text = _query_text(split.query, query)
    params = parse_qs(query_text, keep_blank_values=True)
    validate_host_allowed(client_host)
    validate_no_mutation_route(method, request_path)
    validate_query_params(params)
    return LocalRequestContext(
        method=str(method or "").strip().upper(),
        path=request_path,
        query=query_text,
        params=params,
        client_host=str(client_host or ""),
    )


def _query_text(path_query: str, query: str | Mapping[str, object] | None) -> str:
    if path_query:
        return path_query
    if query is None:
        return ""
    if isinstance(query, Mapping):
        parts: list[str] = []
        for key, value in query.items():
            if isinstance(value, (list, tuple)):
                for item in value:
                    parts.append(f"{key}={item}")
            else:
                parts.append(f"{key}={value}")
        return "&".join(parts)
    return str(query)
