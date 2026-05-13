"""In-process app facade for the read-only local service."""

from typing import Any, Mapping

from runtime.local_appliance import LocalApplianceRuntime

from .errors import LocalServiceError
from .request_context import build_request_context
from .responses import LocalServiceResponse, error_response
from .routes import route_request


class LocalServiceApp:
    def __init__(self, runtime: LocalApplianceRuntime):
        if runtime is None:
            raise LocalServiceError("local appliance runtime is required")
        self.runtime = runtime

    def handle(
        self,
        method: str,
        path: str,
        query: str | Mapping[str, object] | None = None,
        client_host: str = "127.0.0.1",
    ) -> LocalServiceResponse:
        try:
            context = build_request_context(method, path, query, client_host)
            return route_request(self.runtime, context)
        except LocalServiceError as exc:
            return error_response(405 if method.upper() != "GET" else 400, "request_rejected", str(exc))
        except Exception as exc:  # pragma: no cover - defensive app boundary
            return error_response(500, "local_service_failed", str(exc))


def build_local_service_app(runtime: LocalApplianceRuntime) -> LocalServiceApp:
    return LocalServiceApp(runtime)
