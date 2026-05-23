"""Background Search Hunt run records."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping, Sequence
import uuid


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def new_run_id() -> str:
    return "shr_" + uuid.uuid4().hex


class BackgroundHuntRunStatus(str, Enum):
    PLANNED = "planned"
    RUNNING = "running"
    COMPLETE = "complete"
    FAILED = "failed"
    BLOCKED = "blocked"
    SKIPPED = "skipped"


@dataclass(frozen=True)
class BackgroundHuntWorkerPolicyDecision:
    worker_kind: str
    workunit_id: str
    allowed: bool
    status: str
    reason: str
    external_network_allowed: bool = False
    source_probe_allowed: bool = False
    extraction_allowed: bool = False
    model_provider_allowed: bool = False
    download_allowed: bool = False
    install_execution_allowed: bool = False
    deployment_allowed: bool = False
    master_index_mutation_allowed: bool = False

    @classmethod
    def from_mapping(cls, payload: Mapping[str, Any], workunit_id: str) -> "BackgroundHuntWorkerPolicyDecision":
        return cls(
            worker_kind=str(payload.get("worker_kind") or ""),
            workunit_id=str(payload.get("workunit_id") or workunit_id),
            allowed=bool(payload.get("allowed", False)),
            status=str(payload.get("status") or "blocked"),
            reason=str(payload.get("reason") or ""),
            external_network_allowed=bool(payload.get("external_network_allowed", False)),
            source_probe_allowed=bool(payload.get("source_probe_allowed", False)),
            extraction_allowed=bool(payload.get("extraction_allowed", False)),
            model_provider_allowed=bool(payload.get("model_provider_allowed", False)),
            download_allowed=bool(payload.get("download_allowed", False)),
            install_execution_allowed=bool(payload.get("install_execution_allowed", False)),
            deployment_allowed=bool(payload.get("deployment_allowed", False)),
            master_index_mutation_allowed=bool(payload.get("master_index_mutation_allowed", False)),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "background_hunt_worker_policy_decision.v0",
            "worker_kind": self.worker_kind,
            "workunit_id": self.workunit_id,
            "allowed": self.allowed,
            "status": self.status,
            "reason": self.reason,
            "external_network_allowed": self.external_network_allowed,
            "source_probe_allowed": self.source_probe_allowed,
            "extraction_allowed": self.extraction_allowed,
            "model_provider_allowed": self.model_provider_allowed,
            "download_allowed": self.download_allowed,
            "install_execution_allowed": self.install_execution_allowed,
            "deployment_allowed": self.deployment_allowed,
            "master_index_mutation_allowed": self.master_index_mutation_allowed,
        }


@dataclass(frozen=True)
class BackgroundHuntPlanItem:
    workunit_id: str
    search_need_id: str
    hunt_id: str
    exhaustion_report_id: str
    workunit_kind: str
    worker_kind: str
    state: str
    title: str
    policy_state: str
    runnable: bool
    blocked_reason: str
    policy_decision: BackgroundHuntWorkerPolicyDecision

    def to_dict(self) -> dict[str, Any]:
        return {
            "workunit_id": self.workunit_id,
            "search_need_id": self.search_need_id,
            "hunt_id": self.hunt_id,
            "exhaustion_report_id": self.exhaustion_report_id,
            "workunit_kind": self.workunit_kind,
            "worker_kind": self.worker_kind,
            "state": self.state,
            "title": self.title,
            "policy_state": self.policy_state,
            "runnable": self.runnable,
            "blocked_reason": self.blocked_reason,
            "policy_decision": self.policy_decision.to_dict(),
            "source_probe_executed": False,
            "extraction_executed": False,
            "model_provider_used": False,
        }


@dataclass(frozen=True)
class BackgroundHuntPlan:
    hunt_id: str
    items: tuple[BackgroundHuntPlanItem, ...]
    max_workunits_per_batch: int = 10
    default_limit: int = 1
    warnings: tuple[str, ...] = ()
    limitations: tuple[str, ...] = (
        "only deterministic local workers are considered",
        "policy-blocked WorkUnits remain blocked",
    )

    @property
    def runnable_items(self) -> tuple[BackgroundHuntPlanItem, ...]:
        return tuple(item for item in self.items if item.runnable)

    @property
    def blocked_items(self) -> tuple[BackgroundHuntPlanItem, ...]:
        return tuple(item for item in self.items if not item.runnable)

    @property
    def runnable_count(self) -> int:
        return len(self.runnable_items)

    @property
    def blocked_count(self) -> int:
        return len(self.blocked_items)

    def to_dict(self) -> dict[str, Any]:
        runnable = self.runnable_items
        blocked = self.blocked_items
        return {
            "schema_version": "background_hunt_plan.v0",
            "hunt_id": self.hunt_id,
            "item_count": len(self.items),
            "runnable_count": len(runnable),
            "blocked_count": len(blocked),
            "items": [item.to_dict() for item in self.items],
            "runnable_workunits": [item.to_dict() for item in runnable],
            "blocked_workunits": [item.to_dict() for item in blocked],
            "default_limit": self.default_limit,
            "max_workunits_per_batch": self.max_workunits_per_batch,
            "workunit_execution_enabled_for_safe_workers": True,
            "source_probe_execution_enabled": False,
            "extraction_execution_enabled": False,
            "model_provider_enabled": False,
            "external_network_enabled": False,
            "warnings": list(self.warnings),
            "limitations": list(self.limitations),
        }


@dataclass(frozen=True)
class BackgroundHuntRun:
    run_id: str
    hunt_id: str
    search_need_ids: tuple[str, ...]
    workunit_ids: tuple[str, ...]
    worker_kinds: tuple[str, ...]
    started_at: str
    finished_at: str | None
    status: BackgroundHuntRunStatus
    policy_decision: Mapping[str, Any]
    worker_results: tuple[Mapping[str, Any], ...]
    blocked_workunits: tuple[Mapping[str, Any], ...]
    warnings: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()

    @classmethod
    def new(
        cls,
        hunt_id: str,
        *,
        status: BackgroundHuntRunStatus | str,
        search_need_ids: Sequence[str],
        workunit_ids: Sequence[str],
        worker_kinds: Sequence[str],
        policy_decision: Mapping[str, Any],
        worker_results: Sequence[Mapping[str, Any]] = (),
        blocked_workunits: Sequence[Mapping[str, Any]] = (),
        warnings: Sequence[str] = (),
        limitations: Sequence[str] = (),
        started_at: str | None = None,
        finished_at: str | None = None,
    ) -> "BackgroundHuntRun":
        return cls(
            run_id=new_run_id(),
            hunt_id=str(hunt_id),
            search_need_ids=tuple(str(item) for item in search_need_ids if str(item)),
            workunit_ids=tuple(str(item) for item in workunit_ids if str(item)),
            worker_kinds=tuple(str(item) for item in worker_kinds if str(item)),
            started_at=started_at or utc_now(),
            finished_at=finished_at or utc_now(),
            status=coerce_run_status(status),
            policy_decision=dict(policy_decision),
            worker_results=tuple(dict(item) for item in worker_results),
            blocked_workunits=tuple(dict(item) for item in blocked_workunits),
            warnings=tuple(str(item) for item in warnings),
            limitations=tuple(str(item) for item in limitations),
        )

    @classmethod
    def from_dict(cls, payload: Mapping[str, Any]) -> "BackgroundHuntRun":
        return cls(
            run_id=str(payload.get("run_id") or ""),
            hunt_id=str(payload.get("hunt_id") or ""),
            search_need_ids=tuple_text(payload.get("search_need_ids")),
            workunit_ids=tuple_text(payload.get("workunit_ids")),
            worker_kinds=tuple_text(payload.get("worker_kinds")),
            started_at=str(payload.get("started_at") or utc_now()),
            finished_at=optional_text(payload.get("finished_at")),
            status=coerce_run_status(payload.get("status") or BackgroundHuntRunStatus.COMPLETE.value),
            policy_decision=mapping(payload.get("policy_decision")),
            worker_results=tuple(mapping(item) for item in sequence(payload.get("worker_results"))),
            blocked_workunits=tuple(mapping(item) for item in sequence(payload.get("blocked_workunits"))),
            warnings=tuple_text(payload.get("warnings")),
            limitations=tuple_text(payload.get("limitations")),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "background_hunt_run.v0",
            "run_id": self.run_id,
            "hunt_id": self.hunt_id,
            "search_need_ids": list(self.search_need_ids),
            "workunit_ids": list(self.workunit_ids),
            "worker_kinds": list(self.worker_kinds),
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "status": self.status.value,
            "policy_decision": dict(self.policy_decision),
            "worker_results": [dict(item) for item in self.worker_results],
            "blocked_workunits": [dict(item) for item in self.blocked_workunits],
            "warnings": list(self.warnings),
            "limitations": list(self.limitations),
            "source_probe_executed": False,
            "extraction_executed": False,
            "external_network_used": False,
            "model_provider_used": False,
            "download_install_execute_performed": False,
            "review_mutation_performed": False,
            "public_index_mutated_except_allowed_rebuild_worker": False,
            "master_index_mutated": False,
            "deployment_performed": False,
            "production_readiness_claimed": False,
            "public_launch_readiness_claimed": False,
        }


@dataclass(frozen=True)
class BackgroundHuntRunResult:
    hunt_id: str
    mode: str
    plan: BackgroundHuntPlan
    run: BackgroundHuntRun

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "background_hunt_run_result.v0",
            "hunt_id": self.hunt_id,
            "mode": self.mode,
            "plan": self.plan.to_dict(),
            "run": self.run.to_dict(),
            "source_probe_executed": False,
            "extraction_executed": False,
            "external_network_used": False,
            "model_provider_used": False,
            "download_install_execute_performed": False,
            "deployment_performed": False,
        }


def coerce_run_status(value: BackgroundHuntRunStatus | str) -> BackgroundHuntRunStatus:
    return value if isinstance(value, BackgroundHuntRunStatus) else BackgroundHuntRunStatus(str(value))


def optional_text(value: Any) -> str | None:
    text = str(value) if value is not None else ""
    return text or None


def tuple_text(value: Any) -> tuple[str, ...]:
    if not isinstance(value, (list, tuple)):
        return ()
    return tuple(str(item) for item in value)


def mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def sequence(value: Any) -> Sequence[Any]:
    return value if isinstance(value, (list, tuple)) else ()
