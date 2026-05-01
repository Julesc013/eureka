#!/usr/bin/env python3
"""Run Eureka public search through a hosted-safe stdlib wrapper.

The wrapper is intentionally narrow: it serves only public-search routes in
local_index_only mode and leaves deployment, rate limiting, DNS, TLS, accounts,
telemetry, live probes, downloads, uploads, and arbitrary URL fetching outside
this repository milestone.
"""

from __future__ import annotations

import argparse
from copy import deepcopy
from dataclasses import asdict, dataclass
from html import escape
import json
import os
from pathlib import Path
import sys
from typing import Any, Callable, Mapping, Sequence, TextIO
from urllib.parse import parse_qs, unquote
from wsgiref.simple_server import make_server


ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from runtime.gateway.public_api import build_demo_public_search_public_api  # noqa: E402
from runtime.gateway.public_api.public_search import (  # noqa: E402
    DEFAULT_RESULT_LIMIT,
    FORBIDDEN_PARAMETERS,
    MAX_QUERY_LENGTH,
    MAX_RESULT_LIMIT,
    MODE,
    PublicSearchPublicApi,
    public_search_error_response,
)
from runtime.gateway.public_api.public_search_index import public_search_index_exists  # noqa: E402
from runtime.gateway.public_api.resolution_boundary import PublicApiResponse  # noqa: E402


SERVICE_NAME = "eureka_hosted_public_search_wrapper"
DEFAULT_LOCAL_HOST = "127.0.0.1"
DEFAULT_PUBLIC_HOST = "0.0.0.0"
DEFAULT_PORT = 8080
HOSTED_DEFAULT_MAX_RESULTS = 20
HOSTED_DEFAULT_TIMEOUT_MS = 5000
TRUE_VALUES = frozenset({"1", "true", "yes", "on"})
FALSE_VALUES = frozenset({"0", "false", "no", "off", ""})

PROHIBITED_BOOLEAN_ENV = {
    "EUREKA_ALLOW_LIVE_PROBES": "live probes",
    "EUREKA_ALLOW_DOWNLOADS": "downloads",
    "EUREKA_ALLOW_UPLOADS": "uploads",
    "EUREKA_ALLOW_LOCAL_PATHS": "local path access",
    "EUREKA_ALLOW_ARBITRARY_URL_FETCH": "arbitrary URL fetching",
    "EUREKA_ALLOW_INSTALL_ACTIONS": "install or execute actions",
    "EUREKA_ALLOW_TELEMETRY": "telemetry",
}

UNSAFE_CLAIM_ENV = {
    "EUREKA_HOSTED_DEPLOYMENT_VERIFIED": "hosted deployment evidence",
    "EUREKA_DYNAMIC_BACKEND_DEPLOYED": "dynamic backend deployment",
}


@dataclass(frozen=True)
class HostedPublicSearchConfig:
    host: str
    port: int
    public_mode: bool
    search_mode: str
    allow_live_probes: bool
    allow_downloads: bool
    allow_uploads: bool
    allow_local_paths: bool
    allow_arbitrary_url_fetch: bool
    allow_install_actions: bool
    allow_telemetry: bool
    operator_kill_switch: bool
    max_query_len: int
    max_results: int
    global_timeout_ms: int
    hosted_deployment_verified: bool
    dynamic_backend_deployed: bool
    public_index_present: bool
    parse_errors: tuple[str, ...] = ()

    def public_summary(self) -> dict[str, Any]:
        return {
            "service": SERVICE_NAME,
            "host": self.host,
            "port": self.port,
            "public_mode": self.public_mode,
            "search_mode": self.search_mode,
            "public_search_mode": MODE,
            "hosted_wrapper_configured": True,
            "hosted_backend_deployed": False,
            "hosted_deployment_verified": self.hosted_deployment_verified,
            "dynamic_backend_deployed": self.dynamic_backend_deployed,
            "live_probes_enabled": self.allow_live_probes,
            "downloads_enabled": self.allow_downloads,
            "uploads_enabled": self.allow_uploads,
            "installs_enabled": self.allow_install_actions,
            "local_paths_enabled": self.allow_local_paths,
            "arbitrary_url_fetch_enabled": self.allow_arbitrary_url_fetch,
            "telemetry_enabled": self.allow_telemetry,
            "accounts_enabled": False,
            "external_calls_enabled": False,
            "ai_runtime_enabled": False,
            "max_query_len": self.max_query_len,
            "max_results": self.max_results,
            "global_timeout_ms": self.global_timeout_ms,
            "operator_kill_switch_tripped": self.operator_kill_switch,
            "public_index_present": self.public_index_present,
        }


class HostedPublicSearchWsgiApp:
    """Minimal WSGI app for the hosted-safe public search surface."""

    def __init__(
        self,
        *,
        config: HostedPublicSearchConfig,
        public_search_api: PublicSearchPublicApi | None = None,
    ) -> None:
        self.config = config
        self.public_search_api = public_search_api or build_demo_public_search_public_api()

    def __call__(
        self,
        environ: Mapping[str, Any],
        start_response: Callable[[str, list[tuple[str, str]]], None],
    ) -> list[bytes]:
        method = str(environ.get("REQUEST_METHOD", "GET")).upper()
        path = str(environ.get("PATH_INFO", "/"))
        query = _parse_query(str(environ.get("QUERY_STRING", "")))

        if method != "GET":
            response = public_search_error_response(
                405,
                code="bad_request",
                message="Hosted public search v0 only supports GET requests.",
                parameter="method",
            )
            return _json_response(start_response, response.status_code, _augment_payload(response.body, self.config))

        if path == "/healthz":
            return _json_response(start_response, 200, self._health_payload())
        if path in {"/status", "/api/v1/status"}:
            response = self.public_search_api.status(query)
            return _json_response(start_response, response.status_code, self._status_payload(response.body))
        if path == "/api/v1/search":
            response = self.public_search_api.search(query, default_profile="api_client")
            return _json_response(start_response, response.status_code, _augment_payload(response.body, self.config))
        if path == "/api/v1/query-plan":
            response = self.public_search_api.query_plan(query, default_profile="api_client")
            return _json_response(start_response, response.status_code, _augment_payload(response.body, self.config))
        if path == "/api/v1/sources":
            response = self.public_search_api.list_sources(query)
            return _json_response(start_response, response.status_code, _augment_payload(response.body, self.config))
        if path.startswith("/api/v1/source/"):
            source_id = unquote(path.removeprefix("/api/v1/source/"))
            response = self.public_search_api.get_source(source_id, query)
            return _json_response(start_response, response.status_code, _augment_payload(response.body, self.config))
        if path == "/search":
            response = self.public_search_api.search(query, default_profile="standard_web")
            return _html_response(
                start_response,
                response.status_code,
                _render_search_html(_augment_payload(response.body, self.config), query),
            )

        response = public_search_error_response(
            404,
            code="not_found",
            message="This hosted wrapper serves only public search routes.",
            parameter="path",
        )
        return _json_response(start_response, response.status_code, _augment_payload(response.body, self.config))

    def _health_payload(self) -> dict[str, Any]:
        payload = {
            "ok": True,
            "service": SERVICE_NAME,
            "mode": MODE,
            "hosted_wrapper_configured": True,
            "hosted_backend_deployed": False,
            "hosted_deployment_verified": False,
            "dynamic_backend_deployed": False,
            "live_probes_enabled": False,
            "downloads_enabled": False,
            "uploads_enabled": False,
            "local_paths_enabled": False,
            "arbitrary_url_fetch_enabled": False,
            "telemetry_enabled": False,
            "accounts_enabled": False,
            "external_calls_enabled": False,
            "ai_runtime_enabled": False,
        }
        return payload

    def _status_payload(self, base_payload: Mapping[str, Any]) -> dict[str, Any]:
        payload = _augment_payload(base_payload, self.config)
        payload["hosted_search_implemented"] = False
        payload["hosted_wrapper_configured"] = True
        payload["hosted_backend_deployed"] = False
        payload["hosted_deployment_verified"] = False
        payload["dynamic_backend_deployed"] = False
        payload["public_search_mode"] = MODE
        payload["public_search"] = _public_search_status_block(payload.get("public_search"))
        payload["hosted_wrapper"] = {
            "implemented": True,
            "deployment_verified": False,
            "deployment_evidence_required": True,
            "implementation_scope": "deployable_wrapper_local_rehearsal_only",
            "mode": MODE,
            "routes": [
                "/healthz",
                "/status",
                "/search",
                "/api/v1/status",
                "/api/v1/search",
                "/api/v1/query-plan",
                "/api/v1/sources",
                "/api/v1/source/{source_id}",
            ],
        }
        return payload


def build_hosted_public_search_wsgi_app(
    config: HostedPublicSearchConfig | None = None,
) -> HostedPublicSearchWsgiApp:
    return HostedPublicSearchWsgiApp(config=config or load_hosted_public_search_config())


def load_hosted_public_search_config(
    *,
    host: str | None = None,
    port: int | str | None = None,
    public_mode_requested: bool = False,
    environ: Mapping[str, str] | None = None,
) -> HostedPublicSearchConfig:
    env = environ if environ is not None else os.environ
    errors: list[str] = []

    public_mode = _read_bool(env, "EUREKA_PUBLIC_MODE", True, errors)
    bind_host = host or env.get("EUREKA_BIND_HOST") or env.get("HOST")
    if bind_host is None:
        bind_host = DEFAULT_PUBLIC_HOST if public_mode_requested else DEFAULT_LOCAL_HOST

    raw_port = port if port is not None else env.get("PORT", DEFAULT_PORT)
    parsed_port = _parse_int(raw_port, "PORT", DEFAULT_PORT, errors)

    config = HostedPublicSearchConfig(
        host=str(bind_host),
        port=parsed_port,
        public_mode=public_mode,
        search_mode=str(env.get("EUREKA_SEARCH_MODE", MODE)),
        allow_live_probes=_read_bool(env, "EUREKA_ALLOW_LIVE_PROBES", False, errors),
        allow_downloads=_read_bool(env, "EUREKA_ALLOW_DOWNLOADS", False, errors),
        allow_uploads=_read_bool(env, "EUREKA_ALLOW_UPLOADS", False, errors),
        allow_local_paths=_read_bool(env, "EUREKA_ALLOW_LOCAL_PATHS", False, errors),
        allow_arbitrary_url_fetch=_read_bool(env, "EUREKA_ALLOW_ARBITRARY_URL_FETCH", False, errors),
        allow_install_actions=_read_bool(env, "EUREKA_ALLOW_INSTALL_ACTIONS", False, errors),
        allow_telemetry=_read_bool(env, "EUREKA_ALLOW_TELEMETRY", False, errors),
        operator_kill_switch=_read_bool(env, "EUREKA_OPERATOR_KILL_SWITCH", False, errors),
        max_query_len=_parse_int(env.get("EUREKA_MAX_QUERY_LEN", MAX_QUERY_LENGTH), "EUREKA_MAX_QUERY_LEN", MAX_QUERY_LENGTH, errors),
        max_results=_parse_int(env.get("EUREKA_MAX_RESULTS", HOSTED_DEFAULT_MAX_RESULTS), "EUREKA_MAX_RESULTS", HOSTED_DEFAULT_MAX_RESULTS, errors),
        global_timeout_ms=_parse_int(env.get("EUREKA_GLOBAL_TIMEOUT_MS", HOSTED_DEFAULT_TIMEOUT_MS), "EUREKA_GLOBAL_TIMEOUT_MS", HOSTED_DEFAULT_TIMEOUT_MS, errors),
        hosted_deployment_verified=_read_bool(env, "EUREKA_HOSTED_DEPLOYMENT_VERIFIED", False, errors),
        dynamic_backend_deployed=_read_bool(env, "EUREKA_DYNAMIC_BACKEND_DEPLOYED", False, errors),
        public_index_present=public_search_index_exists(),
        parse_errors=tuple(errors),
    )
    return config


def validate_hosted_public_search_config(config: HostedPublicSearchConfig) -> dict[str, Any]:
    errors = list(config.parse_errors)
    warnings: list[str] = []

    if config.public_mode is not True:
        errors.append("EUREKA_PUBLIC_MODE must be enabled for the hosted wrapper.")
    if config.search_mode != MODE:
        errors.append("EUREKA_SEARCH_MODE must be local_index_only.")
    if not 1 <= config.port <= 65535:
        errors.append("PORT must be between 1 and 65535.")
    if not 1 <= config.max_query_len <= MAX_QUERY_LENGTH:
        errors.append(f"EUREKA_MAX_QUERY_LEN must be between 1 and {MAX_QUERY_LENGTH}.")
    if not 1 <= config.max_results <= MAX_RESULT_LIMIT:
        errors.append(f"EUREKA_MAX_RESULTS must be between 1 and {MAX_RESULT_LIMIT}.")
    if not 1 <= config.global_timeout_ms <= HOSTED_DEFAULT_TIMEOUT_MS:
        errors.append(f"EUREKA_GLOBAL_TIMEOUT_MS must be between 1 and {HOSTED_DEFAULT_TIMEOUT_MS}.")
    if config.operator_kill_switch:
        errors.append("EUREKA_OPERATOR_KILL_SWITCH is tripped; the wrapper must not start.")
    if not config.public_index_present:
        errors.append("data/public_index/search_documents.ndjson is required for hosted wrapper mode.")
    for attr, env_name in (
        ("allow_live_probes", "EUREKA_ALLOW_LIVE_PROBES"),
        ("allow_downloads", "EUREKA_ALLOW_DOWNLOADS"),
        ("allow_uploads", "EUREKA_ALLOW_UPLOADS"),
        ("allow_local_paths", "EUREKA_ALLOW_LOCAL_PATHS"),
        ("allow_arbitrary_url_fetch", "EUREKA_ALLOW_ARBITRARY_URL_FETCH"),
        ("allow_install_actions", "EUREKA_ALLOW_INSTALL_ACTIONS"),
        ("allow_telemetry", "EUREKA_ALLOW_TELEMETRY"),
    ):
        if getattr(config, attr):
            errors.append(f"{env_name} must be false for P54 hosted public search.")
    if config.hosted_deployment_verified:
        errors.append("EUREKA_HOSTED_DEPLOYMENT_VERIFIED must not be claimed by local config.")
    if config.dynamic_backend_deployed:
        errors.append("EUREKA_DYNAMIC_BACKEND_DEPLOYED must not be claimed by local config.")
    if config.host == DEFAULT_PUBLIC_HOST:
        warnings.append("Binding 0.0.0.0 is intended only for operator-controlled hosted rehearsal.")

    return {
        "status": "valid" if not errors else "invalid",
        "created_by": "hosted_public_search_wrapper_config_check_v0",
        "config": config.public_summary(),
        "safe_defaults": {
            "EUREKA_PUBLIC_MODE": "1",
            "EUREKA_SEARCH_MODE": MODE,
            "EUREKA_ALLOW_LIVE_PROBES": "0",
            "EUREKA_ALLOW_DOWNLOADS": "0",
            "EUREKA_ALLOW_UPLOADS": "0",
            "EUREKA_ALLOW_LOCAL_PATHS": "0",
            "EUREKA_ALLOW_ARBITRARY_URL_FETCH": "0",
            "EUREKA_ALLOW_INSTALL_ACTIONS": "0",
            "EUREKA_ALLOW_TELEMETRY": "0",
            "EUREKA_MAX_QUERY_LEN": str(MAX_QUERY_LENGTH),
            "EUREKA_MAX_RESULTS": str(HOSTED_DEFAULT_MAX_RESULTS),
            "EUREKA_GLOBAL_TIMEOUT_MS": str(HOSTED_DEFAULT_TIMEOUT_MS),
        },
        "errors": errors,
        "warnings": warnings,
    }


def _augment_payload(payload: Mapping[str, Any], config: HostedPublicSearchConfig) -> dict[str, Any]:
    body = deepcopy(dict(payload))
    body.setdefault("mode", MODE)
    body["hosted_wrapper_configured"] = True
    body["hosted_backend_deployed"] = False
    body["hosted_deployment_verified"] = False
    body["dynamic_backend_deployed"] = False
    body["live_probes_enabled"] = False
    body["downloads_enabled"] = False
    body["uploads_enabled"] = False
    body["installs_enabled"] = False
    body["local_paths_enabled"] = False
    body["arbitrary_url_fetch_enabled"] = False
    body["telemetry_enabled"] = False
    body["accounts_enabled"] = False
    body["external_calls_enabled"] = False
    body["ai_runtime_enabled"] = False
    body["public_index_present"] = config.public_index_present
    body["request_limits"] = _merged_request_limits(body.get("request_limits"), config)
    return body


def _public_search_status_block(value: Any) -> dict[str, Any]:
    block = deepcopy(value) if isinstance(value, Mapping) else {}
    block["implemented"] = True
    block["implementation_scope"] = "local_index_only_hosted_wrapper_local_rehearsal"
    block["hosted_public_deployment"] = False
    block["hosted_deployment_verified"] = False
    block["mode"] = MODE
    block["live_probes_enabled"] = False
    block["downloads_enabled"] = False
    block["installs_enabled"] = False
    block["uploads_enabled"] = False
    block["local_paths_enabled"] = False
    block["arbitrary_url_fetch_enabled"] = False
    block["telemetry_enabled"] = False
    block["production_ready"] = False
    return block


def _merged_request_limits(value: Any, config: HostedPublicSearchConfig) -> dict[str, Any]:
    limits = deepcopy(value) if isinstance(value, Mapping) else {}
    limits.setdefault("max_query_length", config.max_query_len)
    limits.setdefault("default_limit", DEFAULT_RESULT_LIMIT)
    limits.setdefault("max_limit", MAX_RESULT_LIMIT)
    limits["hosted_wrapper_max_query_length"] = config.max_query_len
    limits["hosted_wrapper_max_results"] = config.max_results
    limits["hosted_wrapper_timeout_ms"] = config.global_timeout_ms
    return limits


def _render_search_html(payload: Mapping[str, Any], query: Mapping[str, Sequence[str]]) -> str:
    raw_query = _first_value(query, "q") or ""
    status_note = (
        "Mode local_index_only. Hosted deployment is not verified. Live probes, "
        "downloads, uploads, install actions, local paths, arbitrary URL fetch, "
        "accounts, telemetry, external calls, and AI runtime are disabled."
    )
    parts = [
        "<!doctype html>",
        '<html lang="en">',
        "<head>",
        '<meta charset="utf-8">',
        '<meta name="viewport" content="width=device-width, initial-scale=1">',
        "<title>Eureka Hosted Public Search</title>",
        "</head>",
        "<body>",
        "<main>",
        "<h1>Eureka Hosted Public Search</h1>",
        f"<p>{escape(status_note)}</p>",
        '<form method="get" action="/search">',
        '<label for="q">Search</label> ',
        f'<input id="q" name="q" maxlength="{MAX_QUERY_LENGTH}" value="{escape(raw_query, quote=True)}">',
        "<button type=\"submit\">Search</button>",
        "</form>",
    ]
    if payload.get("ok") is False:
        error = payload.get("error") if isinstance(payload.get("error"), Mapping) else {}
        parts.extend(
            [
                "<section>",
                "<h2>Request blocked</h2>",
                f"<p>{escape(str(error.get('code', 'bad_request')))}: {escape(str(error.get('message', 'Request rejected.')))}</p>",
                "</section>",
            ]
        )
    else:
        results = payload.get("results") if isinstance(payload.get("results"), list) else []
        parts.extend(["<section>", f"<h2>Results ({len(results)})</h2>", "<ol>"])
        for result in results:
            if not isinstance(result, Mapping):
                continue
            title = escape(str(result.get("title", "Untitled")))
            summary = escape(str(result.get("summary", "")))
            source = result.get("source") if isinstance(result.get("source"), Mapping) else {}
            source_label = escape(str(source.get("label", source.get("source_id", "source unknown"))))
            parts.append(f"<li><strong>{title}</strong><br>{summary}<br><small>{source_label}</small></li>")
        parts.extend(["</ol>", "</section>"])
        limitations = payload.get("limitations") if isinstance(payload.get("limitations"), list) else []
        if limitations:
            parts.extend(["<section>", "<h2>Limitations</h2>", "<ul>"])
            for limitation in limitations[:8]:
                parts.append(f"<li>{escape(str(limitation))}</li>")
            parts.extend(["</ul>", "</section>"])
    parts.extend(["</main>", "</body>", "</html>"])
    return "\n".join(parts)


def _json_response(
    start_response: Callable[[str, list[tuple[str, str]]], None],
    status_code: int,
    payload: Mapping[str, Any],
) -> list[bytes]:
    body = json.dumps(payload, indent=2, sort_keys=True).encode("utf-8")
    start_response(
        _status_line(status_code),
        [
            ("Content-Type", "application/json; charset=utf-8"),
            ("Content-Length", str(len(body))),
            ("Cache-Control", "no-store"),
            ("X-Content-Type-Options", "nosniff"),
        ],
    )
    return [body]


def _html_response(
    start_response: Callable[[str, list[tuple[str, str]]], None],
    status_code: int,
    html: str,
) -> list[bytes]:
    body = html.encode("utf-8")
    start_response(
        _status_line(status_code),
        [
            ("Content-Type", "text/html; charset=utf-8"),
            ("Content-Length", str(len(body))),
            ("Cache-Control", "no-store"),
            ("X-Content-Type-Options", "nosniff"),
        ],
    )
    return [body]


def _status_line(status_code: int) -> str:
    labels = {
        200: "OK",
        400: "Bad Request",
        404: "Not Found",
        405: "Method Not Allowed",
        500: "Internal Server Error",
    }
    return f"{status_code} {labels.get(status_code, 'Status')}"


def _parse_query(query_string: str) -> dict[str, list[str]]:
    return {key: list(values) for key, values in parse_qs(query_string, keep_blank_values=True).items()}


def _first_value(query: Mapping[str, Sequence[str]], name: str) -> str | None:
    values = query.get(name)
    if not values:
        return None
    return str(values[0])


def _read_bool(env: Mapping[str, str], name: str, default: bool, errors: list[str]) -> bool:
    raw = env.get(name)
    if raw is None:
        return default
    normalized = raw.strip().casefold()
    if normalized in TRUE_VALUES:
        return True
    if normalized in FALSE_VALUES:
        return False
    errors.append(f"{name} must be a boolean 1/0, true/false, yes/no, or on/off value.")
    return default


def _parse_int(raw: int | str, name: str, default: int, errors: list[str]) -> int:
    try:
        return int(raw)
    except (TypeError, ValueError):
        errors.append(f"{name} must be an integer.")
        return default


def _format_config_report(report: Mapping[str, Any]) -> str:
    config = report.get("config") if isinstance(report.get("config"), Mapping) else {}
    lines = [
        "Hosted public search wrapper config",
        f"status: {report.get('status')}",
        f"host: {config.get('host')}",
        f"port: {config.get('port')}",
        f"mode: {config.get('search_mode')}",
        f"hosted_deployment_verified: {config.get('hosted_deployment_verified')}",
        f"live_probes_enabled: {config.get('live_probes_enabled')}",
        f"downloads_enabled: {config.get('downloads_enabled')}",
        f"uploads_enabled: {config.get('uploads_enabled')}",
        f"local_paths_enabled: {config.get('local_paths_enabled')}",
        f"arbitrary_url_fetch_enabled: {config.get('arbitrary_url_fetch_enabled')}",
        f"telemetry_enabled: {config.get('telemetry_enabled')}",
    ]
    if report.get("errors"):
        lines.append("errors:")
        lines.extend(f"- {error}" for error in report["errors"])
    if report.get("warnings"):
        lines.append("warnings:")
        lines.extend(f"- {warning}" for warning in report["warnings"])
    return "\n".join(lines) + "\n"


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", help="Bind host. Defaults to 127.0.0.1 for local checks.")
    parser.add_argument("--port", help="Bind port. Defaults to PORT env or 8080.")
    parser.add_argument("--public-mode", action="store_true", help="Use hosted bind defaults when host is omitted.")
    parser.add_argument("--check-config", action="store_true", help="Validate hosted wrapper environment and exit.")
    parser.add_argument("--json", action="store_true", help="Emit JSON for --check-config.")
    parser.add_argument("--print-config-json", action="store_true", help="Print resolved config and exit.")
    return parser


def main(argv: Sequence[str] | None = None, *, stdout: TextIO | None = None, stderr: TextIO | None = None) -> int:
    parser = _build_parser()
    args = parser.parse_args(list(argv) if argv is not None else None)
    output = stdout or sys.stdout
    error_output = stderr or sys.stderr

    config = load_hosted_public_search_config(
        host=args.host,
        port=args.port,
        public_mode_requested=args.public_mode,
    )
    report = validate_hosted_public_search_config(config)

    if args.print_config_json:
        output.write(json.dumps(asdict(config), indent=2, sort_keys=True) + "\n")
        return 0

    if args.check_config:
        if args.json:
            output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
        else:
            output.write(_format_config_report(report))
        return 0 if report["status"] == "valid" else 1

    if report["status"] != "valid":
        error_output.write(json.dumps(report, indent=2, sort_keys=True) + "\n")
        return 2

    app = HostedPublicSearchWsgiApp(config=config)
    with make_server(config.host, config.port, app) as server:
        output.write(
            f"{SERVICE_NAME} listening on http://{config.host}:{config.port} "
            f"in {MODE} mode; deployment evidence is not claimed.\n"
        )
        server.serve_forever()
    return 0


__all__ = [
    "DEFAULT_LOCAL_HOST",
    "DEFAULT_PORT",
    "FORBIDDEN_PARAMETERS",
    "HOSTED_DEFAULT_MAX_RESULTS",
    "HOSTED_DEFAULT_TIMEOUT_MS",
    "HostedPublicSearchConfig",
    "HostedPublicSearchWsgiApp",
    "build_hosted_public_search_wsgi_app",
    "load_hosted_public_search_config",
    "validate_hosted_public_search_config",
]


if __name__ == "__main__":
    raise SystemExit(main())
