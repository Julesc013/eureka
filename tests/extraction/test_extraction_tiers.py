import json
import unittest
from pathlib import Path

from runtime.extraction.guards import load_extraction_policy
from runtime.extraction.sandbox import run_fixture_extraction
from runtime.extraction.tier0_outer_metadata import extract_tier0_outer_metadata
from runtime.extraction.tier1_member_listing import extract_tier1_member_listing
from runtime.extraction.tier2_manifest_extract import extract_tier2_manifest_candidates


REPO_ROOT = Path(__file__).resolve().parents[2]


def fixture(rel: str) -> Path:
    return REPO_ROOT / rel


def target(name: str) -> dict:
    return json.loads((REPO_ROOT / "examples" / "extraction" / "targets" / name).read_text(encoding="utf-8"))


class ExtractionTiersTest(unittest.TestCase):
    def setUp(self):
        self.policy = load_extraction_policy()

    def test_tier0_outer_metadata_reads_zip_metadata(self):
        metadata = extract_tier0_outer_metadata(fixture("examples/extraction/fixtures/zip_basic/zip_basic.zip"), self.policy)
        self.assertEqual(metadata["container_type"], "zip")
        self.assertGreater(metadata["input_size_bytes"], 0)
        self.assertFalse(metadata["payload_executed"])

    def test_tier1_member_listing_reads_zip_members(self):
        members = extract_tier1_member_listing(fixture("examples/extraction/fixtures/zip_basic/zip_basic.zip"), self.policy)
        self.assertEqual(len(members), 2)
        self.assertTrue(all(member["extracted_payload_stored"] is False for member in members))

    def test_tier2_manifest_candidates_reads_manifest_preview(self):
        candidates = extract_tier2_manifest_candidates(fixture("examples/extraction/fixtures/zip_manifest/zip_manifest.zip"), self.policy)
        self.assertEqual(len(candidates), 1)
        self.assertEqual(candidates[0]["manifest_kind"], "package_json")
        self.assertFalse(candidates[0]["truth_boundary"]["manifest_candidate_is_accepted_evidence"])

    def test_safe_tar_fixture_passes_tier1(self):
        result = run_fixture_extraction(target("tar_basic_target_v0.json"), ["0", "1"], self.policy)
        self.assertEqual(result["container_type"], "tar")
        self.assertEqual(result["extraction_status"], "completed_fixture")
        self.assertEqual(len(result["member_listing"]), 2)

    def test_manifest_candidate_is_not_accepted_evidence(self):
        result = run_fixture_extraction(target("zip_manifest_target_v0.json"), ["0", "1", "2"], self.policy)
        manifest = result["manifest_candidates"][0]
        self.assertFalse(manifest["truth_boundary"]["manifest_candidate_is_accepted_evidence"])
        self.assertFalse(manifest["evidence_candidate_preview"]["accepted_evidence"])


if __name__ == "__main__":
    unittest.main()
