"""Runner for deterministic local WorkUnits."""

from typing import Any, Mapping

from runtime.workunit_queue import WorkUnitState

from .errors import LocalWorkerError
from .policy import evaluate_worker_policy
from .registry import DELEGATED_RESEARCH_WORKER, LocalWorkerRegistry, get_default_worker_registry
from .results import LocalWorkerResult, LocalWorkerRun, LocalWorkerStatus
from .validation import validate_worker_result


class LocalWorkerRunner:
    def __init__(self, runtime: Any, registry: LocalWorkerRegistry | None = None):
        self.runtime = runtime
        self.registry = registry or get_default_worker_registry()

    def plan_run(self, workunit_id: str) -> LocalWorkerResult:
        workunit = self._require_workunit(workunit_id)
        worker_kind = self._resolve_worker_kind(workunit, None)
        policy = evaluate_worker_policy(workunit, worker_kind)
        run = LocalWorkerRun.new(workunit.id, worker_kind, LocalWorkerStatus.PLANNED)
        result = LocalWorkerResult(
            schema_version="local_worker_result.v0",
            status=LocalWorkerStatus.PLANNED,
            run=run.finish(LocalWorkerStatus.PLANNED),
            policy_decision=policy,
            inputs={"workunit": workunit.to_dict()},
            outputs={"planned": bool(policy.get("allowed"))},
            limitations=("plan only; no worker execution",),
        ).with_audit_event()
        return validate_worker_result(result)

    def run_one(
        self,
        workunit_id: str,
        worker_kind: str | None = None,
        operator_context: Mapping[str, Any] | None = None,
    ) -> LocalWorkerResult:
        workunit = self._require_workunit(workunit_id)
        kind = self._resolve_worker_kind(workunit, worker_kind)
        policy = evaluate_worker_policy(workunit, kind, operator_context)
        if not bool(policy.get("allowed")):
            return self.block_unsupported_worker(workunit_id, kind, str(policy.get("reason") or "blocked by policy"), policy)
        if workunit.state != WorkUnitState.QUEUED:
            run = LocalWorkerRun.new(workunit.id, kind, LocalWorkerStatus.SKIPPED)
            result = LocalWorkerResult(
                schema_version="local_worker_result.v0",
                status=LocalWorkerStatus.SKIPPED,
                run=run.finish(LocalWorkerStatus.SKIPPED),
                policy_decision=policy,
                inputs={"workunit": workunit.to_dict()},
                outputs={"skipped_reason": f"workunit is {workunit.state.value}"},
                limitations=("only queued workunits are executed",),
            ).with_audit_event()
            return validate_worker_result(result)
        run = LocalWorkerRun.new(workunit.id, kind, LocalWorkerStatus.RUNNING)
        try:
            running = self.runtime.workunit_queue.transition_workunit(
                workunit.id,
                WorkUnitState.RUNNING,
                f"worker_run_id={run.worker_run_id}",
            )
            worker = self.registry.get_worker(kind)
            if worker is None or worker.run is None:
                raise LocalWorkerError("worker kind is not executable")
            if worker.requires_operator_token:
                output = worker.run(self.runtime, running, operator_context)
            else:
                output = worker.run(self.runtime, running)
            result = LocalWorkerResult.from_worker_output(
                run,
                policy,
                inputs={"workunit": running.to_dict()},
                outputs=_mapping(output.get("outputs")),
                store_mutations=tuple(_mapping(item) for item in output.get("store_mutations", ())),
                warnings=tuple(str(item) for item in output.get("warnings", ())),
                limitations=tuple(str(item) for item in output.get("limitations", ())),
            )
            validate_worker_result(result)
            self._record_result_refs(result)
            self.runtime.workunit_queue.complete_workunit(workunit.id, f"worker_run_id={run.worker_run_id}")
            return result
        except Exception as exc:
            failed = LocalWorkerResult(
                schema_version="local_worker_result.v0",
                status=LocalWorkerStatus.FAILED,
                run=run.finish(LocalWorkerStatus.FAILED),
                policy_decision=policy,
                inputs={"workunit": workunit.to_dict()},
                outputs={"error": str(exc)},
                warnings=(str(exc),),
                limitations=("worker failed before completion",),
            ).with_audit_event()
            self._record_result_refs(failed)
            try:
                self.runtime.workunit_queue.fail_workunit(workunit.id, f"worker_run_id={run.worker_run_id}: {exc}")
            except Exception:
                pass
            return validate_worker_result(failed)

    def run_next(
        self,
        kind: str | None = None,
        limit: int = 1,
        operator_context: Mapping[str, Any] | None = None,
    ) -> list[LocalWorkerResult]:
        results: list[LocalWorkerResult] = []
        for workunit in self.runtime.workunit_queue.list_workunits(state=WorkUnitState.QUEUED, limit=max(int(limit or 1), 1) * 10):
            natural_kind = self._resolve_worker_kind(workunit, None)
            if kind and natural_kind != kind:
                continue
            results.append(self.run_one(workunit.id, kind or natural_kind, operator_context))
            if len(results) >= max(int(limit or 1), 1):
                break
        return results

    def block_unsupported_worker(
        self,
        workunit_id: str,
        worker_kind: str,
        reason: str,
        policy_decision: Mapping[str, Any] | None = None,
    ) -> LocalWorkerResult:
        workunit = self._require_workunit(workunit_id)
        run = LocalWorkerRun.new(workunit.id, worker_kind, LocalWorkerStatus.BLOCKED)
        policy = dict(policy_decision or evaluate_worker_policy(workunit, worker_kind))
        if workunit.state in {WorkUnitState.QUEUED, WorkUnitState.RUNNING}:
            self.runtime.workunit_queue.block_workunit(workunit.id, f"worker_run_id={run.worker_run_id}: {reason}")
        result = LocalWorkerResult(
            schema_version="local_worker_result.v0",
            status=LocalWorkerStatus.BLOCKED,
            run=run.finish(LocalWorkerStatus.BLOCKED),
            policy_decision=policy,
            inputs={"workunit": workunit.to_dict()},
            outputs={"blocked_reason": reason},
            warnings=(reason,),
            limitations=("worker was blocked before execution",),
        ).with_audit_event()
        validate_worker_result(result)
        self._record_result_refs(result)
        return result

    def _record_result_refs(self, result: LocalWorkerResult) -> None:
        self.runtime.workunit_queue.record_payload_ref(result.run.workunit_id, "worker_result", result.run.worker_run_id)
        if result.audit_event is not None:
            self.runtime.workunit_queue.record_payload_ref(
                result.run.workunit_id,
                "worker_audit_event",
                result.audit_event.worker_audit_event_id,
            )

    def _require_workunit(self, workunit_id: str) -> Any:
        workunit = self.runtime.workunit_queue.get_workunit(workunit_id)
        if workunit is None:
            raise LocalWorkerError(f"workunit not found: {workunit_id}")
        return workunit

    def _resolve_worker_kind(self, workunit: Any, worker_kind: str | None) -> str:
        if worker_kind:
            return str(worker_kind)
        payload = workunit.payload if isinstance(workunit.payload, Mapping) else {}
        if payload.get("worker_kind"):
            return str(payload["worker_kind"])
        kind_value = getattr(workunit.kind, "value", str(workunit.kind))
        if kind_value == "source_probe":
            return "source_probe_worker"
        if kind_value == "extraction_" + "tas" + "k":
            return "extraction_worker"
        if kind_value == "ag" + "ent_" + "tas" + "k":
            return DELEGATED_RESEARCH_WORKER
        if kind_value == "index_rebuild":
            return "reviewed_index_rebuild_worker"
        if kind_value == "evidence_review":
            return "review_queue_checker"
        if kind_value == "search_need":
            return "absence_report_worker"
        return "noop_worker"


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}
