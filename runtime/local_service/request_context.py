"""Request context construction for the read-only local service."""

from dataclasses import dataclass
from typing import Mapping
from urllib.parse import parse_qs, unquote, urlsplit

from .validation import validate_no_mutation_route, validate_query_params


@dataclass(frozen=True)
class LocalRequestContext:
    method: str
    path: str
    query: str
    params: Mapping[str, list[str]]
    client_host: str
    client_scope: str
    body: str = ""
    body_params: Mapping[str, list[str]] = None
    headers: Mapping[str, str] = None
    warnings: tuple[str, ...] = ()
    limitations: tuple[str, ...] = (
        "local reviewed index only",
        "read-only service",
        "no live source inspection",
    )


def build_request_context(
    method: str,
    path: str,
    query: str | Mapping[str, object] | None,
    client_host: str,
    headers: Mapping[str, str] | None = None,
    body: str | bytes | None = None,
) -> LocalRequestContext:
    split = urlsplit(str(path or "/"))
    request_path = unquote(split.path or "/")
    query_text = _query_text(split.query, query)
    params = parse_qs(query_text, keep_blank_values=True)
    body_text = _body_text(body)
    body_params = parse_qs(body_text, keep_blank_values=True)
    method_value = str(method or "").strip().upper()
    scope = _network().classify_client_scope(client_host)
    if scope.value == "loopback":
        validate_no_mutation_route(method_value, request_path)
    validate_query_params(params)
    validate_query_params(body_params)
    return LocalRequestContext(
        method=method_value,
        path=request_path,
        query=query_text,
        params=params,
        body=body_text,
        body_params=body_params,
        headers={str(key): str(value) for key, value in dict(headers or {}).items()},
        client_host=str(client_host or ""),
        client_scope=scope.value,
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


def _body_text(body: str | bytes | None) -> str:
    if body is None:
        return ""
    if isinstance(body, bytes):
        return body.decode("utf-8")
    return str(body)


def _network():
    return __import__("runtime.local_network", fromlist=["classify_client_scope"])
