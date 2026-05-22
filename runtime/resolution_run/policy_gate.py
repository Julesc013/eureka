"""Policy gates for headless resolution runs."""

from __future__ import annotations

from typing import Any, Mapping


DEFAULT_RUN_POLICY: dict[str, Any] = {
    "schema_version": "resolution_run_policy.v0",
    "dry_run_default": True,
    "headless_kernel_only": True,
    "workbench_is_projection_only": True,
    "api_is_projection_only": True,
    "live_source_calls_enabled": False,
    "live_ia_calls_enabled": False,
    "source_probe_enabled": False,
    "downloads_enabled": False,
    "uploads_enabled": False,
    "extraction_enabled": False,
    "execution_enabled": False,
    "model_provider_enabled": False,
    "reviewed_record_creation_enabled": False,
    "source_cache_write_enabled": False,
    "evidence_write_enabled": False,
    "candidate_index_write_enabled": False,
    "review_queue_write_enabled": False,
    "reviewed_index_write_enabled": False,
    "master_index_mutation_enabled": False,
    "operator_instance_mutation_enabled": False,
    "public_fanout_enabled": False,
    "deployment_enabled": False,
    "production_readiness_claimed": False,
    "public_launch_readiness_claimed": False,
}

UNSAFE_COMMANDS = {
    "run_live_source_probe",
    "run_live_ia_metadata",
    "download",
    "extract",
    "execute",
    "call_model_provider",
    "mutate_operator_instance",
    "mutate_master_index",
    "deploy",
    "promote_reviewed_record",
}


def evaluate_run_policy(
    command_type: str,
    policy: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Return a policy decision for a resolution-run command."""
    merged = dict(DEFAULT_RUN_POLICY)
    merged.update(dict(policy or {}))
    blocked_reasons: list[str] = []
    allowed = True
    if command_type in UNSAFE_COMMANDS:
        allowed = False
        blocked_reasons.append(f"{command_type} is blocked by resolution-run foundation policy")
    if not bool(merged.get("dry_run_default", True)):
        allowed = False
        blocked_reasons.append("dry_run_default must remain true in the foundation kernel")
    for key in (
        "live_source_calls_enabled",
        "live_ia_calls_enabled",
        "source_probe_enabled",
        "downloads_enabled",
        "uploads_enabled",
        "extraction_enabled",
        "execution_enabled",
        "model_provider_enabled",
        "reviewed_record_creation_enabled",
        "source_cache_write_enabled",
        "evidence_write_enabled",
        "candidate_index_write_enabled",
        "review_queue_write_enabled",
        "reviewed_index_write_enabled",
        "master_index_mutation_enabled",
        "operator_instance_mutation_enabled",
        "public_fanout_enabled",
        "deployment_enabled",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    ):
        if merged.get(key) is not False:
            allowed = False
            blocked_reasons.append(f"{key} must be false")
    return {
        "schema_version": "resolution_run_policy_decision.v0",
        "command_type": command_type,
        "allowed": allowed,
        "dry_run": bool(merged.get("dry_run_default", True)),
        "blocked_reasons": blocked_reasons,
        "policy": merged,
    }
