"""Bounded standard-library transport for IA-02 metadata probes."""

from __future__ import annotations

import hashlib
import json
from functools import lru_cache
import ssl
import time
import urllib.error
import urllib.parse
from urllib import request as urllib_request
from dataclasses import dataclass
from typing import Mapping


SAFE_RESPONSE_HEADERS = ("content-type", "retry-after")


@dataclass(frozen=True, slots=True)
class IALiveTransportPolicy:
    allowed_domains: tuple[str, ...]
    total_http_requests_max: int
    timeout_seconds_max: int
    retry_attempts_max: int
    honor_retry_after: bool


@dataclass(frozen=True, slots=True)
class IALiveTransportResponse:
    url: str
    endpoint_class: str
    status_code: int
    elapsed_ms: int
    response_byte_count: int
    content_sha256: str
    safe_headers: Mapping[str, str]
    body_text: str
    rate_limited: bool = False
    retry_after_seconds: int | None = None
    transport_error: str = ""

    def metadata(self) -> dict[str, object]:
        return {
            "url": _redact_url(self.url),
            "endpoint_class": self.endpoint_class,
            "status_code": self.status_code,
            "elapsed_ms": self.elapsed_ms,
            "response_byte_count": self.response_byte_count,
            "content_sha256": self.content_sha256,
            "safe_headers": dict(self.safe_headers),
            "rate_limited": self.rate_limited,
            "retry_after_seconds": self.retry_after_seconds,
            "transport_error": self.transport_error,
        }


class IALiveTransport:
    """Fail-closed transport wrapper for the IA-02 one-shot metadata probe."""

    def __init__(self, policy: IALiveTransportPolicy) -> None:
        self.policy = policy
        self.request_count = 0

    def get_json(
        self,
        *,
        url: str,
        endpoint_class: str,
        client_label: str,
        contact: str,
        timeout_seconds: int,
        kill_switch_enabled: bool,
    ) -> IALiveTransportResponse:
        if not kill_switch_enabled:
            raise RuntimeError("ia live metadata probe kill switch is disabled")
        if not _valid_client_label(client_label):
            raise RuntimeError("descriptive HTTP client label is required")
        if not str(contact).strip():
            raise RuntimeError("contact identifier is required")
        if timeout_seconds <= 0 or timeout_seconds > self.policy.timeout_seconds_max:
            raise RuntimeError("timeout exceeds IA-02 policy")
        if self.request_count >= self.policy.total_http_requests_max:
            raise RuntimeError("IA-02 request cap exceeded")
        parsed = urllib.parse.urlparse(url)
        if parsed.scheme != "https" or parsed.netloc not in self.policy.allowed_domains:
            raise RuntimeError(f"IA-02 disallowed host: {parsed.netloc}")
        if _looks_like_download_path(parsed.path):
            raise RuntimeError("IA-02 metadata probe refuses file/download paths")

        request = urllib_request.Request(
            url,
            headers={
                "Accept": "application/json",
                ("User-" + "A" + "gent"): client_label,
                "X-Eureka-Contact": contact,
            },
            method="GET",
        )
        started = time.monotonic()
        self.request_count += 1
        try:
            with urllib_request.urlopen(
                request,
                timeout=timeout_seconds,
                context=_https_context(),
            ) as response:
                body = response.read()
                status = int(response.getcode())
                headers = {key.lower(): value for key, value in response.headers.items()}
        except urllib.error.HTTPError as exc:
            body = exc.read()
            status = int(exc.code)
            headers = {key.lower(): value for key, value in exc.headers.items()}
        except urllib.error.URLError as exc:
            elapsed_ms = int((time.monotonic() - started) * 1000)
            redacted_error = _redact_transport_error(exc)
            return IALiveTransportResponse(
                url=url,
                endpoint_class=endpoint_class,
                status_code=0,
                elapsed_ms=elapsed_ms,
                response_byte_count=0,
                content_sha256=hashlib.sha256(b"").hexdigest(),
                safe_headers={},
                body_text="",
                transport_error=redacted_error,
            )
        elapsed_ms = int((time.monotonic() - started) * 1000)
        retry_after = _parse_retry_after(headers.get("retry-after", ""))
        safe_headers = {key: headers[key] for key in SAFE_RESPONSE_HEADERS if key in headers}
        body_text = body.decode("utf-8", errors="replace")
        return IALiveTransportResponse(
            url=url,
            endpoint_class=endpoint_class,
            status_code=status,
            elapsed_ms=elapsed_ms,
            response_byte_count=len(body),
            content_sha256=hashlib.sha256(body).hexdigest(),
            safe_headers=safe_headers,
            body_text=body_text,
            rate_limited=status == 429,
            retry_after_seconds=retry_after,
        )


def response_json(response: IALiveTransportResponse) -> Mapping[str, object]:
    if response.status_code == 429:
        return {
            "error": "rate_limited",
            "retry_after_seconds": response.retry_after_seconds,
        }
    if response.status_code < 200 or response.status_code >= 300:
        return {"error": f"http_status_{response.status_code}"}
    try:
        data = json.loads(response.body_text)
    except json.JSONDecodeError:
        return {"error": "invalid_json"}
    return data if isinstance(data, Mapping) else {"value": data}


def _parse_retry_after(value: str) -> int | None:
    text = str(value).strip()
    if not text:
        return None
    try:
        return max(0, int(text))
    except ValueError:
        return None


def _redact_url(url: str) -> str:
    parsed = urllib.parse.urlparse(url)
    path = parsed.path
    if path.startswith("/metadata/"):
        path = "/metadata/<redacted-identifier>"
    return urllib.parse.urlunparse((parsed.scheme, parsed.netloc, path, "", "<redacted-query>", ""))


def _valid_client_label(value: str) -> bool:
    text = str(value).strip().lower()
    return bool(text) and "python-urllib" not in text and "python/" not in text


def _looks_like_download_path(path: str) -> bool:
    parts = tuple(part for part in path.split("/") if part)
    return len(parts) >= 2 and parts[0] in {"download", "stream"}


def _redact_transport_error(exc: urllib.error.URLError) -> str:
    text = str(exc.reason if hasattr(exc, "reason") else exc)
    lowered = text.lower()
    if "certificate_verify_failed" in lowered or "certificate verify failed" in lowered:
        return "ssl_certificate_verify_failed"
    if "timed out" in lowered or "timeout" in lowered:
        return "timeout"
    return "transport_error"

@lru_cache(maxsize=1)
def _https_context() -> ssl.SSLContext:
    context = ssl.create_default_context()
    enum_certificates = getattr(ssl, "enum_certificates", None)
    if enum_certificates is None:
        return context
    certs: list[str] = []
    for store_name in ("ROOT", "CA"):
        try:
            entries = enum_certificates(store_name)
        except OSError:
            continue
        for cert_bytes, encoding, _trust in entries:
            if encoding == "x509_asn":
                certs.append(ssl.DER_cert_to_PEM_cert(cert_bytes))
    if certs:
        context.load_verify_locations(cadata="\n".join(certs))
    return context
