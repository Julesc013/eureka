"""Validation helpers for the read-only local service."""

from typing import Mapping

from .errors import LocalServiceHostError, LocalServiceReadOnlyError, LocalServiceValidationError


ALLOWED_HOSTS = {"127.0.0.1", "localhost"}
FORBIDDEN_HOSTS = {"0.0.0.0", "::", "", "*"}
MUTATING_METHODS = {"POST", "PUT", "PATCH", "DELETE"}
READ_ONLY_METHODS = {"GET"}
OPERATOR_MUTATION_METHODS = {"POST"}
MAX_QUERY_LENGTH = 256
MAX_RESULT_LIMIT = 50
DEFAULT_RESULT_LIMIT = 20


def validate_host_allowed(host: str, bind_lan: bool = False) -> str:
    try:
        return _network().validate_service_host(host, bind_lan=bind_lan)
    except Exception as exc:
        raise LocalServiceHostError(str(exc)) from exc


def validate_read_only_method(method: str) -> str:
    value = str(method or "").strip().upper()
    if value in MUTATING_METHODS:
        raise LocalServiceReadOnlyError(f"{value} is disabled for the read-only local service")
    if value not in READ_ONLY_METHODS:
        raise LocalServiceValidationError(f"{value or '<empty>'} is not supported by the local service")
    return value


def validate_supported_method_for_path(method: str, path: str) -> str:
    value = str(method or "").strip().upper()
    if value == "GET":
        return value
    if value in OPERATOR_MUTATION_METHODS and is_operator_mutation_route(path):
        return value
    if value in MUTATING_METHODS:
        raise LocalServiceReadOnlyError(f"{value} is disabled for this local service route")
    raise LocalServiceValidationError(f"{value or '<empty>'} is not supported by the local service")


def validate_query_params(params: Mapping[str, list[str]]) -> Mapping[str, list[str]]:
    for key in ("q", "query"):
        if key in params:
            query = first_param(params, key)
            if len(query) > MAX_QUERY_LENGTH:
                raise LocalServiceValidationError("query exceeds maximum length")
    if "limit" in params:
        limit = parse_limit(first_param(params, "limit"))
        if limit > MAX_RESULT_LIMIT:
            raise LocalServiceValidationError("limit exceeds maximum result limit")
    return params


def validate_no_mutation_route(method: str, path: str) -> None:
    validate_supported_method_for_path(method, path)
    lowered = str(path or "").lower()
    for token in ("write", "delete", "update", "review-decision", "probe", "workunit"):
        if token in lowered:
            raise LocalServiceReadOnlyError(f"route token is disabled for read-only service: {token}")


def is_operator_mutation_route(path: str) -> bool:
    value = str(path or "")
    if value == "/rebuild":
        return True
    if _is_hunt_command_mutation_route(value):
        return True
    return value.startswith("/review/") and value.endswith("/decision")


def _is_hunt_command_mutation_route(path: str) -> bool:
    parts = [part for part in str(path or "").split("/") if part]
    if len(parts) != 3 or parts[0] != "hunt":
        return False
    return parts[2] in {
        "pause",
        "resume",
        "cancel",
        "block",
        "wait-for-user",
        "wait-for-policy",
        "steer",
    }


def validate_no_lan_binding(host: str) -> str:
    return validate_host_allowed(host, bind_lan=False)


def first_param(params: Mapping[str, list[str]], name: str, default: str = "") -> str:
    values = params.get(name, [])
    return str(values[0]) if values else default


def parse_limit(value: str | None, default: int = DEFAULT_RESULT_LIMIT) -> int:
    if value is None or str(value).strip() == "":
        return default
    try:
        limit = int(value)
    except ValueError as exc:
        raise LocalServiceValidationError("limit must be an integer") from exc
    if limit < 1:
        raise LocalServiceValidationError("limit must be positive")
    return min(limit, MAX_RESULT_LIMIT)


def _network():
    return __import__("runtime.local_network", fromlist=["validate_service_host"])
