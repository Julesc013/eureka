"""Deterministic live Hunt engine for bounded local discovery."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import json
import tempfile
import time
from typing import Any, Callable, Mapping

from runtime.connectors.web import FetchRequest, SafeHTTPFetcher
from runtime.index.preview import SQLitePreviewIndexStore

from .live_web import PROVIDER_NOT_CONFIGURED_MESSAGE, WebSearchBudget, WebSearchProvider, WebSearchProviderError
from .providers import provider_from_environment


ProviderFactory = Callable[[str], WebSearchProvider | None]


@dataclass(frozen=True)
class HuntBudget:
    max_queries: int = 20
    max_provider_requests: int = 20
    max_pages: int = 2
    max_fetches: int = 10
    max_depth: int = 1
    max_links_followed: int = 10
    max_duration_seconds: int = 60
    count: int = 10
    timeout_seconds: int = 10

    def bounded(self) -> "HuntBudget":
        return HuntBudget(
            max_queries=max(1, min(int(self.max_queries or 20), 50)),
            max_provider_requests=max(1, min(int(self.max_provider_requests or 20), 100)),
            max_pages=max(1, min(int(self.max_pages or 1), 5)),
            max_fetches=max(0, min(int(self.max_fetches or 0), 100)),
            max_depth=max(0, min(int(self.max_depth or 1), 3)),
            max_links_followed=max(0, min(int(self.max_links_followed or 0), 100)),
            max_duration_seconds=max(1, min(int(self.max_duration_seconds or 60), 600)),
            count=max(1, min(int(self.count or 10), 20)),
            timeout_seconds=max(1, min(int(self.timeout_seconds or 10), 30)),
        )

    def to_dict(self) -> dict[str, int]:
        return {
            "max_queries": self.max_queries,
            "max_provider_requests": self.max_provider_requests,
            "max_pages": self.max_pages,
            "max_fetches": self.max_fetches,
            "max_depth": self.max_depth,
            "max_links_followed": self.max_links_followed,
            "max_duration_seconds": self.max_duration_seconds,
            "count": self.count,
            "timeout_seconds": self.timeout_seconds,
        }


@dataclass(frozen=True)
class HuntEngineResult:
    response: dict[str, Any]
    persisted_summary: dict[str, Any]
    events: tuple[dict[str, Any], ...]


class HuntRunStore:
    """Small local run-control/event store for deterministic Hunt runs."""

    def __init__(self, root: str | Path) -> None:
        self.root = Path(root)
        self.root.mkdir(parents=True, exist_ok=True)
        self.events_path = self.root / "events.jsonl"
        self.control_path = self.root / "control.json"
        self.summary_path = self.root / "summary.json"

    def write(self, summary: Mapping[str, Any], events: list[Mapping[str, Any]]) -> None:
        _atomic_write_json(self.summary_path, dict(summary))
        _atomic_write_text(self.events_path, "\n".join(json.dumps(dict(item), sort_keys=True) for item in events) + ("\n" if events else ""))

    def status(self) -> dict[str, Any]:
        control = _load_json_optional(self.control_path)
        summary = _load_json_optional(self.summary_path)
        return {
            "schema_version": "eureka.hunt_run_status.v0",
            "status": str(control.get("state") or summary.get("final_state") or "not_started"),
            "run_id": str(summary.get("run_id") or ""),
            "event_count": len(self.events()),
            "summary": summary,
        }

    def pause(self) -> dict[str, Any]:
        return self._set_state("paused")

    def resume(self) -> dict[str, Any]:
        return self._set_state("running")

    def cancel(self) -> dict[str, Any]:
        return self._set_state("cancelled")

    def events(self) -> list[dict[str, Any]]:
        if not self.events_path.exists():
            return []
        return [json.loads(line) for line in self.events_path.read_text(encoding="utf-8").splitlines() if line.strip()]

    def _set_state(self, state: str) -> dict[str, Any]:
        payload = {"schema_version": "eureka.hunt_run_control.v0", "state": state, "reviewed_master_mutation": False, "public_index_mutation": False}
        _atomic_write_json(self.control_path, payload)
        return payload


class HuntEngine:
    def __init__(
        self,
        *,
        provider_name: str = "brave",
        provider_factory: ProviderFactory = provider_from_environment,
        fetcher: SafeHTTPFetcher | None = None,
        index_store: SQLitePreviewIndexStore | None = None,
        clock: Callable[[], str] | None = None,
    ) -> None:
        self.provider_name = provider_name
        self.provider_factory = provider_factory
        self.fetcher = fetcher or SafeHTTPFetcher()
        self.index_store = index_store
        self.clock = clock or _utc_now

    def run(self, query: str, *, run_id: str, budget: HuntBudget) -> HuntEngineResult:
        budget = budget.bounded()
        started = time.monotonic()
        clean_query = " ".join(str(query or "").split())
        variants = _hunt_query_variants(clean_query, max_queries=budget.max_queries)
        provider = self.provider_factory(self.provider_name) if clean_query else None
        events: list[dict[str, Any]] = []
        errors: list[dict[str, Any]] = []
        display_cards: list[dict[str, Any]] = []
        fetch_frontier: list[dict[str, str]] = []
        seen_urls: set[str] = set()
        seen_content_hashes: set[str] = set()
        observation_refs: list[str] = []
        raw_lead_count = 0
        provider_request_count = 0
        provider_error_count = 0
        fetch_attempt_count = 0
        pages_fetched = 0
        documents_indexed = 0
        blocked_fetches = 0
        duplicates_removed = 0
        links_followed = 0

        _event(events, "hunt_started", run_id, query=clean_query, budget=budget.to_dict())
        if clean_query and provider is None:
            errors.append({"code": "live_provider_not_configured", "message": PROVIDER_NOT_CONFIGURED_MESSAGE, "provider": self.provider_name})
        elif provider is not None:
            for variant in variants:
                if provider_request_count >= budget.max_provider_requests or _expired(started, budget):
                    break
                _event(events, "query_planned", run_id, query_variant=variant)
                for page in range(budget.max_pages):
                    if provider_request_count >= budget.max_provider_requests or _expired(started, budget):
                        break
                    _event(events, "provider_request_started", run_id, provider=self.provider_name, query_variant=variant, page=page)
                    try:
                        page_payload = provider.search(
                            variant,
                            page=page,
                            count=budget.count,
                            freshness="",
                            country="",
                            language="",
                            safe_search="moderate",
                            budget_context=WebSearchBudget(max_provider_requests=1, timeout_seconds=budget.timeout_seconds, max_retries=0),
                            query_variant=variant,
                        ).to_dict()
                    except WebSearchProviderError as exc:
                        provider_error_count += 1
                        error = {"code": "live_provider_request_failed", "message": str(exc), "provider": exc.provider, "status_code": exc.status_code}
                        errors.append(error)
                        _event(events, "provider_request_failed", run_id, provider=exc.provider, query_variant=variant, page=page, status_code=exc.status_code)
                        break
                    provider_request_count += 1
                    raw_lead_count += int(page_payload.get("result_count") or 0)
                    leads = [lead for lead in page_payload.get("results") or [] if isinstance(lead, Mapping)]
                    _event(events, "provider_results_received", run_id, provider=self.provider_name, query_variant=variant, page=page, lead_count=len(leads))
                    for lead in leads:
                        url = str(lead.get("url") or "")
                        if not url:
                            continue
                        if url in seen_urls:
                            duplicates_removed += 1
                            _event(events, "duplicate_removed", run_id, reason="canonical_url")
                            continue
                        seen_urls.add(url)
                        card = _live_card(lead, page_payload)
                        display_cards.append(card)
                        if len(fetch_frontier) < budget.max_fetches:
                            fetch_frontier.append({"url": url, "query_variant": variant})
                            _event(events, "lead_selected", run_id, selection_index=len(fetch_frontier))
                    if not bool(page_payload.get("more_results_available")):
                        break

        for selected in list(fetch_frontier):
            if fetch_attempt_count >= budget.max_fetches or _expired(started, budget):
                break
            outcome = self._fetch_one(selected["url"], clean_query, run_id, events)
            fetch_attempt_count += 1
            if outcome.get("status") == "fetched" and isinstance(outcome.get("observation"), Mapping):
                observation = dict(outcome["observation"])
                content_hash = str(observation.get("content_hash") or "")
                if content_hash and content_hash in seen_content_hashes:
                    duplicates_removed += 1
                    _event(events, "duplicate_removed", run_id, reason="content_hash")
                    continue
                seen_content_hashes.add(content_hash)
                observation_refs.append(str(observation.get("observation_id") or ""))
                pages_fetched += 1
                if self.index_store is not None:
                    self.index_store.upsert_observations([observation])
                    documents_indexed += 1
                    _event(events, "document_indexed", run_id, observation_ref=str(observation.get("observation_id") or ""))
                for link in observation.get("outbound_links") or []:
                    if links_followed >= budget.max_links_followed or fetch_attempt_count >= budget.max_fetches or budget.max_depth <= 0:
                        break
                    if isinstance(link, Mapping):
                        target = str(link.get("target_url") or "")
                        if target and target not in seen_urls:
                            seen_urls.add(target)
                            links_followed += 1
                            _event(events, "frontier_expanded", run_id, link_count=1)
                            linked_outcome = self._fetch_one(target, clean_query, run_id, events)
                            fetch_attempt_count += 1
                            if linked_outcome.get("status") == "fetched" and isinstance(linked_outcome.get("observation"), Mapping):
                                linked_observation = dict(linked_outcome["observation"])
                                linked_hash = str(linked_observation.get("content_hash") or "")
                                if linked_hash and linked_hash in seen_content_hashes:
                                    duplicates_removed += 1
                                    _event(events, "duplicate_removed", run_id, reason="content_hash")
                                    continue
                                seen_content_hashes.add(linked_hash)
                                observation_refs.append(str(linked_observation.get("observation_id") or ""))
                                pages_fetched += 1
                                if self.index_store is not None:
                                    self.index_store.upsert_observations([linked_observation])
                                    documents_indexed += 1
                                    _event(events, "document_indexed", run_id, observation_ref=str(linked_observation.get("observation_id") or ""))
                            else:
                                blocked_fetches += 1
            else:
                blocked_fetches += 1
                if isinstance(outcome.get("error"), Mapping):
                    errors.append(dict(outcome["error"]))

        final_state = "completed" if not _expired(started, budget) else "budget_exhausted"
        _event(events, "hunt_completed" if final_state == "completed" else "budget_exhausted", run_id)
        summary = {
            "schema_version": "eureka.live_hunt_run.v2",
            "run_id": run_id,
            "query": clean_query,
            "mode": "live",
            "queries_planned": variants,
            "queries_attempted": variants[: min(len(variants), provider_request_count or len(variants))],
            "provider": self.provider_name,
            "providers_checked": [self.provider_name] if provider_request_count else [],
            "provider_request_count": provider_request_count,
            "provider_error_count": provider_error_count,
            "query_variant_count": len(variants),
            "transient_lead_count": raw_lead_count,
            "unique_transient_lead_count": len(display_cards),
            "duplicates_removed": max(0, raw_lead_count - len(display_cards)) + max(0, duplicates_removed - max(0, raw_lead_count - len(display_cards))),
            "fetch_attempt_count": fetch_attempt_count,
            "pages_fetched": pages_fetched,
            "observations_created": len(observation_refs),
            "documents_indexed": documents_indexed,
            "observation_refs": [ref for ref in observation_refs if ref],
            "blocked_fetches": blocked_fetches,
            "errors": _safe_errors(errors),
            "near_miss_count": 0,
            "unresolved_lead_count": max(0, len(display_cards) - fetch_attempt_count),
            "links_followed": links_followed,
            "budget": budget.to_dict(),
            "final_state": final_state,
            "provider_results_persisted": False,
            "provider_result_payload_fields_persisted": [],
            "provider_raw_response_persisted": False,
            "reviewed_master_mutation": False,
            "public_index_mutation": False,
        }
        response = {
            **summary,
            "schema_version": "eureka.live_hunt_response.v1",
            "status": "pass" if not errors or display_cards or observation_refs else "fail",
            "results": display_cards,
            "unresolved_leads": display_cards,
            "result_count": len(display_cards),
            "events": events[-25:],
            "review_required_for_display": False,
            "network_provider_calls": provider_request_count > 0,
        }
        return HuntEngineResult(response=response, persisted_summary=summary, events=tuple(events))

    def _fetch_one(self, url: str, query: str, run_id: str, events: list[dict[str, Any]]) -> dict[str, Any]:
        _event(events, "fetch_started", run_id)
        outcome = self.fetcher.fetch(FetchRequest(url, query=query, run_id=run_id))
        payload = outcome.to_dict()
        if outcome.status == "fetched" and outcome.observation is not None:
            _event(events, "fetch_completed", run_id, observation_ref=outcome.observation.observation_id)
            _event(events, "observation_created", run_id, observation_ref=outcome.observation.observation_id)
        elif outcome.status == "blocked":
            _event(events, "fetch_blocked", run_id, code=outcome.error.code if outcome.error else "")
        else:
            _event(events, "fetch_failed", run_id, code=outcome.error.code if outcome.error else "")
        return payload


def _hunt_query_variants(query: str, *, max_queries: int) -> list[str]:
    clean = " ".join(str(query or "").split())
    terms = [term for term in clean.replace('"', "").split() if len(term) > 2]
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


def _live_card(lead: Mapping[str, Any], page_payload: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "state": "LIVE - UNREVIEWED",
        "title": str(lead.get("title") or lead.get("url") or "Live result"),
        "url": str(lead.get("url") or ""),
        "snippet": str(lead.get("snippet") or ""),
        "provider": str(lead.get("provider") or page_payload.get("provider") or ""),
        "provider_rank": int(lead.get("provider_rank") or 0),
        "retrieved_at": str(lead.get("retrieved_at") or page_payload.get("retrieved_at") or ""),
        "query": str(lead.get("query_variant") or lead.get("query") or page_payload.get("query") or ""),
        "source": "live_web_search",
        "lead_id": str(lead.get("lead_id") or ""),
        "retention_policy": dict(lead.get("retention_policy") or {}),
    }


def _safe_errors(errors: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    safe = []
    for error in errors:
        safe.append({key: value for key, value in dict(error).items() if key not in {"url", "snippet", "provider_rank", "raw_response"}})
    return safe


def _event(events: list[dict[str, Any]], event_type: str, run_id: str, **fields: Any) -> None:
    events.append({"schema_version": "eureka.hunt_event.v0", "event_type": event_type, "run_id": run_id, **fields})


def _expired(started: float, budget: HuntBudget) -> bool:
    return time.monotonic() - started >= budget.max_duration_seconds


def _utc_now() -> str:
    return time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())


def _atomic_write_json(path: Path, payload: Mapping[str, Any]) -> None:
    _atomic_write_text(path, json.dumps(dict(payload), indent=2, sort_keys=True) + "\n")


def _atomic_write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="\n", dir=path.parent, delete=False) as handle:
        handle.write(text)
        temp = Path(handle.name)
    temp.replace(path)


def _load_json_optional(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
