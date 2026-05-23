"""Read-only localhost service over the local appliance runtime."""

from .app import LocalServiceApp, build_local_service_app
from .errors import (
    LocalServiceError,
    LocalServiceHostError,
    LocalServiceReadOnlyError,
    LocalServiceRouteError,
    LocalServiceValidationError,
)
from .request_context import LocalRequestContext, build_request_context
from .responses import LocalServiceResponse, error_response, json_response, text_response
from .routes import route_request
from .server import LocalHTTPServiceHandle, create_local_http_server, run_local_http_service
from .validation import (
    validate_host_allowed,
    validate_no_lan_binding,
    validate_no_mutation_route,
    validate_query_params,
    validate_read_only_method,
)

__all__ = [
    "LocalHTTPServiceHandle",
    "LocalRequestContext",
    "LocalServiceApp",
    "LocalServiceError",
    "LocalServiceHostError",
    "LocalServiceReadOnlyError",
    "LocalServiceResponse",
    "LocalServiceRouteError",
    "LocalServiceValidationError",
    "build_local_service_app",
    "build_request_context",
    "create_local_http_server",
    "error_response",
    "json_response",
    "route_request",
    "run_local_http_service",
    "text_response",
    "validate_host_allowed",
    "validate_no_lan_binding",
    "validate_no_mutation_route",
    "validate_query_params",
    "validate_read_only_method",
]
