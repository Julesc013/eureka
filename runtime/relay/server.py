"""Loopback-only read-only relay server factory.

Importing this module does not start a server. Server startup is only performed
when create_loopback_server or run_loopback_server_once_or_until_interrupt is
called explicitly.
"""

from __future__ import annotations

from http.server import BaseHTTPRequestHandler
import socketserver
from typing import Any, Mapping
from urllib.parse import urlparse

from runtime.relay.renderers import (
    render_relay_file_tree,
    render_relay_json_manifest,
    render_relay_lite_html,
    render_relay_native_fixture_json,
    render_relay_text,
)
from runtime.relay.request_response import build_relay_request, build_relay_response
from runtime.relay.security import build_policy_blocked_response, validate_bind_host


class LoopbackTCPServer(socketserver.TCPServer):
    allow_reuse_address = True


def create_readonly_relay_handler(snapshot_store: Mapping[str, Any], profile: Mapping[str, Any], policy: Mapping[str, Any]):
    class ReadOnlyRelayHandler(BaseHTTPRequestHandler):
        server_version = "EurekaRelayFixture/0"

        def do_GET(self) -> None:  # noqa: N802 - http.server method name
            request = build_relay_request("GET", self.path, None, profile, policy)
            response = build_relay_response(request, snapshot_store, policy)
            content = _render_response(response, policy).encode("utf-8")
            self.send_response(int(response.get("status_code", 200)))
            self.send_header("Content-Type", str(response.get("content_type", "text/plain; charset=utf-8")))
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Eureka-Relay", "fixture-only-readonly")
            self.end_headers()
            self.wfile.write(content)

        def do_POST(self) -> None:  # noqa: N802
            self._blocked_method("POST")

        def do_PUT(self) -> None:  # noqa: N802
            self._blocked_method("PUT")

        def do_PATCH(self) -> None:  # noqa: N802
            self._blocked_method("PATCH")

        def do_DELETE(self) -> None:  # noqa: N802
            self._blocked_method("DELETE")

        def log_message(self, format: str, *args: Any) -> None:  # noqa: A002 - inherited API
            return

        def _blocked_method(self, method: str) -> None:
            response = build_policy_blocked_response(f"{method} is disabled for read-only fixture relay", policy)
            content = render_relay_text(response, policy).encode("utf-8")
            self.send_response(403)
            self.send_header("Content-Type", "text/plain; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.end_headers()
            self.wfile.write(content)

    return ReadOnlyRelayHandler


def create_loopback_server(host: str, port: int, handler: type[BaseHTTPRequestHandler], policy: Mapping[str, Any] | None = None) -> LoopbackTCPServer:
    errors = validate_bind_host(host, policy)
    if errors:
        raise ValueError("; ".join(errors))
    return LoopbackTCPServer((host, int(port)), handler)


def run_loopback_server_once_or_until_interrupt(config: Mapping[str, Any], policy: Mapping[str, Any] | None = None) -> None:
    host = str(config.get("host", "127.0.0.1"))
    port = int(config.get("port", 0))
    handler = config.get("handler")
    if handler is None:
        raise ValueError("handler is required to run relay server")
    with create_loopback_server(host, port, handler, policy) as httpd:
        if config.get("once"):
            httpd.handle_request()
        else:
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                httpd.shutdown()


def _render_response(response: Mapping[str, Any], policy: Mapping[str, Any]) -> str:
    profile = response.get("render_profile", "text")
    if profile == "lite_html":
        return render_relay_lite_html(response, policy)
    if profile == "file_tree":
        return render_relay_file_tree(response, policy)
    if profile == "json_manifest":
        return render_relay_json_manifest(response, policy)
    if profile == "native_fixture_json":
        return render_relay_native_fixture_json(response, policy)
    return render_relay_text(response, policy)

