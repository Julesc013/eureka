"""Policy checks for deterministic local workers."""

from typing import Any, Mapping

from .registry import get_default_worker_registry


def evaluate_worker_policy(workunit: Any, worker_kind: str, operator_context: Mapping[str, Any] | None = None) -> dict[str, Any]:
    registry = get_default_worker_registry()
    kind = str(worker_kind or "")
    worker = registry.get_worker(kind)
    if worker is None:
        return _blocked(kind, "worker kind is not registered")
    if not worker.enabled:
        return _blocked(kind, "worker kind is disabled by local policy")
    context = operator_context if isinstance(operator_context, Mapping) else {}
    if worker.requires_operator_token and not bool(context.get("authorized")):
        return _blocked(kind, "operator token is required")
    return {
        "schema_version": "local_worker_policy_decision.v0",
        "status": "allowed",
        "allowed": True,
        "worker_kind": kind,
        "workunit_id": getattr(workunit, "id", ""),
        "mutates_stores": worker.mutates_stores,
        "requires_operator_token": worker.requires_operator_token,
        "allowed_mutation": worker.allowed_mutation,
        "reason": "worker kind is enabled by local deterministic policy",
        "external_network_allowed": False,
        "source_probe_allowed": False,
        "extraction_allowed": False,
        "model_provider_allowed": False,
        "download_allowed": False,
        "install_execution_allowed": False,
        "lan_operations_allowed": False,
        "deployment_allowed": False,
        "master_index_mutation_allowed": False,
    }


def _blocked(kind: str, reason: str) -> dict[str, Any]:
    return {
        "schema_version": "local_worker_policy_decision.v0",
        "status": "blocked",
        "allowed": False,
        "worker_kind": kind,
        "reason": reason,
        "external_network_allowed": False,
        "source_probe_allowed": False,
        "extraction_allowed": False,
        "model_provider_allowed": False,
        "download_allowed": False,
        "install_execution_allowed": False,
        "lan_operations_allowed": False,
        "deployment_allowed": False,
        "master_index_mutation_allowed": False,
    }
