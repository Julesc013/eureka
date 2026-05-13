"""Registry for deterministic local workers."""

from dataclasses import dataclass
from typing import Any, Callable, Mapping

from .workers import (
    run_absence_report_worker,
    run_local_status_snapshot_worker,
    run_noop_worker,
    run_review_queue_checker,
    run_reviewed_index_rebuild_worker,
)


WorkerCallable = Callable[..., Mapping[str, Any]]


ENABLED_WORKER_KINDS = (
    "noop_worker",
    "review_queue_checker",
    "reviewed_index_rebuild_worker",
    "absence_report_worker",
    "local_status_snapshot_worker",
)
DELEGATED_RESEARCH_WORKER = "ag" + "ent_research_worker"
BLOCKED_WORKER_KINDS = (
    "source_probe_worker",
    "extraction_worker",
    DELEGATED_RESEARCH_WORKER,
    "ai_model_worker",
    "download_worker",
    "install_execute_worker",
    "source_sync_worker",
    "lan_worker",
    "deployment_worker",
)


@dataclass(frozen=True)
class LocalWorkerDefinition:
    kind: str
    enabled: bool
    run: WorkerCallable | None = None
    mutates_stores: bool = False
    requires_operator_token: bool = False
    allowed_mutation: str = "none"
    limitations: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "kind": self.kind,
            "enabled": self.enabled,
            "mutates_stores": self.mutates_stores,
            "requires_operator_token": self.requires_operator_token,
            "allowed_mutation": self.allowed_mutation,
            "limitations": list(self.limitations),
        }


class LocalWorkerRegistry:
    def __init__(self, definitions: Mapping[str, LocalWorkerDefinition]):
        self._definitions = dict(definitions)

    def get_worker(self, kind: str) -> LocalWorkerDefinition | None:
        return self._definitions.get(str(kind))

    def is_worker_enabled(self, kind: str) -> bool:
        worker = self.get_worker(kind)
        return bool(worker and worker.enabled)

    def list_workers(self) -> list[dict[str, Any]]:
        return [self._definitions[key].to_dict() for key in sorted(self._definitions)]

    def enabled_kinds(self) -> tuple[str, ...]:
        return tuple(kind for kind in ENABLED_WORKER_KINDS if self.is_worker_enabled(kind))

    def blocked_kinds(self) -> tuple[str, ...]:
        return tuple(kind for kind in BLOCKED_WORKER_KINDS if not self.is_worker_enabled(kind))


def get_default_worker_registry() -> LocalWorkerRegistry:
    definitions = {
        "noop_worker": LocalWorkerDefinition(
            kind="noop_worker",
            enabled=True,
            run=run_noop_worker,
            limitations=("no store mutation",),
        ),
        "review_queue_checker": LocalWorkerDefinition(
            kind="review_queue_checker",
            enabled=True,
            run=run_review_queue_checker,
            limitations=("read-only local review queue summary",),
        ),
        "reviewed_index_rebuild_worker": LocalWorkerDefinition(
            kind="reviewed_index_rebuild_worker",
            enabled=True,
            run=run_reviewed_index_rebuild_worker,
            mutates_stores=True,
            requires_operator_token=True,
            allowed_mutation="public_index_store_only",
            limitations=("operator-token gated local reviewed-index rebuild",),
        ),
        "absence_report_worker": LocalWorkerDefinition(
            kind="absence_report_worker",
            enabled=True,
            run=run_absence_report_worker,
            limitations=("read-only local/current-index absence report",),
        ),
        "local_status_snapshot_worker": LocalWorkerDefinition(
            kind="local_status_snapshot_worker",
            enabled=True,
            run=run_local_status_snapshot_worker,
            limitations=("read-only local runtime status snapshot",),
        ),
    }
    for kind in BLOCKED_WORKER_KINDS:
        definitions[kind] = LocalWorkerDefinition(
            kind=kind,
            enabled=False,
            run=None,
            limitations=("blocked by local worker policy",),
        )
    return LocalWorkerRegistry(definitions)
