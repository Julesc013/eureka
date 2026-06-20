"""Disabled-by-default Autonomous Index Foundry v0."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import hashlib
import json
import tempfile
from typing import Any, Callable, Mapping, Sequence

from runtime.index.preview import SQLitePreviewIndexStore

from .hunt_engine import HuntBudget, HuntEngine
from .providers import provider_from_environment


FOUNDRY_PLAN_SCHEMA = "eureka.foundry_plan.v0"
FOUNDRY_RUN_SCHEMA = "eureka.foundry_run.v0"


@dataclass(frozen=True)
class SurveyBudget:
    maximum_seeds: int = 1
    maximum_queries: int = 3
    maximum_provider_requests: int = 3
    maximum_fetches: int = 3
    maximum_duration_seconds: int = 120
    maximum_bytes: int = 5 * 1024 * 1024
    maximum_concurrency: int = 1
    per_domain_requests: int = 3
    per_provider_requests: int = 3
    retry_ceiling: int = 0

    def bounded(self) -> "SurveyBudget":
        return SurveyBudget(
            maximum_seeds=max(1, min(int(self.maximum_seeds or 1), 25)),
            maximum_queries=max(1, min(int(self.maximum_queries or 3), 100)),
            maximum_provider_requests=max(1, min(int(self.maximum_provider_requests or 3), 200)),
            maximum_fetches=max(0, min(int(self.maximum_fetches or 3), 200)),
            maximum_duration_seconds=max(1, min(int(self.maximum_duration_seconds or 120), 3600)),
            maximum_bytes=max(1, min(int(self.maximum_bytes or 1), 256 * 1024 * 1024)),
            maximum_concurrency=max(1, min(int(self.maximum_concurrency or 1), 8)),
            per_domain_requests=max(1, min(int(self.per_domain_requests or 3), 100)),
            per_provider_requests=max(1, min(int(self.per_provider_requests or 3), 100)),
            retry_ceiling=max(0, min(int(self.retry_ceiling or 0), 5)),
        )

    def to_dict(self) -> dict[str, int]:
        return {
            "maximum_seeds": self.maximum_seeds,
            "maximum_queries": self.maximum_queries,
            "maximum_provider_requests": self.maximum_provider_requests,
            "maximum_fetches": self.maximum_fetches,
            "maximum_duration_seconds": self.maximum_duration_seconds,
            "maximum_bytes": self.maximum_bytes,
            "maximum_concurrency": self.maximum_concurrency,
            "per_domain_requests": self.per_domain_requests,
            "per_provider_requests": self.per_provider_requests,
            "retry_ceiling": self.retry_ceiling,
        }


@dataclass(frozen=True)
class SeedQuery:
    query: str
    source: str = "operator"
    enabled: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {"query": self.query, "source": self.source, "enabled": self.enabled}


@dataclass(frozen=True)
class SeedSource:
    source_type: str
    path: str = ""
    opt_in: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {"source_type": self.source_type, "path": self.path, "opt_in": self.opt_in}


@dataclass(frozen=True)
class FoundryPlan:
    plan_id: str
    seed_queries: tuple[SeedQuery, ...]
    providers: tuple[str, ...]
    budget: SurveyBudget
    network_enabled: bool = False
    refresh_policy: Mapping[str, Any] | None = None

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": FOUNDRY_PLAN_SCHEMA,
            "plan_id": self.plan_id,
            "seed_queries": [seed.to_dict() for seed in self.seed_queries],
            "providers": list(self.providers),
            "budget": self.budget.to_dict(),
            "network_enabled": self.network_enabled,
            "activation_state": "explicit_local_only" if self.network_enabled else "disabled",
            "network_calls_performed": False,
            "reviewed_master_mutation": False,
            "public_index_mutation": False,
            "refresh_policy": dict(self.refresh_policy or RefreshPolicy().to_dict()),
        }

    @staticmethod
    def from_mapping(payload: Mapping[str, Any]) -> "FoundryPlan":
        budget = _budget_from_mapping(payload.get("budget") if isinstance(payload.get("budget"), Mapping) else {})
        seeds = tuple(
            SeedQuery(str(item.get("query") or ""), str(item.get("source") or "operator"), bool(item.get("enabled", True)))
            for item in payload.get("seed_queries", [])
            if isinstance(item, Mapping) and str(item.get("query") or "").strip()
        )
        return FoundryPlan(
            plan_id=str(payload.get("plan_id") or _plan_id([seed.query for seed in seeds])),
            seed_queries=seeds,
            providers=tuple(str(item) for item in payload.get("providers", []) if str(item).strip()) or ("brave",),
            budget=budget,
            network_enabled=bool(payload.get("network_enabled", False)),
            refresh_policy=payload.get("refresh_policy") if isinstance(payload.get("refresh_policy"), Mapping) else None,
        )


@dataclass(frozen=True)
class FoundryCommand:
    action: str
    plan_path: str = ""
    run_id: str = ""


@dataclass(frozen=True)
class RefreshPolicy:
    interval_seconds: int = 7 * 24 * 60 * 60
    use_http_validators: bool = True

    def to_dict(self) -> dict[str, Any]:
        return {"interval_seconds": self.interval_seconds, "use_http_validators": self.use_http_validators}


@dataclass(frozen=True)
class RefreshCandidate:
    observation_ref: str
    eligibility: str
    reason: str

    def to_dict(self) -> dict[str, str]:
        return {"observation_ref": self.observation_ref, "eligibility": self.eligibility, "reason": self.reason}


@dataclass(frozen=True)
class SourceScorecard:
    provider: str
    provider_request_success: int = 0
    provider_request_error: int = 0
    fetch_success: int = 0
    robots_block_rate: float = 0.0
    duplicate_rate: float = 0.0
    new_observation_yield: int = 0
    new_preview_document_yield: int = 0
    error_rate: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "provider": self.provider,
            "provider_request_success": self.provider_request_success,
            "provider_request_error": self.provider_request_error,
            "provider_latency_ms": 0,
            "search_lead_yield": self.new_observation_yield,
            "fetch_success": self.fetch_success,
            "robots_block_rate": self.robots_block_rate,
            "duplicate_rate": self.duplicate_rate,
            "new_observation_yield": self.new_observation_yield,
            "new_preview_document_yield": self.new_preview_document_yield,
            "content_change_rate": 0.0,
            "error_rate": self.error_rate,
        }


@dataclass(frozen=True)
class FoundryCheckpoint:
    run_id: str
    completed_seeds: tuple[str, ...]
    pending_seeds: tuple[str, ...]
    observation_refs: tuple[str, ...]
    provider_budget_remaining: int
    fetch_budget_remaining: int
    state: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "eureka.foundry_checkpoint.v0",
            "run_id": self.run_id,
            "completed_seeds": list(self.completed_seeds),
            "pending_seeds": list(self.pending_seeds),
            "active_work_units": [],
            "observation_refs": list(self.observation_refs),
            "provider_budget_remaining": self.provider_budget_remaining,
            "fetch_budget_remaining": self.fetch_budget_remaining,
            "state": self.state,
        }


@dataclass(frozen=True)
class ReviewBatchPreparation:
    review_items: tuple[dict[str, Any], ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "eureka.review_batch_preparation.v0",
            "review_items": list(self.review_items),
            "review_decision": None,
            "automatic_review_decision": False,
        }


@dataclass(frozen=True)
class FoundryResult:
    payload: dict[str, Any]


class FoundryPlanner:
    def plan(
        self,
        seeds: Sequence[str],
        *,
        providers: Sequence[str] = ("brave",),
        budget: SurveyBudget | None = None,
        network_enabled: bool = False,
    ) -> FoundryPlan:
        clean_seeds = tuple(SeedQuery(" ".join(str(seed or "").split())) for seed in seeds if str(seed or "").strip())
        bounded = (budget or SurveyBudget()).bounded()
        selected = clean_seeds[: bounded.maximum_seeds] or (SeedQuery("manual for Sound Blaster CT1740"),)
        return FoundryPlan(
            plan_id=_plan_id([seed.query for seed in selected]),
            seed_queries=selected,
            providers=tuple(str(provider).strip() for provider in providers if str(provider).strip()) or ("brave",),
            budget=bounded,
            network_enabled=bool(network_enabled),
            refresh_policy=RefreshPolicy().to_dict(),
        )


class SeedQueue:
    def __init__(self, seeds: Sequence[SeedQuery]) -> None:
        self.pending = [seed for seed in seeds if seed.enabled]
        self.completed: list[SeedQuery] = []

    def pop(self) -> SeedQuery | None:
        if not self.pending:
            return None
        seed = self.pending.pop(0)
        self.completed.append(seed)
        return seed


class RefreshQueue:
    def candidates(self, observations: Sequence[Mapping[str, Any]]) -> list[RefreshCandidate]:
        return [
            RefreshCandidate(str(item.get("observation_id") or ""), "eligible", "stale observation refresh disabled until explicit run")
            for item in observations
            if str(item.get("observation_id") or "")
        ]


class SourceScorecardStore:
    def from_hunt_summaries(self, summaries: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
        cards: dict[str, SourceScorecard] = {}
        for summary in summaries:
            provider = str(summary.get("provider") or "unknown")
            success = int(summary.get("provider_request_count") or 0)
            errors = int(summary.get("provider_error_count") or 0)
            fetch_success = int(summary.get("pages_fetched") or 0)
            observations = int(summary.get("observations_created") or 0)
            documents = int(summary.get("documents_indexed") or 0)
            total = max(1, success + errors)
            cards[provider] = SourceScorecard(
                provider=provider,
                provider_request_success=success,
                provider_request_error=errors,
                fetch_success=fetch_success,
                duplicate_rate=round(float(summary.get("duplicates_removed") or 0) / max(1, int(summary.get("transient_lead_count") or 1)), 4),
                new_observation_yield=observations,
                new_preview_document_yield=documents,
                error_rate=round(errors / total, 4),
            )
        return [card.to_dict() for card in cards.values()]


class FoundryCheckpointStore:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)

    def write(self, checkpoint: FoundryCheckpoint) -> None:
        _atomic_write_json(self.path, checkpoint.to_dict())

    def read(self) -> dict[str, Any]:
        if not self.path.exists():
            return {}
        return json.loads(self.path.read_text(encoding="utf-8"))


class FoundryRunStore:
    def __init__(self, root: str | Path, run_id: str) -> None:
        self.root = Path(root) / run_id
        self.root.mkdir(parents=True, exist_ok=True)
        self.plan_path = self.root / "plan.json"
        self.result_path = self.root / "result.json"
        self.checkpoint_path = self.root / "checkpoint.json"
        self.review_batch_path = self.root / "review_batch.json"
        self.export_root = self.root / "exports"
        self.checkpoints = FoundryCheckpointStore(self.checkpoint_path)

    def write_plan(self, plan: FoundryPlan) -> None:
        _atomic_write_json(self.plan_path, plan.to_dict())

    def write_result(self, payload: Mapping[str, Any]) -> None:
        _atomic_write_json(self.result_path, payload)

    def pause(self) -> dict[str, Any]:
        return self._control("paused")

    def resume(self) -> dict[str, Any]:
        return self._control("running")

    def cancel(self) -> dict[str, Any]:
        return self._control("cancelled")

    def status(self) -> dict[str, Any]:
        result = _load_json_optional(self.result_path)
        checkpoint = self.checkpoints.read()
        return {"schema_version": "eureka.foundry_status.v0", "status": result.get("status") or checkpoint.get("state") or "not_started", "checkpoint": checkpoint, "result": result}

    def _control(self, state: str) -> dict[str, Any]:
        checkpoint = self.checkpoints.read()
        checkpoint["state"] = state
        _atomic_write_json(self.checkpoint_path, checkpoint)
        return {"schema_version": "eureka.foundry_control.v0", "status": state, "reviewed_master_mutation": False, "public_index_mutation": False}


class ReviewBatchPreparer:
    def prepare(self, observation_refs: Sequence[str], summaries: Sequence[Mapping[str, Any]]) -> ReviewBatchPreparation:
        clusters = conservative_identity_clusters(observation_refs)
        items = []
        for index, cluster in enumerate(clusters, start=1):
            items.append(
                {
                    "review_item_id": f"review-item:{index}",
                    "candidate_cluster": cluster,
                    "source_observation_refs": list(cluster["observation_refs"]),
                    "evidence_summary": "Unreviewed Foundry discovery; no automatic truth decision.",
                    "conflicting_claims": [],
                    "missing_information": ["human review"],
                    "source_diversity": len({str(summary.get("provider") or "unknown") for summary in summaries}),
                    "recommended_next_probes": [],
                    "review_decision": None,
                }
            )
        return ReviewBatchPreparation(tuple(items))


class FoundryService:
    def __init__(
        self,
        *,
        run_root: str | Path,
        index_store: SQLitePreviewIndexStore | None = None,
        provider_factory: Callable[[str], Any] = provider_from_environment,
        fetcher: Any | None = None,
    ) -> None:
        self.run_root = Path(run_root)
        self.index_store = index_store
        self.provider_factory = provider_factory
        self.fetcher = fetcher

    def plan(self, seeds: Sequence[str], *, providers: Sequence[str] = ("brave",), budget: SurveyBudget | None = None, network_enabled: bool = False) -> FoundryPlan:
        return FoundryPlanner().plan(seeds, providers=providers, budget=budget, network_enabled=network_enabled)

    def run(self, plan: FoundryPlan, *, run_id: str | None = None, enable_live: bool = False) -> FoundryResult:
        run_id = run_id or "foundry-" + plan.plan_id.split(":", 1)[-1]
        store = FoundryRunStore(self.run_root, run_id)
        store.write_plan(plan)
        if not (plan.network_enabled or enable_live):
            payload = _disabled_result(run_id, plan)
            store.write_result(payload)
            return FoundryResult(payload)
        seed_queue = SeedQueue(plan.seed_queries[: plan.budget.maximum_seeds])
        summaries: list[dict[str, Any]] = []
        observation_refs: list[str] = []
        completed: list[str] = []
        pending = [seed.query for seed in seed_queue.pending]
        while (seed := seed_queue.pop()) is not None:
            pending = [item.query for item in seed_queue.pending]
            completed.append(seed.query)
            engine = HuntEngine(
                provider_name=",".join(plan.providers),
                provider_factory=self.provider_factory,
                fetcher=self.fetcher,
                index_store=self.index_store,
            )
            result = engine.run(
                seed.query,
                run_id=f"{run_id}:{len(completed)}",
                budget=HuntBudget(
                    max_queries=plan.budget.maximum_queries,
                    max_provider_requests=plan.budget.maximum_provider_requests,
                    max_pages=1,
                    max_fetches=plan.budget.maximum_fetches,
                    max_depth=0,
                    max_links_followed=0,
                    max_duration_seconds=plan.budget.maximum_duration_seconds,
                    count=5,
                    timeout_seconds=15,
                ),
            )
            summary = dict(result.persisted_summary)
            summaries.append(summary)
            observation_refs.extend(str(ref) for ref in summary.get("observation_refs") or [] if str(ref))
            checkpoint = FoundryCheckpoint(
                run_id=run_id,
                completed_seeds=tuple(completed),
                pending_seeds=tuple(pending),
                observation_refs=tuple(observation_refs),
                provider_budget_remaining=max(0, plan.budget.maximum_provider_requests - sum(int(item.get("provider_request_count") or 0) for item in summaries)),
                fetch_budget_remaining=max(0, plan.budget.maximum_fetches - sum(int(item.get("fetch_attempt_count") or 0) for item in summaries)),
                state="running" if pending else "completed",
            )
            store.checkpoints.write(checkpoint)
        scorecards = SourceScorecardStore().from_hunt_summaries(summaries)
        review_batch = ReviewBatchPreparer().prepare(observation_refs, summaries)
        _atomic_write_json(store.review_batch_path, review_batch.to_dict())
        generation: dict[str, Any] = {}
        if self.index_store is not None:
            generation = self.index_store.export_generation(store.export_root)
        payload = {
            "schema_version": FOUNDRY_RUN_SCHEMA,
            "status": "pass",
            "run_id": run_id,
            "plan_id": plan.plan_id,
            "activation_state": "explicit_local_only",
            "seed_count": len(plan.seed_queries),
            "completed_seed_count": len(completed),
            "provider_request_count": sum(int(item.get("provider_request_count") or 0) for item in summaries),
            "fetch_attempt_count": sum(int(item.get("fetch_attempt_count") or 0) for item in summaries),
            "observation_refs": observation_refs,
            "observation_count": len(observation_refs),
            "preview_document_count": sum(int(item.get("documents_indexed") or 0) for item in summaries),
            "scorecards": scorecards,
            "refresh_candidates": [item.to_dict() for item in RefreshQueue().candidates([])],
            "identity_clusters": conservative_identity_clusters(observation_refs),
            "review_batch": review_batch.to_dict(),
            "generation": generation,
            "checkpoint": store.checkpoints.read(),
            "circuit_breakers": circuit_breakers_from_scorecards(scorecards),
            "reviewed_master_mutation": False,
            "public_index_mutation": False,
            "automatic_review_decision": False,
        }
        store.write_result(payload)
        return FoundryResult(payload)


def conservative_identity_clusters(observation_refs: Sequence[str]) -> list[dict[str, Any]]:
    clusters: list[dict[str, Any]] = []
    for ref in observation_refs:
        clusters.append({"cluster_id": "cluster:" + hashlib.sha256(str(ref).encode("utf-8")).hexdigest()[:12], "observation_refs": [str(ref)], "merge_confidence": "conservative"})
    return clusters


def circuit_breakers_from_scorecards(scorecards: Sequence[Mapping[str, Any]]) -> list[dict[str, Any]]:
    breakers = []
    for card in scorecards:
        if float(card.get("error_rate") or 0.0) >= 1.0:
            breakers.append({"provider": card.get("provider"), "state": "cooldown", "reason": "consecutive_failure_threshold"})
    return breakers


def load_plan(path: str | Path) -> FoundryPlan:
    return FoundryPlan.from_mapping(json.loads(Path(path).read_text(encoding="utf-8")))


def write_plan(path: str | Path, plan: FoundryPlan) -> None:
    _atomic_write_json(Path(path), plan.to_dict())


def _disabled_result(run_id: str, plan: FoundryPlan) -> dict[str, Any]:
    return {
        "schema_version": FOUNDRY_RUN_SCHEMA,
        "status": "disabled",
        "run_id": run_id,
        "plan_id": plan.plan_id,
        "activation_state": "disabled_waiting_for_explicit_live_enablement",
        "network_calls_performed": False,
        "message": "Foundry runs are disabled by default; rerun with an explicitly live-enabled plan or command.",
        "reviewed_master_mutation": False,
        "public_index_mutation": False,
        "automatic_review_decision": False,
    }


def _budget_from_mapping(payload: Mapping[str, Any]) -> SurveyBudget:
    return SurveyBudget(
        maximum_seeds=int(payload.get("maximum_seeds") or 1),
        maximum_queries=int(payload.get("maximum_queries") or 3),
        maximum_provider_requests=int(payload.get("maximum_provider_requests") or 3),
        maximum_fetches=int(payload.get("maximum_fetches") or 3),
        maximum_duration_seconds=int(payload.get("maximum_duration_seconds") or 120),
        maximum_bytes=int(payload.get("maximum_bytes") or 5 * 1024 * 1024),
        maximum_concurrency=int(payload.get("maximum_concurrency") or 1),
        per_domain_requests=int(payload.get("per_domain_requests") or 3),
        per_provider_requests=int(payload.get("per_provider_requests") or 3),
        retry_ceiling=int(payload.get("retry_ceiling") or 0),
    ).bounded()


def _plan_id(seeds: Sequence[str]) -> str:
    digest = hashlib.sha256("\n".join(seeds).encode("utf-8")).hexdigest()[:16]
    return f"foundry-plan:{digest}"


def _atomic_write_json(path: Path, payload: Mapping[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="\n", dir=path.parent, delete=False) as handle:
        json.dump(dict(payload), handle, indent=2, sort_keys=True)
        handle.write("\n")
        temp = Path(handle.name)
    temp.replace(path)


def _load_json_optional(path: Path) -> dict[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return {}
