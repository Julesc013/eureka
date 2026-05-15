"""Typed disabled agent research task and report-schema records."""

from dataclasses import dataclass, replace
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping, Sequence
import uuid


DEFAULT_LIMITATIONS = (
    "Agent research task is a disabled future escalation request.",
    "Agent research task output would be candidate material only.",
    "Review is required before any candidate can affect local review state.",
    "Provider execution is disabled.",
    "Browser execution is disabled.",
    "Source probes are disabled.",
    "Public and master index mutation is disabled.",
)


class AgentResearchTaskState(str, Enum):
    DRAFTED = "drafted"
    QUEUED_DISABLED = "queued_disabled"
    BLOCKED_BY_POLICY = "blocked_by_policy"
    WAITING_FOR_PROVIDER_GATE = "waiting_for_provider_gate"
    CANCELLED = "cancelled"
    SUPERSEDED = "superseded"


class AgentResearchGoal(str, Enum):
    ALIAS_HYPOTHESES = "alias_hypotheses"
    SOURCE_LEAD_CANDIDATES = "source_lead_candidates"
    DEAD_URL_TRACE_PLAN = "dead_url_trace_plan"
    WAYBACK_TRACE_PLAN = "wayback_trace_plan"
    COMPATIBILITY_CLUES = "compatibility_clues"
    PROVENANCE_QUESTIONS = "provenance_questions"
    EXTRACTION_TARGETS = "extraction_targets"
    NEAR_MISS_EXPLANATION = "near_miss_explanation"
    ABSENCE_EXPLANATION_DRAFT = "absence_explanation_draft"
    WORKUNIT_SUGGESTIONS = "workunit_suggestions"


class AgentResearchForbiddenAction(str, Enum):
    ACCEPT_TRUTH = "accept_truth"
    MUTATE_PUBLIC_INDEX = "mutate_public_index"
    MUTATE_MASTER_INDEX = "mutate_master_index"
    CLEAR_RIGHTS = "clear_rights"
    CERTIFY_MALWARE_SAFETY = "certify_malware_safety"
    DOWNLOAD_ARTIFACT = "download_artifact"
    INSTALL_OR_EXECUTE_ARTIFACT = "install_or_execute_artifact"
    BYPASS_AUTHENTICATION = "bypass_authentication"
    BYPASS_CAPTCHA = "bypass_captcha"
    SCRAPE_RESTRICTED_PLATFORM = "scrape_restricted_platform"
    CALL_MODEL_PROVIDER_CURRENT_TASK = "call_model_provider_current_task"
    RUN_BROWSER_CURRENT_TASK = "run_browser_current_task"
    RUN_SOURCE_PROBE_CURRENT_TASK = "run_source_probe_current_task"


@dataclass(frozen=True)
class AgentResearchReportSchema:
    schema_version: str
    required_fields: tuple[str, ...]
    review_required: bool
    candidate_only: bool
    public_index_mutation_performed: bool
    master_index_mutation_performed: bool
    forbidden_claims: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "required_fields": list(self.required_fields),
            "review_required": self.review_required,
            "candidate_only": self.candidate_only,
            "public_index_mutation_performed": self.public_index_mutation_performed,
            "master_index_mutation_performed": self.master_index_mutation_performed,
            "forbidden_claims": list(self.forbidden_claims),
        }


@dataclass(frozen=True)
class AgentResearchTask:
    task_id: str
    search_hunt_id: str
    search_need_id: str
    exhaustion_report_id: str
    query: str
    normalized_query: str
    intent: str
    destination: str
    checked_layers: tuple[str, ...]
    deferred_layers: tuple[str, ...]
    blocked_by_policy: tuple[str, ...]
    known_candidates: tuple[Mapping[str, Any], ...]
    known_absence_state: str
    steering_preferences: tuple[Mapping[str, Any], ...]
    allowed_source_families: tuple[str, ...]
    blocked_source_families: tuple[str, ...]
    research_goals: tuple[AgentResearchGoal, ...]
    forbidden_actions: tuple[AgentResearchForbiddenAction, ...]
    output_schema: Mapping[str, Any]
    provider_enabled: bool
    execution_enabled: bool
    created_at: str
    updated_at: str
    state: AgentResearchTaskState
    warnings: tuple[str, ...]
    limitations: tuple[str, ...]

    @classmethod
    def new(
        cls,
        *,
        search_hunt_id: str,
        search_need_id: str = "",
        exhaustion_report_id: str,
        query: str,
        intent: str = "",
        destination: str = "",
        checked_layers: Sequence[str] = (),
        deferred_layers: Sequence[str] = (),
        blocked_by_policy: Sequence[str] = (),
        known_candidates: Sequence[Mapping[str, Any]] = (),
        known_absence_state: str = "",
        steering_preferences: Sequence[Mapping[str, Any]] = (),
        allowed_source_families: Sequence[str] = (),
        blocked_source_families: Sequence[str] = (),
        research_goals: Sequence[AgentResearchGoal | str] = (),
        forbidden_actions: Sequence[AgentResearchForbiddenAction | str] = (),
        output_schema: Mapping[str, Any] | None = None,
        state: AgentResearchTaskState | str = AgentResearchTaskState.DRAFTED,
        warnings: Sequence[str] = (),
        limitations: Sequence[str] = DEFAULT_LIMITATIONS,
    ) -> "AgentResearchTask":
        now = utc_now()
        return cls(
            task_id="art_" + uuid.uuid4().hex,
            search_hunt_id=str(search_hunt_id),
            search_need_id=str(search_need_id or ""),
            exhaustion_report_id=str(exhaustion_report_id),
            query=str(query),
            normalized_query=normalize_query(query),
            intent=str(intent or ""),
            destination=str(destination or ""),
            checked_layers=tuple(str(item) for item in checked_layers),
            deferred_layers=tuple(str(item) for item in deferred_layers),
            blocked_by_policy=tuple(str(item) for item in blocked_by_policy),
            known_candidates=tuple(dict(item) for item in known_candidates),
            known_absence_state=str(known_absence_state or ""),
            steering_preferences=tuple(dict(item) for item in steering_preferences),
            allowed_source_families=tuple(str(item) for item in allowed_source_families),
            blocked_source_families=tuple(str(item) for item in blocked_source_families),
            research_goals=tuple(coerce_goal(item) for item in (research_goals or tuple(AgentResearchGoal))),
            forbidden_actions=tuple(coerce_forbidden_action(item) for item in (forbidden_actions or tuple(AgentResearchForbiddenAction))),
            output_schema=dict(output_schema or {}),
            provider_enabled=False,
            execution_enabled=False,
            created_at=now,
            updated_at=now,
            state=coerce_state(state),
            warnings=tuple(str(item) for item in warnings),
            limitations=tuple(str(item) for item in limitations),
        )

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "AgentResearchTask":
        return cls(
            task_id=str(payload.get("task_id", "")),
            search_hunt_id=str(payload.get("search_hunt_id", "")),
            search_need_id=str(payload.get("search_need_id", "")),
            exhaustion_report_id=str(payload.get("exhaustion_report_id", "")),
            query=str(payload.get("query", "")),
            normalized_query=str(payload.get("normalized_query", "")),
            intent=str(payload.get("intent", "")),
            destination=str(payload.get("destination", "")),
            checked_layers=tuple_text(payload.get("checked_layers")),
            deferred_layers=tuple_text(payload.get("deferred_layers")),
            blocked_by_policy=tuple_text(payload.get("blocked_by_policy")),
            known_candidates=tuple_mapping(payload.get("known_candidates")),
            known_absence_state=str(payload.get("known_absence_state", "")),
            steering_preferences=tuple_mapping(payload.get("steering_preferences")),
            allowed_source_families=tuple_text(payload.get("allowed_source_families")),
            blocked_source_families=tuple_text(payload.get("blocked_source_families")),
            research_goals=tuple(coerce_goal(item) for item in tuple_text(payload.get("research_goals"))),
            forbidden_actions=tuple(coerce_forbidden_action(item) for item in tuple_text(payload.get("forbidden_actions"))),
            output_schema=_mapping(payload.get("output_schema")),
            provider_enabled=bool(payload.get("provider_enabled", False)),
            execution_enabled=bool(payload.get("execution_enabled", False)),
            created_at=str(payload.get("created_at", "")),
            updated_at=str(payload.get("updated_at", "")),
            state=coerce_state(str(payload.get("state", AgentResearchTaskState.DRAFTED.value))),
            warnings=tuple_text(payload.get("warnings")),
            limitations=tuple_text(payload.get("limitations")),
        )

    def cancelled(self) -> "AgentResearchTask":
        return replace(self, state=AgentResearchTaskState.CANCELLED, updated_at=utc_now())

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "agent_research_task.v0",
            "task_id": self.task_id,
            "search_hunt_id": self.search_hunt_id,
            "search_need_id": self.search_need_id,
            "exhaustion_report_id": self.exhaustion_report_id,
            "query": self.query,
            "normalized_query": self.normalized_query,
            "intent": self.intent,
            "destination": self.destination,
            "checked_layers": list(self.checked_layers),
            "deferred_layers": list(self.deferred_layers),
            "blocked_by_policy": list(self.blocked_by_policy),
            "known_candidates": [dict(item) for item in self.known_candidates],
            "known_absence_state": self.known_absence_state,
            "steering_preferences": [dict(item) for item in self.steering_preferences],
            "allowed_source_families": list(self.allowed_source_families),
            "blocked_source_families": list(self.blocked_source_families),
            "research_goals": [item.value for item in self.research_goals],
            "forbidden_actions": [item.value for item in self.forbidden_actions],
            "output_schema": dict(self.output_schema),
            "provider_enabled": self.provider_enabled,
            "execution_enabled": self.execution_enabled,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "state": self.state.value,
            "warnings": list(self.warnings),
            "limitations": list(self.limitations),
            "model_provider_used": False,
            "external_network_used": False,
            "source_probe_executed": False,
            "review_mutation_performed": False,
            "public_index_mutated": False,
            "master_index_mutated": False,
            "deployment_performed": False,
            "production_readiness_claimed": False,
            "public_launch_readiness_claimed": False,
        }


@dataclass(frozen=True)
class AgentResearchTaskSummary:
    task_id: str
    search_hunt_id: str
    search_need_id: str
    query: str
    state: str
    provider_enabled: bool
    execution_enabled: bool

    def to_dict(self) -> dict[str, Any]:
        return {
            "task_id": self.task_id,
            "search_hunt_id": self.search_hunt_id,
            "search_need_id": self.search_need_id,
            "query": self.query,
            "state": self.state,
            "provider_enabled": self.provider_enabled,
            "execution_enabled": self.execution_enabled,
        }


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def normalize_query(query: str) -> str:
    return " ".join(str(query or "").strip().lower().split())


def coerce_state(value: AgentResearchTaskState | str) -> AgentResearchTaskState:
    return value if isinstance(value, AgentResearchTaskState) else AgentResearchTaskState(str(value))


def coerce_goal(value: AgentResearchGoal | str) -> AgentResearchGoal:
    return value if isinstance(value, AgentResearchGoal) else AgentResearchGoal(str(value))


def coerce_forbidden_action(value: AgentResearchForbiddenAction | str) -> AgentResearchForbiddenAction:
    return value if isinstance(value, AgentResearchForbiddenAction) else AgentResearchForbiddenAction(str(value))


def tuple_text(value: Any) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        return ()
    return tuple(str(item) for item in value)


def tuple_mapping(value: Any) -> tuple[Mapping[str, Any], ...]:
    if not isinstance(value, (list, tuple)):
        return ()
    return tuple(dict(item) for item in value if isinstance(item, Mapping))


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}
