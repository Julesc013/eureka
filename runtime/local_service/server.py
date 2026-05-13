"""Loopback-default server adapter with explicit read-only LAN guard."""

from dataclasses import dataclass
from http.server import BaseHTTPRequestHandler
from pathlib import Path
import socketserver
from typing import Any

from runtime.local_appliance import close_local_appliance, open_local_appliance

from .app import LocalServiceApp
from .responses import LocalServiceResponse
from .validation import validate_host_allowed


class LocalHTTPServer(socketserver.TCPServer):
    allow_reuse_address = True


class LocalHTTPServerV6(LocalHTTPServer):
    address_family = __import__("socket").AF_INET6


@dataclass
class LocalHTTPServiceHandle:
    httpd: LocalHTTPServer
    runtime: Any
    bind_lan: bool = False
    warnings: tuple[str, ...] = ()

    @property
    def server_port(self) -> int:
        return int(self.httpd.server_address[1])

    def shutdown(self) -> None:
        self.httpd.shutdown()

    def close(self) -> None:
        self.httpd.server_close()
        close_local_appliance(self.runtime)


def create_local_http_handler(app: LocalServiceApp) -> type[BaseHTTPRequestHandler]:
    class LocalHTTPHandler(BaseHTTPRequestHandler):
        server_version = "EurekaLocalService/0"

        def do_GET(self) -> None:  # noqa: N802 - http.server method name
            self._send(app.handle("GET", self.path, None, self._client_host()))

        def do_POST(self) -> None:  # noqa: N802
            self._send(app.handle("POST", self.path, None, self._client_host(), headers=self._headers(), body=self._body()))

        def do_PUT(self) -> None:  # noqa: N802
            self._send(app.handle("PUT", self.path, None, self._client_host()))

        def do_PATCH(self) -> None:  # noqa: N802
            self._send(app.handle("PATCH", self.path, None, self._client_host()))

        def do_DELETE(self) -> None:  # noqa: N802
            self._send(app.handle("DELETE", self.path, None, self._client_host()))

        def log_message(self, format: str, *args: Any) -> None:  # noqa: A002 - inherited API
            return

        def _client_host(self) -> str:
            return str(self.client_address[0])

        def _headers(self) -> dict[str, str]:
            return {str(key): str(value) for key, value in self.headers.items()}

        def _body(self) -> bytes:
            length = int(self.headers.get("Content-Length", "0") or "0")
            if length <= 0:
                return b""
            return self.rfile.read(length)

        def _send(self, response: LocalServiceResponse) -> None:
            body = response.body.encode("utf-8")
            self.send_response(response.status_code)
            self.send_header("Content-Type", response.content_type)
            self.send_header("Content-Length", str(len(body)))
            for key, value in response.headers.items():
                self.send_header(str(key), str(value))
            self.end_headers()
            self.wfile.write(body)

    return LocalHTTPHandler


def create_local_http_server(
    instance_path: str | Path,
    host: str = "127.0.0.1",
    port: int = 8765,
    read_only: bool = True,
    operator_token: str | None = None,
    bind_lan: bool = False,
) -> LocalHTTPServiceHandle:
    validate_host_allowed(host, bind_lan=bind_lan)
    runtime = open_local_appliance(Path(instance_path), read_only=read_only and not operator_token)
    try:
        lan_enabled = host in {"0.0.0.0", "::"} and bind_lan
        setattr(runtime, "lan_enabled", lan_enabled)
        setattr(runtime, "bind_lan", bool(bind_lan))
        setattr(runtime, "lan_read_only", True)
        app = LocalServiceApp(runtime, operator_auth_state=_build_cli_operator_auth_state(operator_token))
        server_class = LocalHTTPServerV6 if host == "::" else LocalHTTPServer
        httpd = server_class((host, int(port)), create_local_http_handler(app))
        warnings = _lan_warnings() if lan_enabled else ()
        return LocalHTTPServiceHandle(httpd=httpd, runtime=runtime, bind_lan=bool(bind_lan), warnings=warnings)
    except Exception:
        close_local_appliance(runtime)
        raise


def run_local_http_service(
    instance_path: str | Path,
    host: str = "127.0.0.1",
    port: int = 8765,
    read_only: bool = True,
    operator_token: str | None = None,
    bind_lan: bool = False,
) -> None:
    handle = create_local_http_server(instance_path, host=host, port=port, read_only=read_only, operator_token=operator_token, bind_lan=bind_lan)
    try:
        handle.httpd.serve_forever()
    finally:
        handle.close()


def _build_cli_operator_auth_state(operator_token: str | None) -> Any:
    module = __import__("runtime.local_operator.auth", fromlist=["build_cli_operator_auth_state"])
    return module.build_cli_operator_auth_state(operator_token)


def _lan_warnings() -> tuple[str, str]:
    module = __import__("runtime.local_network", fromlist=["build_lan_warning"])
    return (module.build_lan_warning(), module.build_firewall_warning())
