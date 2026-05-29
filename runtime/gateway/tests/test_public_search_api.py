from __future__ import annotations

from urllib.parse import parse_qs
import unittest

from runtime.engine.query_planner import DeterministicQueryPlannerService
from runtime.gateway.public_api import (
    PublicSearchPublicApi,
    build_demo_public_search_public_api,
)
from runtime.source.registry import load_source_registry


class PublicSearchPublicApiTestCase(unittest.TestCase):
    def setUp(self) -> None:
        self.public_api = build_demo_public_search_public_api()

    def test_search_returns_governed_result_cards(self) -> None:
        response = self.public_api.search(parse_qs("q=windows+7+apps&limit=3"))

        self.assertEqual(response.status_code, 200)
        payload = response.body
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["mode"], "local_index_only")
        self.assertGreater(len(payload["results"]), 0)
        card = payload["results"][0]
        self.assertEqual(card["contract_id"], "eureka_public_search_result_card_v0")
        self.assertIn(card["result_lane"], {"inside_bundles", "best_direct_answer", "other"})
        self.assertIn("source_id", card["source"])
        self.assertIn("score", card["user_cost"])
        self.assertIn("summaries", card["evidence"])
        self.assertIn("status", card["compatibility"])
        blocked_actions = {entry["action_id"] for entry in card["actions"]["blocked"]}
        self.assertGreaterEqual(blocked_actions, {"download", "install_handoff", "execute", "upload"})
        self.assertIn("no_live_probe", card["limitations"])
        self.assertIn("no_rights_clearance", card["limitations"])

    def test_no_result_returns_absence_success_not_internal_error(self) -> None:
        response = self.public_api.search({"q": ["zzzz no such eureka fixture"]})

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.body["ok"])
        self.assertEqual(response.body["results"], [])
        self.assertEqual(response.body["absence_summary"]["status"], "bounded_absence")
        self.assertEqual(response.body["gaps"][0]["gap_type"], "bounded_absence")

    def test_query_plan_status_and_sources_are_public_safe(self) -> None:
        plan = self.public_api.query_plan(parse_qs("q=windows+7+apps"))
        status = self.public_api.status()
        sources = self.public_api.list_sources({})
        source = self.public_api.get_source("local-bundle-fixtures")

        self.assertEqual(plan.status_code, 200)
        self.assertEqual(plan.body["mode"], "local_index_only")
        self.assertTrue(plan.body["no_live_probe"])
        self.assertEqual(status.body["public_search"]["implementation_scope"], "local_prototype_backend")
        self.assertFalse(status.body["public_search"]["live_probes_enabled"])
        self.assertFalse(status.body["public_search"]["downloads_enabled"])
        self.assertEqual(sources.status_code, 200)
        self.assertGreater(sources.body["source_count"], 0)
        self.assertEqual(source.status_code, 200)
        self.assertEqual(source.body["selected_source_id"], "local-bundle-fixtures")
        serialized = str(source.body)
        self.assertNotIn("D:/", serialized)
        self.assertNotIn("C:/", serialized)

    def test_archive_org_metadata_candidate_lane_is_review_only(self) -> None:
        public_api = PublicSearchPublicApi(
            index_records=(),
            source_registry=load_source_registry(),
            query_planner=DeterministicQueryPlannerService(),
            archive_org_metadata_candidates=FakeArchiveOrgCandidateProvider(),
        )

        response = public_api.search(
            parse_qs("q=audacity&source_policy=archive_org_metadata_candidates")
        )

        self.assertEqual(response.status_code, 200)
        payload = response.body
        self.assertEqual(payload["mode"], "local_index_only")
        self.assertEqual(payload["source_policy"], "archive_org_metadata_candidates")
        self.assertEqual(payload["results"], [])
        self.assertEqual(payload["candidate_result_count"], 1)
        self.assertEqual(payload["absence_summary"]["status"], "candidate_results_only")
        self.assertTrue(payload["archive_org_metadata_candidate_search_enabled"])
        self.assertTrue(payload["archive_org_metadata_external_call_performed"])
        self.assertFalse(payload["live_probes_enabled"])
        self.assertFalse(payload["downloads_enabled"])
        candidate = payload["candidate_results"][0]
        self.assertEqual(candidate["result_lane"], "source_candidates")
        self.assertEqual(candidate["source"]["checked_as"], "archive_org_metadata_candidate_search")
        self.assertEqual(candidate["user_cost"]["label"], "medium")
        self.assertIn("download", {item["action_id"] for item in candidate["actions"]["blocked"]})
        self.assertNotEqual(candidate["rights"]["distribution_allowed"], "yes")
        source_status = {item["source_id"]: item for item in payload["source_status"]}
        self.assertEqual(source_status["internet_archive_metadata"]["status"], "metadata_candidate_source")
        self.assertTrue(source_status["internet_archive_metadata"]["network_required"])
        self.assertFalse(source_status["internet_archive_metadata"]["live_enabled"])


class FakeArchiveOrgCandidateProvider:
    def search_metadata_candidates(self, query: str, limit: int) -> dict[str, object]:
        return {
            "schema_version": "archive_org_metadata_candidate_search.v0",
            "status": "succeeded",
            "query": query,
            "source_id": "internet_archive_metadata",
            "source_family": "internet_archive",
            "source_label": "Internet Archive metadata search",
            "candidate_count": 1,
            "candidates": [
                {
                    "candidate_id": "ia-meta-candidate:test",
                    "candidate_title": "Audacity metadata candidate",
                    "candidate_summary": "Archive.org metadata candidate for Audacity.",
                    "identifier": "audacity_fixture",
                    "date": "2008",
                    "source_locator": {
                        "url": "https://archive.org/details/audacity_fixture",
                    },
                    "limitations": ["archive_org_metadata_only"],
                }
            ],
            "total_http_requests": 1,
            "live_call_performed": True,
            "metadata_request_performed": True,
            "source_probe_executed": False,
            "cache_hit": False,
            "raw_response_committed": False,
            "download_performed": False,
            "upload_performed": False,
            "extraction_executed": False,
            "accepted_truth": False,
            "review_required": True,
            "warnings": ["Archive.org metadata candidate requires review."],
            "limitations": ["archive_org_metadata_only", "candidate_not_reviewed_truth"],
        }


if __name__ == "__main__":
    unittest.main()
