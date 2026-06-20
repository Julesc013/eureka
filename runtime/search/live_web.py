"""Transient live web search provider contracts and adapters."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from html import unescape
import hashlib
import json
import os
import re
import time
from typing import Any, Callable, Mapping, Protocol
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


PROVIDER_NOT_CONFIGURED_MESSAGE = "Live web search is not configured. Configure a provider or search the local index."
BRAVE_SEARCH_ENDPOINT = "https://api.search.brave.com/res/v1/web/search"
BRAVE_ENV_KEYS = ("BRAVE_SEARCH_API_KEY", "BRAVE_API_KEY")
DEFAULT_USER_AGENT = "Eureka/0 local-live-search"


class WebSearchConfigurationError(ValueError):
    """Raised when a live web search provider cannot be configured."""


class WebSearchProviderError(RuntimeError):
    """Raised when a live web search provider request fails."""

    def __init__(
        self,
        message: str,
        *,
        provider: str,
        status_code: int = 0,
        rate_limit: Mapping[str, str] | None = None,
    ) -> None:
        super().__init__(message)
        self.provider = provider
        self.status_code = status_code
        self.rate_limit = dict(rate_limit or {})


class WebSearchRateLimited(WebSearchProviderError):
    """Raised when a live web search provider returns HTTP 429."""


@dataclass(frozen=True)
class WebSearchBudget:
    max_provider_requests: int = 1
    timeout_seconds: int = 10
    max_retries: int = 1
    max_retry_sleep_seconds: float = 2.0

    def bounded(self) -> "WebSearchBudget":
        return WebSearchBudget(
            max_provider_requests=max(0, min(int(self.max_provider_requests), 25)),
            timeout_seconds=max(1, min(int(self.timeout_seconds), 30)),
            max_retries=max(0, min(int(self.max_retries), 3)),
            max_retry_sleep_seconds=max(0.0, min(float(self.max_retry_sleep_seconds), 5.0)),
        )


@dataclass(frozen=True)
class SearchLeadRetentionPolicy:
    display_results: bool
    transient_cache_ttl_seconds: int
    persist_urls: bool
    persist_snippets: bool
    persist_rank: bool
    redistribute: bool
    use_for_model_training: bool
    terms_basis: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "display_results": self.display_results,
            "transient_cache_ttl_seconds": self.transient_cache_ttl_seconds,
            "persist_urls": self.persist_urls,
            "persist_snippets": self.persist_snippets,
            "persist_rank": self.persist_rank,
            "redistribute": self.redistribute,
            "use_for_model_training": self.use_for_model_training,
            "terms_basis": self.terms_basis,
        }


@dataclass(frozen=True)
class ProviderCapabilityManifest:
    provider: str
    display_results: bool
    transient_cache_ttl_seconds: int
    persist_urls: bool
    persist_snippets: bool
    persist_rank: bool
    redistribute: bool
    use_for_model_training: bool
    notes: tuple[str, ...] = ()
    provider_kind: str = "broad_web_search"
    supported_query_modes: tuple[str, ...] = ("keyword", "phrase", "site", "filetype")
    pagination_model: str = "page"
    freshness_support: bool = True
    domain_source_restrictions: tuple[str, ...] = ()
    rate_limits: Mapping[str, Any] | None = None
    persistent_fields_allowed: tuple[str, ...] = ()
    fetch_handoff_allowed: bool = True
    authentication_requirements: tuple[str, ...] = ()
    error_categories: tuple[str, ...] = ("configuration", "http", "rate_limit", "timeout", "invalid_response")

    def retention_policy(self) -> SearchLeadRetentionPolicy:
        return SearchLeadRetentionPolicy(
            display_results=self.display_results,
            transient_cache_ttl_seconds=self.transient_cache_ttl_seconds,
            persist_urls=self.persist_urls,
            persist_snippets=self.persist_snippets,
            persist_rank=self.persist_rank,
            redistribute=self.redistribute,
            use_for_model_training=self.use_for_model_training,
            terms_basis=self.provider,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider": self.provider,
            "display_results": self.display_results,
            "transient_cache_ttl_seconds": self.transient_cache_ttl_seconds,
            "persist_urls": self.persist_urls,
            "persist_snippets": self.persist_snippets,
            "persist_rank": self.persist_rank,
            "redistribute": self.redistribute,
            "use_for_model_training": self.use_for_model_training,
            "notes": list(self.notes),
            "provider_kind": self.provider_kind,
            "supported_query_modes": list(self.supported_query_modes),
            "pagination_model": self.pagination_model,
            "freshness_support": self.freshness_support,
            "domain_source_restrictions": list(self.domain_source_restrictions),
            "rate_limits": dict(self.rate_limits or {}),
            "persistent_fields_allowed": list(self.persistent_fields_allowed),
            "fetch_handoff_allowed": self.fetch_handoff_allowed,
            "authentication_requirements": list(self.authentication_requirements),
            "error_categories": list(self.error_categories),
        }


@dataclass(frozen=True)
class SearchLead:
    lead_id: str
    title: str
    url: str
    snippet: str
    provider: str
    provider_rank: int
    retrieved_at: str
    query: str
    query_variant: str
    page: int
    freshness: str
    retention_policy: SearchLeadRetentionPolicy

    def to_dict(self) -> dict[str, Any]:
        return {
            "lead_id": self.lead_id,
            "title": self.title,
            "url": self.url,
            "snippet": self.snippet,
            "provider": self.provider,
            "provider_rank": self.provider_rank,
            "retrieved_at": self.retrieved_at,
            "query": self.query,
            "query_variant": self.query_variant,
            "page": self.page,
            "freshness": self.freshness,
            "retention_policy": self.retention_policy.to_dict(),
            "state": "LIVE - UNREVIEWED",
        }


@dataclass(frozen=True)
class SearchResultPage:
    provider: str
    query: str
    query_variant: str
    page: int
    count: int
    retrieved_at: str
    results: tuple[SearchLead, ...]
    more_results_available: bool
    rate_limit: Mapping[str, str]
    raw_response_stored: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider": self.provider,
            "query": self.query,
            "query_variant": self.query_variant,
            "page": self.page,
            "count": self.count,
            "retrieved_at": self.retrieved_at,
            "result_count": len(self.results),
            "results": [lead.to_dict() for lead in self.results],
            "more_results_available": self.more_results_available,
            "rate_limit": dict(self.rate_limit),
            "raw_response_stored": self.raw_response_stored,
        }


@dataclass(frozen=True)
class HTTPTransportResult:
    status_code: int
    headers: Mapping[str, str]
    body: bytes


class WebSearchProvider(Protocol):
    provider_id: str
    capability_manifest: ProviderCapabilityManifest

    def search(
        self,
        query: str,
        *,
        page: int,
        count: int,
        freshness: str,
        country: str,
        language: str,
        safe_search: str,
        budget_context: WebSearchBudget,
        query_variant: str | None = None,
    ) -> SearchResultPage:
        """Return a transient page of live search leads."""


Transport = Callable[[str, Mapping[str, str], int], HTTPTransportResult]


def brave_capability_manifest() -> ProviderCapabilityManifest:
    return ProviderCapabilityManifest(
        provider="brave",
        display_results=True,
        transient_cache_ttl_seconds=300,
        persist_urls=False,
        persist_snippets=False,
        persist_rank=False,
        redistribute=False,
        use_for_model_training=False,
        notes=(
            "Brave Search Results are treated as transient discovery leads.",
            "Persist independently fetched page observations instead of provider snippets or ranks.",
        ),
    )


class BraveSearchProvider:
    provider_id = "brave"
    capability_manifest = brave_capability_manifest()

    def __init__(
        self,
        api_key: str,
        *,
        endpoint: str = BRAVE_SEARCH_ENDPOINT,
        transport: Transport | None = None,
        clock: Callable[[], str] | None = None,
        sleeper: Callable[[float], None] | None = None,
    ) -> None:
        clean_key = str(api_key or "").strip()
        if not clean_key:
            raise WebSearchConfigurationError(PROVIDER_NOT_CONFIGURED_MESSAGE)
        self._api_key = clean_key
        self._endpoint = str(endpoint or BRAVE_SEARCH_ENDPOINT)
        self._transport = transport or _urllib_transport
        self._clock = clock or utc_now
        self._sleeper = sleeper or time.sleep

    def search(
        self,
        query: str,
        *,
        page: int,
        count: int,
        freshness: str,
        country: str,
        language: str,
        safe_search: str,
        budget_context: WebSearchBudget,
        query_variant: str | None = None,
    ) -> SearchResultPage:
        clean_query = _clean_text(query)
        if not clean_query:
            raise WebSearchProviderError("query is required", provider=self.provider_id)
        budget = budget_context.bounded()
        if budget.max_provider_requests < 1:
            raise WebSearchProviderError("provider request budget is exhausted", provider=self.provider_id)
        bounded_count = max(1, min(int(count or 10), 20))
        bounded_page = max(0, min(int(page or 0), 9))
        params = _brave_params(
            clean_query,
            page=bounded_page,
            count=bounded_count,
            freshness=freshness,
            country=country,
            language=language,
            safe_search=safe_search,
        )
        url = f"{self._endpoint}?{urlencode(params)}"
        headers = {
            "Accept": "application/json",
            "User-Agent": DEFAULT_USER_AGENT,
            "X-Subscription-Token": self._api_key,
        }
        response = self._request_with_retry(url, headers, budget)
        payload = _decode_json_response(response.body, provider=self.provider_id)
        return self._page_from_payload(
            payload,
            query=clean_query,
            query_variant=_clean_text(query_variant) or clean_query,
            page=bounded_page,
            count=bounded_count,
            freshness=str(freshness or ""),
            retrieved_at=self._clock(),
            rate_limit=_rate_limit_headers(response.headers),
        )

    def _request_with_retry(
        self,
        url: str,
        headers: Mapping[str, str],
        budget: WebSearchBudget,
    ) -> HTTPTransportResult:
        attempts = budget.max_retries + 1
        last_response: HTTPTransportResult | None = None
        for attempt in range(attempts):
            try:
                response = self._transport(url, headers, budget.timeout_seconds)
            except URLError as exc:
                raise WebSearchProviderError(str(exc.reason), provider=self.provider_id) from exc
            last_response = response
            rate_limit = _rate_limit_headers(response.headers)
            if response.status_code != 429:
                if response.status_code >= 400:
                    raise WebSearchProviderError(
                        f"Brave Search API returned HTTP {response.status_code}",
                        provider=self.provider_id,
                        status_code=response.status_code,
                        rate_limit=rate_limit,
                    )
                return response
            if attempt + 1 >= attempts:
                break
            self._sleeper(_retry_sleep_seconds(rate_limit, attempt, budget.max_retry_sleep_seconds))
        response = last_response or HTTPTransportResult(429, {}, b"")
        raise WebSearchRateLimited(
            "Brave Search API rate limit exceeded",
            provider=self.provider_id,
            status_code=response.status_code,
            rate_limit=_rate_limit_headers(response.headers),
        )

    def _page_from_payload(
        self,
        payload: Mapping[str, Any],
        *,
        query: str,
        query_variant: str,
        page: int,
        count: int,
        freshness: str,
        retrieved_at: str,
        rate_limit: Mapping[str, str],
    ) -> SearchResultPage:
        web = payload.get("web") if isinstance(payload.get("web"), Mapping) else {}
        rows = web.get("results") if isinstance(web.get("results"), list) else []
        retention = self.capability_manifest.retention_policy()
        leads: list[SearchLead] = []
        for offset, item in enumerate(rows):
            if not isinstance(item, Mapping):
                continue
            url = _clean_text(item.get("url"))
            if not url:
                continue
            rank = page * count + offset + 1
            title = _plain_text(item.get("title") or url)
            snippet = _plain_text(item.get("description") or "")
            leads.append(
                SearchLead(
                    lead_id=_lead_id(self.provider_id, query_variant, page, rank, url),
                    title=title,
                    url=url,
                    snippet=snippet,
                    provider=self.provider_id,
                    provider_rank=rank,
                    retrieved_at=retrieved_at,
                    query=query,
                    query_variant=query_variant,
                    page=page,
                    freshness=freshness,
                    retention_policy=retention,
                )
            )
        query_meta = payload.get("query") if isinstance(payload.get("query"), Mapping) else {}
        return SearchResultPage(
            provider=self.provider_id,
            query=query,
            query_variant=query_variant,
            page=page,
            count=count,
            retrieved_at=retrieved_at,
            results=tuple(leads),
            more_results_available=bool(query_meta.get("more_results_available")),
            rate_limit=rate_limit,
            raw_response_stored=False,
        )


def provider_from_environment(
    provider: str = "brave",
    *,
    env: Mapping[str, str] | None = None,
    transport: Transport | None = None,
    clock: Callable[[], str] | None = None,
    sleeper: Callable[[float], None] | None = None,
) -> WebSearchProvider | None:
    provider_id = str(provider or "brave").strip().casefold()
    if provider_id != "brave":
        raise WebSearchConfigurationError(f"unsupported live web search provider: {provider}")
    source = env or os.environ
    api_key = next((str(source.get(name) or "").strip() for name in BRAVE_ENV_KEYS if str(source.get(name) or "").strip()), "")
    if not api_key:
        return None
    return BraveSearchProvider(api_key, transport=transport, clock=clock, sleeper=sleeper)


def provider_status(provider: str = "brave", *, env: Mapping[str, str] | None = None) -> dict[str, Any]:
    source = env or os.environ
    configured = any(bool(str(source.get(name) or "").strip()) for name in BRAVE_ENV_KEYS)
    return {
        "provider": str(provider or "brave"),
        "configured": configured,
        "credential_env_keys": list(BRAVE_ENV_KEYS),
        "credential_value_exposed": False,
        "message": "" if configured else PROVIDER_NOT_CONFIGURED_MESSAGE,
        "capability_manifest": brave_capability_manifest().to_dict() if str(provider or "brave").casefold() == "brave" else {},
    }


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")


def _urllib_transport(url: str, headers: Mapping[str, str], timeout_seconds: int) -> HTTPTransportResult:
    request = Request(url, headers=dict(headers), method="GET")
    try:
        with urlopen(request, timeout=timeout_seconds) as response:  # noqa: S310 - explicit opt-in provider API call
            return HTTPTransportResult(
                status_code=int(response.status),
                headers={str(key): str(value) for key, value in response.headers.items()},
                body=response.read(1_000_000),
            )
    except HTTPError as exc:
        return HTTPTransportResult(
            status_code=int(exc.code),
            headers={str(key): str(value) for key, value in exc.headers.items()},
            body=exc.read(1_000_000),
        )


def _brave_params(
    query: str,
    *,
    page: int,
    count: int,
    freshness: str,
    country: str,
    language: str,
    safe_search: str,
) -> dict[str, str]:
    params = {
        "q": query,
        "count": str(max(1, min(int(count), 20))),
        "offset": str(max(0, min(int(page), 9))),
        "safesearch": _safe_search_value(safe_search),
    }
    clean_freshness = _clean_text(freshness)
    if clean_freshness:
        params["freshness"] = clean_freshness
    clean_country = _clean_text(country).upper()
    if clean_country:
        params["country"] = clean_country[:2]
    clean_language = _clean_text(language).lower()
    if clean_language:
        params["search_lang"] = clean_language[:8]
    return params


def _safe_search_value(value: str) -> str:
    normalized = _clean_text(value).casefold()
    if normalized in {"off", "moderate", "strict"}:
        return normalized
    return "moderate"


def _decode_json_response(body: bytes, *, provider: str) -> Mapping[str, Any]:
    try:
        payload = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise WebSearchProviderError("provider response was not valid JSON", provider=provider) from exc
    if not isinstance(payload, Mapping):
        raise WebSearchProviderError("provider response JSON was not an object", provider=provider)
    return payload


def _rate_limit_headers(headers: Mapping[str, str]) -> dict[str, str]:
    lowered = {str(key).lower(): str(value) for key, value in dict(headers or {}).items()}
    result: dict[str, str] = {}
    for name in ("x-ratelimit-limit", "x-ratelimit-policy", "x-ratelimit-remaining", "x-ratelimit-reset"):
        if name in lowered:
            result[_header_case(name)] = lowered[name]
    return result


def _retry_sleep_seconds(rate_limit: Mapping[str, str], attempt: int, cap: float) -> float:
    reset = str(rate_limit.get("X-RateLimit-Reset") or "").split(",", 1)[0].strip()
    try:
        value = float(reset)
    except ValueError:
        value = float(2**attempt)
    return max(0.0, min(value, cap))


def _header_case(name: str) -> str:
    return {
        "x-ratelimit-limit": "X-RateLimit-Limit",
        "x-ratelimit-policy": "X-RateLimit-Policy",
        "x-ratelimit-remaining": "X-RateLimit-Remaining",
        "x-ratelimit-reset": "X-RateLimit-Reset",
    }[name]


def _lead_id(provider: str, query_variant: str, page: int, rank: int, url: str) -> str:
    digest = hashlib.sha256(f"{provider}\n{query_variant}\n{page}\n{rank}\n{url}".encode("utf-8")).hexdigest()
    return f"lead:{provider}:{digest[:20]}"


def _plain_text(value: Any) -> str:
    text = unescape(_clean_text(value))
    return re.sub(r"<[^>]+>", "", text).strip()


def _clean_text(value: Any) -> str:
    return " ".join(str(value or "").replace("\r", " ").replace("\n", " ").split())
