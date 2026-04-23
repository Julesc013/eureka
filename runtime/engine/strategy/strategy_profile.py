from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class StrategyProfile:
    strategy_id: str
    label: str
    description: str
    emphasis_hints: tuple[str, ...] = ()

    def to_dict(self) -> dict[str, Any]:
        return {
            "strategy_id": self.strategy_id,
            "label": self.label,
            "description": self.description,
            "emphasis_hints": list(self.emphasis_hints),
        }


_BOOTSTRAP_STRATEGY_PROFILES: dict[str, StrategyProfile] = {
    "inspect": StrategyProfile(
        strategy_id="inspect",
        label="Inspect",
        description="Prioritize bounded source inspection and evidence-aware review before more direct use.",
        emphasis_hints=(
            "prioritize_source_inspection",
            "prioritize_representation_review",
        ),
    ),
    "preserve": StrategyProfile(
        strategy_id="preserve",
        label="Preserve",
        description="Prioritize deterministic export and local preservation steps over more direct use.",
        emphasis_hints=(
            "prioritize_manifest_export",
            "prioritize_bundle_export",
            "prioritize_local_store",
        ),
    ),
    "acquire": StrategyProfile(
        strategy_id="acquire",
        label="Acquire",
        description="Prioritize direct bounded access paths when representations and compatibility signals allow it.",
        emphasis_hints=(
            "prioritize_direct_access",
            "stay_host_aware",
        ),
    ),
    "compare": StrategyProfile(
        strategy_id="compare",
        label="Compare",
        description="Prioritize side-by-side and timeline-oriented review when bounded comparison context exists.",
        emphasis_hints=(
            "prioritize_subject_states",
            "prioritize_side_by_side_comparison",
        ),
    ),
}


def bootstrap_strategy_profiles() -> tuple[StrategyProfile, ...]:
    return tuple(_BOOTSTRAP_STRATEGY_PROFILES.values())


def bootstrap_strategy_profile_ids() -> tuple[str, ...]:
    return tuple(_BOOTSTRAP_STRATEGY_PROFILES.keys())


def resolve_bootstrap_strategy_profile(strategy_id: str | None) -> StrategyProfile:
    if strategy_id is None:
        return _BOOTSTRAP_STRATEGY_PROFILES["inspect"]

    normalized_strategy_id = strategy_id.strip()
    if not normalized_strategy_id:
        return _BOOTSTRAP_STRATEGY_PROFILES["inspect"]
    try:
        return _BOOTSTRAP_STRATEGY_PROFILES[normalized_strategy_id]
    except KeyError as error:
        allowed = ", ".join(bootstrap_strategy_profile_ids())
        raise ValueError(f"strategy_id must be one of: {allowed}.") from error
