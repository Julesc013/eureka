"""Result models for deterministic local workers."""

from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Mapping, Sequence
import uuid


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def new_worker_run_id() -> str:
    return "lwr_" + uuid.uuid4().hex


def new_worker_audit_id() -> str:
    return "lwa_" + uuid.uuid4().hex


class LocalWorkerStatus(str, Enum):
    PLANNED = "planned"
    RUNNING = "running"
    COMPLETE = "complete"
    FAILED = "failed"
    BLOCKED = "blocked"
    SKIPPED = "skipped"


@dataclass(frozen=True)
class LocalWorkerRun:
    worker_run_id: str
    workunit_id: str
    worker_kind: str
    status: LocalWorkerStatus
    started_at: str
    finished_at: str | None = None

    @classmethod
    def new(cls, workunit_id: str, worker_kind: str, status: LocalWorkerStatus = LocalWorkerStatus.RUNNING) -> "LocalWorkerRun":
        return cls(
            worker_run_id=new_worker_run_id(),
            workunit_id=str(workunit_id),
            worker_kind=str(worker_kind),
            status=status,
            started_at=utc_now(),
        )

    def finish(self, status: LocalWorkerStatus) -> "LocalWorkerRun":
        return LocalWorkerRun(
            worker_run_id=self.worker_run_id,
            workunit_id=self.workunit_id,
            worker_kind=self.worker_kind,
            status=status,
            started_at=self.started_at,
            finished_at=utc_now(),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "worker_run_id": self.worker_run_id,
            "workunit_id": self.workunit_id,
            "worker_kind": self.worker_kind,
            "status": self.status.value,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
        }


@dataclass(frozen=True)
class LocalWorkerAuditEvent:
    worker_audit_event_id: str
    worker_run_id: str
    workunit_id: str
    worker_kind: str
    started_at: str
    finished_at: str | None
    status: str
    policy_decision: Mapping[str, Any]
    inputs: Mapping[str, Any]
    outputs: Mapping[str, Any]
    store_mutations: tuple[Mapping[str, Any], ...]
    warnings: tuple[str, ...]
    limitations: tuple[str, ...]

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "local_worker_audit_event.v0",
            "worker_audit_event_id": self.worker_audit_event_id,
            "worker_run_id": self.worker_run_id,
            "workunit_id": self.workunit_id,
            "worker_kind": self.worker_kind,
            "started_at": self.started_at,
            "finished_at": self.finished_at,
            "status": self.status,
            "policy_decision": dict(self.policy_decision),
            "inputs": dict(self.inputs),
            "outputs": dict(self.outputs),
            "store_mutations": [dict(item) for item in self.store_mutations],
            "warnings": list(self.warnings),
            "limitations": list(self.limitations),
        }


@dataclass(frozen=True)
class LocalWorkerResult:
    schema_version: str
    status: LocalWorkerStatus
    run: LocalWorkerRun
    policy_decision: Mapping[str, Any]
    inputs: Mapping[str, Any] = field(default_factory=dict)
    outputs: Mapping[str, Any] = field(default_factory=dict)
    store_mutations: tuple[Mapping[str, Any], ...] = ()
    audit_event: LocalWorkerAuditEvent | None = None
    warnings: tuple[str, ...] = ()
    limitations: tuple[str, ...] = ()
    external_network_used: bool = False
    source_probe_executed: bool = False
    extraction_executed: bool = False
    model_provider_used: bool = False
    download_install_execute_performed: bool = False
    site_dist_mutated: bool = False
    master_index_mutated: bool = False
    lan_enabled: bool = False
    deployment_performed: bool = False
    production_readiness_claimed: bool = False
    public_launch_readiness_claimed: bool = False

    @classmethod
    def from_worker_output(
        cls,
        run: LocalWorkerRun,
        policy_decision: Mapping[str, Any],
        *,
        inputs: Mapping[str, Any],
        outputs: Mapping[str, Any],
        store_mutations: Sequence[Mapping[str, Any]] = (),
        warnings: Sequence[str] = (),
        limitations: Sequence[str] = (),
    ) -> "LocalWorkerResult":
        finished = run.finish(LocalWorkerStatus.COMPLETE)
        result = cls(
            schema_version="local_worker_result.v0",
            status=LocalWorkerStatus.COMPLETE,
            run=finished,
            policy_decision=dict(policy_decision),
            inputs=dict(inputs),
            outputs=dict(outputs),
            store_mutations=tuple(dict(item) for item in store_mutations),
            warnings=tuple(str(item) for item in warnings),
            limitations=tuple(str(item) for item in limitations),
        )
        return result.with_audit_event()

    def with_status(self, status: LocalWorkerStatus, warnings: Sequence[str] = ()) -> "LocalWorkerResult":
        finished = self.run.finish(status)
        result = LocalWorkerResult(
            schema_version=self.schema_version,
            status=status,
            run=finished,
            policy_decision=dict(self.policy_decision),
            inputs=dict(self.inputs),
            outputs=dict(self.outputs),
            store_mutations=self.store_mutations,
            warnings=tuple(str(item) for item in warnings) or self.warnings,
            limitations=self.limitations,
            external_network_used=self.external_network_used,
            source_probe_executed=self.source_probe_executed,
            extraction_executed=self.extraction_executed,
            model_provider_used=self.model_provider_used,
            download_install_execute_performed=self.download_install_execute_performed,
            site_dist_mutated=self.site_dist_mutated,
            master_index_mutated=self.master_index_mutated,
            lan_enabled=self.lan_enabled,
            deployment_performed=self.deployment_performed,
            production_readiness_claimed=self.production_readiness_claimed,
            public_launch_readiness_claimed=self.public_launch_readiness_claimed,
        )
        return result.with_audit_event()

    def with_audit_event(self) -> "LocalWorkerResult":
        event = LocalWorkerAuditEvent(
            worker_audit_event_id=new_worker_audit_id(),
            worker_run_id=self.run.worker_run_id,
            workunit_id=self.run.workunit_id,
            worker_kind=self.run.worker_kind,
            started_at=self.run.started_at,
            finished_at=self.run.finished_at,
            status=self.status.value,
            policy_decision=dict(self.policy_decision),
            inputs=dict(self.inputs),
            outputs=dict(self.outputs),
            store_mutations=self.store_mutations,
            warnings=self.warnings,
            limitations=self.limitations,
        )
        return LocalWorkerResult(
            schema_version=self.schema_version,
            status=self.status,
            run=self.run,
            policy_decision=dict(self.policy_decision),
            inputs=dict(self.inputs),
            outputs=dict(self.outputs),
            store_mutations=self.store_mutations,
            audit_event=event,
            warnings=self.warnings,
            limitations=self.limitations,
            external_network_used=self.external_network_used,
            source_probe_executed=self.source_probe_executed,
            extraction_executed=self.extraction_executed,
            model_provider_used=self.model_provider_used,
            download_install_execute_performed=self.download_install_execute_performed,
            site_dist_mutated=self.site_dist_mutated,
            master_index_mutated=self.master_index_mutated,
            lan_enabled=self.lan_enabled,
            deployment_performed=self.deployment_performed,
            production_readiness_claimed=self.production_readiness_claimed,
            public_launch_readiness_claimed=self.public_launch_readiness_claimed,
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "status": self.status.value,
            "worker_run": self.run.to_dict(),
            "policy_decision": dict(self.policy_decision),
            "inputs": dict(self.inputs),
            "outputs": dict(self.outputs),
            "store_mutations": [dict(item) for item in self.store_mutations],
            "audit_event": self.audit_event.to_dict() if self.audit_event else None,
            "warnings": list(self.warnings),
            "limitations": list(self.limitations),
            "external_network_used": self.external_network_used,
            "source_probe_executed": self.source_probe_executed,
            "extraction_executed": self.extraction_executed,
            "model_provider_used": self.model_provider_used,
            "download_install_execute_performed": self.download_install_execute_performed,
            "site_dist_mutated": self.site_dist_mutated,
            "master_index_mutated": self.master_index_mutated,
            "lan_enabled": self.lan_enabled,
            "deployment_performed": self.deployment_performed,
            "production_readiness_claimed": self.production_readiness_claimed,
            "public_launch_readiness_claimed": self.public_launch_readiness_claimed,
        }
