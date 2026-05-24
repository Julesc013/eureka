from __future__ import annotations

from typing import Any

from runtime.source.action import build_source_wave_adapter
from runtime.source.action.action_kernel import CREATED_AT, stable_id


def build_registration() -> dict[str, Any]:
    return {
        "schema_version": "source_action_adapter_registration.v0",
        "record_type": "source_action_adapter_registration",
        "created_at": CREATED_AT,
        "source_family": "internet_archive_metadata",
        "display_name": "Internet Archive Metadata Reference",
        "manifest_version": "0.0",
        "adapter_id": "internet_archive_metadata_reference",
        "supported_action_kinds": ["metadata_search", "item_metadata_read", "file_manifest_metadata"],
        "supported_transport_modes": ["fixture", "mock_live", "operator_approved_live"],
        "capability_profile_ref": "contracts/source/action/source_capability_profile.v0.json",
        "policy_ref": "control/policies/source_action_kernel_policy.json",
        "fixture_refs": ["examples/sources/internet_archive_metadata/source_family_descriptor.json"],
        "live_policy_required": True,
        "default_enabled": False,
        "public_fanout_allowed": False,
        "downloads_allowed": False,
        "extraction_allowed": False,
        "review_required": True,
        "source_action_id": stable_id("source_action_manifest", "internet_archive_metadata"),
        "projection_profile": "operator_workbench",
        "dry_run": True,
        "live_call_performed": False,
        "accepted_truth": False,
        "limitations": [
            "registration_stub_only",
            "existing_ia_metadata_lane_behavior_unchanged",
            "no_live_ia_call_performed",
        ],
        "non_claims": ["not_truth", "not_source_expansion", "not_live_ia_behavior"],
    }


def build_adapter():
    return build_source_wave_adapter("internet_archive_metadata_v2")
