from __future__ import annotations

import unittest

from runtime.local.local_search import LocalSearchOptions, LocalSearchService


class LocalSearchP0NoMutationTests(unittest.TestCase):
    def setUp(self) -> None:
        self.service = LocalSearchService()
        self.options = LocalSearchOptions(metadata_fallback="ia_fixture", show_evidence=True)

    def test_fixture_fallback_candidate_path(self) -> None:
        response = self.service.search("manual for Sound Blaster CT1740", self.options)

        self.assertEqual(response["status"], "candidate")
        self.assertTrue(response["metadata_fallback_used"])
        self.assertEqual(response["fallback_summary"]["candidate_count"], 1)
        self.assertEqual(response["source_observations"][0]["total_http_requests"], 0)
        self.assertFalse(response["source_observations"][0]["external_call_performed"])

    def test_fixture_fallback_need_path(self) -> None:
        response = self.service.search("article about ray tracing in a 1994 magazine", self.options)

        self.assertEqual(response["status"], "need")
        self.assertTrue(response["metadata_fallback_used"])
        self.assertEqual(response["fallback_summary"]["need_count"], 1)
        self.assertFalse(response["fallback_summary"]["verified"])

    def test_driver_query_remains_blocked_or_need_without_hardware_details(self) -> None:
        response = self.service.search("driver for Win98", self.options)

        self.assertEqual(response["status"], "need")
        self.assertEqual(response["status_concept"], "blocked_for_user_details")
        self.assertIn("hardware vendor", response["missing"])
        self.assertFalse(response["fallback_created_verified_truth"])

    def test_no_verified_truth_from_fixture_fallback(self) -> None:
        response = self.service.search("manual for Sound Blaster CT1740", self.options)

        self.assertFalse(response["fallback_created_verified_truth"])
        self.assertFalse(response["fallback_summary"]["verified"])
        self.assertFalse(response["fallback_summary"]["accepted_truth"])
        self.assertTrue(response["results"])
        self.assertTrue(all(not item["verified"] for item in response["results"]))
        self.assertTrue(all(not item["accepted_truth"] for item in response["results"]))

    def test_no_index_mutation_during_search(self) -> None:
        response = self.service.search("manual for Sound Blaster CT1740", self.options)

        self.assertFalse(response["reviewed_index_mutated"])
        self.assertFalse(response["public_index_mutated"])
        self.assertFalse(response["master_index_mutated"])
        self.assertFalse(response["reviewed_record_created"])
        self.assertFalse(response["accepted_truth_created"])

    def test_renderer_status_visibility(self) -> None:
        response = self.service.search("manual for Sound Blaster CT1740", self.options)

        text_content = response["renderer_outputs"]["text_v0"]["content"]
        html_content = response["renderer_outputs"]["html_basic_v0"]["content"]
        self.assertIn("Status: candidate", text_content)
        self.assertIn('data-status="candidate"', html_content)


if __name__ == "__main__":
    unittest.main()
