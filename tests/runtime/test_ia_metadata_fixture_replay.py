import json
import unittest
from pathlib import Path

from runtime.source_observation.internet_archive_fixture_replay import (
    assert_no_forbidden_side_effects,
    assert_no_network_imports,
    build_fixture_replay_report,
    replay_fixture,
    replay_fixture_directory,
    replay_fixture_directory_report,
)


ROOT = Path(__file__).resolve().parents[2]
FIXTURE_DIR = ROOT / "examples" / "internet_archive_metadata"


class IAMetadataFixtureReplayTests(unittest.TestCase):
    def test_all_required_fixtures_replay(self):
        results = replay_fixture_directory(FIXTURE_DIR)
        report = build_fixture_replay_report(results)
        self.assertEqual(8, report["fixture_count"])
        self.assertTrue(report["all_fixtures_replay"])
        self.assertEqual(
            [
                "item_file_list",
                "item_metadata",
                "large_file_list",
                "malformed_partial",
                "metadata_search_small",
                "missing_item",
                "no_download_proof",
                "retry_after_429",
            ],
            report["fixture_ids"],
        )

    def test_replay_report_has_no_forbidden_side_effects(self):
        report = replay_fixture_directory_report(FIXTURE_DIR)
        assert_no_forbidden_side_effects(report)
        for key, value in report["boundaries"].items():
            self.assertFalse(value, key)

    def test_expected_records_match_declared_expectations(self):
        report = replay_fixture_directory_report(FIXTURE_DIR)
        expected = json.loads((FIXTURE_DIR / "expected_normalized_records.json").read_text(encoding="utf-8"))
        records = {record["fixture_id"]: record for record in report["normalized_records"]}
        for row in expected["records"]:
            record = records[row["fixture_id"]]
            self.assertEqual(row["observation_id"], record["observation_id"])
            self.assertEqual(row["observation_kind"], record["observation_kind"])
            self.assertEqual(row["file_metadata_count"], len(record["file_metadata_candidates"]))
            self.assertTrue(record["review_required"])
            self.assertFalse(record["accepted_truth"])
            self.assertFalse(record["download_performed"])

    def test_single_fixture_replay(self):
        result = replay_fixture(FIXTURE_DIR / "metadata_search_small.fixture.json")
        self.assertEqual("metadata_search_small", result["fixture_id"])
        self.assertEqual("metadata_search_result", result["normalized_record"]["observation_kind"])
        self.assertTrue(result["boundary_report"]["passed"])

    def test_forbidden_network_imports_absent(self):
        assert_no_network_imports()


if __name__ == "__main__":
    unittest.main()
