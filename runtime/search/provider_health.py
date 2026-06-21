"""Sanitized provider readiness and optional live-auth checks."""

from __future__ import annotations

from dataclasses import dataclass
import os
from typing import Any, Mapping

from .live_web import WebSearchBudget, WebSearchProviderError, WebSearchRateLimited, looks_like_placeholder_secret
from .providers import provider_from_environment, provider_status


@dataclass(frozen=True)
class ProviderHealth:
    provider: str
    configured: bool
    category: str
    status: str
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
            live_check_requested=bool(live_check),
            message="Provider credential looks like a placeholder.",
        ).to_dict()
    if keys and not has_value:
        return ProviderHealth(
            provider=provider_id,
            configured=False,
            category="missing_key",
            status="warning",
            live_check_requested=bool(live_check),
            message=str(status_payload.get("message") or "Provider credential is not configured."),
        ).to_dict()
    if not configured:
        return ProviderHealth(
            provider=provider_id,
            configured=False,
            category="provider_not_configured",
            status="warning",
            live_check_requested=bool(live_check),
            message=str(status_payload.get("error") or status_payload.get("message") or "Provider is not configured."),
        ).to_dict()
    if not live_check:
        return ProviderHealth(
            provider=provider_id,
            configured=True,
            category="configured_not_checked",
            status="pass",
            message="Provider is configured; auth was not checked.",
        ).to_dict()

    provider_instance = provider_from_environment(provider_id, env=source)
    if provider_instance is None:
        return ProviderHealth(
            provider=provider_id,
            configured=False,
            category="provider_not_configured",
            status="warning",
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
    return ProviderHealth(
        provider=provider,
        configured=True,
        category=category,
        status="fail",
        live_check_requested=True,
        live_check_performed=True,
        http_status=status_code,
        message=str(exc),
    ).to_dict()
