"""Validation helpers for deterministic local worker results."""

from typing import Any

from .errors import LocalWorkerValidationError
from .registry import get_default_worker_registry
from .results import LocalWorkerResult


def validate_worker_result(result: LocalWorkerResult) -> LocalWorkerResult:
    if not result.run.worker_run_id:
        raise LocalWorkerValidationError("worker_run_id is required")
    if not result.run.workunit_id:
        raise LocalWorkerValidationError("workunit_id is required")
    if not result.run.worker_kind:
        raise LocalWorkerValidationError("worker_kind is required")
    if result.audit_event is None:
        raise LocalWorkerValidationError("worker audit event is required")
    validate_worker_side_effects(result)
    return result


def validate_worker_side_effects(result: LocalWorkerResult) -> LocalWorkerResult:
    for mutation in result.store_mutations:
        store_id = str(mutation.get("store_id", ""))
        if store_id != "public_index":
            raise LocalWorkerValidationError(f"forbidden store mutation: {store_id}")
        if result.run.worker_kind != "reviewed_index_rebuild_worker":
            raise LocalWorkerValidationError("only reviewed_index_rebuild_worker may mutate public_index")
    return validate_no_external_effects(result)


def validate_no_forbidden_worker_kind(kind: str) -> str:
    registry = get_default_worker_registry()
    worker = registry.get_worker(kind)
    if worker is None or not worker.enabled:
        raise LocalWorkerValidationError(f"worker kind is disabled: {kind}")
    return kind


def validate_no_external_effects(result: LocalWorkerResult) -> LocalWorkerResult:
    forbidden_flags = {
        "external_network_used": result.external_network_used,
        "source_probe_executed": result.source_probe_executed,
        "extraction_executed": result.extraction_executed,
        "model_provider_used": result.model_provider_used,
        "download_install_execute_performed": result.download_install_execute_performed,
        "site_dist_mutated": result.site_dist_mutated,
        "master_index_mutated": result.master_index_mutated,
        "lan_enabled": result.lan_enabled,
        "deployment_performed": result.deployment_performed,
        "production_readiness_claimed": result.production_readiness_claimed,
        "public_launch_readiness_claimed": result.public_launch_readiness_claimed,
    }
    for key, value in forbidden_flags.items():
        if value:
            raise LocalWorkerValidationError(f"{key} must be false")
    return result


def result_flags(payload: dict[str, Any]) -> dict[str, bool]:
    return {
        "external_network_used": bool(payload.get("external_network_used")),
        "source_probe_executed": bool(payload.get("source_probe_executed")),
        "extraction_executed": bool(payload.get("extraction_executed")),
        "model_provider_used": bool(payload.get("model_provider_used")),
        "download_install_execute_performed": bool(payload.get("download_install_execute_performed")),
        "site_dist_mutated": bool(payload.get("site_dist_mutated")),
        "master_index_mutated": bool(payload.get("master_index_mutated")),
        "lan_enabled": bool(payload.get("lan_enabled")),
        "deployment_performed": bool(payload.get("deployment_performed")),
    }
