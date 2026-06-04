from __future__ import annotations

import unittest

from runtime.surface.output_policy import apply_surface_output_policy


class SurfaceOutputPolicyTests(unittest.TestCase):
    def test_public_policy_filters_operator_and_unknown_actions(self) -> None:
        view = {
            "schema_version": "surface_view_model.v0",
            "view_model_version": "surface_view_model.v0",
            "view_family": "resolution_run",
            "route_id": "resolution_run",
            "entity_id": "run",
            "canonical_status": "candidate",
            "actions": [
                {"action_id": "view"},
                {"action_id": "cite"},
                {"action_id": "review_candidate"},
                {"action_id": "promote"},
                {"action_id": "mystery_action"},
            ],
            "payload": {
                "operator_actions": [{"action_id": "reject"}],
                "fallback_summary": {
                    "public_action_posture": {
                        "allowed": ["view", "inspect_evidence", "promote"],
                    },
                    "candidates": [
                        {"candidate_id": "candidate", "public_actions": ["view", "promote", "mystery_action"]}
                    ]
                },
            },
        }

        filtered = apply_surface_output_policy(view, visibility_posture="public")

        action_ids = {item["action_id"] for item in filtered["actions"]}
        candidate_actions = filtered["payload"]["fallback_summary"]["candidates"][0]["public_actions"]
        candidate_action_ids = {item["action_id"] for item in candidate_actions}

        self.assertEqual(action_ids, {"view", "cite"})
        self.assertEqual(candidate_action_ids, {"view"})
        self.assertEqual(
            filtered["payload"]["fallback_summary"]["public_action_posture"]["allowed"],
            ["view", "inspect_evidence"],
        )
        self.assertNotIn("operator_actions", repr(filtered))
        self.assertFalse(filtered["renderer_may_call_sources"])
        self.assertFalse(filtered["reviewed_index_mutated"])

    def test_operator_policy_keeps_operator_actions(self) -> None:
        view = {
            "schema_version": "surface_view_model.v0",
            "view_model_version": "surface_view_model.v0",
            "view_family": "workbench_run_review",
            "route_id": "workbench_run_review",
            "entity_id": "run",
            "canonical_status": "candidate",
            "actions": [{"action_id": "review_candidate"}, {"action_id": "promote"}],
            "payload": {},
        }

        filtered = apply_surface_output_policy(view, visibility_posture="operator_private")

        self.assertEqual(
            {item["action_id"] for item in filtered["actions"]},
            {"review_candidate", "promote"},
        )
        self.assertFalse(filtered["renderer_may_create_records"])


if __name__ == "__main__":
    unittest.main()
