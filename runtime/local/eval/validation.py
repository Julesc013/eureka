"""Validation helpers for local evaluation."""

from __future__ import annotations

from typing import Any, Mapping
import urllib.parse

from .errors import LocalEvalSafetyError, LocalEvalValidationError


ALLOWED_HOSTS = {"127.0.0.1", "localhost"}
FORBIDDEN_HOSTS = {"", "*", "0.0.0.0", "::"}


def validate_localhost_base_url(base_url: str) -> str:
    split = urllib.parse.urlsplit(str(base_url or ""))
    if split.scheme != "http":
        raise LocalEvalValidationError("base-url must use http")
    host = (split.hostname or "").lower()
    if host in FORBIDDEN_HOSTS or host not in ALLOWED_HOSTS:
        raise LocalEvalValidationError("base-url must use 127.0.0.1 or localhost")
    if not split.port:
        raise LocalEvalValidationError("base-url must include an explicit port")
    return urllib.parse.urlunsplit((split.scheme, split.netloc, split.path.rstrip("/"), "", ""))


def validate_eval_report(report: Mapping[str, Any]) -> Mapping[str, Any]:
    if report.get("schema_version") != "local_eval_report.v0":
        raise LocalEvalValidationError("unexpected local eval report schema")
    if report.get("status") not in {"pass", "pass_with_warnings", "fail"}:
        raise LocalEvalValidationError("unexpected local eval report status")
    if not isinstance(report.get("suite_results"), list):
        raise LocalEvalValidationError("suite_results list is required")
    return report


def validate_no_forbidden_eval_effects(report: Mapping[str, Any]) -> Mapping[str, Any]:
    for key in (
        "external_network_used",
        "source_probe_executed",
        "extraction_executed",
        "model_provider_used",
        "download_install_execute_performed",
        "site_dist_mutated",
        "master_index_mutated",
        "lan_enabled",
        "deployment_performed",
        "production_readiness_claimed",
        "public_launch_readiness_claimed",
    ):
        if report.get(key) is not False:
            raise LocalEvalSafetyError(f"forbidden eval effect is not false: {key}")
    return report
