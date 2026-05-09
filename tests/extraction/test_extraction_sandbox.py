import json
import tempfile
import unittest
from pathlib import Path

from runtime.extraction.guards import detect_truth_or_product_violations, load_extraction_policy
from runtime.extraction.sandbox import run_fixture_extraction, validate_extraction_target


REPO_ROOT = Path(__file__).resolve().parents[2]


def load_target(name: str) -> dict:
    return json.loads((REPO_ROOT / "examples" / "extraction" / "targets" / name).read_text(encoding="utf-8"))


class ExtractionSandboxTest(unittest.TestCase):
    def setUp(self):
        self.policy = load_extraction_policy()

    def test_safe_zip_fixture_passes_tier0(self):
        target = load_target("zip_basic_target_v0.json")
        result = run_fixture_extraction(target, ["0"], self.policy)
        self.assertEqual(result["extraction_status"], "completed_fixture")
        self.assertEqual(result["tiers_completed"], ["0"])
        self.assertEqual(result["container_type"], "zip")
        self.assertFalse(result["truth_boundary"]["public_index_mutated"])

    def test_private_path_input_is_rejected(self):
        target = load_target("zip_basic_target_v0.json")
        target["target_path"] = "C:/Users/private/archive.zip"
        with self.assertRaises(ValueError):
            validate_extraction_target(target, self.policy)

    def test_unsupported_container_is_blocked(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "payload.bin"
            path.write_bytes(b"not an archive")
            target = {
                **load_target("zip_basic_target_v0.json"),
                "target_id": "extraction.target.unsupported.v0",
                "target_path": str(path),
                "declared_container_type": "unknown_binary",
            }
            result = run_fixture_extraction(target, ["0"], self.policy)
            self.assertEqual(result["extraction_status"], "unsupported_container")

    def test_candidate_effect_is_not_accepted_candidate(self):
        result = run_fixture_extraction(load_target("zip_manifest_target_v0.json"), ["0", "1", "2"], self.policy)
        self.assertTrue(result["candidate_effects"])
        for effect in result["candidate_effects"]:
            self.assertFalse(effect["truth_boundary"]["candidate_effect_is_accepted_candidate"])
            self.assertFalse(effect["source_cache_candidate_preview"]["accepted_source_truth"])

    def test_public_and_master_index_claims_are_rejected(self):
        result = run_fixture_extraction(load_target("zip_manifest_target_v0.json"), ["0", "1", "2"], self.policy)
        result["truth_boundary"]["public_index_mutated"] = True
        self.assertTrue(detect_truth_or_product_violations(result))

    def test_rights_malware_installability_claims_are_rejected(self):
        result = run_fixture_extraction(load_target("zip_manifest_target_v0.json"), ["0", "1", "2"], self.policy)
        result["truth_boundary"]["rights_clearance_claimed"] = True
        result["truth_boundary"]["malware_safety_claimed"] = True
        result["truth_boundary"]["verified_installability_claimed"] = True
        violations = detect_truth_or_product_violations(result)
        self.assertGreaterEqual(len(violations), 3)


if __name__ == "__main__":
    unittest.main()
