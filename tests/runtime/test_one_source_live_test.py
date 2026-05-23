import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from runtime.source.observation.sources import pypi_json_metadata as source
from scripts.run_one_source_live_test import run_one_source_live_test
from scripts.validate_one_source_live_test import validate
from runtime.review.queue import ReviewDecisionKind


class FakeResponse:
    status = 200

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return None

    def read(self):
        return json.dumps(
            {
                "info": {
                    "name": "sampleproject",
                    "version": "4.0.0",
                    "summary": "A sample Python project",
                    "project_urls": {
                        "Homepage": "https://github.com/pypa/sampleproject"
                    },
                },
                "releases": {
                    "4.0.0": []
                },
                "urls": [
                    {
                        "url": "https://files.pythonhosted.org/packages/sampleproject-4.0.0.tar.gz"
                    }
                ],
            }
        ).encode("utf-8")

    def getcode(self):
        return 200


class OneSourceLiveTestPipelineTests(unittest.TestCase):
    def run_pipeline(self, tmp: str, *, live=False, decision=ReviewDecisionKind.ACCEPT):
        root = Path(tmp)
        return run_one_source_live_test(
            package_name="sampleproject",
            source_cache_db=root / "source.sqlite",
            evidence_db=root / "evidence.sqlite",
            review_db=root / "review.sqlite",
            public_index_db=root / "public.sqlite",
            live=live,
            decision_kind=decision,
        )

    def test_dry_run_does_not_call_network(self):
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(source.urllib.request, "urlopen", side_effect=AssertionError("network called")):
                result = self.run_pipeline(tmp, live=False)
        self.assertEqual("pass", result["status"])
        self.assertFalse(result["network_used"])
        self.assertEqual(0, result["request_count"])

    def test_mocked_live_pipeline_creates_cache_evidence_review_and_index(self):
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(source.urllib.request, "urlopen", return_value=FakeResponse()) as urlopen:
                result = self.run_pipeline(tmp, live=True)
        self.assertEqual("pass", result["status"])
        self.assertEqual(1, urlopen.call_count)
        self.assertTrue(result["source_cache_entry_created"])
        self.assertTrue(result["evidence_candidate_created"])
        self.assertTrue(result["review_item_created"])
        self.assertTrue(result["review_decision_recorded"])
        self.assertTrue(result["public_index_rebuilt"])
        self.assertEqual(1, result["search_hit_count"])
        self.assertEqual(0, result["absence_hit_count"])

    def test_rejected_decision_does_not_produce_public_index_record(self):
        with tempfile.TemporaryDirectory() as tmp:
            with mock.patch.object(source.urllib.request, "urlopen", return_value=FakeResponse()):
                result = self.run_pipeline(tmp, live=True, decision=ReviewDecisionKind.REJECT)
        self.assertEqual("pass", result["status"])
        self.assertEqual(0, result["rebuild_report"]["included_count"])
        self.assertEqual(0, result["search_hit_count"])

    def test_pipeline_boundaries_are_recorded(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = self.run_pipeline(tmp, live=False)
        self.assertEqual(0, result["download_count"])
        self.assertEqual(0, result["install_execution_count"])
        self.assertFalse(result["source_sync_used"])
        self.assertFalse(result["site_dist_mutated"])
        self.assertFalse(result["master_index_mutated"])
        self.assertFalse(result["model_provider_used"])
        serialized = json.dumps(result, sort_keys=True)
        self.assertNotIn("truth_boundary", serialized)
        self.assertNotIn("product_boundary", serialized)

    def test_validator_passes_without_live_requirement(self):
        result = validate(require_live=False)
        self.assertEqual("pass", result["status"])
        self.assertEqual(0, result["download_count"])
        self.assertFalse(result["source_sync_used"])

    def test_no_h_series_module_import_or_connector_dependency(self):
        text = Path(source.__file__).read_text(encoding="utf-8").lower()
        self.assertNotIn("runtime.connectors", text)
        self.assertNotIn("runtime.local_foundry", text)
        self.assertNotIn("h14", text)
        self.assertNotIn("h1_", text)


if __name__ == "__main__":
    unittest.main()
