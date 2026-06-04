from __future__ import annotations

from copy import deepcopy
import unittest

from runtime.engine.interfaces.public import ResolutionRunRecord
from runtime.local.service.workbench_run_review_projection import project_workbench_run_review
from runtime.surface import SurfaceKernel, SurfaceRequest, dispatch_surface_renderer
from runtime.surface.renderers.html_basic_v0 import render_html_basic_v0
from runtime.surface.renderers.json_v0 import render_json_v0
from runtime.surface.renderers.snapshot_v0 import render_snapshot_v0
from runtime.surface.renderers.text_v0 import render_text_v0


class SurfaceBaselineRendererTests(unittest.TestCase):
    def test_json_renderer_outputs_public_candidate_without_operator_actions(self) -> None:
        result = _project_public_run(_candidate_fallback(), "json_v0")
        output = result["renderer_result"]["renderer_output"]

        self.assertEqual(output["media_type"], "application/json")
        self.assertEqual(output["content"]["status"], "candidate")
        self.assertEqual(output["content"]["view_model"]["canonical_status"], "candidate")
        self.assertEqual(result["cache"]["parts"]["renderer_id"], "surface_json_v0")
        self.assertFalse(result["renderer_result"]["renderer_called_source_provider"])
        self.assertFalse(result["renderer_result"]["renderer_mutated_reviewed_index"])
        self.assertFalse(output["content"]["view_model"]["payload"]["fallback_summary"]["verified"])
        serialized = repr(output)
        for action in ("review_candidate", "promote", "reject", "rebuild_index", "freeze_review"):
            self.assertNotIn(action, serialized)

    def test_all_baseline_renderers_preserve_fallback_statuses(self) -> None:
        cases = (
            ("candidate", _candidate_fallback()),
            ("need", _need_fallback()),
            ("policy_blocked", _status_fallback("policy_blocked")),
            ("unavailable", _status_fallback("unavailable")),
            ("unknown", _status_fallback("not_a_known_status")),
        )
        profiles = ("json_v0", "text_v0", "html_basic_v0", "snapshot_v0")
        for expected_status, fallback in cases:
            for profile in profiles:
                with self.subTest(status=expected_status, profile=profile):
                    result = _project_public_run(fallback, profile)
                    output = result["renderer_result"]["renderer_output"]

                    self.assertEqual(result["view_model"]["canonical_status"], expected_status)
                    self.assertIn(expected_status, repr(output))
                    self.assertNotEqual(expected_status, "verified")

    def test_text_renderer_keeps_degraded_state_visible(self) -> None:
        result = _project_public_run(_status_fallback("unavailable"), "text_v0")
        content = result["renderer_result"]["renderer_output"]["content"]

        self.assertIn("Status: unavailable", content)
        self.assertIn("Fallback status: unavailable", content)
        self.assertIn("Actions:", content)

    def test_html_basic_renderer_escapes_unsafe_text(self) -> None:
        result = SurfaceKernel().project(
            SurfaceRequest(
                route_id="candidate",
                payload={
                    "candidate_id": "unsafe-candidate",
                    "status": "candidate",
                    "title": '<script>alert(1)</script> Tom & Jerry',
                    "summary": '"quoted" <unsafe>',
                },
                requested_profile="html_basic_v0",
                visibility_posture="public",
            )
        )

        html = result["renderer_result"]["renderer_output"]["content"]

        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt; Tom &amp; Jerry", html)
        self.assertIn("&quot;quoted&quot; &lt;unsafe&gt;", html)
        self.assertNotIn("<script>alert(1)</script>", html)
        self.assertNotIn('"quoted" <unsafe>', html)

    def test_snapshot_renderer_is_deterministic(self) -> None:
        request = SurfaceRequest(
            route_id="resolution_run",
            payload=_run_with_fallback(_candidate_fallback()),
            requested_profile="snapshot_v0",
            visibility_posture="public",
            data_version="test-data-v1",
        )

        first = SurfaceKernel().project(request)
        second = SurfaceKernel().project(request)

        self.assertEqual(first["renderer_result"]["renderer_output"], second["renderer_result"]["renderer_output"])
        self.assertEqual(first["cache"], second["cache"])
        self.assertEqual(first["renderer_result"]["renderer_output"]["content"]["canonical_status"], "candidate")

    def test_private_workbench_projection_can_retain_operator_actions(self) -> None:
        workbench = project_workbench_run_review(_run_with_fallback(_candidate_fallback()))

        result = SurfaceKernel().project(
            SurfaceRequest(
                route_id="workbench_run_review",
                payload=workbench,
                requested_profile="json_v0",
                visibility_posture="operator_private",
            )
        )

        output = result["renderer_result"]["renderer_output"]
        action_ids = {item["action_id"] for item in output["content"]["view_model"]["actions"]}

        self.assertIn("review_candidate", action_ids)
        self.assertIn("promote", action_ids)
        self.assertFalse(result["renderer_result"]["renderer_mutated_public_index"])

    def test_unsupported_profile_degrades_to_html_renderer(self) -> None:
        result = _project_public_run(_candidate_fallback(), "immersive_canvas_v9")

        self.assertEqual(result["capability"]["representation_profile"], "html_basic_v0")
        self.assertTrue(result["capability"]["fallback_used"])
        self.assertEqual(result["renderer_result"]["renderer_id"], "surface_html_basic_v0")
        self.assertEqual(result["renderer_result"]["renderer_output"]["media_type"], "text/html; charset=utf-8")

    def test_renderers_do_not_mutate_input_view_model(self) -> None:
        view_model = SurfaceKernel().project(
            SurfaceRequest(
                route_id="resolution_run",
                payload=_run_with_fallback(_candidate_fallback()),
                requested_profile="json_v0",
                visibility_posture="public",
            )
        )["view_model"]
        original = deepcopy(view_model)

        for renderer in (render_json_v0, render_text_v0, render_html_basic_v0, render_snapshot_v0):
            with self.subTest(renderer=renderer.__name__):
                renderer(view_model)
                self.assertEqual(view_model, original)

    def test_dispatch_uses_policy_filtered_copy_and_does_not_call_sources_or_mutate_indexes(self) -> None:
        view_model = SurfaceKernel().project(
            SurfaceRequest(
                route_id="resolution_run",
                payload=_run_with_fallback(_candidate_fallback()),
                requested_profile="json_v0",
                visibility_posture="public",
            )
        )["view_model"]

        result = dispatch_surface_renderer(view_model, representation_profile="json_v0")

        self.assertFalse(result["renderer_input_mutated"])
        self.assertFalse(result["renderer_called_source_provider"])
        self.assertFalse(result["renderer_mutated_reviewed_index"])
        self.assertFalse(result["renderer_mutated_public_index"])
        self.assertFalse(result["renderer_mutated_master_index"])
        self.assertNotIn("promote", repr(result["renderer_input"]))


def _project_public_run(fallback: dict[str, object], profile: str) -> dict[str, object]:
    return SurfaceKernel().project(
        SurfaceRequest(
            route_id="resolution_run",
            entity_id="run-renderer-0001",
            payload=_run_with_fallback(fallback),
            requested_profile=profile,
            visibility_posture="public",
        )
    )


def _run_with_fallback(fallback: dict[str, object]) -> ResolutionRunRecord:
    return ResolutionRunRecord(
        run_id="run-renderer-0001",
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
                "candidate_id": "ia-meta-candidate:renderer",
                "status": "candidate",
                "title": "Archive metadata candidate",
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
            "needs": [
                {
                    "need_id": "need-renderer",
                    "status": "need",
                    "title": "Review need",
                    "verified": False,
                }
            ],
        }
    )
    return fallback


def _status_fallback(status: str) -> dict[str, object]:
    fallback = _candidate_fallback()
    fallback.update({"status": status, "candidate_count": 0, "candidates": [], "need_count": 0, "needs": []})
    return fallback


if __name__ == "__main__":
    unittest.main()
