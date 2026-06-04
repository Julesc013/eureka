from __future__ import annotations

import unittest

from runtime.engine.interfaces.public import ResolutionRunRecord
from runtime.local.service.workbench_run_review_projection import project_workbench_run_review
from runtime.surface import SurfaceKernel, SurfaceRequest


class SurfaceKernelTests(unittest.TestCase):
    def test_public_resolution_run_filters_operator_actions_and_preserves_candidate(self) -> None:
        run = _run_with_fallback(_candidate_fallback())
        result = SurfaceKernel().project(
            SurfaceRequest(
                route_id="resolution_run",
                entity_id=run.run_id,
                payload=run,
                requested_profile="json_v0",
                visibility_posture="public",
            )
        )

        view = result["view_model"]
        fallback = view["payload"]["fallback_summary"]

        self.assertEqual(result["capability"]["representation_profile"], "json_v0")
        self.assertEqual(view["canonical_status"], "candidate")
        self.assertEqual(fallback["canonical_status"], "candidate")
        self.assertFalse(fallback["verified"])
        self.assertFalse(fallback["accepted_truth"])
        self.assertFalse(result["surface_kernel_called_source_provider"])
        self.assertFalse(result["surface_kernel_mutated_public_index"])
        serialized = repr(result["renderer_result"]["renderer_input"])
        for action in ("review_candidate", "promote", "reject", "rebuild_index"):
            self.assertNotIn(action, serialized)

    def test_fallback_statuses_project_honestly(self) -> None:
        cases = (
            ("candidate", _candidate_fallback(), "candidate"),
            ("need", _need_fallback(), "need"),
            ("policy_blocked", _status_fallback("policy_blocked"), "policy_blocked"),
            ("unavailable", _status_fallback("unavailable"), "unavailable"),
            ("mystery_state", _status_fallback("mystery_state"), "unknown"),
        )
        for label, fallback, expected in cases:
            with self.subTest(status=label):
                result = SurfaceKernel().project(
                    SurfaceRequest(
                        route_id="resolution_run",
                        payload=_run_with_fallback(fallback),
                        visibility_posture="public",
                    )
                )
                view = result["view_model"]
                fallback_view = view["payload"]["fallback_summary"]
                self.assertEqual(view["canonical_status"], expected)
                self.assertEqual(fallback_view["canonical_status"], expected)
                self.assertFalse(fallback_view["verified"])
                self.assertNotEqual(expected, "verified")

    def test_private_workbench_projection_keeps_operator_actions_private(self) -> None:
        workbench = project_workbench_run_review(_run_with_fallback(_candidate_fallback()))

        private_result = SurfaceKernel().project(
            SurfaceRequest(
                route_id="workbench_run_review",
                payload=workbench,
                visibility_posture="operator_private",
                requested_profile="json_v0",
            )
        )
        public_result = SurfaceKernel().project(
            SurfaceRequest(
                route_id="workbench_run_review",
                payload=workbench,
                visibility_posture="public",
                requested_profile="json_v0",
            )
        )

        private_actions = {item["action_id"] for item in private_result["view_model"]["actions"]}
        public_actions = {item["action_id"] for item in public_result["view_model"]["actions"]}

        self.assertIn("review_candidate", private_actions)
        self.assertIn("promote", private_actions)
        self.assertNotIn("review_candidate", public_actions)
        self.assertEqual(public_result["view_model"]["view_family"], "degraded")
        self.assertFalse(private_result["surface_kernel_mutated_master_index"])

    def test_renderer_receives_policy_filtered_copy_and_cannot_mutate_kernel_view(self) -> None:
        def mutating_renderer(view_model):
            view_model["actions"].append({"action_id": "promote"})
            return {"content": "ok", "action_count_seen": len(view_model["actions"])}

        result = SurfaceKernel().project(
            SurfaceRequest(
                route_id="resolution_run",
                payload=_run_with_fallback(_candidate_fallback()),
                visibility_posture="public",
                renderer=mutating_renderer,
            )
        )

        view_actions = {item["action_id"] for item in result["view_model"]["actions"]}
        renderer_actions = {item["action_id"] for item in result["renderer_result"]["renderer_input"]["actions"]}

        self.assertNotIn("promote", view_actions)
        self.assertNotIn("promote", renderer_actions)
        self.assertFalse(result["renderer_result"]["renderer_input_mutated"])
        self.assertFalse(result["renderer_result"]["renderer_called_source_provider"])
        self.assertFalse(result["renderer_result"]["renderer_created_verified_state"])

    def test_kernel_does_not_call_source_provider_from_context(self) -> None:
        calls = []

        def loader(_request):
            return _run_with_fallback(_candidate_fallback())

        result = SurfaceKernel(view_loader=loader).project(
            SurfaceRequest(route_id="resolution_run", entity_id="run", visibility_posture="public")
        )

        self.assertEqual(calls, [])
        self.assertFalse(result["surface_kernel_called_source_provider"])


def _run_with_fallback(fallback: dict[str, object]) -> ResolutionRunRecord:
    return ResolutionRunRecord(
        run_id="run-surface-0001",
        run_kind="deterministic_search",
        requested_value=str(fallback.get("query", "missing")),
        status="completed",
        started_at="2026-04-24T00:00:00+00:00",
        completed_at="2026-04-24T00:00:00+00:00",
        checked_source_ids=(),
        checked_source_families=(),
        fallback_summary=fallback,
    )


def _candidate_fallback() -> dict[str, object]:
    return {
        "schema_version": "eureka.resolution_run.indexless_fallback.v0",
        "mode": "indexless_live_search_fallback",
        "status": "candidate",
        "trigger": "local_lookup_no_results",
        "query": "missing",
        "source_id": "internet_archive_metadata",
        "source_family": "internet_archive",
        "source_allowlisted": True,
        "fallback_enabled": True,
        "reason_codes": ["fallback_candidates_available"],
        "candidate_count": 1,
        "candidates": [
            {
                "candidate_id": "ia-meta-candidate:surface",
                "status": "candidate",
                "title": "Archive.org metadata candidate",
                "verified": False,
                "accepted_truth": False,
                "public_actions": ["view", "inspect_evidence", "promote"],
            }
        ],
        "need_count": 0,
        "needs": [],
        "accepted_truth": False,
        "verified": False,
        "reviewed_record_created": False,
        "reviewed_index_mutated": False,
        "public_index_mutated": False,
    }


def _need_fallback() -> dict[str, object]:
    fallback = _candidate_fallback()
    fallback.update(
        {
            "status": "need",
            "candidate_count": 0,
            "candidates": [],
            "need_count": 1,
            "needs": [{"need_id": "need-surface", "status": "need", "verified": False}],
        }
    )
    return fallback


def _status_fallback(status: str) -> dict[str, object]:
    fallback = _candidate_fallback()
    fallback.update({"status": status, "candidate_count": 0, "candidates": [], "need_count": 0, "needs": []})
    return fallback


if __name__ == "__main__":
    unittest.main()
