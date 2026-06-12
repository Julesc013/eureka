#!/usr/bin/env python3
"""Run the local Eureka search MVP HTTP server."""

from __future__ import annotations

import argparse
from http.server import BaseHTTPRequestHandler
import json
from pathlib import Path
import socketserver
import sys
from typing import Any, Mapping, Sequence, TextIO
from urllib.parse import parse_qs, urlparse


REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from runtime.local.search_mvp import (
    DEFAULT_METADATA_BUDGET,
    DEFAULT_METADATA_TIMEOUT_SECONDS,
    HARD_QUERY_SMOKE_SET,
    LocalSearchOptions,
    LocalSearchService,
    SUPPORTED_METADATA_FALLBACKS,
    health_payload,
    render_search_html,
    render_search_json,
    status_payload,
)
from runtime.local.search_index import DEFAULT_INDEX_PATH, SUPPORTED_INDEX_MODES, index_file_status


class LocalSearchHTTPServer(socketserver.TCPServer):
    allow_reuse_address = True


def main(argv: Sequence[str] | None = None, stdout: TextIO = sys.stdout, stderr: TextIO = sys.stderr) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--host", default="127.0.0.1")
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--metadata-fallback", choices=SUPPORTED_METADATA_FALLBACKS, default="none")
    parser.add_argument("--allow-live-metadata", action="store_true")
    parser.add_argument("--metadata-timeout", type=int, default=DEFAULT_METADATA_TIMEOUT_SECONDS)
    parser.add_argument("--metadata-budget", type=int, default=DEFAULT_METADATA_BUDGET)
    parser.add_argument("--index", choices=SUPPORTED_INDEX_MODES, default="none")
    parser.add_argument("--index-path", default=DEFAULT_INDEX_PATH)
    parser.add_argument("--limit", type=int, default=10)
    parser.add_argument("--smoke", action="store_true", help="Run hard-query smoke searches and exit.")
    args = parser.parse_args(argv)

    options = LocalSearchOptions(
        metadata_fallback=args.metadata_fallback,
        limit=args.limit,
        allow_live_metadata=args.allow_live_metadata,
        metadata_timeout_seconds=args.metadata_timeout,
        metadata_budget=args.metadata_budget,
        index=args.index,
        index_path=args.index_path,
    )
    service = LocalSearchService()
    if args.metadata_fallback == "ia_live" and not args.allow_live_metadata:
        if args.smoke:
            response = service.search_many(HARD_QUERY_SMOKE_SET, options)
            print(render_search_json(response), end="", file=stdout)
        print(
            "ia_live requires --allow-live-metadata; no live metadata request was performed.",
            file=stderr,
        )
        return 2
    if args.metadata_fallback == "ia_live" and args.allow_live_metadata and not _is_loopback_host(args.host):
        print(
            "ia_live local server mode requires a loopback host such as 127.0.0.1 or localhost.",
            file=stderr,
        )
        return 2
    if args.smoke:
        response = service.search_many(HARD_QUERY_SMOKE_SET, options)
        print(render_search_json(response), end="", file=stdout)
        return 0

    handler = _handler_for(service, options)
    with LocalSearchHTTPServer((args.host, int(args.port)), handler) as httpd:
        base_url = f"http://{args.host}:{httpd.server_address[1]}"
        print(f"Eureka local search MVP listening on {base_url}", file=stdout, flush=True)
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            return 0
    return 0


def _handler_for(service: LocalSearchService, options: LocalSearchOptions) -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        server_version = "EurekaLocalSearchMVP/0"

        def do_GET(self) -> None:  # noqa: N802 - stdlib HTTP API
            parsed = urlparse(self.path)
            params = parse_qs(parsed.query)
            if parsed.path == "/":
                self._send_html(200, _home_html(options))
                return
            if parsed.path == "/health":
                self._send_json(200, health_payload())
                return
            if parsed.path == "/api/status":
                self._send_json(
                    200,
                    status_payload(
                        options.metadata_fallback,
                        allow_live_metadata=options.allow_live_metadata,
                        metadata_timeout_seconds=options.metadata_timeout_seconds,
                        metadata_budget=options.metadata_budget,
                        index=options.index,
                        index_path=options.index_path,
                    ),
                )
                return
            if parsed.path == "/api/search":
                self._send_json(200, _search_payload(service, params, options))
                return
            if parsed.path == "/search":
                response = _search_payload(service, params, options)
                self._send_html(200, render_search_html(response))
                return
            self._send_json(
                404,
                {
                    "schema_version": "eureka.local_search_error.v0",
                    "status": "not_found",
                    "path": parsed.path,
                    "read_only": True,
                    "public_mutation_enabled": False,
                },
            )

        def log_message(self, format: str, *args: Any) -> None:  # noqa: A002 - inherited API
            return

        def _send_json(self, status_code: int, payload: Mapping[str, Any]) -> None:
            body = json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True).encode("utf-8")
            self.send_response(status_code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _send_html(self, status_code: int, html: str) -> None:
            body = html.encode("utf-8")
            self.send_response(status_code)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    return Handler


def _search_payload(
    service: LocalSearchService,
    params: Mapping[str, Sequence[str]],
    options: LocalSearchOptions,
) -> dict[str, Any]:
    query = _first(params, "q") or _first(params, "query")
    limit_raw = _first(params, "limit")
    request_options = options
    if limit_raw:
        try:
            request_options = LocalSearchOptions(
                metadata_fallback=options.metadata_fallback,
                limit=int(limit_raw),
                show_evidence=options.show_evidence,
                show_debug=options.show_debug,
                allow_live_metadata=options.allow_live_metadata,
                metadata_timeout_seconds=options.metadata_timeout_seconds,
                metadata_budget=options.metadata_budget,
                index=options.index,
                index_path=options.index_path,
            )
        except ValueError:
            request_options = options
    return service.search(query, request_options)


def _first(params: Mapping[str, Sequence[str]], key: str) -> str:
    values = params.get(key)
    if not values:
        return ""
    return str(values[0])


def _is_loopback_host(host: str) -> bool:
    normalized = str(host or "").strip().casefold()
    return normalized in {"localhost", "::1"} or normalized.startswith("127.")


def _home_html(options: LocalSearchOptions) -> str:
    index_status = index_file_status(options.index, options.index_path)
    return "\n".join(
        [
            "<!doctype html>",
            '<html lang="en">',
            "<head><meta charset=\"utf-8\"><title>Eureka Local Search</title></head>",
            "<body>",
            "<main>",
            "<h1>Eureka Local Search</h1>",
            '<form action="/search" method="get">',
            '<label for="q">Search</label>',
            '<input id="q" name="q">',
            '<button type="submit">Search</button>',
            "</form>",
            f"<p>Metadata fallback: {options.metadata_fallback}</p>",
            f"<p>Index mode: {index_status['index_mode']}</p>",
            f"<p>Index loaded: {str(index_status['index_loaded']).lower()}</p>",
            f"<p>Index path: {index_status['index_path']}</p>",
            f"<p>Indexed documents: {index_status['index_document_count']}</p>",
            f"<p>Reviewed records: {index_status.get('reviewed_record_count', 0)}</p>",
            f"<p>Artifact verified count: {index_status.get('artifact_verified_count', 0)}</p>",
            f"<p>Live metadata enabled: {str(options.metadata_fallback == 'ia_live' and options.allow_live_metadata).lower()}</p>",
            "<p>Read-only local fallback demo. Metadata fallback is non-verified and no downloads, file fetching, Wayback replay, public fanout, or public mutation are enabled.</p>",
            "<ul>",
            '<li><a href="/health">Health</a></li>',
            '<li><a href="/api/status">API status</a></li>',
            '<li><a href="/search?q=old%20blue%20FTP%20client%20for%20XP">Example search</a></li>',
            "</ul>",
            "</main>",
            "</body>",
            "</html>",
            "",
        ]
    )


if __name__ == "__main__":
    raise SystemExit(main())
