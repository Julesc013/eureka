from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping


SOURCE_CAPABILITY_FIELDS = (
    "supports_search",
    "supports_item_metadata",
    "supports_file_listing",
    "supports_bulk_access",
    "supports_delta_or_feed",
    "supports_live_probe",
    "supports_member_listing",
    "supports_reviews_or_comments",
    "supports_hashes",
    "supports_signatures",
    "supports_content_text",
    "supports_temporal_captures",
    "supports_action_paths",
    "auth_required",
    "network_required",
    "local_private",
    "fixture_backed",
    "recorded_fixture_backed",
    "live_supported",
    "live_deferred",
)


@dataclass(frozen=True)
class SourceCapabilityRecord:
    supports_search: bool
    supports_item_metadata: bool
    supports_file_listing: bool
    supports_bulk_access: bool
    supports_delta_or_feed: bool
    supports_live_probe: bool
    supports_member_listing: bool
    supports_reviews_or_comments: bool
    supports_hashes: bool
    supports_signatures: bool
    supports_content_text: bool
    supports_temporal_captures: bool
    supports_action_paths: bool
    auth_required: bool
    network_required: bool
    local_private: bool
    fixture_backed: bool
    recorded_fixture_backed: bool
    live_supported: bool
    live_deferred: bool

    @classmethod
    def from_mapping(
        cls,
        raw_capabilities: Mapping[str, Any],
        *,
        field_name: str = "capabilities",
    ) -> "SourceCapabilityRecord":
        if not isinstance(raw_capabilities, Mapping):
            raise ValueError(f"Field '{field_name}' must be an object.")
        unknown_fields = sorted(set(raw_capabilities) - set(SOURCE_CAPABILITY_FIELDS))
        if unknown_fields:
            joined_fields = ", ".join(unknown_fields)
            raise ValueError(f"Field '{field_name}' has unknown capability keys: {joined_fields}.")
        values: dict[str, bool] = {}
        for capability_name in SOURCE_CAPABILITY_FIELDS:
            if capability_name not in raw_capabilities:
                raise ValueError(f"Missing required field '{field_name}.{capability_name}'.")
            capability_value = raw_capabilities[capability_name]
            if not isinstance(capability_value, bool):
                raise ValueError(
                    f"Field '{field_name}.{capability_name}' must be a boolean."
                )
            values[capability_name] = capability_value
        return cls(**values)

    def to_dict(self) -> dict[str, bool]:
        return {
            capability_name: bool(getattr(self, capability_name))
            for capability_name in SOURCE_CAPABILITY_FIELDS
        }

    def enabled_capabilities(self) -> tuple[str, ...]:
        return tuple(
            capability_name
            for capability_name in SOURCE_CAPABILITY_FIELDS
            if getattr(self, capability_name)
        )

    def supports(self, capability_name: str) -> bool:
        if capability_name not in SOURCE_CAPABILITY_FIELDS:
            return False
        return bool(getattr(self, capability_name))
