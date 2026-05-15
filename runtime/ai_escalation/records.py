"""Typed disabled AI escalation gate records."""

from dataclasses import dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping, Sequence
import uuid


DEFAULT_LIMITATIONS = (
    "AI escalation gate is disabled by default.",
    "Provider use is disabled.",
    "Escalation output would be candidate material only.",
    "Review is required before candidates can affect local state.",
    "Source probes and extraction are disabled.",
    "Public and master index mutation is disabled.",
)


class AIEscalationGateState(str, Enum):
    DISABLED_BY_DEFAULT = "disabled_by_default"
    ELIGIBLE_BUT_DISABLED = "eligible_but_disabled"
    BLOCKED_MISSING_EXHAUSTION_REPORT = "blocked_missing_exhaustion_report"
    BLOCKED_MISSING_SEARCH_NEED = "blocked_missing_search_need"
    BLOCKED_BY_POLICY = "blocked_by_policy"
    WAITING_FOR_OPERATOR_APPROVAL = "waiting_for_operator_approval"
    WAITING_FOR_PROVIDER_GATE = "waiting_for_provider_gate"
    CANCELLED = "cancelled"
    SUPERSEDED = "superseded"


class AIEscalationOutputClass(str, Enum):
    ALIAS_HYPOTHESES = "alias_hypotheses"
    SOURCE_LEAD_CANDIDATES = "source_lead_candidates"
    DEAD_URL_TRACE_PLAN = "dead_url_trace_plan"
    WAYBACK_TRACE_PLAN = "wayback_trace_plan"
    COMPATIBILITY_CLUES = "compatibility_clues"
    PROVENANCE_QUESTIONS = "provenance_questions"
    EXTRACTION_TARGETS = "extraction_targets"
    CANDIDATE_WORKUNITS = "candidate_workunits"
    ABSENCE_EXPLANATION_DRAFT = "absence_explanation_draft"


class AIEscalationForbiddenAction(str, Enum):
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
    RUN_EXTRACTION_CURRENT_TASK = "run_extraction_current_task"


@dataclass(frozen=True)
class AIEscalationInputPacket:
    search_hunt_id: str
    search_need_id: str
    exhaustion_report_id: str
    agent_research_task_id: str
    query: str
    normalized_query: str
    checked_layers: tuple[str, ...]
    deferred_layers: tuple[str, ...]
    blocked_by_policy: tuple[str, ...]
    steering_preferences: tuple[Mapping[str, Any], ...]
    candidate_context: tuple[Mapping[str, Any], ...]
    absence_context: Mapping[str, Any]
    forbidden_actions: tuple[AIEscalationForbiddenAction, ...]
    desired_output_schema: Mapping[str, Any]
    provider_enabled: bool = False
    execution_enabled: bool = False

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "AIEscalationInputPacket":
        return cls(
            search_hunt_id=str(payload.get("search_hunt_id", "")),
            search_need_id=str(payload.get("search_need_id", "")),
            exhaustion_report_id=str(payload.get("exhaustion_report_id", "")),
            agent_research_task_id=str(payload.get("agent_research_task_id", "")),
            query=str(payload.get("query", "")),
            normalized_query=str(payload.get("normalized_query", "")),
            checked_layers=tuple_text(payload.get("checked_layers")),
            deferred_layers=tuple_text(payload.get("deferred_layers")),
            blocked_by_policy=tuple_text(payload.get("blocked_by_policy")),
            steering_preferences=tuple_mapping(payload.get("steering_preferences")),
            candidate_context=tuple_mapping(payload.get("candidate_context")),
            absence_context=_mapping(payload.get("absence_context")),
            forbidden_actions=tuple(coerce_forbidden_action(item) for item in tuple_text(payload.get("forbidden_actions"))),
            desired_output_schema=_mapping(payload.get("desired_output_schema")),
            provider_enabled=bool(payload.get("provider_enabled", False)),
            execution_enabled=bool(payload.get("execution_enabled", False)),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "ai_escalation_input_packet.v0",
            "search_hunt_id": self.search_hunt_id,
            "search_need_id": self.search_need_id,
            "exhaustion_report_id": self.exhaustion_report_id,
            "agent_research_task_id": self.agent_research_task_id,
            "query": self.query,
            "normalized_query": self.normalized_query,
            "checked_layers": list(self.checked_layers),
            "deferred_layers": list(self.deferred_layers),
            "blocked_by_policy": list(self.blocked_by_policy),
            "steering_preferences": [dict(item) for item in self.steering_preferences],
            "candidate_context": [dict(item) for item in self.candidate_context],
            "absence_context": dict(self.absence_context),
            "forbidden_actions": [item.value for item in self.forbidden_actions],
            "desired_output_schema": dict(self.desired_output_schema),
            "provider_enabled": False,
            "execution_enabled": False,
        }


@dataclass(frozen=True)
class AIEscalationEligibility:
    state: AIEscalationGateState
    eligible: bool
    input_packet: AIEscalationInputPacket
    missing_requirements: tuple[str, ...]
    warnings: tuple[str, ...]
    limitations: tuple[str, ...]
    provider_enabled: bool = False
    execution_enabled: bool = False

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "AIEscalationEligibility":
        return cls(
            state=coerce_state(str(payload.get("state", AIEscalationGateState.DISABLED_BY_DEFAULT.value))),
            eligible=bool(payload.get("eligible", False)),
            input_packet=AIEscalationInputPacket.from_dict(_mapping(payload.get("input_packet"))),
            missing_requirements=tuple_text(payload.get("missing_requirements")),
            warnings=tuple_text(payload.get("warnings")),
            limitations=tuple_text(payload.get("limitations")) or DEFAULT_LIMITATIONS,
            provider_enabled=False,
            execution_enabled=False,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "ai_escalation_eligibility.v0",
            "state": self.state.value,
            "eligible": self.eligible,
            "input_packet": self.input_packet.to_dict(),
            "missing_requirements": list(self.missing_requirements),
            "warnings": list(self.warnings),
            "limitations": list(self.limitations),
            "provider_enabled": False,
            "execution_enabled": False,
        }


@dataclass(frozen=True)
class AIEscalationGate:
    gate_id: str
    search_hunt_id: str
    search_need_id: str
    exhaustion_report_id: str
    agent_research_task_id: str
    query: str
    normalized_query: str
    state: AIEscalationGateState
    eligibility: AIEscalationEligibility
    input_packet: AIEscalationInputPacket
    output_classes: tuple[AIEscalationOutputClass, ...]
    forbidden_actions: tuple[AIEscalationForbiddenAction, ...]
    provider_enabled: bool
    execution_enabled: bool
    candidate_only_output: bool
    review_required: bool
    created_at: str
    updated_at: str
    operator_label: str
    warnings: tuple[str, ...]
    limitations: tuple[str, ...]

    @classmethod
    def new(
        cls,
        eligibility: AIEscalationEligibility,
        *,
        operator_label: str | None = None,
        state: AIEscalationGateState | str | None = None,
    ) -> "AIEscalationGate":
        packet = eligibility.input_packet
        now = utc_now()
        return cls(
            gate_id="aig_" + uuid.uuid4().hex,
            search_hunt_id=packet.search_hunt_id,
            search_need_id=packet.search_need_id,
            exhaustion_report_id=packet.exhaustion_report_id,
            agent_research_task_id=packet.agent_research_task_id,
            query=packet.query,
            normalized_query=packet.normalized_query,
            state=coerce_state(state or eligibility.state),
            eligibility=eligibility,
            input_packet=packet,
            output_classes=tuple(AIEscalationOutputClass),
            forbidden_actions=tuple(AIEscalationForbiddenAction),
            provider_enabled=False,
            execution_enabled=False,
            candidate_only_output=True,
            review_required=True,
            created_at=now,
            updated_at=now,
            operator_label=str(operator_label or "local_operator"),
            warnings=tuple(eligibility.warnings),
            limitations=tuple(eligibility.limitations) or DEFAULT_LIMITATIONS,
        )

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "AIEscalationGate":
        eligibility = AIEscalationEligibility.from_dict(_mapping(payload.get("eligibility")))
        packet = AIEscalationInputPacket.from_dict(_mapping(payload.get("input_packet")) or eligibility.input_packet.to_dict())
        return cls(
            gate_id=str(payload.get("gate_id", "")),
            search_hunt_id=str(payload.get("search_hunt_id", "")),
            search_need_id=str(payload.get("search_need_id", "")),
            exhaustion_report_id=str(payload.get("exhaustion_report_id", "")),
            agent_research_task_id=str(payload.get("agent_research_task_id", "")),
            query=str(payload.get("query", "")),
            normalized_query=str(payload.get("normalized_query", "")),
            state=coerce_state(str(payload.get("state", AIEscalationGateState.DISABLED_BY_DEFAULT.value))),
            eligibility=eligibility,
            input_packet=packet,
            output_classes=tuple(coerce_output_class(item) for item in tuple_text(payload.get("output_classes"))),
            forbidden_actions=tuple(coerce_forbidden_action(item) for item in tuple_text(payload.get("forbidden_actions"))),
            provider_enabled=False,
            execution_enabled=False,
            candidate_only_output=bool(payload.get("candidate_only_output", True)),
            review_required=bool(payload.get("review_required", True)),
            created_at=str(payload.get("created_at", "")),
            updated_at=str(payload.get("updated_at", "")),
            operator_label=str(payload.get("operator_label", "")),
            warnings=tuple_text(payload.get("warnings")),
            limitations=tuple_text(payload.get("limitations")) or DEFAULT_LIMITATIONS,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "ai_escalation_gate.v0",
            "gate_id": self.gate_id,
            "search_hunt_id": self.search_hunt_id,
            "search_need_id": self.search_need_id,
            "exhaustion_report_id": self.exhaustion_report_id,
            "agent_research_task_id": self.agent_research_task_id,
            "query": self.query,
            "normalized_query": self.normalized_query,
            "state": self.state.value,
            "eligibility": self.eligibility.to_dict(),
            "input_packet": self.input_packet.to_dict(),
            "output_classes": [item.value for item in self.output_classes],
            "forbidden_actions": [item.value for item in self.forbidden_actions],
            "provider_enabled": False,
            "execution_enabled": False,
            "candidate_only_output": True,
            "review_required": True,
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "operator_label": self.operator_label,
            "warnings": list(self.warnings),
            "limitations": list(self.limitations),
            "model_provider_used": False,
            "external_network_used": False,
            "source_probe_executed": False,
            "extraction_executed": False,
            "review_mutation_performed": False,
            "public_index_mutated": False,
            "master_index_mutated": False,
            "deployment_performed": False,
            "production_readiness_claimed": False,
            "public_launch_readiness_claimed": False,
        }


@dataclass(frozen=True)
class AIEscalationPreflightResult:
    preflight_id: str
    gate_id: str
    search_hunt_id: str
    search_need_id: str
    exhaustion_report_id: str
    agent_research_task_id: str
    state: AIEscalationGateState
    eligibility: AIEscalationEligibility
    input_packet: AIEscalationInputPacket
    output_classes: tuple[AIEscalationOutputClass, ...]
    forbidden_actions: tuple[AIEscalationForbiddenAction, ...]
    safety_checks: Mapping[str, Any]
    provider_enabled: bool
    execution_enabled: bool
    created_at: str
    operator_label: str
    warnings: tuple[str, ...]
    limitations: tuple[str, ...]

    @classmethod
    def new(cls, eligibility: AIEscalationEligibility, *, operator_label: str | None = None, gate_id: str = "") -> "AIEscalationPreflightResult":
        packet = eligibility.input_packet
        return cls(
            preflight_id="aip_" + uuid.uuid4().hex,
            gate_id=str(gate_id or ""),
            search_hunt_id=packet.search_hunt_id,
            search_need_id=packet.search_need_id,
            exhaustion_report_id=packet.exhaustion_report_id,
            agent_research_task_id=packet.agent_research_task_id,
            state=eligibility.state,
            eligibility=eligibility,
            input_packet=packet,
            output_classes=tuple(AIEscalationOutputClass),
            forbidden_actions=tuple(AIEscalationForbiddenAction),
            safety_checks=default_safety_checks(),
            provider_enabled=False,
            execution_enabled=False,
            created_at=utc_now(),
            operator_label=str(operator_label or "local_operator"),
            warnings=tuple(eligibility.warnings),
            limitations=tuple(eligibility.limitations) or DEFAULT_LIMITATIONS,
        )

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "AIEscalationPreflightResult":
        eligibility = AIEscalationEligibility.from_dict(_mapping(payload.get("eligibility")))
        packet = AIEscalationInputPacket.from_dict(_mapping(payload.get("input_packet")) or eligibility.input_packet.to_dict())
        return cls(
            preflight_id=str(payload.get("preflight_id", "")),
            gate_id=str(payload.get("gate_id", "")),
            search_hunt_id=str(payload.get("search_hunt_id", "")),
            search_need_id=str(payload.get("search_need_id", "")),
            exhaustion_report_id=str(payload.get("exhaustion_report_id", "")),
            agent_research_task_id=str(payload.get("agent_research_task_id", "")),
            state=coerce_state(str(payload.get("state", AIEscalationGateState.DISABLED_BY_DEFAULT.value))),
            eligibility=eligibility,
            input_packet=packet,
            output_classes=tuple(coerce_output_class(item) for item in tuple_text(payload.get("output_classes"))),
            forbidden_actions=tuple(coerce_forbidden_action(item) for item in tuple_text(payload.get("forbidden_actions"))),
            safety_checks=_mapping(payload.get("safety_checks")),
            provider_enabled=False,
            execution_enabled=False,
            created_at=str(payload.get("created_at", "")),
            operator_label=str(payload.get("operator_label", "")),
            warnings=tuple_text(payload.get("warnings")),
            limitations=tuple_text(payload.get("limitations")) or DEFAULT_LIMITATIONS,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "ai_escalation_preflight.v0",
            "preflight_id": self.preflight_id,
            "gate_id": self.gate_id,
            "search_hunt_id": self.search_hunt_id,
            "search_need_id": self.search_need_id,
            "exhaustion_report_id": self.exhaustion_report_id,
            "agent_research_task_id": self.agent_research_task_id,
            "state": self.state.value,
            "eligibility": self.eligibility.to_dict(),
            "input_packet": self.input_packet.to_dict(),
            "output_classes": [item.value for item in self.output_classes],
            "forbidden_actions": [item.value for item in self.forbidden_actions],
            "safety_checks": dict(self.safety_checks),
            "provider_enabled": False,
            "execution_enabled": False,
            "created_at": self.created_at,
            "operator_label": self.operator_label,
            "warnings": list(self.warnings),
            "limitations": list(self.limitations),
            "model_provider_used": False,
            "external_network_used": False,
            "source_probe_executed": False,
            "extraction_executed": False,
            "review_mutation_performed": False,
            "public_index_mutated": False,
            "master_index_mutated": False,
            "deployment_performed": False,
            "production_readiness_claimed": False,
            "public_launch_readiness_claimed": False,
        }


def default_output_schema() -> dict[str, Any]:
    return {
        "schema_version": "ai_escalation_future_output_schema.v0",
        "candidate_only": True,
        "review_required": True,
        "output_classes": [item.value for item in AIEscalationOutputClass],
        "public_index_mutation_performed": False,
        "master_index_mutation_performed": False,
    }


def default_safety_checks() -> dict[str, Any]:
    return {
        "provider_enabled": False,
        "execution_enabled": False,
        "browser_calls_enabled": False,
        "external_network_enabled": False,
        "source_probe_enabled": False,
        "extraction_enabled": False,
        "candidate_only_output": True,
        "review_required": True,
        "preflight_only": True,
    }


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def normalize_query(query: str) -> str:
    return " ".join(str(query or "").strip().lower().split())


def coerce_state(value: AIEscalationGateState | str) -> AIEscalationGateState:
    return value if isinstance(value, AIEscalationGateState) else AIEscalationGateState(str(value))


def coerce_output_class(value: AIEscalationOutputClass | str) -> AIEscalationOutputClass:
    return value if isinstance(value, AIEscalationOutputClass) else AIEscalationOutputClass(str(value))


def coerce_forbidden_action(value: AIEscalationForbiddenAction | str) -> AIEscalationForbiddenAction:
    return value if isinstance(value, AIEscalationForbiddenAction) else AIEscalationForbiddenAction(str(value))


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
