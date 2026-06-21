"""Discovery provider registry and second-provider conformance adapters."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Mapping, Protocol
from urllib.parse import urlparse, urlunparse

from runtime.source.observation.archive_org_public_metadata import ArchiveOrgMetadataCandidateProvider

from .live_web import (
    BRAVE_ENV_KEYS,
    MOJEEK_ENV_KEYS,
    PROVIDER_NOT_CONFIGURED_MESSAGE,
    BraveSearchProvider,
    ProviderCapabilityManifest,
    SearchLead,
    SearchResultPage,
    WebSearchBudget,
    WebSearchConfigurationError,
    WebSearchProvider,
    WebSearchProviderError,
    brave_capability_manifest,
    looks_like_placeholder_secret,
    mojeek_capability_manifest,
    provider_from_environment as brave_provider_from_environment,
    utc_now,
)
from .provider_policy import ProviderPolicyError, ProviderPolicyRegistry, load_provider_policy_registry, normalize_provider_id


class DiscoveryProvider(Protocol):
    provider_id: str
    capability_manifest: ProviderCapabilityManifest

    def search(self, request: "ProviderSearchRequest", budget: "ProviderBudget") -> "ProviderSearchPage":
        """Return a normalized transient provider result page."""


@dataclass(frozen=True)
class ProviderSearchRequest:
    query: str
    page: int = 0
    count: int = 10
    freshness: str = ""
    country: str = ""
    language: str = ""
    safe_search: str = "moderate"
    query_variant: str = ""


@dataclass(frozen=True)
class ProviderBudget:
    max_provider_requests: int = 1
    timeout_seconds: int = 10
    max_retries: int = 0


@dataclass(frozen=True)
class ProviderSearchPage:
    provider: str
    page: SearchResultPage
    request_count: int
    errors: tuple[dict[str, Any], ...] = ()


@dataclass(frozen=True)
class ProviderSelection:
    requested_provider: str
    provider_ids: tuple[str, ...]
    reason: str


@dataclass(frozen=True)
class ProviderExecutionPlan:
    query: str
    selection: ProviderSelection
    budget: ProviderBudget


@dataclass(frozen=True)
class ProviderResultEnvelope:
    plan: ProviderExecutionPlan
    pages: tuple[ProviderSearchPage, ...]
    errors: tuple[dict[str, Any], ...]
    deduplicated_page: SearchResultPage
    partial_failure: bool


class BraveWebSearchAdapter:
    """DiscoveryProvider adapter over the existing Brave WebSearchProvider."""

    provider_id = "brave"
    capability_manifest = brave_capability_manifest()

    def __init__(self, provider: WebSearchProvider) -> None:
        self.provider = provider

    def search(self, request: ProviderSearchRequest, budget: ProviderBudget) -> ProviderSearchPage:
        page = self.provider.search(
            request.query,
            page=request.page,
            count=request.count,
            freshness=request.freshness,
            country=request.country,
            language=request.language,
            safe_search=request.safe_search,
            budget_context=WebSearchBudget(
                max_provider_requests=budget.max_provider_requests,
                timeout_seconds=budget.timeout_seconds,
                max_retries=budget.max_retries,
            ),
            query_variant=request.query_variant or request.query,
        )
        return ProviderSearchPage(provider=self.provider_id, page=page, request_count=1)


class InternetArchiveMetadataAdapter:
    """Metadata-search adapter for Internet Archive details-page leads only."""

    provider_id = "internet_archive_metadata"
    capability_manifest = ProviderCapabilityManifest(
        provider=provider_id,
        display_results=True,
        transient_cache_ttl_seconds=600,
        persist_urls=True,
        persist_snippets=True,
        persist_rank=False,
        redistribute=False,
        use_for_model_training=False,
        notes=(
            "Internet Archive metadata candidates are unreviewed metadata leads.",
            "The adapter performs metadata search only; it does not download files or create truth.",
        ),
        provider_kind="archive_metadata_search",
        supported_query_modes=("keyword", "phrase", "archive_metadata"),
        pagination_model="rows_page",
        freshness_support=False,
        domain_source_restrictions=("archive.org",),
        rate_limits={"default_request_cap": "bounded_by_provider_budget"},
        persistent_fields_allowed=("identifier", "details_url", "title", "summary", "metadata_fields"),
        fetch_handoff_allowed=True,
        authentication_requirements=(),
        error_categories=("http", "rate_limit", "timeout", "invalid_response", "metadata_policy"),
    )

    def __init__(self, candidate_provider: ArchiveOrgMetadataCandidateProvider | None = None, *, clock: Callable[[], str] | None = None) -> None:
        self.candidate_provider = candidate_provider or ArchiveOrgMetadataCandidateProvider()
        self.clock = clock or utc_now

    def search(self, request: ProviderSearchRequest, budget: ProviderBudget) -> ProviderSearchPage:
        rows = max(1, min(int(request.count or 10), 10))
        result = self.candidate_provider.search_metadata_candidates(request.query, limit=rows)
        status = str(result.get("status") or "")
        if status not in {"succeeded"}:
            raise WebSearchProviderError(
                str(result.get("failure_reason") or result.get("failure_detail") or "Internet Archive metadata search failed"),
                provider=self.provider_id,
                status_code=int(result.get("http_status") or 0),
            )
        retention = self.capability_manifest.retention_policy()
        leads: list[SearchLead] = []
        for index, candidate in enumerate(result.get("candidates") or [], start=1):
            if not isinstance(candidate, Mapping):
                continue
            locator = candidate.get("source_locator") if isinstance(candidate.get("source_locator"), Mapping) else {}
            url = str(locator.get("url") or "").strip()
            if not url:
                continue
            title = str(candidate.get("candidate_title") or candidate.get("identifier") or url)
            leads.append(
                SearchLead(
                    lead_id=f"lead:{self.provider_id}:{candidate.get('candidate_id') or index}",
                    title=title,
                    url=url,
                    snippet=str(candidate.get("candidate_summary") or ""),
                    provider=self.provider_id,
                    provider_rank=index,
                    retrieved_at=self.clock(),
                    query=request.query,
                    query_variant=request.query_variant or request.query,
                    page=max(0, int(request.page or 0)),
                    freshness=request.freshness,
                    retention_policy=retention,
                )
            )
        page = SearchResultPage(
            provider=self.provider_id,
            query=request.query,
            query_variant=request.query_variant or request.query,
            page=max(0, int(request.page or 0)),
            count=rows,
            retrieved_at=self.clock(),
            results=tuple(leads),
            more_results_available=False,
            rate_limit={},
            raw_response_stored=False,
        )
        return ProviderSearchPage(provider=self.provider_id, page=page, request_count=int(result.get("total_http_requests") or 0))


class ProviderRegistry:
    def __init__(
        self,
        *,
        env: Mapping[str, str] | None = None,
        ia_candidate_provider: ArchiveOrgMetadataCandidateProvider | None = None,
        policy_registry: ProviderPolicyRegistry | None = None,
        policy_path: str | None = None,
    ) -> None:
        self.env = env
        self.ia_candidate_provider = ia_candidate_provider
        self.policy_registry = policy_registry or load_provider_policy_registry(policy_path)

    def select(self, query: str, requested_provider: str = "brave") -> ProviderSelection:
        requested = str(requested_provider or "brave").strip().casefold()
        if requested in {"brave", "mojeek", "internet_archive_metadata", "ia"}:
            provider_id = "internet_archive_metadata" if requested == "ia" else requested
            return ProviderSelection(requested_provider=requested_provider, provider_ids=self._selectable((provider_id,)), reason="explicit_provider")
        if requested in {"auto", "multi", "blended"}:
            providers = ("internet_archive_metadata", "brave", "mojeek") if _archive_query(query) else ("brave", "mojeek")
            return ProviderSelection(requested_provider=requested_provider, provider_ids=self._selectable(providers), reason="deterministic_query_routing")
        if "," in requested_provider:
            ids = tuple(_normalize_provider_id(item) for item in requested_provider.split(",") if _normalize_provider_id(item))
            return ProviderSelection(requested_provider=requested_provider, provider_ids=self._selectable(ids or ("brave",)), reason="explicit_provider_list")
        raise WebSearchConfigurationError(f"unsupported live web search provider: {requested_provider}")

    def provider(self, provider_id: str) -> WebSearchProvider | None:
        normalized = _normalize_provider_id(provider_id)
        self._validate_activation(normalized)
        if normalized == "brave":
            return brave_provider_from_environment("brave", env=self.env)
        if normalized == "mojeek":
            return brave_provider_from_environment("mojeek", env=self.env)
        if normalized == "internet_archive_metadata":
            return _DiscoveryProviderWebSearchAdapter(InternetArchiveMetadataAdapter(self.ia_candidate_provider))
        raise WebSearchConfigurationError(f"unsupported live web search provider: {provider_id}")

    def provider_or_multi(self, requested_provider: str, query: str = "") -> WebSearchProvider | None:
        selection = self.select(query, requested_provider)
        if len(selection.provider_ids) == 1:
            return self.provider(selection.provider_ids[0])
        providers = [provider for provider_id in selection.provider_ids if (provider := self.provider(provider_id)) is not None]
        if not providers:
            return None
        return MultiProviderSearchProvider(tuple(providers), requested_provider=requested_provider)

    def execution_plan(self, query: str, requested_provider: str, budget: ProviderBudget) -> ProviderExecutionPlan:
        selection = self.select(query, requested_provider)
        for provider_id in selection.provider_ids:
            self._validate_activation(provider_id, budget=budget)
        return ProviderExecutionPlan(query=query, selection=selection, budget=budget)

    def _selectable(self, provider_ids: tuple[str, ...]) -> tuple[str, ...]:
        allowed = self.policy_registry.selectable_provider_ids(provider_ids, mode="local_live")
        if not allowed:
            raise WebSearchConfigurationError("no requested live provider is allowed by provider policy")
        return allowed

    def _validate_activation(self, provider_id: str, *, budget: ProviderBudget | None = None) -> None:
        try:
            self.policy_registry.validate_activation(provider_id, mode="local_live", requested_budget=budget, env=self.env)
        except ProviderPolicyError as exc:
            raise WebSearchConfigurationError(str(exc)) from exc


class MultiProviderSearchProvider:
    provider_id = "multi"

    def __init__(self, providers: tuple[WebSearchProvider, ...], *, requested_provider: str = "multi") -> None:
        self.providers = providers
        self.requested_provider = requested_provider
        self.capability_manifest = ProviderCapabilityManifest(
            provider="multi",
            display_results=True,
            transient_cache_ttl_seconds=min(provider.capability_manifest.transient_cache_ttl_seconds for provider in providers),
            persist_urls=all(provider.capability_manifest.persist_urls for provider in providers),
            persist_snippets=all(provider.capability_manifest.persist_snippets for provider in providers),
            persist_rank=all(provider.capability_manifest.persist_rank for provider in providers),
            redistribute=False,
            use_for_model_training=False,
            notes=("Multi-provider transient search envelope.",),
            provider_kind="multi_provider_discovery",
            supported_query_modes=tuple(sorted({mode for provider in providers for mode in provider.capability_manifest.supported_query_modes})),
            pagination_model="provider_native",
            freshness_support=any(provider.capability_manifest.freshness_support for provider in providers),
            fetch_handoff_allowed=all(provider.capability_manifest.fetch_handoff_allowed for provider in providers),
        )

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
        leads: list[SearchLead] = []
        errors: list[WebSearchProviderError] = []
        more = False
        for provider in self.providers:
            try:
                result = provider.search(
                    query,
                    page=page,
                    count=count,
                    freshness=freshness,
                    country=country,
                    language=language,
                    safe_search=safe_search,
                    budget_context=budget_context,
                    query_variant=query_variant,
                )
            except WebSearchProviderError as exc:
                errors.append(exc)
                continue
            leads.extend(result.results)
            more = more or result.more_results_available
        deduped = _dedupe_leads(leads)
        if not deduped and errors:
            raise errors[0]
        return SearchResultPage(
            provider=self.provider_id,
            query=query,
            query_variant=query_variant or query,
            page=page,
            count=count,
            retrieved_at=utc_now(),
            results=tuple(deduped),
            more_results_available=more,
            rate_limit={"partial_failure_count": str(len(errors))} if errors else {},
            raw_response_stored=False,
        )


class _DiscoveryProviderWebSearchAdapter:
    def __init__(self, provider: DiscoveryProvider) -> None:
        self.provider = provider
        self.provider_id = provider.provider_id
        self.capability_manifest = provider.capability_manifest

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
        result = self.provider.search(
            ProviderSearchRequest(
                query=query,
                page=page,
                count=count,
                freshness=freshness,
                country=country,
                language=language,
                safe_search=safe_search,
                query_variant=query_variant or query,
            ),
            ProviderBudget(
                max_provider_requests=budget_context.max_provider_requests,
                timeout_seconds=budget_context.timeout_seconds,
                max_retries=budget_context.max_retries,
            ),
        )
        return result.page


def provider_from_environment(provider: str = "brave", *, env: Mapping[str, str] | None = None, **_kwargs: Any) -> WebSearchProvider | None:
    requested = str(provider or "brave").strip().casefold()
    query_hint = str(_kwargs.get("query") or "")
    return ProviderRegistry(env=env).provider_or_multi(provider, query=query_hint)


def provider_status(provider: str = "brave", *, env: Mapping[str, str] | None = None) -> dict[str, Any]:
    registry = ProviderRegistry(env=env)
    try:
        selection = registry.select("", provider)
    except WebSearchConfigurationError as exc:
        return {"provider": provider, "configured": False, "error": str(exc), "credential_value_exposed": False}
    configured: dict[str, bool] = {}
    manifests: dict[str, Any] = {}
    for provider_id in selection.provider_ids:
        if provider_id == "brave":
            source = env or __import__("os").environ
            configured[provider_id] = any(
                bool(str(source.get(name) or "").strip()) and not looks_like_placeholder_secret(str(source.get(name) or "").strip())
                for name in BRAVE_ENV_KEYS
            )
            manifests[provider_id] = brave_capability_manifest().to_dict()
        elif provider_id == "mojeek":
            source = env or __import__("os").environ
            configured[provider_id] = any(
                bool(str(source.get(name) or "").strip()) and not looks_like_placeholder_secret(str(source.get(name) or "").strip())
                for name in MOJEEK_ENV_KEYS
            )
            manifests[provider_id] = mojeek_capability_manifest().to_dict()
        elif provider_id == "internet_archive_metadata":
            configured[provider_id] = True
            manifests[provider_id] = InternetArchiveMetadataAdapter.capability_manifest.to_dict()
    return {
        "provider": provider,
        "configured": any(configured.values()),
        "providers": configured,
        "credential_env_keys": _credential_env_keys(configured),
        "credential_value_exposed": False,
        "message": "" if any(configured.values()) else PROVIDER_NOT_CONFIGURED_MESSAGE,
        "capability_manifest": manifests,
        "provider_policy_registry": registry.policy_registry.safe_status(),
        "public_live_fanout": False,
    }


def execute_provider_plan(registry: ProviderRegistry, plan: ProviderExecutionPlan) -> ProviderResultEnvelope:
    pages: list[ProviderSearchPage] = []
    errors: list[dict[str, Any]] = []
    leads: list[SearchLead] = []
    for provider_id in plan.selection.provider_ids:
        provider = registry.provider(provider_id)
        if provider is None:
            errors.append({"provider": provider_id, "code": "provider_not_configured"})
            continue
        try:
            page = provider.search(
                plan.query,
                page=0,
                count=plan.budget.max_provider_requests,
                freshness="",
                country="",
                language="",
                safe_search="moderate",
                budget_context=WebSearchBudget(max_provider_requests=1, timeout_seconds=plan.budget.timeout_seconds, max_retries=plan.budget.max_retries),
            )
        except WebSearchProviderError as exc:
            errors.append({"provider": exc.provider, "code": "provider_error", "status_code": exc.status_code})
            continue
        pages.append(ProviderSearchPage(provider=provider_id, page=page, request_count=1))
        leads.extend(page.results)
    deduped = _dedupe_leads(leads)
    envelope_page = SearchResultPage(
        provider="registry",
        query=plan.query,
        query_variant=plan.query,
        page=0,
        count=len(deduped),
        retrieved_at=utc_now(),
        results=tuple(deduped),
        more_results_available=any(item.page.more_results_available for item in pages),
        rate_limit={},
        raw_response_stored=False,
    )
    return ProviderResultEnvelope(plan=plan, pages=tuple(pages), errors=tuple(errors), deduplicated_page=envelope_page, partial_failure=bool(errors and pages))


def _dedupe_leads(leads: list[SearchLead]) -> list[SearchLead]:
    seen: set[str] = set()
    result: list[SearchLead] = []
    for lead in leads:
        key = _canonical_url_key(lead.url) or lead.lead_id
        if key in seen:
            continue
        seen.add(key)
        result.append(lead)
    return result


def _canonical_url_key(url: str) -> str:
    parsed = urlparse(str(url or "").strip())
    if not parsed.netloc:
        return ""
    path = parsed.path.rstrip("/") or "/"
    return urlunparse((parsed.scheme.casefold(), parsed.netloc.casefold(), path, "", parsed.query, ""))


def _normalize_provider_id(provider: str) -> str:
    return normalize_provider_id(provider)


def _credential_env_keys(configured: Mapping[str, bool]) -> list[str]:
    keys: list[str] = []
    if "brave" in configured:
        keys.extend(BRAVE_ENV_KEYS)
    if "mojeek" in configured:
        keys.extend(MOJEEK_ENV_KEYS)
    return keys


def _archive_query(query: str) -> bool:
    normalized = str(query or "").casefold()
    hints = ("archive", "manual", "software", "magazine", "scan", "sound blaster", "driver", "ftp", "old", "historical")
    return any(hint in normalized for hint in hints)
