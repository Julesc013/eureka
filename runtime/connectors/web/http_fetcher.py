"""Policy-guarded HTTP fetching for independently observed web pages."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
import hashlib
from typing import Any, Callable, Mapping
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin, urlparse
from urllib.request import HTTPRedirectHandler, Request as URLRequest, build_opener

from .dns_guard import DNSGuard, DNSGuardResult
from .extract_html import ExtractedDocument, extract_document
from .robots import AllowAllRobotsClient, RobotsDecision


HTTPTransport = Callable[[str, Mapping[str, str], int, int], "HTTPTransportResult"]


@dataclass(frozen=True)
class FetchPolicy:
    allowed_schemes: tuple[str, ...] = ("http", "https")
    allowed_ports: tuple[int, ...] = (80, 443)
    max_redirects: int = 5
    timeout_seconds: int = 15
    max_body_bytes: int = 5 * 1024 * 1024
    max_decompressed_bytes: int = 5 * 1024 * 1024
    allowed_mime_types: tuple[str, ...] = ("text/html", "text/plain")
    user_agent: str = "EurekaBot/0.1 (+https://eureka.local/bot; local-first research fetcher)"
    robots_required: bool = True
    block_non_public_ips: bool = True

    def bounded(self) -> "FetchPolicy":
        return FetchPolicy(
            allowed_schemes=tuple(item for item in self.allowed_schemes if item in {"http", "https"}) or ("http", "https"),
            allowed_ports=tuple(sorted({int(port) for port in self.allowed_ports if int(port) in {80, 443}})) or (80, 443),
            max_redirects=max(0, min(int(self.max_redirects), 5)),
            timeout_seconds=max(1, min(int(self.timeout_seconds), 30)),
            max_body_bytes=max(1, min(int(self.max_body_bytes), 5 * 1024 * 1024)),
            max_decompressed_bytes=max(1, min(int(self.max_decompressed_bytes), 5 * 1024 * 1024)),
            allowed_mime_types=tuple(self.allowed_mime_types) or ("text/html", "text/plain"),
            user_agent=str(self.user_agent or "EurekaBot/0.1"),
            robots_required=bool(self.robots_required),
            block_non_public_ips=bool(self.block_non_public_ips),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "fetch_policy.v0",
            "allowed_schemes": list(self.allowed_schemes),
            "allowed_ports": list(self.allowed_ports),
            "max_redirects": self.max_redirects,
            "timeout_seconds": self.timeout_seconds,
            "max_body_bytes": self.max_body_bytes,
            "max_decompressed_bytes": self.max_decompressed_bytes,
            "allowed_mime_types": list(self.allowed_mime_types),
            "user_agent": self.user_agent,
            "robots_required": self.robots_required,
            "block_non_public_ips": self.block_non_public_ips,
        }


@dataclass(frozen=True)
class FetchRequest:
    url: str
    query: str = ""
    run_id: str = ""
    source: str = "live_hunt_selected_url"
    method: str = "GET"

    def to_dict(self) -> dict[str, str]:
        return {
            "schema_version": "fetch_request.v0",
            "url": self.url,
            "method": self.method,
            "query": self.query,
            "run_id": self.run_id,
            "source": self.source,
        }


@dataclass(frozen=True)
class FetchError:
    code: str
    message: str
    url: str
    policy_blocked: bool = True

    def to_dict(self) -> dict[str, object]:
        return {
            "schema_version": "fetch_error.v0",
            "code": self.code,
            "message": self.message,
            "url": self.url,
            "policy_blocked": self.policy_blocked,
        }


@dataclass(frozen=True)
class HTTPTransportResult:
    status_code: int
    headers: Mapping[str, str]
    body: bytes


@dataclass(frozen=True)
class SourceObservation:
    observation_id: str
    canonical_url: str
    retrieved_at: str
    http_status: int
    content_type: str
    content_hash: str
    extracted_title: str
    extracted_text: str
    outbound_links: tuple[dict[str, str], ...]
    query: str
    run_id: str
    fetch_policy_result: str
    selected_headers: Mapping[str, str]
    redirects: tuple[str, ...]
    status: str = "unreviewed"

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "source_observation.v0",
            "observation_id": self.observation_id,
            "status": self.status,
            "canonical_url": self.canonical_url,
            "retrieved_at": self.retrieved_at,
            "http_status": self.http_status,
            "content_type": self.content_type,
            "content_hash": self.content_hash,
            "extracted_title": self.extracted_title,
            "extracted_text": self.extracted_text,
            "outbound_links": list(self.outbound_links),
            "query": self.query,
            "run_id": self.run_id,
            "fetch_policy_result": self.fetch_policy_result,
            "selected_headers": dict(self.selected_headers),
            "redirects": list(self.redirects),
        }


@dataclass(frozen=True)
class FetchOutcome:
    status: str
    request: FetchRequest
    policy: FetchPolicy
    observation: SourceObservation | None = None
    error: FetchError | None = None
    dns: tuple[Mapping[str, object], ...] = ()
    robots: tuple[Mapping[str, object], ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "fetch_outcome.v0",
            "status": self.status,
            "request": self.request.to_dict(),
            "policy": self.policy.to_dict(),
            "observation": self.observation.to_dict() if self.observation else None,
            "error": self.error.to_dict() if self.error else None,
            "dns": [dict(item) for item in self.dns],
            "robots": [dict(item) for item in self.robots],
            "reviewed_master_mutation": False,
            "public_index_mutation": False,
            "provider_result_payload_persisted": False,
        }


class SafeHTTPFetcher:
    def __init__(
        self,
        *,
        policy: FetchPolicy | None = None,
        dns_guard: DNSGuard | None = None,
        robots_client: Any | None = None,
        transport: HTTPTransport | None = None,
        clock: Callable[[], str] | None = None,
    ) -> None:
        self.policy = (policy or FetchPolicy()).bounded()
        self.dns_guard = dns_guard or DNSGuard()
        self.robots_client = robots_client or AllowAllRobotsClient()
        self.transport = transport or _urllib_transport
        self.clock = clock or utc_now

    def fetch(self, request: FetchRequest) -> FetchOutcome:
        current_url = str(request.url or "").strip()
        redirects: list[str] = []
        dns_results: list[Mapping[str, object]] = []
        robots_results: list[Mapping[str, object]] = []
        for redirect_index in range(self.policy.max_redirects + 1):
            blocked = self._validate_target(current_url, dns_results, robots_results)
            if blocked:
                return FetchOutcome("blocked", request, self.policy, error=blocked, dns=tuple(dns_results), robots=tuple(robots_results))
            response = self._transport(current_url)
            if isinstance(response, FetchError):
                return FetchOutcome("error", request, self.policy, error=response, dns=tuple(dns_results), robots=tuple(robots_results))
            if _is_redirect(response.status_code):
                location = _header(response.headers, "location")
                if not location:
                    return self._blocked(request, current_url, "redirect_without_location", "redirect response did not include Location", dns_results, robots_results)
                if redirect_index >= self.policy.max_redirects:
                    return self._blocked(request, current_url, "too_many_redirects", "redirect limit exceeded", dns_results, robots_results)
                current_url = urljoin(current_url, location)
                redirects.append(current_url)
                continue
            content_type = _content_type(response.headers)
            if _mime(content_type) not in set(self.policy.allowed_mime_types):
                return self._blocked(request, current_url, "unsupported_mime_type", f"unsupported MIME type: {content_type}", dns_results, robots_results)
            if len(response.body) > self.policy.max_body_bytes or len(response.body) > self.policy.max_decompressed_bytes:
                return self._blocked(request, current_url, "body_too_large", "response body exceeds configured limit", dns_results, robots_results)
            extracted = extract_document(current_url, response.body, content_type)
            observation = self._observation(request, current_url, response, extracted, redirects)
            return FetchOutcome("fetched", request, self.policy, observation=observation, dns=tuple(dns_results), robots=tuple(robots_results))
        return self._blocked(request, current_url, "too_many_redirects", "redirect limit exceeded", dns_results, robots_results)

    def _validate_target(
        self,
        url: str,
        dns_results: list[Mapping[str, object]],
        robots_results: list[Mapping[str, object]],
    ) -> FetchError | None:
        parsed = urlparse(url)
        if parsed.scheme not in set(self.policy.allowed_schemes):
            return FetchError("unsupported_scheme", f"unsupported URL scheme: {parsed.scheme}", url)
        port = parsed.port or (443 if parsed.scheme == "https" else 80)
        if port not in set(self.policy.allowed_ports):
            return FetchError("unsupported_port", f"unsupported URL port: {port}", url)
        if self.policy.block_non_public_ips:
            dns = self.dns_guard.validate_url(url)
            dns_results.append(dns.to_dict())
            if dns.status != "pass":
                return FetchError("non_public_network_target", dns.error or "target did not resolve to public IPs", url)
        if self.policy.robots_required:
            decision: RobotsDecision = self.robots_client.can_fetch(url, self.policy.user_agent)
            robots_results.append(decision.to_dict())
            if not decision.allowed:
                return FetchError("robots_blocked", decision.error or decision.matched_rule or "blocked by robots.txt", url)
        return None

    def _transport(self, url: str) -> HTTPTransportResult | FetchError:
        try:
            return self.transport(url, {"User-Agent": self.policy.user_agent, "Accept-Encoding": "identity"}, self.policy.timeout_seconds, self.policy.max_body_bytes + 1)
        except Exception as exc:
            return FetchError("transport_error", str(exc), url, policy_blocked=False)

    def _observation(
        self,
        request: FetchRequest,
        url: str,
        response: HTTPTransportResult,
        extracted: ExtractedDocument,
        redirects: list[str],
    ) -> SourceObservation:
        content_hash = hashlib.sha256(response.body).hexdigest()
        canonical_url = extracted.canonical_url or url
        return SourceObservation(
            observation_id="observation:" + hashlib.sha256(f"{canonical_url}\n{content_hash}".encode("utf-8")).hexdigest()[:24],
            canonical_url=canonical_url,
            retrieved_at=self.clock(),
            http_status=int(response.status_code),
            content_type=_content_type(response.headers),
            content_hash="sha256:" + content_hash,
            extracted_title=extracted.title,
            extracted_text=extracted.text,
            outbound_links=tuple(item.to_dict() for item in extracted.outbound_links),
            query=request.query,
            run_id=request.run_id,
            fetch_policy_result="allowed",
            selected_headers=_selected_headers(response.headers),
            redirects=tuple(redirects),
        )

    def _blocked(
        self,
        request: FetchRequest,
        url: str,
        code: str,
        message: str,
        dns_results: list[Mapping[str, object]],
        robots_results: list[Mapping[str, object]],
    ) -> FetchOutcome:
        return FetchOutcome("blocked", request, self.policy, error=FetchError(code, message, url), dns=tuple(dns_results), robots=tuple(robots_results))


class _NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):  # type: ignore[no-untyped-def]
        return None


def _urllib_transport(url: str, headers: Mapping[str, str], timeout_seconds: int, max_bytes: int) -> HTTPTransportResult:
    opener = build_opener(_NoRedirect)
    request = URLRequest(url, headers=dict(headers), method="GET")
    try:
        with opener.open(request, timeout=timeout_seconds) as response:  # noqa: S310 - explicit safe fetch path validates target first
            return HTTPTransportResult(int(response.status), {str(k): str(v) for k, v in response.headers.items()}, response.read(max_bytes))
    except HTTPError as exc:
        return HTTPTransportResult(int(exc.code), {str(k): str(v) for k, v in exc.headers.items()}, exc.read(max_bytes))
    except URLError as exc:
        raise RuntimeError(str(exc.reason)) from exc


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _is_redirect(status_code: int) -> bool:
    return int(status_code) in {301, 302, 303, 307, 308}


def _header(headers: Mapping[str, str], name: str) -> str:
    wanted = name.casefold()
    for key, value in headers.items():
        if str(key).casefold() == wanted:
            return str(value)
    return ""


def _content_type(headers: Mapping[str, str]) -> str:
    return _header(headers, "content-type") or "application/octet-stream"


def _mime(content_type: str) -> str:
    return str(content_type or "").split(";", 1)[0].strip().casefold()


def _selected_headers(headers: Mapping[str, str]) -> dict[str, str]:
    allowed = {"content-type", "last-modified", "etag", "content-length"}
    return {str(k): str(v) for k, v in headers.items() if str(k).casefold() in allowed}
