"""Provider-neutral discovery planning, execution, and lead fusion."""

from __future__ import annotations

from dataclasses import dataclass
import re
import time
from typing import Any, Iterable, Mapping, Sequence
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from .live_web import SearchLead, SearchResultPage, WebSearchBudget, WebSearchProviderError
from .provider_health import ProviderHealthState, provider_health_check
from .providers import ProviderRegistry, provider_status


class DiscoveryIntentId:
    GENERAL_WEB = "general_web"
    ARCHIVE = "archive"
    HISTORICAL_SOFTWARE = "historical_software"
    MANUAL_OR_DOCUMENT = "manual_or_document"
    SOURCE_CODE = "source_code"
    PACKAGE = "package"
    ACADEMIC = "academic"
    URL_DIRECT = "url_direct"
    LOCAL_ONLY = "local_only"


@dataclass(frozen=True)
class DiscoveryIntent:
    intent_id: str
    query: str
    confidence: float
    reasons: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "intent_id": self.intent_id,
            "query": self.query,
            "confidence": self.confidence,
            "reasons": list(self.reasons),
        }


@dataclass(frozen=True)
class ProviderSelection:
    provider_id: str
    provider_kind: str
    health_state: str
    configured: bool
    retention_policy: Mapping[str, Any]
    run_policy: str
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider_id": self.provider_id,
            "provider_kind": self.provider_kind,
            "health_state": self.health_state,
            "configured": self.configured,
            "retention_policy": dict(self.retention_policy),
            "run_policy": self.run_policy,
            "reason": self.reason,
        }


@dataclass(frozen=True)
class DiscoveryStage:
    stage_id: str
    stage_type: str
    provider_selection: ProviderSelection
    request_budget: int
    timeout_seconds: int
    minimum_unique_yield: int
    maximum_cost_units: float
    stop_conditions: tuple[str, ...]

    @property
    def provider_id(self) -> str:
        return self.provider_selection.provider_id

    def to_dict(self) -> dict[str, Any]:
        return {
            "stage_id": self.stage_id,
            "stage_type": self.stage_type,
            "provider": self.provider_selection.to_dict(),
            "request_budget": self.request_budget,
            "timeout_seconds": self.timeout_seconds,
            "minimum_unique_yield": self.minimum_unique_yield,
            "maximum_cost_units": self.maximum_cost_units,
            "stop_conditions": list(self.stop_conditions),
        }


@dataclass(frozen=True)
class DiscoveryPlan:
    query: str
    intent: DiscoveryIntent
    stages: tuple[DiscoveryStage, ...]
    local_result_count: int = 0
    public_live_fanout: bool = False
    reviewed_truth_mutation: bool = False
    network_calls_performed: bool = False

    def provider_ids(self) -> tuple[str, ...]:
        return tuple(
            stage.provider_id
            for stage in self.stages
            if stage.provider_id not in {"local", "direct_fetch"} and stage.provider_selection.run_policy == "eligible"
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "eureka.discovery_plan.v1",
            "query": self.query,
            "intent": self.intent.to_dict(),
            "intent_id": self.intent.intent_id,
            "stages": [stage.to_dict() for stage in self.stages],
            "provider_ids": list(self.provider_ids()),
            "local_result_count": self.local_result_count,
            "public_live_fanout": self.public_live_fanout,
            "reviewed_truth_mutation": self.reviewed_truth_mutation,
            "network_calls_performed": self.network_calls_performed,
        }


@dataclass(frozen=True)
class DiscoveryCost:
    request_count: int = 0
    estimated_monetary_cost: float = 0.0
    latency_ms: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "request_count": self.request_count,
            "estimated_monetary_cost": self.estimated_monetary_cost,
            "latency_ms": self.latency_ms,
        }


@dataclass(frozen=True)
class DiscoveryYield:
    lead_count: int = 0
    unique_lead_count: int = 0
    fetchable_count: int = 0
    successful_fetch_count: int = 0
    new_source_observation_count: int = 0
    new_preview_document_count: int = 0
    duplicate_count: int = 0
    policy_block_count: int = 0
    error_count: int = 0

    def to_dict(self) -> dict[str, int]:
        return {
            "lead_count": self.lead_count,
            "unique_lead_count": self.unique_lead_count,
            "fetchable_count": self.fetchable_count,
            "successful_fetch_count": self.successful_fetch_count,
            "new_source_observation_count": self.new_source_observation_count,
            "new_preview_document_count": self.new_preview_document_count,
            "duplicate_count": self.duplicate_count,
            "policy_block_count": self.policy_block_count,
            "error_count": self.error_count,
        }


@dataclass(frozen=True)
class LeadEnvelope:
    lead_id: str
    title: str
    url: str
    snippet: str
    provider_id: str
    upstream_provider_ids: tuple[str, ...]
    provider_rank: int
    retrieved_at: str
    query: str
    query_variant: str
    retention_policy: Mapping[str, Any]
    display_allowed: bool
    cache_ttl_seconds: int
    persist_url: bool
    persist_title: bool
    persist_snippet: bool
    persist_rank: bool
    redistribute: bool
    independent_fetch_allowed: bool

    @classmethod
    def from_lead(cls, lead: Mapping[str, Any], *, provider_id: str = "") -> "LeadEnvelope":
        retention = dict(lead.get("retention_policy") or {})
        provider = str(lead.get("provider") or provider_id)
        return cls(
            lead_id=str(lead.get("lead_id") or ""),
            title=str(lead.get("title") or lead.get("url") or ""),
            url=str(lead.get("url") or ""),
            snippet=str(lead.get("snippet") or ""),
            provider_id=provider,
            upstream_provider_ids=tuple(str(item) for item in lead.get("upstream_provider_ids") or (provider,) if str(item)),
            provider_rank=int(lead.get("provider_rank") or 0),
            retrieved_at=str(lead.get("retrieved_at") or ""),
            query=str(lead.get("query") or ""),
            query_variant=str(lead.get("query_variant") or lead.get("query") or ""),
            retention_policy=retention,
            display_allowed=bool(retention.get("display_results", True)),
            cache_ttl_seconds=int(retention.get("transient_cache_ttl_seconds") or 0),
            persist_url=bool(retention.get("persist_urls")),
            persist_title=bool(retention.get("persist_title") or retention.get("persist_urls")),
            persist_snippet=bool(retention.get("persist_snippets")),
            persist_rank=bool(retention.get("persist_rank")),
            redistribute=bool(retention.get("redistribute")),
            independent_fetch_allowed=True,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "lead_id": self.lead_id,
            "title": self.title,
            "url": self.url,
            "snippet": self.snippet,
            "provider_id": self.provider_id,
            "upstream_provider_ids": list(self.upstream_provider_ids),
            "provider_rank": self.provider_rank,
            "retrieved_at": self.retrieved_at,
            "query": self.query,
            "query_variant": self.query_variant,
            "retention_policy": dict(self.retention_policy),
            "display_allowed": self.display_allowed,
            "cache_ttl_seconds": self.cache_ttl_seconds,
            "persist_url": self.persist_url,
            "persist_title": self.persist_title,
            "persist_snippet": self.persist_snippet,
            "persist_rank": self.persist_rank,
            "redistribute": self.redistribute,
            "independent_fetch_allowed": self.independent_fetch_allowed,
        }


@dataclass(frozen=True)
class ProviderExecutionResult:
    provider_id: str
    status: str
    request_count: int
    cost: DiscoveryCost
    page: Mapping[str, Any]
    leads: tuple[LeadEnvelope, ...]
    errors: tuple[dict[str, Any], ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider_id": self.provider_id,
            "status": self.status,
            "request_count": self.request_count,
            "cost": self.cost.to_dict(),
            "lead_count": len(self.leads),
            "errors": [dict(error) for error in self.errors],
            "provider_payload_persisted": False,
            "raw_response_stored": False,
        }


@dataclass(frozen=True)
class ProviderOutcome:
    provider_id: str
    health_state: str
    cost: DiscoveryCost
    yield_: DiscoveryYield
    errors: tuple[dict[str, Any], ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider_id": self.provider_id,
            "health_state": self.health_state,
            "cost": self.cost.to_dict(),
            "yield": self.yield_.to_dict(),
            "errors": [dict(error) for error in self.errors],
        }


@dataclass(frozen=True)
class LeadFusionResult:
    leads: tuple[LeadEnvelope, ...]
    duplicate_count: int
    provider_ids: tuple[str, ...]
    conflicting_metadata: tuple[dict[str, Any], ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "eureka.lead_fusion_result.v0",
            "lead_count": sum(1 for _lead in self.leads) + self.duplicate_count,
            "unique_lead_count": len(self.leads),
            "duplicate_count": self.duplicate_count,
            "provider_ids": list(self.provider_ids),
            "conflicting_metadata": [dict(item) for item in self.conflicting_metadata],
            "leads": [lead.to_dict() for lead in self.leads],
            "provider_payload_persisted": False,
        }


@dataclass(frozen=True)
class DiscoveryResult:
    plan: DiscoveryPlan
    execution_results: tuple[ProviderExecutionResult, ...]
    fusion: LeadFusionResult
    provider_outcomes: tuple[ProviderOutcome, ...]
    stopped_reason: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "eureka.discovery_result.v1",
            "status": "pass" if self.fusion.leads or not self.execution_results else "pass_with_warnings",
            "query": self.plan.query,
            "intent_id": self.plan.intent.intent_id,
            "stopped_reason": self.stopped_reason,
            "plan": self.plan.to_dict(),
            "provider_results": [result.to_dict() for result in self.execution_results],
            "fusion": self.fusion.to_dict(),
            "provider_outcomes": [outcome.to_dict() for outcome in self.provider_outcomes],
            "reviewed_master_mutation": False,
            "public_index_mutation": False,
            "provider_result_payload_persisted": False,
        }


@dataclass(frozen=True)
class ProviderBudgetLedger:
    max_provider_requests: int = 3
    count: int = 10
    timeout_seconds: int = 10
    minimum_unique_yield: int = 1

    def bounded(self) -> "ProviderBudgetLedger":
        return ProviderBudgetLedger(
            max_provider_requests=max(0, min(int(self.max_provider_requests or 3), 25)),
            count=max(1, min(int(self.count or 10), 20)),
            timeout_seconds=max(1, min(int(self.timeout_seconds or 10), 30)),
            minimum_unique_yield=max(0, min(int(self.minimum_unique_yield or 1), 50)),
        )


class LeadFusionService:
    def fuse(self, leads: Iterable[LeadEnvelope]) -> LeadFusionResult:
        by_url: dict[str, LeadEnvelope] = {}
        provider_ids: set[str] = set()
        conflicts: list[dict[str, Any]] = []
        duplicate_count = 0
        for lead in leads:
            provider_ids.add(lead.provider_id)
            key = canonical_url_key(lead.url) or lead.lead_id
            if key not in by_url:
                by_url[key] = lead
                continue
            duplicate_count += 1
            current = by_url[key]
            if current.title != lead.title or current.snippet != lead.snippet:
                conflicts.append(
                    {
                        "url_key": key,
                        "providers": sorted({current.provider_id, lead.provider_id}),
                        "fields": _metadata_conflict_fields(current, lead),
                    }
                )
        ranked = sorted(by_url.values(), key=lambda item: (_provider_rank_sort(item), item.provider_rank or 999999, item.url))
        return LeadFusionResult(tuple(ranked), duplicate_count, tuple(sorted(provider_ids)), tuple(conflicts))


class DiscoveryBroker:
    """Plan and run bounded provider discovery without owning fetch/index/review logic."""

    def __init__(self, *, registry: ProviderRegistry | None = None, env: Mapping[str, str] | None = None) -> None:
        self.registry = registry or ProviderRegistry(env=env)
        self.env = env
        self.fusion = LeadFusionService()

    def plan(
        self,
        query: str,
        context: Mapping[str, Any] | None = None,
        *,
        requested_provider: str = "auto",
        local_result_count: int = 0,
    ) -> DiscoveryPlan:
        clean_query = _clean_query(query)
        context_payload = dict(context or {})
        local_count = int(context_payload.get("local_result_count", local_result_count) or 0)
        intent = classify_discovery_intent(clean_query, context_payload)
        stages = [
            DiscoveryStage(
                stage_id="stage:local",
                stage_type="local_index",
                provider_selection=ProviderSelection(
                    provider_id="local",
                    provider_kind="local_index",
                    health_state=ProviderHealthState.HEALTHY,
                    configured=True,
                    retention_policy={"persist_urls": True, "persist_snippets": True, "persist_rank": True},
                    run_policy="eligible",
                    reason="Local indexes are free, durable, and fastest.",
                ),
                request_budget=0,
                timeout_seconds=0,
                minimum_unique_yield=1,
                maximum_cost_units=0.0,
                stop_conditions=("stop_when_local_results_sufficient",),
            )
        ]
        if local_count > 0 and str(requested_provider or "auto").casefold() == "auto":
            return DiscoveryPlan(clean_query, intent, tuple(stages), local_result_count=local_count)
        for provider_id, stage_type, reason, min_yield, cost_units in self._provider_order(intent.intent_id, requested_provider):
            stages.append(
                DiscoveryStage(
                    stage_id=f"stage:{provider_id}",
                    stage_type=stage_type,
                    provider_selection=self._provider_selection(provider_id, reason),
                    request_budget=1,
                    timeout_seconds=10,
                    minimum_unique_yield=min_yield,
                    maximum_cost_units=cost_units,
                    stop_conditions=("stop_when_minimum_unique_yield_met", "stop_on_budget_exhausted"),
                )
            )
        return DiscoveryPlan(clean_query, intent, tuple(stages), local_result_count=local_count)

    def execute(self, plan: DiscoveryPlan, budget: ProviderBudgetLedger | Mapping[str, Any] | None = None) -> DiscoveryResult:
        ledger = _budget_from_any(budget).bounded()
        execution_results: list[ProviderExecutionResult] = []
        all_leads: list[LeadEnvelope] = []
        provider_outcomes: list[ProviderOutcome] = []
        request_count = 0
        stopped_reason = "exhausted_plan"
        for stage in plan.stages:
            if stage.provider_id in {"local", "direct_fetch"}:
                continue
            if stage.provider_selection.run_policy != "eligible":
                provider_outcomes.append(
                    ProviderOutcome(
                        stage.provider_id,
                        stage.provider_selection.health_state,
                        DiscoveryCost(),
                        DiscoveryYield(policy_block_count=1),
                        ({"code": stage.provider_selection.run_policy, "provider": stage.provider_id},),
                    )
                )
                continue
            if request_count >= ledger.max_provider_requests:
                stopped_reason = "provider_request_budget_exhausted"
                break
            result = self._execute_provider_stage(plan.query, stage, ledger)
            request_count += result.request_count
            execution_results.append(result)
            all_leads.extend(result.leads)
            fusion_so_far = self.fusion.fuse(all_leads)
            provider_outcomes.append(_provider_outcome_from_result(stage, result, fusion_so_far))
            if len(fusion_so_far.leads) >= max(stage.minimum_unique_yield, ledger.minimum_unique_yield):
                stopped_reason = "minimum_unique_yield_met"
                break
        fusion = self.fusion.fuse(all_leads)
        return DiscoveryResult(plan, tuple(execution_results), fusion, tuple(provider_outcomes), stopped_reason)

    def check_providers(self, provider_ids: Sequence[str] | str = ("auto",), *, live: bool = False) -> list[dict[str, Any]]:
        ids = self._provider_ids_for_check(provider_ids)
        health: list[dict[str, Any]] = []
        for provider_id in ids:
            item = provider_health_check(provider_id, env=self.env, live_check=live)
            status = provider_status(provider_id, env=self.env)
            manifest = _manifest_for(provider_id, status)
            item["provider_kind"] = str(manifest.get("provider_kind") or "")
            item["approved_broad_web_provider"] = str(manifest.get("provider_kind") or "") == "broad_web_search"
            item["retention_policy"] = dict(_retention_from_manifest(manifest))
            item["credential_env_keys"] = list(status.get("credential_env_keys") or [])
            health.append(item)
        return health

    def _provider_order(self, intent_id: str, requested_provider: str) -> tuple[tuple[str, str, str, int, float], ...]:
        requested = str(requested_provider or "auto").strip().casefold()
        if requested not in {"auto", "multi", "blended"}:
            provider_id = "internet_archive_metadata" if requested == "ia" else requested
            return ((provider_id, "explicit_provider", "Explicit provider request.", 1, _provider_cost_units(provider_id)),)
        if intent_id == DiscoveryIntentId.URL_DIRECT:
            return (("direct_fetch", "direct_fetch", "URL-like input should go to safe fetch before providers.", 1, 0.0),)
        if intent_id in {DiscoveryIntentId.ARCHIVE, DiscoveryIntentId.HISTORICAL_SOFTWARE, DiscoveryIntentId.MANUAL_OR_DOCUMENT}:
            return (
                ("internet_archive_metadata", "vertical_provider", "Archive/manual query: try Internet Archive metadata before broad web.", 1, 0.0),
                ("brave", "broad_web_provider", "Escalate to broad web if vertical yield is insufficient.", 1, _provider_cost_units("brave")),
            )
        return (("brave", "broad_web_provider", "General query: use an approved broad-web provider after local search.", 1, _provider_cost_units("brave")),)

    def _provider_selection(self, provider_id: str, reason: str) -> ProviderSelection:
        if provider_id == "direct_fetch":
            return ProviderSelection("direct_fetch", "safe_fetch", ProviderHealthState.HEALTHY, True, {}, "eligible", reason)
        status = provider_status(provider_id, env=self.env)
        manifest = _manifest_for(provider_id, status)
        health_state = _unchecked_state(status)
        return ProviderSelection(
            provider_id=provider_id,
            provider_kind=str(manifest.get("provider_kind") or provider_id),
            health_state=health_state,
            configured=bool(status.get("configured")),
            retention_policy=_retention_from_manifest(manifest),
            run_policy=_run_policy(status),
            reason=reason,
        )

    def _execute_provider_stage(self, query: str, stage: DiscoveryStage, budget: ProviderBudgetLedger) -> ProviderExecutionResult:
        provider_id = stage.provider_id
        start = time.monotonic()
        provider = self.registry.provider(provider_id)
        if provider is None:
            error = {"code": "provider_not_configured", "provider": provider_id}
            return ProviderExecutionResult(provider_id, "not_configured", 0, DiscoveryCost(), {}, (), (error,))
        try:
            page = provider.search(
                query,
                page=0,
                count=budget.count,
                freshness="",
                country="",
                language="",
                safe_search="moderate",
                budget_context=WebSearchBudget(max_provider_requests=1, timeout_seconds=min(stage.timeout_seconds or budget.timeout_seconds, budget.timeout_seconds), max_retries=0),
            )
        except WebSearchProviderError as exc:
            cost = DiscoveryCost(request_count=1 if exc.status_code else 0, estimated_monetary_cost=_provider_cost_units(provider_id), latency_ms=_elapsed_ms(start))
            error = {"code": "provider_error", "provider": exc.provider, "status_code": exc.status_code, "health_state": _state_from_status_code(exc.status_code)}
            return ProviderExecutionResult(provider_id, "fail", cost.request_count, cost, {}, (), (error,))
        payload = page.to_dict()
        leads = tuple(LeadEnvelope.from_lead(lead, provider_id=provider_id) for lead in payload.get("results") or [] if isinstance(lead, Mapping))
        cost = DiscoveryCost(request_count=1, estimated_monetary_cost=_provider_cost_units(provider_id), latency_ms=_elapsed_ms(start))
        return ProviderExecutionResult(provider_id, "pass", 1, cost, _safe_page_payload(payload), leads)

    def _provider_ids_for_check(self, provider_ids: Sequence[str] | str) -> tuple[str, ...]:
        if isinstance(provider_ids, str):
            requested = tuple(item.strip() for item in provider_ids.split(",") if item.strip()) or ("auto",)
        else:
            requested = tuple(str(item).strip() for item in provider_ids if str(item).strip()) or ("auto",)
        if "auto" not in requested:
            return tuple("internet_archive_metadata" if item == "ia" else item for item in requested)
        ids = []
        for provider_id in ("brave", "mojeek", "internet_archive_metadata"):
            status = provider_status(provider_id, env=self.env)
            if _run_policy(status) != "blocked_by_policy":
                ids.append(provider_id)
        return tuple(ids)


def classify_query_intent(query: str) -> str:
    return classify_discovery_intent(query).intent_id


def classify_discovery_intent(query: str, context: Mapping[str, Any] | None = None) -> DiscoveryIntent:
    clean = _clean_query(query)
    normalized = clean.casefold()
    if bool((context or {}).get("local_only")):
        return DiscoveryIntent(DiscoveryIntentId.LOCAL_ONLY, clean, 1.0, ("context_local_only",))
    if re.search(r"https?://", normalized):
        return DiscoveryIntent(DiscoveryIntentId.URL_DIRECT, clean, 0.98, ("url_like_input",))
    if any(term in normalized for term in ("crossref", "openalex", "doi:", "paper", "journal", "academic")):
        return DiscoveryIntent(DiscoveryIntentId.ACADEMIC, clean, 0.78, ("academic_terms",))
    if any(term in normalized for term in ("npm", "pypi", "nuget", "maven", "crate", "package registry")):
        return DiscoveryIntent(DiscoveryIntentId.PACKAGE, clean, 0.86, ("package_terms",))
    if any(term in normalized for term in ("github", "source code", "github release", "software heritage")):
        return DiscoveryIntent(DiscoveryIntentId.SOURCE_CODE, clean, 0.84, ("source_code_terms",))
    if any(term in normalized for term in ("manual", "datasheet", "pdf", "document", "specification")):
        return DiscoveryIntent(DiscoveryIntentId.MANUAL_OR_DOCUMENT, clean, 0.82, ("manual_document_terms",))
    if any(term in normalized for term in ("driver", "old", "ftp", "sound blaster", "win98", "windows xp", "historical software")):
        return DiscoveryIntent(DiscoveryIntentId.HISTORICAL_SOFTWARE, clean, 0.86, ("historical_software_terms",))
    if any(term in normalized for term in ("archive", "wayback", "scan", "magazine", "historical")):
        return DiscoveryIntent(DiscoveryIntentId.ARCHIVE, clean, 0.8, ("archive_terms",))
    return DiscoveryIntent(DiscoveryIntentId.GENERAL_WEB, clean, 0.65, ("default_general_web",))


def canonical_url_key(url: str) -> str:
    parsed = urlparse(str(url or "").strip())
    if not parsed.netloc:
        return ""
    query = urlencode(sorted((key, value) for key, value in parse_qsl(parsed.query, keep_blank_values=True) if not key.lower().startswith("utm_")))
    path = parsed.path.rstrip("/") or "/"
    return urlunparse((parsed.scheme.casefold() or "https", parsed.netloc.casefold(), path, "", query, ""))


def _budget_from_any(payload: ProviderBudgetLedger | Mapping[str, Any] | None) -> ProviderBudgetLedger:
    if isinstance(payload, ProviderBudgetLedger):
        return payload
    source = dict(payload or {})
    return ProviderBudgetLedger(
        max_provider_requests=int(source.get("max_provider_requests") or 3),
        count=int(source.get("count") or 10),
        timeout_seconds=int(source.get("timeout_seconds") or 10),
        minimum_unique_yield=int(source.get("minimum_unique_yield") or 1),
    )


def _manifest_for(provider_id: str, status: Mapping[str, Any]) -> Mapping[str, Any]:
    manifest = status.get("capability_manifest") or {}
    if isinstance(manifest, Mapping) and provider_id in manifest and isinstance(manifest[provider_id], Mapping):
        return dict(manifest[provider_id])
    return dict(manifest) if isinstance(manifest, Mapping) else {}


def _retention_from_manifest(manifest: Mapping[str, Any]) -> Mapping[str, Any]:
    retention = manifest.get("retention_policy") if isinstance(manifest.get("retention_policy"), Mapping) else None
    if retention is not None:
        return dict(retention)
    return {
        "display_results": bool(manifest.get("display_results", True)),
        "transient_cache_ttl_seconds": int(manifest.get("transient_cache_ttl_seconds") or 0),
        "persist_urls": bool(manifest.get("persist_urls")),
        "persist_snippets": bool(manifest.get("persist_snippets")),
        "persist_rank": bool(manifest.get("persist_rank")),
        "redistribute": bool(manifest.get("redistribute")),
    }


def _run_policy(status: Mapping[str, Any]) -> str:
    if status.get("error"):
        error_text = str(status.get("error") or "").casefold()
        return "disabled_by_policy" if "disabled" in error_text or "deprecated" in error_text else "blocked_by_policy"
    if not status.get("configured"):
        return "needs_configuration"
    return "eligible"


def _unchecked_state(status: Mapping[str, Any]) -> str:
    policy = _run_policy(status)
    if policy in {"blocked_by_policy", "disabled_by_policy"}:
        return ProviderHealthState.DISABLED_BY_POLICY
    if policy == "needs_configuration":
        return ProviderHealthState.NOT_CONFIGURED
    return ProviderHealthState.CONFIGURED_UNCHECKED


def _state_from_status_code(status_code: int) -> str:
    if status_code == 401:
        return ProviderHealthState.AUTHENTICATION_FAILED
    if status_code == 403:
        return ProviderHealthState.PERMISSION_FAILED
    if status_code == 402:
        return ProviderHealthState.QUOTA_EXHAUSTED
    if status_code == 429:
        return ProviderHealthState.RATE_LIMITED
    if status_code == 408:
        return ProviderHealthState.TIMEOUT
    return ProviderHealthState.DEGRADED


def _provider_outcome_from_result(stage: DiscoveryStage, result: ProviderExecutionResult, fusion: LeadFusionResult) -> ProviderOutcome:
    errors = tuple(dict(error) for error in result.errors)
    return ProviderOutcome(
        provider_id=result.provider_id,
        health_state=stage.provider_selection.health_state if not errors else str(errors[0].get("health_state") or ProviderHealthState.DEGRADED),
        cost=result.cost,
        yield_=DiscoveryYield(
            lead_count=len(result.leads),
            unique_lead_count=len(fusion.leads),
            fetchable_count=sum(1 for lead in result.leads if lead.independent_fetch_allowed),
            duplicate_count=fusion.duplicate_count,
            error_count=len(errors),
        ),
        errors=errors,
    )


def _safe_page_payload(payload: Mapping[str, Any]) -> Mapping[str, Any]:
    return {
        "provider": str(payload.get("provider") or ""),
        "query": str(payload.get("query") or ""),
        "query_variant": str(payload.get("query_variant") or ""),
        "page": int(payload.get("page") or 0),
        "count": int(payload.get("count") or 0),
        "result_count": int(payload.get("result_count") or 0),
        "more_results_available": bool(payload.get("more_results_available")),
        "raw_response_stored": False,
    }


def _provider_rank_sort(lead: LeadEnvelope) -> int:
    if lead.provider_id == "internet_archive_metadata":
        return 0
    if lead.provider_id == "brave":
        return 1
    if lead.provider_id == "mojeek":
        return 2
    return 10


def _metadata_conflict_fields(left: LeadEnvelope, right: LeadEnvelope) -> list[str]:
    fields = []
    if left.title != right.title:
        fields.append("title")
    if left.snippet != right.snippet:
        fields.append("snippet")
    return fields


def _provider_cost_units(provider_id: str) -> float:
    if provider_id == "brave":
        return 0.005
    if provider_id == "mojeek":
        return 0.0025
    return 0.0


def _elapsed_ms(start: float) -> int:
    return max(0, int((time.monotonic() - start) * 1000))


def _clean_query(query: str) -> str:
    return " ".join(str(query or "").split())[:256]
