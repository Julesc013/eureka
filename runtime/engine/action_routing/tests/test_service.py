from __future__ import annotations

import unittest

from runtime.connectors.github_releases import GitHubReleasesConnector
from runtime.connectors.synthetic_software import SyntheticSoftwareConnector
from runtime.engine.core import NormalizedCatalog
from runtime.engine.action_routing.service import DeterministicActionPlanService
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

    def test_resolved_target_with_no_strategy_returns_bounded_default_action_plan(self) -> None:
        result = self.service.plan_actions(
            ActionPlanRequest.from_parts("fixture:software/synthetic-demo-app@1.0.0")
        )

        self.assertEqual(result.status, "planned")
        self.assertEqual(result.target_ref, "fixture:software/synthetic-demo-app@1.0.0")
        self.assertEqual(result.strategy_profile.strategy_id, "inspect")
        self.assertIsNone(result.compatibility_status)
        self.assertEqual(
            next(action for action in result.actions if action.action_id == "inspect_primary_representation").status,
            "recommended",
        )
        self.assertEqual(
            next(action for action in result.actions if action.action_id == "access_representation").status,
            "available",
        )

    def test_same_target_produces_different_emphasis_under_two_strategies(self) -> None:
        inspect_plan = self.service.plan_actions(
            ActionPlanRequest.from_parts(
                "github-release:cli/cli@v2.65.0",
                "windows-x86_64",
                "inspect",
            )
        )
        acquire_plan = self.service.plan_actions(
            ActionPlanRequest.from_parts(
                "github-release:cli/cli@v2.65.0",
                "windows-x86_64",
                "acquire",
            )
        )

        inspect_direct = next(action for action in inspect_plan.actions if action.action_id == "access_representation")
        acquire_direct = next(action for action in acquire_plan.actions if action.action_id == "access_representation")
        inspect_review = next(
            action for action in inspect_plan.actions if action.action_id == "inspect_primary_representation"
        )
        acquire_review = next(
            action for action in acquire_plan.actions if action.action_id == "inspect_primary_representation"
        )

        self.assertEqual(inspect_plan.strategy_profile.strategy_id, "inspect")
        self.assertEqual(acquire_plan.strategy_profile.strategy_id, "acquire")
        self.assertEqual(inspect_review.status, "recommended")
        self.assertEqual(inspect_direct.status, "available")
        self.assertEqual(acquire_review.status, "available")
        self.assertEqual(acquire_direct.status, "recommended")

    def test_strategy_changes_recommendation_emphasis_without_changing_resolution_identity_or_evidence(self) -> None:
        inspect_plan = self.service.plan_actions(
            ActionPlanRequest.from_parts("fixture:software/archivebox@0.8.5", None, "inspect")
        )
        preserve_plan = self.service.plan_actions(
            ActionPlanRequest.from_parts(
                "fixture:software/archivebox@0.8.5",
                None,
                "preserve",
                store_actions_enabled=True,
            )
        )

        self.assertEqual(inspect_plan.resolved_resource_id, preserve_plan.resolved_resource_id)
        self.assertEqual(inspect_plan.primary_object.id, preserve_plan.primary_object.id)
        self.assertEqual(
            [entry.to_dict() for entry in inspect_plan.evidence],
            [entry.to_dict() for entry in preserve_plan.evidence],
        )
        self.assertNotEqual(
            [action.status for action in inspect_plan.actions],
            [action.status for action in preserve_plan.actions],
        )

    def test_unavailable_actions_remain_explicit_under_all_strategies(self) -> None:
        for strategy_id in ("inspect", "preserve", "acquire", "compare"):
            with self.subTest(strategy_id=strategy_id):
                result = self.service.plan_actions(
                    ActionPlanRequest.from_parts(
                        "fixture:software/archivebox@0.8.5",
                        None,
                        strategy_id,
                    )
                )
                direct_action = next(action for action in result.actions if action.action_id == "access_representation")
                self.assertEqual(direct_action.status, "unavailable")
                self.assertIn("direct_representation_missing", direct_action.reason_codes)

    def test_strategy_aware_action_plan_remains_host_aware_when_host_is_supplied(self) -> None:
        compatible_result = self.service.plan_actions(
            ActionPlanRequest.from_parts(
                "github-release:cli/cli@v2.65.0",
                "windows-x86_64",
                "acquire",
            )
        )
        incompatible_result = self.service.plan_actions(
            ActionPlanRequest.from_parts(
                "github-release:cli/cli@v2.65.0",
                "linux-x86_64",
                "acquire",
            )
        )

        compatible_direct = next(
            action for action in compatible_result.actions if action.action_id == "access_representation"
        )
        incompatible_direct = next(
            action for action in incompatible_result.actions if action.action_id == "access_representation"
        )

        self.assertEqual(compatible_result.compatibility_status, "compatible")
        self.assertEqual(incompatible_result.compatibility_status, "incompatible")
        self.assertEqual(compatible_direct.status, "recommended")
        self.assertEqual(incompatible_direct.status, "unavailable")

    def test_compare_strategy_promotes_subject_state_and_comparison_actions_when_meaningful(self) -> None:
        result = self.service.plan_actions(
            ActionPlanRequest.from_parts("fixture:software/archivebox@0.8.5", None, "compare")
        )

        subject_states_action = next(
            action for action in result.actions if action.action_id == "list_subject_states"
        )
        compare_action = next(action for action in result.actions if action.action_id == "compare_target")

        self.assertEqual(result.strategy_profile.strategy_id, "compare")
        self.assertEqual(subject_states_action.status, "recommended")
        self.assertEqual(compare_action.status, "recommended")
        self.assertEqual(subject_states_action.subject_key, "archivebox")
        self.assertEqual(compare_action.subject_key, "archivebox")

    def test_unknown_compatibility_target_preserves_honest_unknown_friendly_planning(self) -> None:
        result = self.service.plan_actions(
            ActionPlanRequest.from_parts(
                "fixture:software/synthetic-demo-app@1.0.0",
                "windows-x86_64",
                "acquire",
            )
        )

        self.assertEqual(result.status, "planned")
        self.assertEqual(result.compatibility_status, "unknown")
        self.assertEqual(result.compatibility_reasons[0].code, "compatibility_requirements_missing")
        inspect_action = next(action for action in result.actions if action.action_id == "inspect_primary_representation")
        self.assertEqual(inspect_action.status, "recommended")
