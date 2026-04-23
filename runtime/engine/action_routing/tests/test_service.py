from __future__ import annotations

import unittest

from runtime.connectors.github_releases import GitHubReleasesConnector
from runtime.connectors.synthetic_software import SyntheticSoftwareConnector
from runtime.engine.action_routing.service import DeterministicActionPlanService
from runtime.engine.core import NormalizedCatalog
from runtime.engine.interfaces.extract import (
    extract_github_release_source_record,
    extract_synthetic_source_record,
)
from runtime.engine.interfaces.normalize import (
    normalize_extracted_record,
    normalize_github_release_record,
)
from runtime.engine.interfaces.public import ActionPlanRequest


def _build_demo_catalog() -> NormalizedCatalog:
    synthetic_records = tuple(
        normalize_extracted_record(extract_synthetic_source_record(record))
        for record in SyntheticSoftwareConnector().load_source_records()
    )
    github_records = tuple(
        normalize_github_release_record(extract_github_release_source_record(record))
        for record in GitHubReleasesConnector().load_source_records()
    )
    return NormalizedCatalog(synthetic_records + github_records)


class DeterministicActionPlanServiceTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.service = DeterministicActionPlanService(_build_demo_catalog())

    def test_resolved_target_with_no_host_profile_returns_bounded_default_action_plan(self) -> None:
        result = self.service.plan_actions(
            ActionPlanRequest.from_parts("fixture:software/synthetic-demo-app@1.0.0")
        )

        self.assertEqual(result.status, "planned")
        self.assertEqual(result.target_ref, "fixture:software/synthetic-demo-app@1.0.0")
        self.assertIsNone(result.compatibility_status)
        self.assertEqual(result.actions[0].action_id, "inspect_primary_representation")
        self.assertEqual(result.actions[0].status, "recommended")
        self.assertEqual(result.actions[1].action_id, "access_representation")
        self.assertEqual(result.actions[1].status, "unavailable")

    def test_compatible_target_and_host_yield_a_recommended_action(self) -> None:
        result = self.service.plan_actions(
            ActionPlanRequest.from_parts(
                "github-release:cli/cli@v2.65.0",
                "windows-x86_64",
            )
        )

        self.assertEqual(result.status, "planned")
        self.assertEqual(result.compatibility_status, "compatible")
        self.assertEqual(result.host_profile.host_profile_id, "windows-x86_64")
        direct_action = next(action for action in result.actions if action.action_id == "access_representation")
        self.assertEqual(direct_action.status, "recommended")
        self.assertEqual(direct_action.representation_kind, "release_asset")
        self.assertEqual(direct_action.source_family, "github_releases")
        self.assertTrue(direct_action.access_locator.endswith("gh_2.65.0_windows_amd64.msi"))

    def test_incompatible_target_and_host_yield_conservative_action_statuses(self) -> None:
        result = self.service.plan_actions(
            ActionPlanRequest.from_parts(
                "github-release:cli/cli@v2.65.0",
                "linux-x86_64",
            )
        )

        self.assertEqual(result.status, "planned")
        self.assertEqual(result.compatibility_status, "incompatible")
        inspect_action = next(action for action in result.actions if action.action_id == "inspect_primary_representation")
        direct_action = next(action for action in result.actions if action.action_id == "access_representation")
        self.assertEqual(inspect_action.status, "recommended")
        self.assertEqual(direct_action.status, "unavailable")
        self.assertIn("host_incompatible_for_direct_representation", direct_action.reason_codes)

    def test_unknown_compatibility_target_preserves_honest_unknown_friendly_planning(self) -> None:
        result = self.service.plan_actions(
            ActionPlanRequest.from_parts(
                "fixture:software/synthetic-demo-app@1.0.0",
                "windows-x86_64",
            )
        )

        self.assertEqual(result.status, "planned")
        self.assertEqual(result.compatibility_status, "unknown")
        self.assertEqual(result.compatibility_reasons[0].code, "compatibility_requirements_missing")
        inspect_action = next(action for action in result.actions if action.action_id == "inspect_primary_representation")
        self.assertEqual(inspect_action.status, "recommended")

    def test_store_context_marks_store_actions_available(self) -> None:
        result = self.service.plan_actions(
            ActionPlanRequest.from_parts(
                "github-release:cli/cli@v2.65.0",
                store_actions_enabled=True,
            )
        )

        store_manifest = next(action for action in result.actions if action.action_id == "store_resolution_manifest")
        store_bundle = next(action for action in result.actions if action.action_id == "store_resolution_bundle")
        self.assertEqual(store_manifest.status, "available")
        self.assertEqual(store_bundle.status, "available")
