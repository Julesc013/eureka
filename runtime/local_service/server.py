"""Loopback-only server adapter for the read-only local service."""

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


@dataclass
class LocalHTTPServiceHandle:
    httpd: LocalHTTPServer
    runtime: Any

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
            self._send(app.handle("POST", self.path, None, self._client_host()))

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
) -> LocalHTTPServiceHandle:
    validate_host_allowed(host)
    if not read_only:
        raise ValueError("local service only supports read-only mode")
    runtime = open_local_appliance(Path(instance_path), read_only=True)
    try:
        app = LocalServiceApp(runtime)
        httpd = LocalHTTPServer((host, int(port)), create_local_http_handler(app))
        return LocalHTTPServiceHandle(httpd=httpd, runtime=runtime)
    except Exception:
        close_local_appliance(runtime)
        raise


def run_local_http_service(
    instance_path: str | Path,
    host: str = "127.0.0.1",
    port: int = 8765,
    read_only: bool = True,
) -> None:
    handle = create_local_http_server(instance_path, host=host, port=port, read_only=read_only)
    try:
        handle.httpd.serve_forever()
    finally:
        handle.close()
