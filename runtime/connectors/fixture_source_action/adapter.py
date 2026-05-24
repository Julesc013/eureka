from __future__ import annotations

from typing import Any, Mapping

from runtime.source.action.action_kernel import CREATED_AT, stable_id


class FixtureSourceActionAdapter:
    adapter_id = "fixture_source_action"
    source_family = "fixture_source_action"
    supported_action_kinds = ("metadata_search",)
    supported_transport_modes = ("fixture", "mock_live")

    def manifest(self) -> dict[str, Any]:
        return {
            "schema_version": "source_action_manifest.v0",
            "record_type": "source_action_manifest",
            "created_at": CREATED_AT,
            "source_family": self.source_family,
            "display_name": "Fixture Source Action",
            "manifest_version": "0.0",
            "adapter_id": self.adapter_id,
            "supported_action_kinds": list(self.supported_action_kinds),
            "supported_transport_modes": list(self.supported_transport_modes),
            "capability_profile_ref": "contracts/source/action/source_capability_profile.v0.json",
            "policy_ref": "control/policies/source_action_kernel_policy.json",
            "fixture_refs": ["examples/source_actions/fixture_source_action_manifest.json"],
            "live_policy_required": True,
            "default_enabled": False,
            "public_fanout_allowed": False,
            "downloads_allowed": False,
            "extraction_allowed": False,
            "review_required": True,
            "source_action_id": stable_id("source_action_manifest", self.source_family),
            "projection_profile": "operator_workbench",
            "dry_run": True,
            "live_call_performed": False,
            "accepted_truth": False,
            "limitations": ["deterministic_fixture_only"],
            "non_claims": ["not_truth", "not_live_source_behavior"],
        }

    def run_fixture(self, plan: Mapping[str, Any]) -> dict[str, Any]:
        query = plan.get("query_context", {}).get("query", "sampleproject")
        return {"records": [fixture_record(str(query), plan)]}

    def run_mock(self, plan: Mapping[str, Any]) -> dict[str, Any]:
        query = plan.get("query_context", {}).get("query", "sampleproject")
        record = fixture_record(str(query), plan)
        record["transport_mode"] = "mock_live"
        record["source_locator"] = "mock://fixture-source-action/sampleproject"
        return {"records": [record]}

    def normalize(self, transport_result: Mapping[str, Any]) -> dict[str, Any]:
        observations = []
        for record in transport_result.get("records", []):
            observations.append(
                {
                    "observation_id": stable_id("source_observation", record.get("source_record_id")),
                    "source_family": self.source_family,
                    "title": record.get("title"),
                    "summary": record.get("summary"),
                    "source_locator": record.get("source_locator"),
                    "identifiers": record.get("identifiers", {}),
                    "provenance": {
                        "transport_mode": transport_result.get("transport_mode"),
                        "fixture": True,
                        "raw_response_persisted": False,
                    },
                    "confidence": "fixture",
                }
            )
        return {"observations": observations}


def fixture_record(query: str, plan: Mapping[str, Any]) -> dict[str, Any]:
    normalized_query = " ".join(query.strip().lower().split()) or "sampleproject"
    return {
        "source_record_id": stable_id("fixture_source_record", normalized_query),
        "source_family": "fixture_source_action",
        "title": f"Fixture result for {normalized_query}",
        "summary": "Deterministic fixture metadata result for source-action kernel validation.",
        "source_locator": f"fixture://source-action/{stable_id('locator', normalized_query)}",
        "identifiers": {
            "query": normalized_query,
            "action_kind": plan.get("action_kind", "metadata_search"),
            "fixture_key": "sampleproject",
        },
        "transport_mode": plan.get("transport_mode", "fixture"),
        "live_call_performed": False,
        "accepted_truth": False,
        "review_required": True,
    }


def build_adapter() -> FixtureSourceActionAdapter:
    return FixtureSourceActionAdapter()
