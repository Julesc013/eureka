"""Sanitized provider readiness and optional live-auth checks."""

from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Any, Mapping

from .live_web import WebSearchBudget, WebSearchProviderError, WebSearchRateLimited, looks_like_placeholder_secret
from .providers import provider_from_environment, provider_status


class ProviderHealthState:
    NOT_CONFIGURED = "not_configured"
    CONFIGURED_UNCHECKED = "configured_unchecked"
    HEALTHY = "healthy"
    HEALTHY_ZERO_RESULTS = "healthy_zero_results"
    AUTHENTICATION_FAILED = "authentication_failed"
    PERMISSION_FAILED = "permission_failed"
    RATE_LIMITED = "rate_limited"
    QUOTA_EXHAUSTED = "quota_exhausted"
    TIMEOUT = "timeout"
    NETWORK_UNREACHABLE = "network_unreachable"
    INVALID_RESPONSE = "invalid_response"
    DEGRADED = "degraded"
    CIRCUIT_OPEN = "circuit_open"
    DISABLED_BY_POLICY = "disabled_by_policy"

    HEALTHY_STATES = (HEALTHY, HEALTHY_ZERO_RESULTS)


@dataclass(frozen=True)
class ProviderHealth:
    provider: str
    configured: bool
    category: str
    status: str
    state: str = ProviderHealthState.NOT_CONFIGURED
    auth_verified: bool = False
    live_check_requested: bool = False
    live_check_performed: bool = False
    result_count: int = 0
    http_status: int = 0
    message: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "eureka.provider_health.v0",
            "provider": self.provider,
            "configured": self.configured,
            "state": self.state,
            "category": self.category,
            "status": self.status,
            "auth_verified": self.auth_verified,
            "live_check_requested": self.live_check_requested,
            "live_check_performed": self.live_check_performed,
            "result_count": self.result_count,
            "http_status": self.http_status,
            "message": self.message,
            "credential_value_exposed": False,
            "provider_payload_included": False,
            "provider_result_payload_persisted": False,
            "public_live_fanout": False,
        }


def provider_health_check(
    provider: str = "brave",
    *,
    env: Mapping[str, str] | None = None,
    live_check: bool = False,
    query: str = "eureka provider health check",
    timeout_seconds: int = 10,
) -> dict[str, Any]:
    """Return sanitized provider readiness without exposing credentials or result payloads."""

    provider_id = str(provider or "brave").strip().casefold()
    source = env or os.environ
    status_payload = provider_status(provider_id, env=source)
    keys = [str(item) for item in status_payload.get("credential_env_keys") or []]
    has_value = any(bool(str(source.get(key) or "").strip()) for key in keys)
    has_placeholder = any(looks_like_placeholder_secret(str(source.get(key) or "")) for key in keys)
    configured = bool(status_payload.get("configured"))
    if has_placeholder and not configured:
        return ProviderHealth(
            provider=provider_id,
            configured=False,
            category="invalid_key_placeholder",
            status="fail",
            state=ProviderHealthState.NOT_CONFIGURED,
            live_check_requested=bool(live_check),
            message="Provider credential looks like a placeholder.",
        ).to_dict()
    if keys and not has_value:
        return ProviderHealth(
            provider=provider_id,
            configured=False,
            category="missing_key",
            status="warning",
            state=ProviderHealthState.NOT_CONFIGURED,
            live_check_requested=bool(live_check),
            message=str(status_payload.get("message") or "Provider credential is not configured."),
        ).to_dict()
    if not configured:
        return ProviderHealth(
            provider=provider_id,
            configured=False,
            category="provider_not_configured",
            status="warning",
            state=ProviderHealthState.DISABLED_BY_POLICY if "disabled" in str(status_payload.get("error") or "").casefold() else ProviderHealthState.NOT_CONFIGURED,
            live_check_requested=bool(live_check),
            message=str(status_payload.get("error") or status_payload.get("message") or "Provider is not configured."),
        ).to_dict()
    if not live_check:
        return ProviderHealth(
            provider=provider_id,
            configured=True,
            category="configured_not_checked",
            status="pass",
            state=ProviderHealthState.CONFIGURED_UNCHECKED,
            message="Provider is configured; auth was not checked.",
        ).to_dict()

    provider_instance = provider_from_environment(provider_id, env=source)
    if provider_instance is None:
        return ProviderHealth(
            provider=provider_id,
            configured=False,
            category="provider_not_configured",
            status="warning",
            state=ProviderHealthState.NOT_CONFIGURED,
            live_check_requested=True,
            message="Provider factory did not return a configured provider.",
        ).to_dict()
    try:
        page = provider_instance.search(
            " ".join(str(query or "eureka provider health check").split()),
            page=0,
            count=1,
            freshness="",
            country="",
            language="",
            safe_search="moderate",
            budget_context=WebSearchBudget(max_provider_requests=1, timeout_seconds=max(1, min(int(timeout_seconds or 10), 15)), max_retries=0),
        )
    except WebSearchRateLimited as exc:
        return _provider_error_health(provider_id, exc, category="rate_limited")
    except WebSearchProviderError as exc:
        return _provider_error_health(provider_id, exc)
    except TimeoutError as exc:
        return ProviderHealth(
            provider=provider_id,
            configured=True,
            category="network_timeout",
            status="fail",
            state=ProviderHealthState.TIMEOUT,
            live_check_requested=True,
            live_check_performed=True,
            message=str(exc) or "Provider health check timed out.",
        ).to_dict()
    except OSError as exc:
        return ProviderHealth(
            provider=provider_id,
            configured=True,
            category="network_error",
            status="fail",
            state=ProviderHealthState.NETWORK_UNREACHABLE,
            live_check_requested=True,
            live_check_performed=True,
            message=str(exc) or "Provider health check failed at the network layer.",
        ).to_dict()
    result_count = len(page.results)
    return ProviderHealth(
        provider=provider_id,
        configured=True,
        category="provider_ok_results_available" if result_count else "provider_ok_zero_results",
        status="pass",
        state=ProviderHealthState.HEALTHY if result_count else ProviderHealthState.HEALTHY_ZERO_RESULTS,
        auth_verified=True,
        live_check_requested=True,
        live_check_performed=True,
        result_count=result_count,
        message="Provider health check completed without storing provider payload.",
    ).to_dict()


def _provider_error_health(provider: str, exc: WebSearchProviderError, *, category: str = "") -> dict[str, Any]:
    status_code = int(getattr(exc, "status_code", 0) or 0)
    if not category:
        if status_code in {401, 403}:
            category = "provider_auth"
        elif status_code == 429:
            category = "rate_limited"
        elif status_code == 408:
            category = "network_timeout"
        else:
            category = "provider_response"
    state = _state_from_provider_error(category, status_code, str(exc))
    return ProviderHealth(
        provider=provider,
        configured=True,
        category=category,
        status="fail",
        state=state,
        live_check_requested=True,
        live_check_performed=True,
        http_status=status_code,
        message=str(exc),
    ).to_dict()


def _state_from_provider_error(category: str, status_code: int, message: str) -> str:
    if status_code == 401:
        return ProviderHealthState.AUTHENTICATION_FAILED
    if status_code == 403:
        return ProviderHealthState.PERMISSION_FAILED
    if status_code == 402:
        return ProviderHealthState.QUOTA_EXHAUSTED
    if status_code == 429 or category == "rate_limited":
        return ProviderHealthState.RATE_LIMITED
    if status_code == 408 or category == "network_timeout":
        return ProviderHealthState.TIMEOUT
    lowered = str(message or "").casefold()
    if "invalid" in lowered or "json" in lowered or "response" in lowered:
        return ProviderHealthState.INVALID_RESPONSE
    return ProviderHealthState.DEGRADED
