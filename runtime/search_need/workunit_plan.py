"""Build local WorkUnit plans from SearchNeeds without executing work."""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Mapping, Sequence

from runtime.workunit_queue.records import WorkUnitPriority, WorkUnitType

from .errors import SearchNeedNotFoundError, SearchNeedValidationError
from .records import SearchNeed, SearchNeedKind


class SearchNeedWorkUnitPolicyState(str, Enum):
    QUEUED_LOCAL_SAFE = "queued_local_safe"
    BLOCKED_BY_POLICY = "blocked_by_policy"
    BLOCKED_UNTIL_EVIDENCE = "blocked_until_evidence"
    NOTE_ONLY = "note_only"


@dataclass(frozen=True)
class SearchNeedWorkUnitPlanItem:
    plan_item_id: str
    kind: WorkUnitType
    title: str
    policy_state: SearchNeedWorkUnitPolicyState
    reason: str
    priority: WorkUnitPriority
    payload: Mapping[str, Any]
    blocked_reason: str | None = None
    execution_enabled: bool = False
    source_probe_enabled: bool = False
    extraction_enabled: bool = False
    model_provider_enabled: bool = False

    def to_dict(self) -> dict[str, Any]:
        return {
            "plan_item_id": self.plan_item_id,
            "kind": self.kind.value,
            "title": self.title,
            "policy_state": self.policy_state.value,
            "reason": self.reason,
            "priority": self.priority.value,
            "payload": dict(self.payload),
            "blocked_reason": self.blocked_reason,
            "execution_enabled": self.execution_enabled,
            "source_probe_enabled": self.source_probe_enabled,
            "extraction_enabled": self.extraction_enabled,
            "model_provider_enabled": self.model_provider_enabled,
        }


@dataclass(frozen=True)
class SearchNeedWorkUnitPlan:
    need_id: str
    search_hunt_id: str
    exhaustion_report_id: str
    generated_from: str
    items: tuple[SearchNeedWorkUnitPlanItem, ...]
    warnings: tuple[str, ...]
    limitations: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "search_need_workunit_plan.v0",
            "need_id": self.need_id,
            "search_hunt_id": self.search_hunt_id,
            "exhaustion_report_id": self.exhaustion_report_id,
            "generated_from": self.generated_from,
            "item_count": len(self.items),
            "items": [item.to_dict() for item in self.items],
            "workunit_execution_enabled": False,
            "source_probe_execution_enabled": False,
            "extraction_execution_enabled": False,
            "model_provider_enabled": False,
            "warnings": list(self.warnings),
            "limitations": list(self.limitations),
        }


@dataclass(frozen=True)
class SearchNeedWorkUnitCreationResult:
    need_id: str
    search_hunt_id: str
    exhaustion_report_id: str
    plan: SearchNeedWorkUnitPlan
    workunits: tuple[Mapping[str, Any], ...]
    created_count: int
    linked_count: int
    warnings: tuple[str, ...]
    limitations: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "search_need_workunit_creation_result.v0",
            "need_id": self.need_id,
            "search_hunt_id": self.search_hunt_id,
            "exhaustion_report_id": self.exhaustion_report_id,
            "plan": self.plan.to_dict(),
            "workunit_count": len(self.workunits),
            "created_count": self.created_count,
            "linked_count": self.linked_count,
            "workunits": [dict(item) for item in self.workunits],
            "workunit_execution_performed": False,
            "source_probe_executed": False,
            "extraction_executed": False,
            "external_network_used": False,
            "model_provider_used": False,
            "review_mutation_performed": False,
            "public_index_mutated": False,
            "master_index_mutated": False,
            "deployment_performed": False,
            "warnings": list(self.warnings),
            "limitations": list(self.limitations),
        }


def build_workunit_plan_for_need(runtime: Any, need_id: str, *, operator_label: str | None = None) -> SearchNeedWorkUnitPlan:
    need = runtime.search_need.get_need(need_id)
    if need is None:
        raise SearchNeedNotFoundError(f"SearchNeed not found: {need_id}")
    return validate_workunit_plan(map_need_kind_to_workunit_plan(need))


def map_need_kind_to_workunit_plan(need: SearchNeed) -> SearchNeedWorkUnitPlan:
    item_specs = _item_specs_for_kind(need.need_kind)
    items = tuple(_plan_item(need, index, spec) for index, spec in enumerate(item_specs, start=1) if spec[2] is not SearchNeedWorkUnitPolicyState.NOTE_ONLY)
    return SearchNeedWorkUnitPlan(
        need_id=need.id,
        search_hunt_id=need.hunt_id,
        exhaustion_report_id=need.exhaustion_report_id,
        generated_from="search_need_workunit_pipeline",
        items=items,
        warnings=tuple(need.warnings),
        limitations=(
            "WorkUnit records are local queue records only",
            "WorkUnit execution remains disabled",
            "source probes, extraction, and model/provider calls remain disabled",
        ),
    )


def validate_workunit_plan(plan: SearchNeedWorkUnitPlan) -> SearchNeedWorkUnitPlan:
    if not plan.need_id:
        raise SearchNeedValidationError("WorkUnit plan requires a SearchNeed id")
    if not plan.items:
        return plan
    for item in plan.items:
        if item.execution_enabled:
            raise SearchNeedValidationError("WorkUnit plan item must not enable execution")
        if item.source_probe_enabled:
            raise SearchNeedValidationError("WorkUnit plan item must not enable source probes")
        if item.extraction_enabled:
            raise SearchNeedValidationError("WorkUnit plan item must not enable extraction")
        if item.model_provider_enabled:
            raise SearchNeedValidationError("WorkUnit plan item must not enable model providers")
        if item.kind == WorkUnitType.SOURCE_PROBE and item.policy_state is not SearchNeedWorkUnitPolicyState.BLOCKED_BY_POLICY:
            raise SearchNeedValidationError("source probe WorkUnits must be blocked by policy")
        if item.kind in {WorkUnitType.EXTRACTION_TASK, WorkUnitType.DELEGATED_OPERATOR} and item.policy_state is not SearchNeedWorkUnitPolicyState.BLOCKED_BY_POLICY:
            raise SearchNeedValidationError("policy-gated WorkUnits must be blocked by policy")
    return plan


def _item_specs_for_kind(
    kind: SearchNeedKind,
) -> tuple[tuple[WorkUnitType, str, SearchNeedWorkUnitPolicyState, str, WorkUnitPriority], ...]:
    regression = (
        WorkUnitType.REGRESSION_TEST,
        "Run deterministic local regression check",
        SearchNeedWorkUnitPolicyState.QUEUED_LOCAL_SAFE,
        "Local-safe regression checks can be queued while the runner remains disabled.",
        WorkUnitPriority.NORMAL,
    )
    source_probe = (
        WorkUnitType.SOURCE_PROBE,
        "Prepare policy-gated source probe",
        SearchNeedWorkUnitPolicyState.BLOCKED_BY_POLICY,
        "Source probes require a later source policy gate.",
        WorkUnitPriority.NORMAL,
    )
    evidence_review = (
        WorkUnitType.EVIDENCE_REVIEW,
        "Review evidence when available",
        SearchNeedWorkUnitPolicyState.BLOCKED_UNTIL_EVIDENCE,
        "Evidence review waits for evidence produced by a future allowed path.",
        WorkUnitPriority.NORMAL,
    )
    queued_evidence_review = (
        WorkUnitType.EVIDENCE_REVIEW,
        "Review local provenance state",
        SearchNeedWorkUnitPolicyState.QUEUED_LOCAL_SAFE,
        "Local review planning can be queued without accepting evidence.",
        WorkUnitPriority.NORMAL,
    )
    delegated = (
        WorkUnitType.DELEGATED_OPERATOR,
        "Prepare policy-gated delegated research request",
        SearchNeedWorkUnitPolicyState.BLOCKED_BY_POLICY,
        "Delegated research remains disabled until a later provider gate.",
        WorkUnitPriority.LOW,
    )
    extraction = (
        WorkUnitType.EXTRACTION_TASK,
        "Prepare policy-gated extraction request",
        SearchNeedWorkUnitPolicyState.BLOCKED_BY_POLICY,
        "Extraction remains deferred behind a later safety gate.",
        WorkUnitPriority.NORMAL,
    )
    policy_review = (
        WorkUnitType.EVIDENCE_REVIEW,
        "Record policy review note for blocked need",
        SearchNeedWorkUnitPolicyState.BLOCKED_BY_POLICY,
        "Policy-blocked needs produce only blocked local queue records by default.",
        WorkUnitPriority.LOW,
    )
    mapping = {
        SearchNeedKind.FIND_EXACT_ARTIFACT: (regression, source_probe, evidence_review),
        SearchNeedKind.FIND_COMPATIBLE_VERSION: (regression, source_probe, evidence_review),
        SearchNeedKind.FIND_SOURCE_OR_MIRROR: (source_probe, evidence_review),
        SearchNeedKind.IDENTIFY_UNKNOWN_ARTIFACT: (regression, source_probe, delegated),
        SearchNeedKind.VERIFY_PROVENANCE: (queued_evidence_review, source_probe),
        SearchNeedKind.EXTRACT_HIDDEN_MEMBER: (extraction,),
        SearchNeedKind.IMPROVE_ABSENCE_REPORT: (regression, source_probe),
        SearchNeedKind.IMPROVE_RANKING_OR_IDENTITY: (regression, queued_evidence_review),
        SearchNeedKind.SOURCE_GAP: (source_probe,),
        SearchNeedKind.POLICY_BLOCKED_NEED: (policy_review,),
    }
    return mapping[kind]


def _plan_item(
    need: SearchNeed,
    index: int,
    spec: tuple[WorkUnitType, str, SearchNeedWorkUnitPolicyState, str, WorkUnitPriority],
) -> SearchNeedWorkUnitPlanItem:
    kind, title, policy_state, reason, priority = spec
    plan_item_id = f"{kind.value}_{index}"
    blocked_reason = reason if policy_state in {SearchNeedWorkUnitPolicyState.BLOCKED_BY_POLICY, SearchNeedWorkUnitPolicyState.BLOCKED_UNTIL_EVIDENCE} else None
    payload = {
        "search_need_id": need.id,
        "search_hunt_id": need.hunt_id,
        "exhaustion_report_id": need.exhaustion_report_id,
        "generated_from": "search_need_workunit_pipeline",
        "plan_item_id": plan_item_id,
        "need_kind": need.need_kind.value,
        "local_result_state": need.local_result_state,
        "policy_state": policy_state.value,
        "execution_enabled": False,
        "source_probe_enabled": False,
        "source_probe_execution_enabled": False,
        "extraction_enabled": False,
        "extraction_execution_enabled": False,
        "model_provider_enabled": False,
        "public_index_mutation_enabled": False,
        "master_index_mutation_enabled": False,
    }
    return SearchNeedWorkUnitPlanItem(
        plan_item_id=plan_item_id,
        kind=kind,
        title=title,
        policy_state=policy_state,
        reason=reason,
        priority=priority,
        payload=payload,
        blocked_reason=blocked_reason,
    )
