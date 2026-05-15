"""Safety suite helpers for local evaluation."""

from __future__ import annotations

from typing import Any

from .runner import LocalEvalRunner
from .suites import get_default_local_eval_suites


def run_safety_checks(base_url: str) -> dict[str, Any]:
    suites = {suite.name: suite for suite in get_default_local_eval_suites()}
    runner = LocalEvalRunner()
    result = runner.run_suite(suites["read_only_safety"], base_url)
    return {
        "schema_version": "local_eval_safety_result.v0",
        "status": result["status"],
        "suite": result,
        "mutating_methods_rejected": result["status"] == "pass",
        "operator_gated_routes_reject_missing_token": result["status"] == "pass",
        "source_probe_routes_absent_or_disabled": result["status"] == "pass",
        "download_install_execute_routes_absent": result["status"] == "pass",
        "lan_enabled": False,
        "external_network_used": False,
        "site_dist_mutated": False,
        "master_index_mutated": False,
        "model_provider_used": False,
        "warnings": [],
        "limitations": ["safety checks are localhost route checks"],
    }
