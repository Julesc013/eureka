"""Shared live search and Hunt orchestration for local surfaces."""

from __future__ import annotations

from dataclasses import dataclass
import hashlib
from pathlib import Path
import re
import threading
import time
from typing import Any, Callable, Mapping, Protocol

from .live_web import (
    PROVIDER_NOT_CONFIGURED_MESSAGE,
    WebSearchBudget,
    WebSearchProvider,
    WebSearchProviderError,
)
from .providers import provider_from_environment, provider_status


ProviderFactory = Callable[[str], WebSearchProvider | None]


class LeadBufferClock(Protocol):
    def __call__(self) -> float:
        """Return monotonic-ish seconds for in-memory TTL checks."""


class TransientLeadBuffer:
    """Small in-memory buffer for provider leads that must not become durable state."""

    def __init__(self, *, ttl_seconds: int = 300, max_leads: int = 500, clock: LeadBufferClock | None = None) -> None:
        self.ttl_seconds = max(1, min(int(ttl_seconds or 300), 3600))
        self.max_leads = max(1, min(int(max_leads or 500), 10_000))
        self._clock = clock or time.monotonic
        self._entries: dict[str, tuple[float, dict[str, Any]]] = {}
        self._lock = threading.RLock()

    def store_page(self, provider_page: Mapping[str, Any] | None) -> list[str]:
        if not provider_page:
            return []
        with self._lock:
            self._expire_locked()
            stored: list[str] = []
            for lead in provider_page.get("results") or []:
                if not isinstance(lead, Mapping):
                    continue
                lead_id = str(lead.get("lead_id") or "").strip()
                if not lead_id:
                    continue
                self._entries[lead_id] = (self._clock() + self.ttl_seconds, dict(lead))
                stored.append(lead_id)
            self._trim_locked()
            return stored

    def get(self, lead_id: str) -> dict[str, Any] | None:
        with self._lock:
            self._expire_locked()
            entry = self._entries.get(str(lead_id or ""))
            return dict(entry[1]) if entry else None

    def active_count(self) -> int:
        with self._lock:
            self._expire_locked()
            return len(self._entries)

    def _expire_locked(self) -> None:
        now = self._clock()
        expired = [lead_id for lead_id, (expires_at, _lead) in self._entries.items() if expires_at <= now]
        for lead_id in expired:
            self._entries.pop(lead_id, None)

    def _trim_locked(self) -> None:
        overflow = len(self._entries) - self.max_leads
        if overflow <= 0:
            return
        oldest = sorted(self._entries.items(), key=lambda item: item[1][0])[:overflow]
        for lead_id, _entry in oldest:
            self._entries.pop(lead_id, None)


@dataclass(frozen=True)
class LiveHuntResult:
    response: dict[str, Any]
    persisted_summary: dict[str, Any]
    events: tuple[dict[str, Any], ...] = ()


class LiveSearchService:
    """Provider invocation, transient lead display, and sanitized Hunt summaries."""

    def __init__(
        self,
        *,
        provider_name: str = "brave",
        provider_factory: ProviderFactory = provider_from_environment,
        lead_buffer: TransientLeadBuffer | None = None,
    ) -> None:
        self.provider_name = str(provider_name or "brave")
        self.provider_factory = provider_factory
        self.lead_buffer = lead_buffer or TransientLeadBuffer()

    def search(
        self,
        query: str,
        *,
        mode: str = "blended",
        local_results: Mapping[str, Any] | None = None,
        page: int = 0,
        count: int = 10,
        freshness: str = "",
        country: str = "",
        language: str = "",
        safe_search: str = "moderate",
        timeout_seconds: int = 10,
    ) -> dict[str, Any]:
        clean_query = _clean_query(query)
        search_mode = str(mode or "blended").strip().lower()
        if search_mode not in {"local", "live", "blended", "replay"}:
            search_mode = "blended"
        local = dict(local_results or _local_index_disabled())
        provider_page: dict[str, Any] | None = None
        live_error: dict[str, Any] | None = None
        network_used = False
        if clean_query and search_mode in {"live", "blended"}:
            provider_page, live_error, network_used = self._search_provider_page(
                clean_query,
                page=page,
                count=count,
                freshness=freshness,
                country=country,
                language=language,
                safe_search=safe_search,
                timeout_seconds=timeout_seconds,
            )
            self.lead_buffer.store_page(provider_page)
        live_cards = live_display_cards(provider_page)
        local_cards = list(local.get("results") or [])
        results = [*local_cards, *live_cards] if search_mode == "blended" else (live_cards if search_mode == "live" else local_cards)
        live_unavailable = _live_unavailable(self.provider_name, live_error)
        status = _search_status(results, live_error=live_error, search_mode=search_mode, query=clean_query)
        return {
            "schema_version": "eureka.live_web_search_response.v0",
            "status": status,
            "query": clean_query,
            "mode": search_mode,
            "result_count": len(results),
            "results": results,
            "local_index": local,
            "live": provider_page or live_unavailable,
            "provider_status": provider_status(self.provider_name),
            "message": "" if clean_query else "Enter a query to search the web and your Eureka index.",
            "error": live_error or {},
            "network_provider_calls": network_used,
            "live_results_transient": True,
            "transient_lead_buffer_count": self.lead_buffer.active_count(),
            "provider_results_persisted": False,
            "review_required_for_display": False,
            "reviewed_master_mutation": False,
            "public_index_mutation": False,
        }

    def start_hunt(
        self,
        query: str,
        *,
        run_id: str,
        max_queries: int,
        max_fetches: int,
        count: int = 10,
        timeout_seconds: int = 10,
        max_pages: int = 2,
        max_links_followed: int = 10,
        preview_index_path: str | Path | None = None,
        fetcher: Any | None = None,
        index_store: Any | None = None,
    ) -> LiveHuntResult:
        clean_query = _clean_query(query)
        if preview_index_path is not None or fetcher is not None or index_store is not None:
            if clean_query and self.provider_factory(self.provider_name) is None:
                return self._transient_only_hunt(
                    clean_query,
                    run_id=run_id,
                    max_queries=max_queries,
                    max_fetches=max_fetches,
                    count=count,
                    timeout_seconds=timeout_seconds,
                )
            from runtime.index.preview import SQLitePreviewIndexStore
            from runtime.search.hunt_engine import HuntBudget, HuntEngine

            created_store = None
            if index_store is None and preview_index_path is not None:
                created_store = SQLitePreviewIndexStore(preview_index_path)
                index_store = created_store
            try:
                result = HuntEngine(
                    provider_name=self.provider_name,
                    provider_factory=self.provider_factory,
                    fetcher=fetcher,
                    index_store=index_store,
                ).run(
                    clean_query,
                    run_id=run_id,
                    budget=HuntBudget(
                        max_queries=max_queries,
                        max_provider_requests=max_queries * max(1, int(max_pages or 1)),
                        max_pages=max_pages,
                        max_fetches=max_fetches,
                        max_links_followed=max_links_followed,
                        count=count,
                        timeout_seconds=timeout_seconds,
                    ),
                )
                return LiveHuntResult(response=result.response, persisted_summary=result.persisted_summary, events=result.events)
            finally:
                if created_store is not None:
                    created_store.close()
        return self._transient_only_hunt(
            clean_query,
            run_id=run_id,
            max_queries=max_queries,
            max_fetches=max_fetches,
            count=count,
            timeout_seconds=timeout_seconds,
        )

    def _transient_only_hunt(
        self,
        clean_query: str,
        *,
        run_id: str,
        max_queries: int,
        max_fetches: int,
        count: int,
        timeout_seconds: int,
    ) -> LiveHuntResult:
        variants = hunt_query_variants(clean_query, max_queries=max_queries) if clean_query else []
        provider = self.provider_factory(self.provider_name) if clean_query else None
        errors: list[dict[str, Any]] = []
        display_cards: list[dict[str, Any]] = []
        seen_urls: set[str] = set()
        attempted: list[str] = []
        request_count = 0
        raw_lead_count = 0
        duplicate_count = 0
        network_used = False
        if clean_query and provider is None:
            errors.append({"code": "live_provider_not_configured", "message": PROVIDER_NOT_CONFIGURED_MESSAGE, "provider": self.provider_name})
        elif provider is not None:
            for variant in variants:
                attempted.append(variant)
                try:
                    page_payload = provider.search(
                        variant,
                        page=0,
                        count=max(1, min(int(count or 10), 20)),
                        freshness="",
                        country="",
                        language="",
                        safe_search="moderate",
                        budget_context=WebSearchBudget(max_provider_requests=1, timeout_seconds=timeout_seconds, max_retries=0),
                        query_variant=variant,
                    ).to_dict()
                    request_count += 1
                    network_used = True
                except WebSearchProviderError as exc:
                    errors.append(
                        {
                            "code": "live_provider_request_failed",
                            "message": str(exc),
                            "provider": exc.provider,
                            "query_variant": variant,
                            "status_code": exc.status_code,
                            "rate_limit": dict(exc.rate_limit),
                        }
                    )
                    continue
                self.lead_buffer.store_page(page_payload)
                raw_lead_count += int(page_payload.get("result_count") or 0)
                for card in live_display_cards(page_payload):
                    url = str(card.get("url") or "")
                    if not url:
                        continue
                    if url in seen_urls:
                        duplicate_count += 1
                        continue
                    seen_urls.add(url)
                    display_cards.append(card)
        summary = self._persistable_hunt_summary(
            run_id=run_id,
            query=clean_query,
            variants=variants,
            attempted=attempted,
            request_count=request_count,
            raw_lead_count=raw_lead_count,
            unique_lead_count=len(display_cards),
            duplicate_count=duplicate_count,
            max_fetches=max_fetches,
            errors=errors,
        )
        response = {
            **summary,
            "status": "fail" if errors and not display_cards else "pass",
            "unresolved_leads": display_cards,
            "results": display_cards,
            "result_count": len(display_cards),
            "network_provider_calls": network_used,
            "transient_lead_buffer_count": self.lead_buffer.active_count(),
            "review_required_for_display": False,
            "reviewed_master_mutation": False,
            "public_index_mutation": False,
        }
        return LiveHuntResult(response=response, persisted_summary=summary)

    def get_run(self, run_id: str, *, persisted_summary: Mapping[str, Any] | None = None) -> dict[str, Any]:
        if persisted_summary and str(persisted_summary.get("run_id") or "") == str(run_id or ""):
            return dict(persisted_summary)
        return {"schema_version": "eureka.live_hunt_run_lookup.v0", "status": "not_found", "run_id": str(run_id or "")}

    def cancel_run(self, run_id: str) -> dict[str, Any]:
        return {
            "schema_version": "eureka.live_hunt_cancel.v0",
            "status": "not_running",
            "run_id": str(run_id or ""),
            "message": "Live Hunt cancellation is reserved for the asynchronous Hunt engine milestone.",
        }

    def _search_provider_page(
        self,
        query: str,
        *,
        page: int,
        count: int,
        freshness: str,
        country: str,
        language: str,
        safe_search: str,
        timeout_seconds: int,
        query_variant: str | None = None,
    ) -> tuple[dict[str, Any] | None, dict[str, Any] | None, bool]:
        provider = self.provider_factory(self.provider_name)
        if provider is None:
            return None, {"code": "live_provider_not_configured", "message": PROVIDER_NOT_CONFIGURED_MESSAGE, "provider": self.provider_name}, False
        try:
            page_payload = provider.search(
                query,
                page=max(0, int(page or 0)),
                count=max(1, min(int(count or 10), 20)),
                freshness=freshness,
                country=country,
                language=language,
                safe_search=safe_search,
                budget_context=WebSearchBudget(max_provider_requests=1, timeout_seconds=timeout_seconds),
                query_variant=query_variant,
            ).to_dict()
        except WebSearchProviderError as exc:
            return (
                None,
                {
                    "code": "live_provider_request_failed",
                    "message": str(exc),
                    "provider": exc.provider,
                    "status_code": exc.status_code,
                    "rate_limit": dict(exc.rate_limit),
                },
                bool(exc.status_code),
            )
        return page_payload, None, True

    def _persistable_hunt_summary(
        self,
        *,
        run_id: str,
        query: str,
        variants: list[str],
        attempted: list[str],
        request_count: int,
        raw_lead_count: int,
        unique_lead_count: int,
        duplicate_count: int,
        max_fetches: int,
        errors: list[dict[str, Any]],
    ) -> dict[str, Any]:
        return {
            "schema_version": "eureka.live_hunt_run.v1",
            "run_id": run_id,
            "query": query,
            "mode": "live",
            "queries_planned": list(variants),
            "queries_attempted": list(attempted),
            "provider": self.provider_name,
            "providers_checked": [self.provider_name] if attempted else [],
            "request_count": int(request_count),
            "transient_lead_count": int(raw_lead_count),
            "unique_transient_lead_count": int(unique_lead_count),
            "new_unique_results": int(unique_lead_count),
            "duplicates_removed": max(0, int(raw_lead_count) - int(unique_lead_count)),
            "fetch_attempt_count": 0,
            "observation_refs": [],
            "pages_fetched": 0,
            "max_fetches": max(0, int(max_fetches or 0)),
            "blocked_fetches": 0,
            "errors": list(errors),
            "near_miss_count": 0,
            "unresolved_lead_count": int(unique_lead_count),
            "provider_results_persisted": False,
            "provider_result_payload_fields_persisted": [],
            "provider_raw_response_persisted": False,
            "provider_results_are_transient": True,
            "fetch_milestone_complete": False,
            "persistent_preview_index_update_complete": False,
        }


def live_display_cards(provider_page: Mapping[str, Any] | None) -> list[dict[str, Any]]:
    if not provider_page:
        return []
    cards: list[dict[str, Any]] = []
    for lead in provider_page.get("results") or []:
        if not isinstance(lead, Mapping):
            continue
        cards.append(
            {
                "state": "LIVE - UNREVIEWED",
                "title": str(lead.get("title") or lead.get("url") or "Live result"),
                "url": str(lead.get("url") or ""),
                "snippet": str(lead.get("snippet") or ""),
                "provider": str(lead.get("provider") or provider_page.get("provider") or ""),
                "provider_rank": int(lead.get("provider_rank") or 0),
                "retrieved_at": str(lead.get("retrieved_at") or provider_page.get("retrieved_at") or ""),
                "query": str(lead.get("query_variant") or lead.get("query") or provider_page.get("query") or ""),
                "source": "live_web_search",
                "lead_id": str(lead.get("lead_id") or ""),
                "retention_policy": dict(lead.get("retention_policy") or {}),
            }
        )
    return cards


def hunt_query_variants(query: str, *, max_queries: int) -> list[str]:
    clean = " ".join(str(query or "").split())
    terms = [term for term in re.split(r"[^A-Za-z0-9]+", clean) if len(term) > 2]
    variants = [clean]
    if " " in clean:
        variants.append(f'"{clean}"')
    if terms:
        variants.append(" ".join(terms[:4]))
    variants.extend([f"{clean} filetype:pdf", f"{clean} filetype:zip", f"{clean} site:archive.org"])
    unique: list[str] = []
    for item in variants:
        if item and item not in unique:
            unique.append(item)
    return unique[: max(1, min(int(max_queries or 1), 50))]


def live_hunt_run_id(query: str, started_at: str) -> str:
    return "live-hunt-" + hashlib.sha256(f"{query}\n{started_at}".encode("utf-8")).hexdigest()[:16]


def _search_status(
    result_cards: list[Mapping[str, Any]],
    *,
    live_error: Mapping[str, Any] | None,
    search_mode: str,
    query: str,
) -> str:
    if not query:
        return "pass"
    if live_error is None:
        return "pass"
    if result_cards and search_mode == "blended":
        return "pass_with_warnings"
    return "fail"


def _local_index_disabled() -> dict[str, Any]:
    return {"status": "disabled", "result_count": 0, "results": [], "warnings": []}


def _live_unavailable(provider_name: str, live_error: Mapping[str, Any] | None) -> dict[str, Any]:
    return {
        "provider": str(provider_name or "brave"),
        "status": "unavailable" if live_error else "not_requested",
        "result_count": 0,
        "results": [],
        "error": dict(live_error or {}),
        "raw_response_stored": False,
    }


def _clean_query(query: str) -> str:
    return " ".join(str(query or "").split())
