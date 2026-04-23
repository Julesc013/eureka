from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from runtime.engine.action_routing.action_plan import ActionPlanEntry
from runtime.engine.compatibility import CompatibilityReason, HostProfile
from runtime.engine.provenance import EvidenceSummary
from runtime.engine.strategy import StrategyProfile
from runtime.engine.interfaces.public.resolution import Notice, ObjectSummary, SourceSummary


@dataclass(frozen=True)
class ActionPlanRequest:
    target_ref: str
    host_profile_id: str | None = None
    strategy_id: str | None = None
    store_actions_enabled: bool = False

    @classmethod
    def from_parts(
        cls,
        target_ref: str,
        host_profile_id: str | None = None,
        strategy_id: str | None = None,
        *,
        store_actions_enabled: bool = False,
    ) -> "ActionPlanRequest":
        normalized_target_ref = target_ref.strip()
        if not normalized_target_ref:
            raise ValueError("target_ref must be a non-empty string.")
        normalized_host_profile_id = None
        if host_profile_id is not None:
            stripped_host_profile_id = host_profile_id.strip()
            normalized_host_profile_id = stripped_host_profile_id or None
        normalized_strategy_id = None
        if strategy_id is not None:
            stripped_strategy_id = strategy_id.strip()
            normalized_strategy_id = stripped_strategy_id or None
        return cls(
            target_ref=normalized_target_ref,
            host_profile_id=normalized_host_profile_id,
            strategy_id=normalized_strategy_id,
            store_actions_enabled=bool(store_actions_enabled),
        )


@dataclass(frozen=True)
class ActionPlanResult:
    status: str
    target_ref: str
    resolved_resource_id: str | None = None
    primary_object: ObjectSummary | None = None
    source: SourceSummary | None = None
    evidence: tuple[EvidenceSummary, ...] = ()
    strategy_profile: StrategyProfile | None = None
    strategy_rationale: tuple[str, ...] = ()
    host_profile: HostProfile | None = None
    compatibility_status: str | None = None
    compatibility_reasons: tuple[CompatibilityReason, ...] = ()
    actions: tuple[ActionPlanEntry, ...] = ()
    notices: tuple[Notice, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "status": self.status,
            "target_ref": self.target_ref,
            "actions": [action.to_dict() for action in self.actions],
            "evidence": [summary.to_dict() for summary in self.evidence],
            "strategy_rationale": list(self.strategy_rationale),
            "compatibility_reasons": [reason.to_dict() for reason in self.compatibility_reasons],
            "notices": [notice.to_dict() for notice in self.notices],
        }
        if self.resolved_resource_id is not None:
            payload["resolved_resource_id"] = self.resolved_resource_id
        if self.primary_object is not None:
            payload["primary_object"] = self.primary_object.to_dict()
        if self.source is not None:
            payload["source"] = self.source.to_dict()
        if self.strategy_profile is not None:
            payload["strategy_profile"] = self.strategy_profile.to_dict()
        if self.host_profile is not None:
            payload["host_profile"] = self.host_profile.to_dict()
        if self.compatibility_status is not None:
            payload["compatibility_status"] = self.compatibility_status
        return payload
