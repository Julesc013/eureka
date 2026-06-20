"""Deterministic E2E reference evaluation oracle."""

from .oracle import (
    DEFAULT_ORACLE_ROOT,
    DEFAULT_OUTPUT_ROOT,
    ORACLE_VERSION,
    OracleError,
    compare_oracle_results,
    explain_case,
    list_cases,
    load_registry,
    run_oracle,
    status_for_run,
    validate_oracle_run,
    validate_registry,
)

__all__ = [
    "DEFAULT_ORACLE_ROOT",
    "DEFAULT_OUTPUT_ROOT",
    "ORACLE_VERSION",
    "OracleError",
    "compare_oracle_results",
    "explain_case",
    "list_cases",
    "load_registry",
    "run_oracle",
    "status_for_run",
    "validate_oracle_run",
    "validate_registry",
]
