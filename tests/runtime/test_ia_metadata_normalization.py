import json
import unittest
from pathlib import Path

from runtime.source.observation.internet_archive_normalization import normalize_ia_metadata_fixture


ROOT = Path(__file__).resolve().parents[2]
FIXTURE_DIR = ROOT / "examples" / "internet_archive_metadata"


def load_fixture(name: str) -> dict:
    return json.loads((FIXTURE_DIR / name).read_text(encoding="utf-8"))


class IAMetadataNormalizationTests(unittest.TestCase):
    def test_metadata_search_fixture_normalizes(self):
        record = normalize_ia_metadata_fixture(load_fixture("metadata_search_small.fixture.json")).to_dict()
        self.assertEqual("metadata_search_result", record["observation_kind"])
        self.assertEqual("eureka-fixture-dtheater-sample", record["item_identifier"])
        self.assertEqual("Eureka Fixture D-Theater Demo Tape Metadata", record["title_candidate"])
        self.assertTrue(record["review_required"])
        self.assertFalse(record["accepted_truth"])

    def test_item_metadata_fixture_normalizes(self):
        record = normalize_ia_metadata_fixture(load_fixture("item_metadata.fixture.json")).to_dict()
        self.assertEqual("item_metadata", record["observation_kind"])
        self.assertEqual("software", record["mediatype_candidate"])
        self.assertEqual(1, len(record["file_metadata_candidates"]))
        self.assertEqual(1, len(record["checksum_candidates"]))

    def test_file_list_fixture_normalizes(self):
        record = normalize_ia_metadata_fixture(load_fixture("item_file_list.fixture.json")).to_dict()
        self.assertEqual("item_file_list", record["observation_kind"])
        self.assertEqual(2, len(record["file_metadata_candidates"]))
        self.assertFalse(record["download_performed"])

    def test_missing_item_becomes_source_miss_state(self):
        record = normalize_ia_metadata_fixture(load_fixture("missing_item.fixture.json")).to_dict()
        self.assertEqual("missing_item", record["observation_kind"])
        self.assertIn("source_miss", record["risk_flags"])
        self.assertIn("source reported missing item", record["limitations"])

    def test_malformed_partial_becomes_partial_state(self):
        record = normalize_ia_metadata_fixture(load_fixture("malformed_partial.fixture.json")).to_dict()
        self.assertEqual("malformed_partial", record["observation_kind"])
        self.assertIn("malformed_partial", record["risk_flags"])
        self.assertIn("required item identifier missing", record["limitations"])

    def test_retry_after_becomes_backoff_state(self):
        record = normalize_ia_metadata_fixture(load_fixture("retry_after_429.fixture.json")).to_dict()
        self.assertEqual("retry_after", record["observation_kind"])
        self.assertIn("retry_after_required", record["risk_flags"])
        self.assertIn("Retry-After required: 60 seconds", record["limitations"])

    def test_large_file_list_respects_cap(self):
        record = normalize_ia_metadata_fixture(load_fixture("large_file_list.fixture.json")).to_dict()
        self.assertEqual("large_file_list", record["observation_kind"])
        self.assertEqual(5, len(record["file_metadata_candidates"]))
        self.assertIn("file metadata candidates capped at 5 of 8", record["limitations"])

    def test_no_download_proof_normalizes_metadata_only(self):
        record = normalize_ia_metadata_fixture(load_fixture("no_download_proof.fixture.json")).to_dict()
        self.assertEqual("no_download_proof", record["observation_kind"])
        self.assertEqual(1, len(record["file_metadata_candidates"]))
        self.assertFalse(record["download_performed"])


if __name__ == "__main__":
    unittest.main()
