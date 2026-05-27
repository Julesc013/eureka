from __future__ import annotations

import unittest

from runtime.gateway.public_api import build_demo_public_alpha_readonly_api


class PublicAlphaReadOnlyApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.api = build_demo_public_alpha_readonly_api()

    def test_status_is_snapshot_backed_and_read_only(self) -> None:
        response = self.api.status({})
        payload = response.body

        self.assertEqual(response.status_code, 200)
        self.assertTrue(payload["read_only"])
        self.assertTrue(payload["reviewed_index_only"])
        self.assertTrue(payload["snapshot_backed"])
        self.assertTrue(payload["relay_backed"])
        self.assertFalse(payload["live_source_actions_enabled"])
        self.assertFalse(payload["download_enabled"])
        self.assertFalse(payload["extraction_enabled"])
        self.assertFalse(payload["deployment_performed"])
        self.assertFalse(payload["production_readiness_claimed"])
        self.assertFalse(payload["public_launch_readiness_claimed"])
        self.assertGreater(payload["snapshot"]["record_count"], 0)

    def test_search_returns_reviewed_snapshot_record(self) -> None:
        response = self.api.search({"q": ["sampleproject"]})
        payload = response.body

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["mode"], "reviewed_snapshot_read_only")
        self.assertEqual(payload["result_count"], 1)
        self.assertEqual(payload["results"][0]["object_id"], "sampleproject")
        self.assertEqual(payload["relay_query_response"]["result_count"], 1)
        self.assertEqual(payload["object_pages"][0]["record"]["object_id"], "sampleproject")
        self.assertGreater(len(payload["source_summaries"]), 0)
        self.assertGreater(len(payload["evidence_summaries"]), 0)

    def test_unknown_search_returns_absence_and_known_need(self) -> None:
        response = self.api.search({"q": ["not present in snapshot"]})
        payload = response.body

        self.assertEqual(response.status_code, 200)
        self.assertEqual(payload["result_count"], 0)
        self.assertGreater(len(payload["absence_summaries"]), 0)
        self.assertGreater(len(payload["known_needs"]), 0)

    def test_object_and_summary_packets_are_public_safe(self) -> None:
        object_response = self.api.object("sampleproject")
        source_response = self.api.source_summary("source-summary-sampleproject-001")
        evidence_response = self.api.evidence_summary("evidence-summary-sampleproject-001")

        self.assertEqual(object_response.status_code, 200)
        self.assertNotIn("private_notes", object_response.body["record"])
        self.assertEqual(source_response.status_code, 200)
        self.assertFalse(source_response.body["source_summary"]["raw_response_included"])
        self.assertEqual(evidence_response.status_code, 200)
        self.assertFalse(evidence_response.body["evidence_summary"]["raw_evidence_blob_included"])

    def test_forbidden_public_alpha_controls_are_blocked(self) -> None:
        for query, expected_code in (
            ({"q": ["sampleproject"], "download": ["1"]}, "downloads_disabled"),
            ({"q": ["sampleproject"], "live_probe": ["1"]}, "live_probes_disabled"),
            ({"q": ["sampleproject"], "index_path": ["D:/private/index.sqlite3"]}, "local_paths_forbidden"),
            ({"q": ["sampleproject"], "url": ["https://example.invalid"]}, "forbidden_parameter"),
        ):
            with self.subTest(query=query):
                response = self.api.search(query)
                self.assertEqual(response.status_code, 400)
                self.assertEqual(response.body["error"]["code"], expected_code)


if __name__ == "__main__":
    unittest.main()
