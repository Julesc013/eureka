import copy
import re
import unittest
from pathlib import Path

from runtime.connectors.internet_archive import (
    load_fixture,
    map_normalized_to_source_cache_candidate,
    normalize_ia_metadata,
    preview_evidence_candidates,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_ROOT = REPO_ROOT / "examples" / "connectors" / "internet_archive" / "fixtures"
NORMALIZER = REPO_ROOT / "runtime" / "connectors" / "internet_archive" / "metadata_normalizer.py"


def fixture(name: str):
    return load_fixture(FIXTURE_ROOT / name)


class InternetArchiveMetadataFoundationTest(unittest.TestCase):
    def test_fixtures_load(self):
        for name in (
            "minimal_item_metadata.json",
            "software_item_metadata.json",
            "manual_item_metadata.json",
            "multi_file_item_metadata.json",
            "policy_blocked_item_metadata.json",
        ):
            with self.subTest(name=name):
                payload = fixture(name)
                self.assertEqual(payload["source_id"], "internet_archive")
                self.assertFalse(payload["live_call_used"])
                self.assertFalse(payload["network_used"])
                self.assertFalse(payload["external_api_used"])

    def test_minimal_fixture_normalizes(self):
        record = normalize_ia_metadata(fixture("minimal_item_metadata.json"))
        self.assertEqual(record["item_identifier"], "eureka-minimal-fixture")
        self.assertEqual(record["file_count"], 0)
        self.assertFalse(record["truth_boundary"]["accepted_public_truth"])

    def test_software_fixture_normalizes_with_file_summary(self):
        record = normalize_ia_metadata(fixture("software_item_metadata.json"))
        self.assertEqual(record["mediatype"], "software")
        self.assertEqual(record["file_count"], 2)
        self.assertIn("ZIP", record["file_summary"]["formats"])

    def test_manual_fixture_normalizes(self):
        record = normalize_ia_metadata(fixture("manual_item_metadata.json"))
        self.assertEqual(record["item_identifier"], "eureka-manual-fixture")
        self.assertEqual(record["mediatype"], "texts")
        self.assertEqual(record["creator"], ["Eureka Fixture Documentation Team"])

    def test_multi_file_fixture_normalizes_with_member_candidates(self):
        record = normalize_ia_metadata(fixture("multi_file_item_metadata.json"))
        self.assertEqual(record["file_count"], 4)
        member_names = [item["name"] for item in record["file_candidates"]]
        self.assertIn("disc-one.zip", member_names)
        self.assertTrue(all(item["downloadable_now"] is False for item in record["file_candidates"]))

    def test_policy_blocked_fixture_remains_blocked(self):
        record = normalize_ia_metadata(fixture("policy_blocked_item_metadata.json"))
        self.assertTrue(record["policy"]["blocked_current"])
        self.assertIn("source policy pending", record["policy"]["blocked_reasons"])

    def test_source_cache_candidate_preview_is_not_accepted_source_truth(self):
        record = normalize_ia_metadata(fixture("software_item_metadata.json"))
        preview = map_normalized_to_source_cache_candidate(record)
        self.assertFalse(preview["accepted_source_truth"])
        self.assertFalse(preview["source_cache_write_enabled"])
        self.assertFalse(preview["truth_boundary"]["source_cache_preview_is_accepted_source"])

    def test_evidence_candidate_preview_is_not_accepted_evidence(self):
        record = normalize_ia_metadata(fixture("software_item_metadata.json"))
        preview = preview_evidence_candidates(record)
        self.assertFalse(preview["accepted_evidence"])
        self.assertGreaterEqual(preview["candidate_count"], 6)
        self.assertTrue(all(item["accepted_evidence"] is False for item in preview["candidates"]))

    def assert_mutation_rejected(self, mutation):
        payload = copy.deepcopy(fixture("software_item_metadata.json"))
        mutation(payload)
        with self.assertRaises(ValueError):
            normalize_ia_metadata(payload)

    def test_live_call_claim_is_rejected(self):
        self.assert_mutation_rejected(lambda payload: payload.update({"live_call_used": True}))

    def test_download_file_fetch_claim_is_rejected(self):
        self.assert_mutation_rejected(lambda payload: payload.update({"file_download_approved": True}))

    def test_public_index_mutation_claim_is_rejected(self):
        self.assert_mutation_rejected(lambda payload: payload["truth_boundary"].update({"public_index_mutated": True}))

    def test_master_index_mutation_claim_is_rejected(self):
        self.assert_mutation_rejected(lambda payload: payload["truth_boundary"].update({"master_index_mutated": True}))

    def test_rights_malware_installability_claims_are_rejected(self):
        for key in ("claimed_rights_clearance", "claimed_malware_safety", "claimed_verified_installability"):
            with self.subTest(key=key):
                self.assert_mutation_rejected(lambda payload, key=key: payload["truth_boundary"].update({key: True}))

    def test_normalizer_has_no_network_api_model_provider_imports(self):
        text = NORMALIZER.read_text(encoding="utf-8")
        banned = re.compile(r"^\s*(?:from|import)\s+(requests|urllib|http|socket|webbrowser|openai|anthropic|selenium|playwright)\b", re.MULTILINE)
        self.assertIsNone(banned.search(text))


if __name__ == "__main__":
    unittest.main()
