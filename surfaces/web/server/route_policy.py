from __future__ import annotations

from dataclasses import dataclass
from typing import Mapping

from surfaces.web.server.server_config import WebServerConfig


UNSAFE_LOCAL_PATH_PARAMETERS = frozenset(
    {
        "index_path",
        "run_store_root",
        "task_store_root",
        "memory_store_root",
        "store_root",
        "bundle_path",
        "output",
    }
)

PUBLIC_ALPHA_BLOCKED_API_ROUTES = frozenset(
    {
        "/api/fetch",
        "/api/index/build",
        "/api/index/status",
        "/api/index/query",
        "/api/inspect/bundle",
        "/api/member",
        "/api/memories",
        "/api/memory",
        "/api/memory/create",
        "/api/run",
        "/api/run/resolve",
        "/api/run/search",
        "/api/run/planned-search",
        "/api/runs",
        "/api/store/manifest",
        "/api/store/bundle",
        "/api/stored",
        "/api/stored/artifact",
        "/api/task",
        "/api/task/run/build-local-index",
        "/api/task/run/query-local-index",
        "/api/task/run/validate-archive-resolution-evals",
        "/api/task/run/validate-source-registry",
        "/api/tasks",
        "/api/export/bundle",
    }
)

PUBLIC_ALPHA_BLOCKED_WEB_ROUTES = frozenset(
    {
        "/actions/export-resolution-bundle",
        "/fetch",
        "/index/build",
        "/index/status",
        "/index/search",
        "/inspect/bundle",
        "/member",
        "/memories",
        "/memory",
        "/memory/create",
        "/run",
        "/run/resolve",
        "/run/search",
        "/run/planned-search",
        "/runs",
        "/store/manifest",
        "/store/bundle",
        "/stored/artifact",
        "/task",
        "/task/run/build-local-index",
        "/task/run/query-local-index",
        "/task/run/validate-archive-resolution-evals",
        "/task/run/validate-source-registry",
        "/tasks",
    }
)


@dataclass(frozen=True)
class RoutePolicyDecision:
    allowed: bool
    code: str = "allowed"
    message: str = "Route is allowed by the current web server mode."
    mode: str = "local_dev"
    path: str = ""
    blocked_parameters: tuple[str, ...] = ()

    def to_blocked_payload(self) -> dict[str, object]:
        return {
            "status": "blocked",
            "code": self.code,
            "message": self.message,
            "mode": self.mode,
            "path": self.path,
            "blocked_parameters": list(self.blocked_parameters),
        }


class PublicAlphaRoutePolicy:
    def __init__(self, config: WebServerConfig) -> None:
        self._config = config

    def evaluate_api_request(
        self,
        path: str,
        query: Mapping[str, list[str]],
    ) -> RoutePolicyDecision:
        return self._evaluate(
            path,
            query,
            blocked_routes=PUBLIC_ALPHA_BLOCKED_API_ROUTES,
            route_kind="API",
        )

    def evaluate_web_request(
        self,
        path: str,
        query: Mapping[str, list[str]],
    ) -> RoutePolicyDecision:
        return self._evaluate(
            path,
            query,
            blocked_routes=PUBLIC_ALPHA_BLOCKED_WEB_ROUTES,
            route_kind="web",
        )

    def _evaluate(
        self,
        path: str,
        query: Mapping[str, list[str]],
        *,
        blocked_routes: frozenset[str],
        route_kind: str,
    ) -> RoutePolicyDecision:
        if self._config.mode == "local_dev":
            return RoutePolicyDecision(mode=self._config.mode, path=path, allowed=True)

        if not self._config.allow_eval_runner and path in {
            "/api/evals/archive-resolution",
            "/evals/archive-resolution",
        }:
            return self._blocked(
                path,
                "archive_resolution_evals_disabled",
                "Archive-resolution eval execution is disabled by this server configuration.",
            )

        blocked_parameters = _present_unsafe_parameters(query)
        if blocked_parameters:
            return self._blocked(
                path,
                "local_path_parameters_blocked",
                (
                    "Public Alpha Safe Mode v0 blocks caller-provided local filesystem "
                    "path parameters."
                ),
                blocked_parameters=blocked_parameters,
            )

        if path in blocked_routes:
            return self._blocked(
                path,
                "route_disabled_in_public_alpha",
                (
                    f"This {route_kind} route is disabled in public_alpha mode because it "
                    "requires local path access, writes local state, or exposes local fixture bytes."
                ),
            )

        return RoutePolicyDecision(mode=self._config.mode, path=path, allowed=True)

    def _blocked(
        self,
        path: str,
        code: str,
        message: str,
        *,
        blocked_parameters: tuple[str, ...] = (),
    ) -> RoutePolicyDecision:
        return RoutePolicyDecision(
            allowed=False,
            code=code,
            message=message,
            mode=self._config.mode,
            path=path,
            blocked_parameters=blocked_parameters,
        )


def _present_unsafe_parameters(query: Mapping[str, list[str]]) -> tuple[str, ...]:
    blocked: list[str] = []
    for name in sorted(UNSAFE_LOCAL_PATH_PARAMETERS):
        values = query.get(name)
        if values and values[0].strip():
            blocked.append(name)
    return tuple(blocked)
