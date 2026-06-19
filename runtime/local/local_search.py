"""Local search service over existing resolution and surface primitives."""

from __future__ import annotations

from dataclasses import dataclass
from html import escape
import json
from pathlib import Path
import tempfile
from typing import Any, Callable, Mapping, Protocol, Sequence
from urllib.parse import quote_plus

from evals.hard_queries import fixture_cases, resolution_run_for_fixture
from evals.hard_queries.metadata_fallback_smoke.ia_00.loader import load_fixture_payload
from runtime.connectors.github_releases import GitHubReleasesConnector
from runtime.connectors.synthetic_software import SyntheticSoftwareConnector
from runtime.engine.absence import DeterministicAbsenceService
from runtime.engine.core import NormalizedCatalog
from runtime.engine.interfaces.extract import (
    extract_github_release_source_record,
    extract_synthetic_source_record,
)
from runtime.engine.interfaces.normalize import (
    normalize_extracted_record,
    normalize_github_release_record,
)
from runtime.engine.interfaces.public import DeterministicSearchRunRequest, ResolutionRunRecord
from runtime.engine.resolve import DeterministicSearchService, ExactMatchResolutionService
from runtime.engine.resolution_runs import (
    LocalResolutionRunService,
    LocalResolutionRunStore,
    ResolutionRunFallbackPolicy,
)
from runtime.local.search_index import (
    DEFAULT_INDEX_PATH,
    SUPPORTED_INDEX_MODES,
    IndexSearchState,
    document_to_result_card,
    index_file_status,
    search_index_path,
)
from runtime.source.observation.archive_org_public_metadata import ArchiveOrgMetadataCandidateProvider
from runtime.source.registry import load_source_registry
from runtime.surface import SurfaceKernel, SurfaceRequest


SCHEMA_VERSION = "eureka.local_search_response.v0"
TASK_ID = "REVIEWED-RECORD-MATERIALIZATION-00"
DATA_VERSION = "reviewed-record-materialization-v0"
REPO_ROOT = Path(__file__).resolve().parents[2]
DEMO_FIXTURE_PATH = REPO_ROOT / "evals" / "hard_queries" / "local_metadata_fallback_demo" / "ia_metadata_fixtures.json"
SUPPORTED_METADATA_FALLBACKS = ("none", "ia_fixture", "ia_live")
DEFAULT_METADATA_TIMEOUT_SECONDS = 5
DEFAULT_METADATA_BUDGET = 1
CANONICAL_STATUSES = (
    "verified",
    "candidate",
    "need",
    "near_miss",
    "policy_blocked",
    "unavailable",
    "unknown",
)
HARD_QUERY_SMOKE_SET = (
    "old blue FTP client for XP",
    "manual for Sound Blaster CT1740",
    "driver for Win98",
    "Windows 7 apps",
    "latest Firefox before XP support ended",
    "article about ray tracing in a 1994 magazine",
)
STATUS_CONCEPTS = {
    "hq_windows_7_apps": "candidate",
    "hq_driver_win98": "blocked_for_user_details",
    "hq_blue_ftp_client_xp": "near_miss",
    "hq_sound_blaster_ct1740_manual": "candidate",
    "hq_firefox_last_xp": "policy_blocked",
    "hq_ray_tracing_1994_magazine": "unavailable",
}


@dataclass(frozen=True)
class LocalSearchOptions:
    metadata_fallback: str = "none"
    limit: int = 10
    show_evidence: bool = False
    show_debug: bool = False
    allow_live_metadata: bool = False
    metadata_timeout_seconds: int = DEFAULT_METADATA_TIMEOUT_SECONDS
    metadata_budget: int = DEFAULT_METADATA_BUDGET
    index: str = "none"
    index_path: str = DEFAULT_INDEX_PATH


class MetadataFallbackProvider(Protocol):
    source_id: str
    source_family: str

    def search_metadata_candidates(self, query: str, limit: int) -> Mapping[str, Any]:
        """Return metadata-only fallback candidates for a local search miss."""


class LocalSearchService:
    """Thin product-facing adapter for local fixture/search/surface behavior."""

    def __init__(
        self,
        *,
        live_provider_factory: Callable[[LocalSearchOptions], MetadataFallbackProvider] | None = None,
    ) -> None:
        self._surface = SurfaceKernel()
        self._fixture_payload = _load_ia_fixture_payload()
        self._live_provider_factory = live_provider_factory
        self._live_provider_cache: dict[tuple[int, int], MetadataFallbackProvider] = {}

    def search(self, query: str, options: LocalSearchOptions | None = None) -> dict[str, Any]:
        opts = _normalize_options(options)
        normalized_query = _normalize_query(query)
        if not normalized_query:
            return _empty_query_response(opts)

        index_state = _search_index_state(opts, normalized_query)
        hard_fixture = _hard_fixture_for_query(normalized_query)
        ia_fixture_case = _ia_fixture_case_for_query(normalized_query, self._fixture_payload)
        provider_call_count = 0
        source_path = "local_resolution_run"
        if opts.metadata_fallback == "ia_live" and not opts.allow_live_metadata:
            return _blocked_live_metadata_response(normalized_query, opts)
        if opts.index == "local" and index_state.loaded and index_state.results:
            return _response_from_index(
                query=normalized_query,
                options=opts,
                index_state=index_state,
            )
        if opts.index == "local" and opts.metadata_fallback == "none":
            return _index_miss_response(
                query=normalized_query,
                options=opts,
                index_state=index_state,
            )
        if opts.metadata_fallback == "ia_live":
            provider = self._live_provider(opts)
            run = self._run_resolution_search(normalized_query, opts, provider)
            provider_call_count = _provider_call_count(provider)
            source_path = "ia_live_metadata_fallback"
            status_concept = _status_concept_from_fallback(run.fallback_summary)
        elif opts.metadata_fallback == "ia_fixture" and ia_fixture_case is not None:
            provider = IAFixtureMetadataProvider(self._fixture_payload)
            run = self._run_resolution_search(normalized_query, opts, provider)
            provider_call_count = _provider_call_count(provider)
            source_path = "ia_fixture_metadata_fallback"
            status_concept = _status_concept_from_fallback(run.fallback_summary)
        elif hard_fixture is not None:
            run = resolution_run_for_fixture(hard_fixture)
            source_path = "hard_query_fixture"
            status_concept = STATUS_CONCEPTS.get(str(hard_fixture.get("query_id")), str(hard_fixture.get("expected_status", "unknown")))
        else:
            provider = IAFixtureMetadataProvider(self._fixture_payload) if opts.metadata_fallback == "ia_fixture" else None
            run = self._run_resolution_search(normalized_query, opts, provider)
            provider_call_count = _provider_call_count(provider)
            source_path = "ia_fixture_metadata_fallback" if provider is not None else "local_resolution_run"
            status_concept = _status_concept_from_fallback(run.fallback_summary)

        projections = self._project_run(run, include_debug=opts.show_debug)
        primary_projection = projections["json_v0"]
        view_model = primary_projection["view_model"]
        response = _response_from_projection(
            query=normalized_query,
            options=opts,
            run=run,
            source_path=source_path,
            status_concept=status_concept,
            provider_call_count=provider_call_count,
            view_model=view_model,
            projections=projections,
            index_state=index_state,
        )
        return response

    def search_many(self, queries: Sequence[str], options: LocalSearchOptions | None = None) -> dict[str, Any]:
        opts = _normalize_options(options)
        responses = [self.search(query, opts) for query in queries]
        return {
            "schema_version": "eureka.local_search_batch_response.v0",
            "task_id": TASK_ID,
            "metadata_fallback": opts.metadata_fallback,
            "fallback_mode": _fallback_mode(opts.metadata_fallback, "batch"),
            "fallback_used": any(bool(response.get("fallback_used")) for response in responses),
            "provider_family": _batch_provider_family(opts.metadata_fallback),
            "index_mode": opts.index,
            "index_enabled": opts.index == "local",
            "index_loaded": any(bool(response.get("index_loaded")) for response in responses),
            "index_path": opts.index_path,
            "index_document_count": max((int(response.get("index_document_count") or 0) for response in responses), default=0),
            "reviewed_record_count": max((int(response.get("reviewed_record_count") or 0) for response in responses), default=0),
            "artifact_verified_count": max((int(response.get("artifact_verified_count") or 0) for response in responses), default=0),
            "index_results_used": any(bool(response.get("index_results_used")) for response in responses),
            "index_result_count": sum(int(response.get("index_result_count") or 0) for response in responses),
            "live_metadata_enabled": opts.metadata_fallback == "ia_live" and opts.allow_live_metadata,
            "network_default": False,
            "network_used": any(bool(response.get("network_used")) for response in responses),
            "timeout_seconds": opts.metadata_timeout_seconds,
            "budget": {"max_requests": opts.metadata_budget, "candidate_limit": opts.limit},
            "budget_used": sum(int(response.get("budget_used") or 0) for response in responses),
            "public_live_fanout": False,
            "limit": opts.limit,
            "query_count": len(responses),
            "status_summary": _aggregate_status_summary(responses),
            "queries": responses,
            "no_mutation": _no_mutation_indicator(),
            **_review_boundary_flags(live_network_used=any(bool(response.get("network_used")) for response in responses)),
        }

    def _run_resolution_search(
        self,
        query: str,
        options: LocalSearchOptions,
        provider: MetadataFallbackProvider | None,
    ) -> ResolutionRunRecord:
        policy = ResolutionRunFallbackPolicy(
            enabled=provider is not None,
            allowed_source_families=("internet_archive",),
            candidate_limit=max(1, min(options.limit, 25)),
            max_requests=options.metadata_budget,
            timeout_seconds=options.metadata_timeout_seconds,
        )
        with tempfile.TemporaryDirectory() as temp_dir:
            service = _build_resolution_service(temp_dir, provider, policy)
            return service.run_deterministic_search(DeterministicSearchRunRequest.from_parts(query))

    def _live_provider(self, options: LocalSearchOptions) -> MetadataFallbackProvider:
        if self._live_provider_factory is not None:
            return self._live_provider_factory(options)
        rows = max(1, min(options.limit, 10))
        key = (rows, options.metadata_timeout_seconds)
        provider = self._live_provider_cache.get(key)
        if provider is None:
            provider = ArchiveOrgMetadataCandidateProvider(
                rows=rows,
                timeout_seconds=options.metadata_timeout_seconds,
            )
            self._live_provider_cache[key] = provider
        return provider

    def _project_run(self, run: ResolutionRunRecord, *, include_debug: bool) -> dict[str, Any]:
        profiles = ("json_v0", "text_v0", "html_basic_v0")
        projections = {
            profile: self._surface.project(
                SurfaceRequest(
                    route_id="resolution_run",
                    entity_id=run.run_id,
                    payload=run,
                    requested_profile=profile,
                    visibility_posture="public",
                    data_version=DATA_VERSION,
                )
            )
            for profile in profiles
        }
        if not include_debug:
            for projection in projections.values():
                projection.pop("cache", None)
        return projections


class IAFixtureMetadataProvider:
    """Fixture-only metadata provider compatible with ResolutionRun fallback."""

    source_id = "internet_archive_metadata"
    source_family = "internet_archive"

    def __init__(self, fixture_payload: Mapping[str, Any]) -> None:
        self._fixture_payload = dict(fixture_payload)
        self.calls: list[tuple[str, int]] = []

    def search_metadata_candidates(self, query: str, limit: int) -> dict[str, Any]:
        normalized = _normalize_query(query)
        self.calls.append((normalized, limit))
        case = _ia_fixture_case_for_query(normalized, self._fixture_payload)
        if case is None:
            return _fixture_provider_result(
                normalized,
                status="succeeded",
                candidates=(),
                warnings=("No matching IA fixture row exists; returning a search need only.",),
            )
        mode = str(case.get("fixture_mode") or "empty")
        if mode == "near_miss":
            return _fixture_provider_result(
                normalized,
                status="near_miss",
                candidates=(),
                failure_reason="metadata_near_miss",
                warnings=(str(case.get("near_miss_reason") or "metadata fixture near miss requires review"),),
            )
        if mode in {"malformed", "timeout"}:
            return _fixture_provider_result(
                normalized,
                status="failed",
                candidates=(),
                failure_reason=f"fixture_{mode}",
                warnings=(f"IA metadata fixture returned {mode}.",),
            )
        docs = case.get("docs") if isinstance(case.get("docs"), list) else []
        candidates = tuple(_candidate_from_doc(normalized, doc) for doc in docs[:limit] if isinstance(doc, Mapping))
        return _fixture_provider_result(normalized, status="succeeded", candidates=candidates)


def render_search_json(response: Mapping[str, Any]) -> str:
    return json.dumps(response, indent=2, sort_keys=True, ensure_ascii=True) + "\n"


def render_search_text(response: Mapping[str, Any]) -> str:
    if response.get("schema_version") == "eureka.local_search_batch_response.v0":
        lines = [
            "Eureka Local Search",
            f"metadata fallback: {response.get('metadata_fallback')}",
            f"fallback mode: {response.get('fallback_mode')}",
            f"fallback used: {str(response.get('fallback_used')).lower()}",
            f"provider family: {response.get('provider_family')}",
            f"index mode: {response.get('index_mode')}",
            f"index loaded: {str(response.get('index_loaded')).lower()}",
            f"index path: {response.get('index_path')}",
            f"index results used: {str(response.get('index_results_used')).lower()}",
            f"index result count: {response.get('index_result_count')} of {response.get('index_document_count')} indexed document(s)",
            f"reviewed record count: {response.get('reviewed_record_count', 0)}",
            f"artifact verified count: {response.get('artifact_verified_count', 0)}",
            f"live metadata enabled: {str(response.get('live_metadata_enabled')).lower()}",
            f"network used: {str(response.get('network_used')).lower()}",
            _status_summary_line(response.get("status_summary")),
            "",
        ]
        for item in response.get("queries") or []:
            lines.extend(_single_text_lines(item))
            lines.append("")
        return "\n".join(lines).rstrip() + "\n"
    return "\n".join(_single_text_lines(response)).rstrip() + "\n"


def render_search_html(response: Mapping[str, Any]) -> str:
    if response.get("schema_version") == "eureka.local_search_batch_response.v0":
        sections = "\n".join(_html_search_section(item) for item in response.get("queries") or [])
        query_value = ""
        title = "Eureka Local Search"
    else:
        sections = _html_search_section(response)
        query_value = str(response.get("query", {}).get("raw") if isinstance(response.get("query"), Mapping) else "")
        title = f"Eureka Search - {query_value or 'Local'}"
    return "\n".join(
        [
            "<!doctype html>",
            '<html lang="en">',
            "<head>",
            '<meta charset="utf-8">',
            '<meta name="viewport" content="width=device-width, initial-scale=1">',
            f"<title>{_e(title)}</title>",
            "<style>body{font-family:system-ui,-apple-system,Segoe UI,sans-serif;line-height:1.45;margin:0;color:#162027}main,header{max-width:920px;margin:auto;padding:1rem}header{border-bottom:1px solid #ccd6dc}.search{display:flex;gap:.5rem;flex-wrap:wrap}.search input{min-width:18rem;max-width:100%;padding:.5rem}.search button{padding:.5rem .8rem}.card{border:1px solid #ccd6dc;border-left:.4rem solid #637381;padding:.8rem;margin:.75rem 0}.status-candidate,.status-near_miss{border-left-color:#8a5a00}.status-need{border-left-color:#5d4aa5}.status-policy_blocked{border-left-color:#9b2c2c}.status-unavailable,.status-unknown{border-left-color:#59636c}.status-verified{border-left-color:#087443}.meta{color:#52616b}</style>",
            "</head>",
            "<body>",
            "<header>",
            "<h1>Eureka Local Search</h1>",
            '<form class="search" action="/search" method="get">',
            '<label for="q">Search</label>',
            f'<input id="q" name="q" value="{_e(query_value)}">',
            '<button type="submit">Search</button>',
            "</form>",
            '<p class="meta">Local fallback demo. Read-only. Fixture/live metadata fallback is candidate/need/near-miss only and never verified truth.</p>',
            "</header>",
            "<main>",
            sections,
            "</main>",
            "</body>",
            "</html>",
            "",
        ]
    )


def status_payload(
    metadata_fallback: str = "none",
    *,
    allow_live_metadata: bool = False,
    metadata_timeout_seconds: int = DEFAULT_METADATA_TIMEOUT_SECONDS,
    metadata_budget: int = DEFAULT_METADATA_BUDGET,
    index: str = "none",
    index_path: str = DEFAULT_INDEX_PATH,
) -> dict[str, Any]:
    fallback = _normalize_metadata_fallback(metadata_fallback)
    live_enabled = fallback == "ia_live" and bool(allow_live_metadata)
    index_status = index_file_status(_normalize_index(index), str(index_path or DEFAULT_INDEX_PATH))
    return {
        "schema_version": "eureka.local_search_status.v0",
        "task_id": TASK_ID,
        "status": "pass",
        "service": "local_search_service",
        "routes": ["/", "/health", "/api/status", "/api/search?q=", "/search?q="],
        "commands": ["scripts/eureka_search.py", "scripts/run_eureka_local.py"],
        "metadata_fallback": fallback,
        "fallback_mode": _fallback_mode(fallback, _status_source_path(fallback, live_enabled)),
        "provider_family": _batch_provider_family(fallback),
        **index_status,
        "index_modes": list(SUPPORTED_INDEX_MODES),
        "live_metadata_enabled": live_enabled,
        "network_default": False,
        "network_used": False,
        "timeout_seconds": max(1, int(metadata_timeout_seconds)),
        "budget": {"max_requests": max(0, int(metadata_budget))},
        "public_live_fanout": False,
        "metadata_fallback_modes": list(SUPPORTED_METADATA_FALLBACKS),
        "canonical_statuses": list(CANONICAL_STATUSES),
        "hard_query_smoke_set": list(HARD_QUERY_SMOKE_SET),
        "read_only": True,
        "live_network_enabled": live_enabled,
        "live_metadata_opt_in_required": fallback == "ia_live" and not live_enabled,
        "downloads_enabled": False,
        "public_mutation_enabled": False,
        "reviewed_index_mutation_enabled": False,
        "production_readiness_claimed": False,
        "public_launch_readiness_claimed": False,
        "no_mutation": _no_mutation_indicator(),
        **_review_boundary_flags(),
    }


def health_payload() -> dict[str, Any]:
    return {
        "schema_version": "eureka.local_search_health.v0",
        "status": "pass",
        "service": "local_search_service",
        "read_only": True,
        "live_network_enabled": False,
        "downloads_enabled": False,
        "public_mutation_enabled": False,
    }


def _response_from_index(
    *,
    query: str,
    options: LocalSearchOptions,
    index_state: IndexSearchState,
) -> dict[str, Any]:
    cards = [document_to_result_card(document) for document in index_state.results]
    status = str(cards[0].get("status") if cards else "unknown")
    source_hints = sorted({hint for card in cards for hint in _strings(card.get("source_hints") or [])})
    evidence_hints = [hint for card in cards for hint in _strings(card.get("evidence_hints") or [])]
    missing = sorted({item for card in cards for item in _strings(card.get("missing") or [])})
    return {
        "schema_version": SCHEMA_VERSION,
        "task_id": TASK_ID,
        "query": {"raw": query, "normalized": query},
        "normalized_query": query,
        "status": status,
        "status_concept": "indexed_result",
        "status_summary": _status_summary(status, cards),
        "result_count": len(cards),
        "results": cards,
        "missing": missing,
        "safe_next_action": str(cards[0].get("safe_next_action") if cards else "refine the query"),
        "metadata_fallback": options.metadata_fallback,
        "fallback_mode": "none",
        "fallback_used": False,
        "metadata_fallback_used": False,
        "provider_family": "none",
        **_index_response_fields(index_state, results_used=True),
        "live_metadata_enabled": options.metadata_fallback == "ia_live" and options.allow_live_metadata,
        "network_default": False,
        "network_used": False,
        "timeout_seconds": options.metadata_timeout_seconds,
        "budget": {"max_requests": options.metadata_budget, "candidate_limit": max(1, min(options.limit, 25))},
        "budget_used": 0,
        "public_live_fanout": False,
        "non_verified_reason": str(cards[0].get("non_verified_reason") if cards else "indexed result is not accepted truth"),
        "source_path": "local_search_index",
        "run_id": "",
        "run": {},
        "fallback_summary": None,
        "source_observations": [],
        "evidence_hints": evidence_hints[:3] if not options.show_evidence else evidence_hints,
        "source_hints": source_hints,
        "renderer_outputs": {},
        "fixture_backed": True,
        "provider_call_count": 0,
        "canonical_statuses": list(CANONICAL_STATUSES),
        "no_mutation": _no_mutation_indicator(),
        **_review_boundary_flags(),
    }


def _index_miss_response(
    *,
    query: str,
    options: LocalSearchOptions,
    index_state: IndexSearchState,
) -> dict[str, Any]:
    status = "need" if index_state.loaded else "unavailable"
    missing = ["indexed result or enabled metadata fallback"]
    if not index_state.loaded:
        missing.append("valid local search index")
    errors = list(index_state.errors)
    summary = (
        "Local index did not contain a sufficient result and metadata fallback is disabled."
        if index_state.loaded
        else "Local index was unavailable or invalid and metadata fallback is disabled."
    )
    card = {
        "result_id": "local-index-miss",
        "status": status,
        "title": "Local index search need",
        "summary": summary,
        "source_hints": ["local_search_index"],
        "evidence_hints": errors or ["reason: local_index_no_results"],
        "missing": missing,
        "safe_next_action": "build or refresh the local index, refine the query, or enable governed metadata fallback",
        "non_verified_reason": "no indexed reviewed truth was created",
        "verified": False,
        "accepted_truth": False,
        "review_required": False,
    }
    return {
        "schema_version": SCHEMA_VERSION,
        "task_id": TASK_ID,
        "query": {"raw": query, "normalized": query},
        "normalized_query": query,
        "status": status,
        "status_concept": "local_index_miss",
        "status_summary": _status_summary(status, [card]),
        "result_count": 1,
        "results": [card],
        "missing": missing,
        "safe_next_action": str(card["safe_next_action"]),
        "metadata_fallback": options.metadata_fallback,
        "fallback_mode": "none",
        "fallback_used": False,
        "metadata_fallback_used": False,
        "provider_family": "none",
        **_index_response_fields(index_state, results_used=False),
        "live_metadata_enabled": False,
        "network_default": False,
        "network_used": False,
        "timeout_seconds": options.metadata_timeout_seconds,
        "budget": {"max_requests": options.metadata_budget, "candidate_limit": max(1, min(options.limit, 25))},
        "budget_used": 0,
        "public_live_fanout": False,
        "non_verified_reason": str(card["non_verified_reason"]),
        "source_path": "local_search_index",
        "run_id": "",
        "run": {},
        "fallback_summary": None,
        "source_observations": [],
        "evidence_hints": list(card["evidence_hints"]),
        "source_hints": list(card["source_hints"]),
        "renderer_outputs": {},
        "fixture_backed": False,
        "provider_call_count": 0,
        "canonical_statuses": list(CANONICAL_STATUSES),
        "no_mutation": _no_mutation_indicator(),
        **_review_boundary_flags(),
    }


def _response_from_projection(
    *,
    query: str,
    options: LocalSearchOptions,
    run: ResolutionRunRecord,
    source_path: str,
    status_concept: str,
    provider_call_count: int,
    view_model: Mapping[str, Any],
    projections: Mapping[str, Any],
    index_state: IndexSearchState,
) -> dict[str, Any]:
    fallback = _mapping(view_model.get("payload", {}).get("fallback_summary") if isinstance(view_model.get("payload"), Mapping) else None)
    status = str(view_model.get("canonical_status") or "unknown")
    cards = _result_cards(view_model)
    status_summary = _status_summary(status, cards)
    fallback_used = bool(fallback and source_path in {"ia_fixture_metadata_fallback", "ia_live_metadata_fallback"})
    provider_family = _provider_family(source_path, options.metadata_fallback)
    non_verified_reason = _non_verified_reason(source_path, status, fallback)
    network_used = _network_used(fallback)
    budget_used = _budget_used(fallback)
    response: dict[str, Any] = {
        "schema_version": SCHEMA_VERSION,
        "task_id": TASK_ID,
        "query": {"raw": query, "normalized": query},
        "normalized_query": query,
        "status": status,
        "status_concept": status_concept or status,
        "status_summary": status_summary,
        "result_count": len(cards),
        "results": cards,
        "missing": _missing_information(fallback, status),
        "safe_next_action": _safe_next_action(status, fallback),
        "metadata_fallback": options.metadata_fallback,
        "fallback_mode": _fallback_mode(options.metadata_fallback, source_path),
        "fallback_used": fallback_used,
        "metadata_fallback_used": fallback_used,
        "provider_family": provider_family,
        **_index_response_fields(index_state, results_used=False),
        "live_metadata_enabled": options.metadata_fallback == "ia_live" and options.allow_live_metadata,
        "network_default": False,
        "network_used": network_used,
        "timeout_seconds": options.metadata_timeout_seconds,
        "budget": {"max_requests": options.metadata_budget, "candidate_limit": max(1, min(options.limit, 25))},
        "budget_used": budget_used,
        "public_live_fanout": False,
        "non_verified_reason": non_verified_reason,
        "source_path": source_path,
        "run_id": run.run_id,
        "run": {
            "run_id": run.run_id,
            "run_kind": run.run_kind,
            "status": run.status,
            "requested_value": run.requested_value,
        },
        "fallback_summary": fallback or None,
        "source_observations": _source_observations(fallback),
        "evidence_hints": _evidence_hints(cards, fallback),
        "source_hints": _source_hints(cards, fallback),
        "renderer_outputs": {
            profile: projection["renderer_result"]["renderer_output"]
            for profile, projection in projections.items()
        },
        "fixture_backed": source_path in {"hard_query_fixture", "ia_fixture_metadata_fallback"},
        "provider_call_count": provider_call_count,
        "canonical_statuses": list(CANONICAL_STATUSES),
        "no_mutation": _no_mutation_indicator(),
        **_review_boundary_flags(live_network_used=network_used),
    }
    if options.show_debug:
        response["debug"] = {
            "surface_projections": dict(projections),
            "run_record": run.to_dict(),
        }
    if not options.show_evidence:
        response["evidence_hints"] = response["evidence_hints"][:3]
    return response


def _result_cards(view_model: Mapping[str, Any]) -> list[dict[str, Any]]:
    payload = view_model.get("payload") if isinstance(view_model.get("payload"), Mapping) else {}
    fallback = _mapping(payload.get("fallback_summary"))
    result_summary = _mapping(payload.get("result_summary"))
    cards: list[dict[str, Any]] = []
    for item in fallback.get("candidates") or []:
        if isinstance(item, Mapping):
            status = str(item.get("status") or fallback.get("canonical_status") or "candidate")
            cards.append(_card_from_item(item, status=status, id_key="candidate_id", fallback=fallback))
    fallback_status = str(fallback.get("canonical_status") or fallback.get("status") or "unknown")
    for item in fallback.get("needs") or []:
        if isinstance(item, Mapping):
            cards.append(_card_from_item(item, status="near_miss" if fallback_status == "near_miss" else "need", id_key="need_id", fallback=fallback))
    if cards:
        return cards
    for item in result_summary.get("items") or []:
        if isinstance(item, Mapping):
            obj = _mapping(item.get("object_summary"))
            cards.append(
                {
                    "result_id": str(item.get("target_ref") or obj.get("object_id") or "local-result"),
                    "status": "verified",
                    "title": str(obj.get("label") or item.get("target_ref") or "Local result"),
                    "summary": "Local reviewed/index result returned by the existing resolution run path.",
                    "source_hints": _strings([_mapping(item.get("source")).get("source_id")]),
                    "evidence_hints": _strings([evidence.get("summary") for evidence in item.get("evidence") or [] if isinstance(evidence, Mapping)]),
                    "missing": [],
                    "safe_next_action": "inspect existing local result and evidence before reuse",
                    "non_verified_reason": "",
                    "verified": True,
                    "accepted_truth": True,
                    "review_required": False,
                }
            )
    if cards:
        return cards
    if fallback:
        status = str(fallback.get("canonical_status") or fallback.get("status") or "unknown")
        cards.append(
            {
                "result_id": str(fallback.get("source_id") or status),
                "status": status,
                "title": str(fallback.get("title") or status.replace("_", " ").title()),
                "summary": _fallback_summary_text(fallback),
                "source_hints": _source_hints([], fallback),
                "evidence_hints": _evidence_hints([], fallback),
                "missing": _missing_information(fallback, status),
                "safe_next_action": _safe_next_action(status, fallback),
                "non_verified_reason": _non_verified_reason("ia_fixture_metadata_fallback", status, fallback),
                "verified": False,
                "accepted_truth": False,
                "review_required": bool(fallback.get("review_required")),
            }
        )
    return cards


def _card_from_item(
    item: Mapping[str, Any],
    *,
    status: str,
    id_key: str,
    fallback: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    fallback_map = _mapping(fallback)
    source_locator = item.get("source_locator") if isinstance(item.get("source_locator"), Mapping) else {}
    title = str(item.get("title") or item.get("candidate_title") or item.get("need_title") or item.get(id_key) or status)
    summary = str(
        item.get("summary")
        or item.get("candidate_summary")
        or item.get("need_summary")
        or "Fixture metadata observation; review required before truth promotion."
    )
    missing = _strings(item.get("limitations") or []) or _missing_information(fallback_map, status)
    non_verified_reason = (
        "live IA metadata result requires review and is not accepted truth"
        if _network_used(fallback_map)
        else "metadata-derived result requires review and is not accepted truth"
    )
    return {
        "result_id": str(item.get(id_key) or item.get("item_id") or status),
        "status": status,
        "title": title,
        "summary": summary,
        "source_hints": _strings([item.get("source_id"), item.get("source_family"), source_locator.get("url")]),
        "evidence_hints": _strings([summary, source_locator.get("identifier")]),
        "missing": missing,
        "safe_next_action": _safe_next_action(status, fallback_map),
        "non_verified_reason": non_verified_reason,
        "verified": False,
        "accepted_truth": False,
        "review_required": bool(item.get("review_required", status in {"candidate", "need", "near_miss"})),
    }


def _single_text_lines(response: Mapping[str, Any]) -> list[str]:
    query = response.get("query", {}).get("raw") if isinstance(response.get("query"), Mapping) else ""
    lines = [
        f"Query: {query}",
        f"Status: {response.get('status')} ({response.get('status_concept')})",
        _status_summary_line(response.get("status_summary")),
        f"Source path: {response.get('source_path')}",
        f"Fallback mode: {response.get('fallback_mode')}",
        f"Fallback used: {str(response.get('fallback_used', response.get('metadata_fallback_used'))).lower()}",
        f"Provider family: {response.get('provider_family')}",
        f"Index mode: {response.get('index_mode')}",
        f"Index loaded: {str(response.get('index_loaded')).lower()}",
        f"Index path: {response.get('index_path')}",
        f"Index results used: {str(response.get('index_results_used')).lower()}",
        f"Index result count: {response.get('index_result_count')} of {response.get('index_document_count')} indexed document(s)",
        f"Reviewed record count: {response.get('reviewed_record_count', 0)}",
        f"Artifact verified count: {response.get('artifact_verified_count', 0)}",
        f"Live metadata enabled: {str(response.get('live_metadata_enabled')).lower()}",
        f"Network used: {str(response.get('network_used')).lower()}",
        f"Timeout seconds: {response.get('timeout_seconds')}",
        f"Budget used: {response.get('budget_used')} of {_mapping(response.get('budget')).get('max_requests', 0)} metadata request(s)",
        f"Metadata fallback: {response.get('metadata_fallback')} used={str(response.get('metadata_fallback_used')).lower()}",
        f"Non-verified reason: {response.get('non_verified_reason') or 'not applicable'}",
        "Truth boundary: fallback/fixture results are not verified truth; search does not mutate reviewed or public indexes.",
    ]
    source_hints = ", ".join(response.get("source_hints") or [])
    if source_hints:
        lines.append(f"Source hints: {source_hints}")
    evidence_hints = ", ".join(response.get("evidence_hints") or [])
    if evidence_hints:
        lines.append(f"Evidence hints: {evidence_hints}")
    cards = response.get("results") or []
    if cards:
        lines.append("Results:")
        for index, card in enumerate(cards, start=1):
            lines.append(f"  {index}. [{card.get('status')}] {card.get('title')}")
            lines.append(f"     {card.get('summary')}")
            hints = ", ".join(card.get("source_hints") or [])
            if hints:
                lines.append(f"     source: {hints}")
            evidence = ", ".join(card.get("evidence_hints") or [])
            if evidence:
                lines.append(f"     evidence: {evidence}")
            non_verified = str(card.get("non_verified_reason") or "")
            if non_verified:
                lines.append(f"     non-verified: {non_verified}")
            review_state = str(card.get("review_state") or "")
            if review_state:
                lines.append(f"     review state: {review_state}")
            reviewed_record_id = str(card.get("reviewed_record_id") or "")
            if reviewed_record_id:
                lines.append(f"     reviewed record: {reviewed_record_id}")
            review_event_id = str(card.get("review_event_id") or "")
            if review_event_id:
                lines.append(f"     review event: {review_event_id}")
            if "artifact_verified" in card:
                lines.append(f"     artifact verified: {str(card.get('artifact_verified')).lower()}")
            missing = ", ".join(card.get("missing") or [])
            if missing:
                lines.append(f"     missing: {missing}")
            lines.append(f"     safe next action: {card.get('safe_next_action')}")
    else:
        lines.append("Results: none")
    missing = ", ".join(response.get("missing") or [])
    lines.append(f"What is missing: {missing or 'no extra missing-detail hint available'}")
    lines.append(f"Safe next action: {response.get('safe_next_action')}")
    return lines


def _html_search_section(response: Mapping[str, Any]) -> str:
    query = response.get("query", {}).get("raw") if isinstance(response.get("query"), Mapping) else ""
    cards = response.get("results") or []
    card_html = []
    for card in cards:
        status = str(card.get("status") or "unknown")
        source_hints = ", ".join(card.get("source_hints") or [])
        evidence_hints = ", ".join(card.get("evidence_hints") or [])
        missing = ", ".join(card.get("missing") or [])
        non_verified = str(card.get("non_verified_reason") or "")
        review_state = str(card.get("review_state") or "")
        reviewed_record_id = str(card.get("reviewed_record_id") or "")
        review_event_id = str(card.get("review_event_id") or "")
        artifact_verified = str(card.get("artifact_verified")).lower() if "artifact_verified" in card else "not applicable"
        card_html.extend(
            [
                f'<article class="card status-{_e(status)}">',
                f"<h3>{_e(str(card.get('title') or 'Untitled'))}</h3>",
                f"<p><strong>Status:</strong> {_e(status)}</p>",
                f"<p>{_e(str(card.get('summary') or ''))}</p>",
                f"<p><strong>Source hints:</strong> {_e(source_hints or 'none')}</p>",
                f"<p><strong>Evidence hints:</strong> {_e(evidence_hints or 'none')}</p>",
                f"<p><strong>Non-verified:</strong> {_e(non_verified or 'not applicable')}</p>",
                f"<p><strong>Review state:</strong> {_e(review_state or 'unreviewed')}</p>",
                f"<p><strong>Reviewed record:</strong> {_e(reviewed_record_id or 'none')}</p>",
                f"<p><strong>Review event:</strong> {_e(review_event_id or 'none')}</p>",
                f"<p><strong>Artifact verified:</strong> {_e(artifact_verified)}</p>",
                f"<p><strong>Missing:</strong> {_e(missing or 'no extra missing-detail hint available')}</p>",
                f"<p><strong>Safe next action:</strong> {_e(str(card.get('safe_next_action') or ''))}</p>",
                "</article>",
            ]
        )
    if not card_html:
        card_html.append('<p class="meta">No local result cards were produced.</p>')
    return "\n".join(
        [
            "<section>",
            f"<h2>{_e(str(query or 'Search'))}</h2>",
            f'<p data-status="{_e(str(response.get("status") or "unknown"))}"><strong>Status:</strong> {_e(str(response.get("status") or "unknown"))}</p>',
            f"<p>{_e(_status_summary_line(response.get('status_summary')))}</p>",
            f"<p><strong>Fallback mode:</strong> {_e(str(response.get('fallback_mode') or response.get('metadata_fallback') or 'none'))}</p>",
            f"<p><strong>Fallback used:</strong> {_e(str(response.get('fallback_used', response.get('metadata_fallback_used'))).lower())}</p>",
            f"<p><strong>Provider family:</strong> {_e(str(response.get('provider_family') or 'none'))}</p>",
            f"<p><strong>Index mode:</strong> {_e(str(response.get('index_mode') or 'none'))}</p>",
            f"<p><strong>Index loaded:</strong> {_e(str(response.get('index_loaded')).lower())}</p>",
            f"<p><strong>Index path:</strong> {_e(str(response.get('index_path') or ''))}</p>",
            f"<p><strong>Index results used:</strong> {_e(str(response.get('index_results_used')).lower())}</p>",
            f"<p><strong>Index result count:</strong> {_e(str(response.get('index_result_count') or 0))} of {_e(str(response.get('index_document_count') or 0))} indexed document(s)</p>",
            f"<p><strong>Reviewed record count:</strong> {_e(str(response.get('reviewed_record_count') or 0))}</p>",
            f"<p><strong>Artifact verified count:</strong> {_e(str(response.get('artifact_verified_count') or 0))}</p>",
            f"<p><strong>Live metadata enabled:</strong> {_e(str(response.get('live_metadata_enabled')).lower())}</p>",
            f"<p><strong>Network used:</strong> {_e(str(response.get('network_used')).lower())}</p>",
            f"<p><strong>Timeout seconds:</strong> {_e(str(response.get('timeout_seconds') or 0))}</p>",
            f"<p><strong>Budget used:</strong> {_e(str(response.get('budget_used') or 0))} of {_e(str(_mapping(response.get('budget')).get('max_requests', 0)))} metadata request(s)</p>",
            f"<p><strong>Non-verified reason:</strong> {_e(str(response.get('non_verified_reason') or 'not applicable'))}</p>",
            f"<p><strong>Source hints:</strong> {_e(', '.join(response.get('source_hints') or []) or 'none')}</p>",
            f"<p><strong>Evidence hints:</strong> {_e(', '.join(response.get('evidence_hints') or []) or 'none')}</p>",
            f"<p><strong>What is missing:</strong> {_e(', '.join(response.get('missing') or []) or 'no extra missing-detail hint available')}</p>",
            f"<p><strong>Safe next action:</strong> {_e(str(response.get('safe_next_action') or ''))}</p>",
            *card_html,
            "</section>",
        ]
    )


def _build_resolution_service(
    root: str,
    fallback_provider: MetadataFallbackProvider | None,
    fallback_policy: ResolutionRunFallbackPolicy,
) -> LocalResolutionRunService:
    catalog = _build_demo_normalized_catalog()
    resolution_service = ExactMatchResolutionService(catalog)
    search_service = DeterministicSearchService(catalog)
    absence_service = DeterministicAbsenceService(
        catalog,
        resolution_service=resolution_service,
        search_service=search_service,
    )
    return LocalResolutionRunService(
        catalog=catalog,
        source_registry=load_source_registry(),
        resolution_service=resolution_service,
        search_service=search_service,
        absence_service=absence_service,
        run_store=LocalResolutionRunStore(root),
        fallback_provider=fallback_provider,
        fallback_policy=fallback_policy,
        timestamp_factory=lambda: "2026-06-12T00:00:00+10:00",
    )


def _build_demo_normalized_catalog() -> NormalizedCatalog:
    synthetic_connector = SyntheticSoftwareConnector()
    github_connector = GitHubReleasesConnector()
    synthetic_records = tuple(
        normalize_extracted_record(extract_synthetic_source_record(record))
        for record in synthetic_connector.load_source_records()
    )
    github_records = tuple(
        normalize_github_release_record(extract_github_release_source_record(record))
        for record in github_connector.load_source_records()
    )
    return NormalizedCatalog(synthetic_records + github_records)


def _fixture_provider_result(
    query: str,
    *,
    status: str,
    candidates: Sequence[Mapping[str, Any]],
    failure_reason: str | None = None,
    warnings: Sequence[str] = (),
) -> dict[str, Any]:
    return {
        "schema_version": "archive_org_metadata_candidate_search.v0",
        "status": status,
        "query": query,
        "source_id": IAFixtureMetadataProvider.source_id,
        "source_family": IAFixtureMetadataProvider.source_family,
        "source_label": "Internet Archive metadata fixture",
        "candidate_count": len(candidates),
        "candidates": [dict(candidate) for candidate in candidates],
        "total_http_requests": 0,
        "live_call_performed": False,
        "metadata_request_performed": True,
        "source_probe_executed": False,
        "raw_response_committed": False,
        "download_performed": False,
        "upload_performed": False,
        "extraction_executed": False,
        "accepted_truth": False,
        "review_required": True,
        "failure_reason": failure_reason,
        "limitations": ["ia_fixture", "metadata_only", "candidate_not_reviewed_truth", "no_download"],
        "warnings": list(warnings)
        or [
            "Fixture metadata candidate requires review before promotion.",
            "No live network request, file fetch, or download occurred.",
        ],
    }


def _candidate_from_doc(query: str, doc: Mapping[str, Any]) -> dict[str, Any]:
    identifier = str(doc.get("identifier") or "ia-fixture")
    title = str(doc.get("title") or identifier)
    return {
        "candidate_id": _stable_id("ia-fixture-candidate", query, identifier, title),
        "candidate_title": title,
        "candidate_summary": str(doc.get("description") or "IA fixture metadata candidate; review required."),
        "source_id": IAFixtureMetadataProvider.source_id,
        "source_family": IAFixtureMetadataProvider.source_family,
        "source_locator": {
            "locator_kind": "archive_org_fixture_details_page",
            "identifier": identifier,
            "url": f"https://archive.org/details/{quote_plus(identifier)}",
        },
        "limitations": ["ia_fixture", "metadata_only", "candidate_not_reviewed_truth", "no_download"],
        "warnings": ["Fixture metadata only; not reviewed truth."],
    }


def _hard_fixture_for_query(query: str) -> Mapping[str, Any] | None:
    normalized = _normalize_query(query).casefold()
    for fixture in fixture_cases():
        if _normalize_query(str(fixture.get("query_text") or "")).casefold() == normalized:
            return fixture
    return None


def _ia_fixture_case_for_query(query: str, fixture_payload: Mapping[str, Any]) -> Mapping[str, Any] | None:
    normalized = _normalize_query(query).casefold()
    for case in fixture_payload.get("cases") or []:
        if isinstance(case, Mapping) and _normalize_query(str(case.get("query_text") or "")).casefold() == normalized:
            if str(case.get("case_id")) == "policy_blocked_disabled":
                continue
            return case
    return None


def _normalize_options(options: LocalSearchOptions | None) -> LocalSearchOptions:
    if options is None:
        return LocalSearchOptions()
    return LocalSearchOptions(
        metadata_fallback=_normalize_metadata_fallback(options.metadata_fallback),
        limit=max(1, min(int(options.limit), 25)),
        show_evidence=bool(options.show_evidence),
        show_debug=bool(options.show_debug),
        allow_live_metadata=bool(options.allow_live_metadata),
        metadata_timeout_seconds=max(1, min(int(options.metadata_timeout_seconds), 30)),
        metadata_budget=max(0, min(int(options.metadata_budget), 5)),
        index=_normalize_index(options.index),
        index_path=str(options.index_path or DEFAULT_INDEX_PATH),
    )


def _normalize_metadata_fallback(value: str) -> str:
    normalized = str(value or "none").strip()
    if normalized not in SUPPORTED_METADATA_FALLBACKS:
        raise ValueError(f"unsupported metadata fallback: {value}")
    return normalized


def _normalize_index(value: str) -> str:
    normalized = str(value or "none").strip()
    if normalized not in SUPPORTED_INDEX_MODES:
        raise ValueError(f"unsupported index mode: {value}")
    return normalized


def _search_index_state(options: LocalSearchOptions, query: str) -> IndexSearchState:
    if options.index != "local":
        return _disabled_index_state(options)
    return search_index_path(options.index_path, query, limit=options.limit)


def _disabled_index_state(options: LocalSearchOptions) -> IndexSearchState:
    return IndexSearchState(
        enabled=options.index == "local",
        loaded=False,
        path=str(options.index_path or DEFAULT_INDEX_PATH),
        document_count=0,
        results=(),
        errors=(),
    )


def _index_response_fields(index_state: IndexSearchState, *, results_used: bool) -> dict[str, Any]:
    return {
        "index_mode": "local" if index_state.enabled else "none",
        "index_enabled": index_state.enabled,
        "index_loaded": index_state.loaded,
        "index_path": index_state.path,
        "index_document_count": index_state.document_count,
        "reviewed_record_count": index_state.reviewed_record_count,
        "artifact_verified_count": index_state.artifact_verified_count,
        "index_results_used": bool(results_used and index_state.results),
        "index_result_count": len(index_state.results) if results_used else 0,
        "index_errors": list(index_state.errors),
    }


def _empty_query_response(options: LocalSearchOptions) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "task_id": TASK_ID,
        "query": {"raw": "", "normalized": ""},
        "normalized_query": "",
        "status": "unknown",
        "status_concept": "empty_query",
        "status_summary": _status_summary("unknown", []),
        "result_count": 0,
        "results": [],
        "missing": ["query"],
        "safe_next_action": "provide a non-empty query",
        "metadata_fallback": options.metadata_fallback,
        "fallback_mode": _fallback_mode(options.metadata_fallback, "none"),
        "fallback_used": False,
        "metadata_fallback_used": False,
        "provider_family": "none",
        **_index_response_fields(_disabled_index_state(options), results_used=False),
        "live_metadata_enabled": options.metadata_fallback == "ia_live" and options.allow_live_metadata,
        "network_default": False,
        "network_used": False,
        "timeout_seconds": options.metadata_timeout_seconds,
        "budget": {"max_requests": options.metadata_budget, "candidate_limit": max(1, min(options.limit, 25))},
        "budget_used": 0,
        "public_live_fanout": False,
        "non_verified_reason": "empty query produced no result",
        "source_path": "none",
        "run_id": "",
        "fallback_summary": None,
        "source_observations": [],
        "evidence_hints": [],
        "source_hints": [],
        "renderer_outputs": {},
        "fixture_backed": False,
        "provider_call_count": 0,
        "canonical_statuses": list(CANONICAL_STATUSES),
        "no_mutation": _no_mutation_indicator(),
        **_review_boundary_flags(),
    }


def _status_summary(primary_status: str, cards: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    summary = {status: 0 for status in CANONICAL_STATUSES}
    if cards:
        for card in cards:
            status = str(card.get("status") or "unknown")
            summary[status if status in summary else "unknown"] += 1
    else:
        summary[primary_status if primary_status in summary else "unknown"] += 1
    return summary


def _aggregate_status_summary(responses: Sequence[Mapping[str, Any]]) -> dict[str, int]:
    summary = {status: 0 for status in CANONICAL_STATUSES}
    for response in responses:
        counts = response.get("status_summary") if isinstance(response.get("status_summary"), Mapping) else {}
        for status in CANONICAL_STATUSES:
            summary[status] += int(counts.get(status, 0))
    return summary


def _status_summary_line(value: Any) -> str:
    counts = value if isinstance(value, Mapping) else {}
    return "Status summary: " + ", ".join(f"{status}={int(counts.get(status, 0))}" for status in CANONICAL_STATUSES)


def _blocked_live_metadata_response(query: str, options: LocalSearchOptions) -> dict[str, Any]:
    fallback = {
        "schema_version": "eureka.resolution_run.indexless_fallback.v0",
        "mode": "ia_live_opt_in_gate",
        "status": "policy_blocked",
        "trigger": "live_metadata_opt_in_missing",
        "query": query,
        "source_id": "internet_archive_metadata",
        "source_family": "internet_archive",
        "source_allowlisted": True,
        "fallback_enabled": False,
        "reason_codes": ["live_metadata_opt_in_missing"],
        "failure_reason": "allow_live_metadata_required",
        "budget": {
            "max_requests": options.metadata_budget,
            "candidate_limit": max(1, min(options.limit, 25)),
            "timeout_seconds": options.metadata_timeout_seconds,
        },
        "source_observation": None,
        "candidate_count": 0,
        "candidates": [],
        "need_count": 0,
        "needs": [],
        "accepted_truth": False,
        "verified": False,
        "review_required": False,
        "reviewed_record_created": False,
        "reviewed_index_mutated": False,
        "master_index_mutated": False,
        "public_index_mutated": False,
        "public_action_posture": {
            "allowed": [],
            "operator_actions_exposed": False,
            "unsafe_actions_enabled": False,
        },
        "limitations": [
            "live_metadata_requires_explicit_opt_in",
            "metadata_only",
            "candidate_not_reviewed_truth",
            "no_download",
            "no_file_fetch",
            "no_wayback_replay",
            "no_public_source_fanout",
        ],
    }
    status = "policy_blocked"
    cards = [
        {
            "result_id": "ia-live-opt-in-required",
            "status": status,
            "title": "Live IA metadata opt-in required",
            "summary": "Use --allow-live-metadata with --metadata-fallback ia_live to permit a bounded developer-only metadata request.",
            "source_hints": ["internet_archive_metadata", "internet_archive"],
            "evidence_hints": ["reason: live_metadata_opt_in_missing"],
            "missing": ["explicit live metadata opt-in"],
            "safe_next_action": "rerun locally with --allow-live-metadata, a short timeout, and a small metadata budget",
            "non_verified_reason": "no live metadata request was performed and no truth was created",
            "verified": False,
            "accepted_truth": False,
            "review_required": False,
        }
    ]
    return {
        "schema_version": SCHEMA_VERSION,
        "task_id": TASK_ID,
        "query": {"raw": query, "normalized": query},
        "normalized_query": query,
        "status": status,
        "status_concept": "live_metadata_opt_in_missing",
        "status_summary": _status_summary(status, cards),
        "result_count": len(cards),
        "results": cards,
        "missing": ["explicit live metadata opt-in"],
        "safe_next_action": "rerun locally with --allow-live-metadata, a short timeout, and a small metadata budget",
        "metadata_fallback": options.metadata_fallback,
        "fallback_mode": "ia_live_blocked_missing_opt_in",
        "fallback_used": False,
        "metadata_fallback_used": False,
        "provider_family": "ia_live",
        **_index_response_fields(_disabled_index_state(options), results_used=False),
        "live_metadata_enabled": False,
        "network_default": False,
        "network_used": False,
        "timeout_seconds": options.metadata_timeout_seconds,
        "budget": dict(fallback["budget"]),
        "budget_used": 0,
        "public_live_fanout": False,
        "non_verified_reason": "live metadata is disabled until --allow-live-metadata is present",
        "source_path": "ia_live_metadata_fallback_blocked",
        "run_id": "",
        "run": {},
        "fallback_summary": fallback,
        "source_observations": [],
        "evidence_hints": ["reason: live_metadata_opt_in_missing"],
        "source_hints": ["internet_archive_metadata", "internet_archive"],
        "renderer_outputs": {},
        "fixture_backed": False,
        "provider_call_count": 0,
        "canonical_statuses": list(CANONICAL_STATUSES),
        "no_mutation": _no_mutation_indicator(),
        **_review_boundary_flags(),
    }


def _review_boundary_flags(*, live_network_used: bool = False) -> dict[str, bool | int]:
    return {
        "accepted_truth_created": False,
        "fallback_created_verified_truth": False,
        "reviewed_record_created": False,
        "verified_artifacts_created": 0,
        "reviewed_index_mutated": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "downloads_performed": False,
        "live_network_used": bool(live_network_used),
        "public_mutation_enabled": False,
    }


def _load_ia_fixture_payload() -> dict[str, Any]:
    base_payload = load_fixture_payload()
    base_cases = [case for case in base_payload.get("cases") or [] if isinstance(case, Mapping)]
    demo_cases: list[Mapping[str, Any]] = []
    if DEMO_FIXTURE_PATH.is_file():
        demo_payload = json.loads(DEMO_FIXTURE_PATH.read_text(encoding="utf-8"))
        demo_cases = [case for case in demo_payload.get("cases") or [] if isinstance(case, Mapping)]
    return {
        "schema_version": "ia_metadata_fallback_fixtures.v0",
        "task_id": TASK_ID,
        "metadata_only": True,
        "live_network_required": False,
        "cases": [dict(case) for case in (*demo_cases, *base_cases)],
    }


def _no_mutation_indicator() -> dict[str, bool | str]:
    return {
        "search_is_read_only": True,
        "reviewed_records_mutated": False,
        "review_ledgers_mutated": False,
        "reviewed_index_mutated": False,
        "public_index_mutated": False,
        "master_index_mutated": False,
        "truth_promotion_performed": False,
        "note": "Local search and metadata fallback are read-only.",
    }


def _fallback_mode(metadata_fallback: str, source_path: str) -> str:
    if metadata_fallback == "none":
        return "none"
    if source_path == "ia_live_metadata_fallback":
        return "ia_live_metadata_fallback"
    if source_path == "ia_live_metadata_fallback_blocked":
        return "ia_live_blocked_missing_opt_in"
    if source_path == "ia_fixture_metadata_fallback":
        return "ia_fixture_metadata_fallback"
    if source_path == "hard_query_fixture":
        return "hard_query_fixture"
    if source_path == "batch":
        return "batch_mixed"
    if metadata_fallback == "ia_live":
        return "ia_live_requested_no_fallback"
    return "ia_fixture_requested_no_fixture_match"


def _provider_family(source_path: str, metadata_fallback: str) -> str:
    if source_path in {"ia_live_metadata_fallback", "ia_live_metadata_fallback_blocked"}:
        return "ia_live"
    if source_path == "ia_fixture_metadata_fallback":
        return "ia_fixture"
    if source_path == "hard_query_fixture":
        return "hard_query_fixture"
    if metadata_fallback == "ia_live":
        return "ia_live"
    if metadata_fallback == "ia_fixture":
        return "ia_fixture"
    return "none"


def _non_verified_reason(source_path: str, status: str, fallback: Mapping[str, Any]) -> str:
    if status == "verified" and source_path == "local_resolution_run":
        return ""
    if source_path == "ia_live_metadata_fallback":
        return "live IA metadata is source observation only; review is required before truth promotion"
    if source_path == "ia_live_metadata_fallback_blocked":
        return "live metadata was not requested because explicit opt-in is missing"
    if source_path == "ia_fixture_metadata_fallback":
        return "fixture metadata is source observation only; review is required before truth promotion"
    if source_path == "hard_query_fixture":
        return "hard-query fixture output is demo evidence only; it is not reviewed artifact truth"
    if fallback:
        return "fallback-derived output is not accepted truth"
    return "no reviewed local result was created"


def _status_source_path(metadata_fallback: str, live_enabled: bool) -> str:
    if metadata_fallback == "ia_live":
        return "ia_live_metadata_fallback" if live_enabled else "ia_live_metadata_fallback_blocked"
    if metadata_fallback == "ia_fixture":
        return "ia_fixture_metadata_fallback"
    return "none"


def _batch_provider_family(metadata_fallback: str) -> str:
    if metadata_fallback == "ia_live":
        return "ia_live"
    if metadata_fallback == "ia_fixture":
        return "ia_fixture"
    return "none"


def _provider_call_count(provider: MetadataFallbackProvider | None) -> int:
    if provider is None:
        return 0
    calls = getattr(provider, "calls", None)
    if isinstance(calls, list):
        return len(calls)
    cache = getattr(provider, "_cache", None)
    if isinstance(cache, dict):
        return 1 if cache else 0
    return 0


def _network_used(fallback: Mapping[str, Any]) -> bool:
    observation = fallback.get("source_observation") if isinstance(fallback, Mapping) else None
    return bool(isinstance(observation, Mapping) and observation.get("external_call_performed") is True)


def _budget_used(fallback: Mapping[str, Any]) -> int:
    observation = fallback.get("source_observation") if isinstance(fallback, Mapping) else None
    if isinstance(observation, Mapping):
        value = observation.get("total_http_requests")
        if isinstance(value, int) and value >= 0:
            return value
    return 0


def _source_observations(fallback: Mapping[str, Any]) -> list[dict[str, Any]]:
    observation = fallback.get("source_observation") if isinstance(fallback, Mapping) else None
    return [dict(observation)] if isinstance(observation, Mapping) else []


def _source_hints(cards: Sequence[Mapping[str, Any]], fallback: Mapping[str, Any]) -> list[str]:
    hints: list[str] = []
    for card in cards:
        hints.extend(_strings(card.get("source_hints") or []))
    if fallback:
        hints.extend(_strings([fallback.get("source_id"), fallback.get("source_family")]))
        observation = fallback.get("source_observation")
        if isinstance(observation, Mapping):
            hints.extend(_strings([observation.get("source_id"), observation.get("source_label")]))
    return sorted(set(hints))


def _evidence_hints(cards: Sequence[Mapping[str, Any]], fallback: Mapping[str, Any]) -> list[str]:
    hints: list[str] = []
    for card in cards:
        hints.extend(_strings(card.get("evidence_hints") or []))
    if fallback:
        hints.extend(_strings([fallback.get("evidence_summary"), fallback.get("failure_reason")]))
        for reason in fallback.get("reason_codes") or []:
            hints.append(f"reason: {reason}")
    return [hint for hint in hints if hint]


def _missing_information(fallback: Mapping[str, Any], status: str) -> list[str]:
    missing = []
    reason_codes = set(_strings(fallback.get("reason_codes") or []))
    if "hardware_identifier_missing" in reason_codes:
        missing.extend(["hardware vendor", "hardware model", "device id or chipset", "exact Windows 98 version"])
    if status in {"candidate", "near_miss"}:
        missing.append("human review before truth promotion")
    if status == "need":
        missing.append("more source evidence or narrower query scope")
    if status == "policy_blocked":
        missing.append("policy/review approval")
    if status == "unavailable":
        missing.append("available source response or fixture coverage")
    return sorted(set(missing))


def _safe_next_action(status: str, fallback: Mapping[str, Any]) -> str:
    reason_codes = set(_strings(fallback.get("reason_codes") or [])) if isinstance(fallback, Mapping) else set()
    if "hardware_identifier_missing" in reason_codes:
        return "collect hardware vendor, model, device id or chipset, bus/interface, and exact Windows 98 version"
    if status == "verified":
        return "inspect local evidence before reuse"
    if status == "candidate":
        return "review candidate metadata and evidence before promotion"
    if status == "near_miss":
        return "refine identity clues and compare near-miss evidence"
    if status == "need":
        return "collect missing scope or source evidence"
    if status == "policy_blocked":
        return "wait for the relevant review or policy gate"
    if status == "unavailable":
        return "retry with narrower scope or add reviewed fixture coverage"
    return "refine the query"


def _fallback_summary_text(fallback: Mapping[str, Any]) -> str:
    if fallback.get("policy_block_reason"):
        return str(fallback.get("policy_block_reason"))
    if fallback.get("unavailable_reason"):
        return str(fallback.get("unavailable_reason"))
    if fallback.get("failure_reason"):
        return f"Fallback ended with {fallback.get('failure_reason')}."
    if fallback.get("reason_codes"):
        return "Fallback state: " + ", ".join(_strings(fallback.get("reason_codes") or []))
    return "Fallback returned no reviewed truth."


def _status_concept_from_fallback(fallback: Mapping[str, Any] | None) -> str:
    if not isinstance(fallback, Mapping):
        return "unknown"
    reason_codes = set(_strings(fallback.get("reason_codes") or []))
    if "hardware_identifier_missing" in reason_codes:
        return "blocked_for_user_details"
    return str(fallback.get("status") or "unknown")


def _mapping(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _strings(value: Any) -> list[str]:
    if not isinstance(value, (list, tuple, set)):
        return []
    return [str(item) for item in value if item not in (None, "")]


def _normalize_query(value: str) -> str:
    return " ".join(str(value or "").split())[:160]


def _stable_id(prefix: str, *parts: Any) -> str:
    import hashlib

    encoded = json.dumps(parts, sort_keys=True, separators=(",", ":"), default=str).encode("utf-8")
    return f"{prefix}:{hashlib.sha256(encoded).hexdigest()[:16]}"


def _e(value: str) -> str:
    return escape(str(value), quote=True)
