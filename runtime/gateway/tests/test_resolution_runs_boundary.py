from __future__ import annotations

import tempfile
import unittest

from runtime.engine.interfaces.public import ResolutionRunRecord
from runtime.gateway import build_demo_resolution_runs_public_api
from runtime.gateway.public_api import (
    DeterministicSearchRunRequest,
    ExactResolutionRunRequest,
    PlannedSearchRunRequest,
    ResolutionRunReadRequest,
    ResolutionRunsPublicApi,
)
from runtime.local.service.workbench_run_review_projection import (
    PUBLIC_DISALLOWED_ACTIONS,
    public_surface_operator_action_audit,
)


KNOWN_TARGET_REF = "fixture:software/synthetic-demo-app@1.0.0"
MISSING_TARGET_REF = "fixture:software/missing-demo-app@0.0.1"


class ResolutionRunsPublicApiTestCase(unittest.TestCase):
    def test_start_read_and_list_exact_and_search_runs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            public_api = build_demo_resolution_runs_public_api(temp_dir)

            resolve_response = public_api.start_exact_resolution_run(
                ExactResolutionRunRequest.from_parts(KNOWN_TARGET_REF)
            )
            search_response = public_api.start_deterministic_search_run(
                DeterministicSearchRunRequest.from_parts("synthetic")
            )
            listed_response = public_api.list_runs()
            read_response = public_api.get_run(
                ResolutionRunReadRequest.from_parts("run-exact-resolution-0001")
            )

        self.assertEqual(resolve_response.status_code, 200)
        self.assertEqual(resolve_response.body["selected_run_id"], "run-exact-resolution-0001")
        self.assertEqual(resolve_response.body["runs"][0]["checked_source_ids"], [
            "article-scan-recorded-fixtures",
            "github-releases-recorded-fixtures",
            "internet-archive-recorded-fixtures",
            "local-bundle-fixtures",
            "manual-document-recorded-fixtures",
            "package-registry-recorded-fixtures",
            "review-description-recorded-fixtures",
            "software-heritage-recorded-fixtures",
            "sourceforge-recorded-fixtures",
            "synthetic-fixtures",
            "wayback-memento-recorded-fixtures",
        ])
        self.assertEqual(search_response.status_code, 200)
        self.assertEqual(search_response.body["selected_run_id"], "run-deterministic-search-0002")
        self.assertEqual(listed_response.body["run_count"], 2)
        self.assertEqual(read_response.body["runs"][0]["run_kind"], "exact_resolution")

    def test_missing_run_returns_structured_not_found(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            public_api = build_demo_resolution_runs_public_api(temp_dir)
            response = public_api.get_run(
                ResolutionRunReadRequest.from_parts("run-exact-resolution-9999")
            )

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.body["status"], "blocked")
        self.assertEqual(response.body["notices"][0]["code"], "resolution_run_not_found")

    def test_missing_exact_target_records_absence_without_placeholder_sources(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            public_api = build_demo_resolution_runs_public_api(temp_dir)
            response = public_api.start_exact_resolution_run(
                ExactResolutionRunRequest.from_parts(MISSING_TARGET_REF)
            )

        self.assertEqual(response.status_code, 200)
        run = response.body["runs"][0]
        self.assertIsNone(run["result_summary"])
        self.assertEqual(run["absence_report"]["request_kind"], "resolve")
        self.assertNotIn("internet-archive-placeholder", run["checked_source_ids"])

    def test_planned_search_run_stores_resolution_task_summary(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            public_api = build_demo_resolution_runs_public_api(temp_dir)
            response = public_api.start_planned_search_run(
                PlannedSearchRunRequest.from_parts("latest Firefox before XP support ended")
            )

        self.assertEqual(response.status_code, 200)
        run = response.body["runs"][0]
        self.assertEqual(run["run_kind"], "planned_search")
        self.assertEqual(run["resolution_task"]["task_kind"], "find_latest_compatible_release")
        self.assertEqual(run["resolution_task"]["constraints"]["product_hint"], "Firefox")

    def test_fallback_summary_projects_without_operator_actions(self) -> None:
        service = FakeFallbackRunService()
        public_api = ResolutionRunsPublicApi(service)

        response = public_api.start_deterministic_search_run(
            DeterministicSearchRunRequest.from_parts("missing"),
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(service.search_requests, ["missing"])
        fallback = response.body["runs"][0]["fallback_summary"]
        self.assertEqual(fallback["status"], "candidate")
        self.assertEqual(fallback["public_action_posture"]["allowed"], ["view", "inspect_evidence"])
        serialized = str(fallback)
        for action in PUBLIC_DISALLOWED_ACTIONS:
            self.assertNotIn(action, serialized)
        audit = public_surface_operator_action_audit(response.body)
        self.assertEqual(audit["status"], "pass")
        self.assertFalse(audit["operator_actions_exposed_publicly"])


class FakeFallbackRunService:
    def __init__(self) -> None:
        self.search_requests: list[str] = []

    def run_exact_resolution(self, request: ExactResolutionRunRequest) -> ResolutionRunRecord:
        raise AssertionError("fallback projection test should not run exact resolution")

    def run_deterministic_search(self, request: DeterministicSearchRunRequest) -> ResolutionRunRecord:
        self.search_requests.append(request.query)
        return ResolutionRunRecord(
            run_id="run-deterministic-search-0001",
            run_kind="deterministic_search",
            requested_value=request.query,
            status="completed",
            started_at="2026-04-24T00:00:00+00:00",
            completed_at="2026-04-24T00:00:00+00:00",
            checked_source_ids=(),
            checked_source_families=(),
            fallback_summary={
                "schema_version": "eureka.resolution_run.indexless_fallback.v0",
                "mode": "indexless_live_search_fallback",
                "status": "candidate",
                "candidate_count": 1,
                "candidates": [
                    {
                        "candidate_id": "ia-meta-candidate:test",
                        "status": "candidate",
                        "verified": False,
                        "accepted_truth": False,
                        "public_actions": ["view", "inspect_evidence"],
                    }
                ],
                "accepted_truth": False,
                "verified": False,
                "reviewed_record_created": False,
                "reviewed_index_mutated": False,
                "public_action_posture": {
                    "allowed": ["view", "inspect_evidence"],
                    "operator_actions_exposed": False,
                    "unsafe_actions_enabled": False,
                },
            },
        )

    def run_planned_search(self, request: PlannedSearchRunRequest) -> ResolutionRunRecord:
        raise AssertionError("fallback projection test should not run planned search")

    def get_run(self, run_id: str) -> ResolutionRunRecord:
        raise AssertionError("fallback projection test should not read runs")

    def list_runs(self) -> tuple[ResolutionRunRecord, ...]:
        return ()


if __name__ == "__main__":
    unittest.main()
