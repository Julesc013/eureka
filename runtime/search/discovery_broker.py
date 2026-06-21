"""Policy-aware discovery planning above live providers."""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import Any, Mapping

from .providers import ProviderRegistry, provider_status


@dataclass(frozen=True)
class DiscoveryPlanStep:
    tier: int
    source: str
    provider_id: str
    role: str
    reason: str
    configured: bool
    retention: Mapping[str, Any]
    estimated_cost: str
    run_policy: str = "eligible"

    def to_dict(self) -> dict[str, Any]:
        return {
            "tier": self.tier,
            "source": self.source,
            "provider_id": self.provider_id,
            "role": self.role,
            "reason": self.reason,
            "configured": self.configured,
            "retention": dict(self.retention),
            "estimated_cost": self.estimated_cost,
            "run_policy": self.run_policy,
        }


@dataclass(frozen=True)
class DiscoveryBrokerPlan:
    query: str
    intent: str
    steps: tuple[DiscoveryPlanStep, ...]
    public_live_fanout: bool = False
    reviewed_truth_mutation: bool = False
    network_calls_performed: bool = False

    def provider_ids(self) -> tuple[str, ...]:
        return tuple(step.provider_id for step in self.steps if step.tier > 0 and step.provider_id and step.run_policy == "eligible")

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": "eureka.discovery_broker_plan.v0",
            "query": self.query,
            "intent": self.intent,
            "steps": [step.to_dict() for step in self.steps],
            "provider_ids": list(self.provider_ids()),
            "public_live_fanout": self.public_live_fanout,
            "reviewed_truth_mutation": self.reviewed_truth_mutation,
            "network_calls_performed": self.network_calls_performed,
        }


class DiscoveryBroker:
    """Choose a bounded provider plan without performing provider calls."""

    def __init__(self, *, registry: ProviderRegistry | None = None, env: Mapping[str, str] | None = None) -> None:
        self.registry = registry or ProviderRegistry(env=env)
        self.env = env

    def plan(self, query: str, *, requested_provider: str = "auto", local_result_count: int = 0) -> DiscoveryBrokerPlan:
        clean_query = _clean_query(query)
        intent = classify_query_intent(clean_query)
        steps: list[DiscoveryPlanStep] = [
            DiscoveryPlanStep(
                tier=0,
                source="local_preview_reviewed_index",
                provider_id="local",
                role="durable_first_pass",
                reason="Local index is fastest, free, and durable.",
                configured=True,
                retention={"persist_urls": True, "persist_snippets": True, "persist_rank": True},
                estimated_cost="free",
                run_policy="eligible",
            )
        ]
        if local_result_count > 0 and requested_provider == "auto":
            return DiscoveryBrokerPlan(query=clean_query, intent=intent, steps=tuple(steps))
        for provider_id, reason, tier, cost in self._provider_order(intent, requested_provider):
            steps.append(self._provider_step(provider_id, tier=tier, reason=reason, estimated_cost=cost))
        steps.append(
            DiscoveryPlanStep(
                tier=3,
                source="self_hosted_metasearch",
                provider_id="searxng",
                role="optional_fallback",
                reason="Use only a configured self-hosted instance; public instances are not reliable infrastructure.",
                configured=False,
                retention={"persist_urls": False, "persist_snippets": False, "persist_rank": False},
                estimated_cost="operator-hosted",
                run_policy="disabled_until_self_hosted_configured",
            )
        )
        return DiscoveryBrokerPlan(query=clean_query, intent=intent, steps=tuple(steps))

    def _provider_order(self, intent: str, requested_provider: str) -> tuple[tuple[str, str, int, str], ...]:
        requested = str(requested_provider or "auto").strip().casefold()
        if requested not in {"auto", "multi", "blended"}:
            return ((requested, "Explicit provider request.", 2, "provider_native"),)
        if intent in {"archive", "historical_artifact", "software_artifact"}:
            return (
                ("internet_archive_metadata", "Archive/software/manual query: search open archive metadata first.", 1, "free"),
                ("brave", "Escalate to broad web when vertical sources may miss pages.", 2, "metered"),
                ("mojeek", "Independent broad-web fallback for additional coverage.", 2, "metered"),
            )
        if intent == "code_or_package":
            return (
                ("brave", "Broad web currently covers code/package pages until vertical code providers are added.", 2, "metered"),
                ("mojeek", "Independent broad-web fallback for code/package pages.", 2, "metered"),
            )
        if intent == "site_specific":
            return (
                ("brave", "Site-specific query needs a provider with site operator support.", 2, "metered"),
                ("mojeek", "Fallback broad-web site search provider.", 2, "metered"),
            )
        return (
            ("brave", "Current-web query: use a broad-web provider after local index.", 2, "metered"),
            ("mojeek", "Independent broad-web fallback for coverage and outage resilience.", 2, "metered"),
        )

    def _provider_step(self, provider_id: str, *, tier: int, reason: str, estimated_cost: str) -> DiscoveryPlanStep:
        status = provider_status(provider_id, env=self.env)
        manifest = status.get("capability_manifest") or {}
        if isinstance(manifest, Mapping) and provider_id in manifest and isinstance(manifest[provider_id], Mapping):
            manifest = manifest[provider_id]
        retention = manifest.get("retention_policy") if isinstance(manifest, Mapping) else {}
        if not isinstance(retention, Mapping):
            retention = {
                "persist_urls": bool(manifest.get("persist_urls")) if isinstance(manifest, Mapping) else False,
                "persist_snippets": bool(manifest.get("persist_snippets")) if isinstance(manifest, Mapping) else False,
                "persist_rank": bool(manifest.get("persist_rank")) if isinstance(manifest, Mapping) else False,
            }
        return DiscoveryPlanStep(
            tier=tier,
            source=str(manifest.get("provider_kind") or provider_id) if isinstance(manifest, Mapping) else provider_id,
            provider_id=provider_id,
            role="vertical_search" if tier == 1 else "broad_web_search",
            reason=reason,
            configured=bool(status.get("configured")),
            retention=retention,
            estimated_cost=estimated_cost,
            run_policy=_run_policy(status),
        )


def classify_query_intent(query: str) -> str:
    normalized = str(query or "").casefold()
    if re.search(r"https?://|(?:^|\s)site:", normalized):
        return "site_specific"
    if any(term in normalized for term in ("github", "source code", "github release", "npm", "pypi", "crate", "package registry", "software heritage")):
        return "code_or_package"
    if any(term in normalized for term in ("archive", "wayback", "scan", "magazine", "manual", "driver", "old", "historical", "ftp", "sound blaster")):
        return "historical_artifact" if any(term in normalized for term in ("manual", "driver", "sound blaster", "old", "ftp")) else "archive"
    return "current_web"


def _clean_query(query: str) -> str:
    return " ".join(str(query or "").split())[:256]


def _run_policy(status: Mapping[str, Any]) -> str:
    if status.get("error"):
        return "blocked_by_policy"
    if not status.get("configured"):
        return "needs_configuration"
    return "eligible"
