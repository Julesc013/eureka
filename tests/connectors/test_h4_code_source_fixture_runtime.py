import importlib
import json
from pathlib import Path
import unittest

from archive.prototypes.legacy_runtime.connectors.h4_code_source_release.fixture_loader import load_h4_code_source_fixture
from archive.prototypes.legacy_runtime.connectors.h4_code_source_release.normalizer_common import H4_FIXTURE_KINDS, H4_SOURCE_IDS

REPO_ROOT = Path(__file__).resolve().parents[2]


class H4CodeSourceFixtureRuntimeTests(unittest.TestCase):
    def test_all_normalizers_handle_all_fixture_kinds(self):
        for source_id in H4_SOURCE_IDS:
            module = importlib.import_module(f"archive.prototypes.legacy_runtime.connectors.h4_code_source_release.{source_id}")
            for kind in H4_FIXTURE_KINDS:
                filename = "policy_blocked_record.json" if kind == "policy_blocked" else f"{kind}_record.json"
                fixture = load_h4_code_source_fixture(REPO_ROOT / "examples/connectors/h4_code_source_release/fixtures" / source_id / filename)
                normalized = module.normalize(fixture)
                self.assertEqual(normalized["source_id"], source_id)
                self.assertEqual(normalized["schema_version"], "h4_code_source_normalized_record.v0")
                self.assertFalse(normalized["truth_boundary"]["normalized_record_is_public_truth"])
                self.assertFalse(normalized["product_boundary"]["repository_clone_used"])
                self.assertIn("source_identity_candidate", normalized)
                self.assertIn("release_identity_candidate", normalized)
                self.assertIn("source_to_binary_relation_candidate_preview", normalized)

    def test_missing_optional_fields_produce_limitations(self):
        fixture = load_h4_code_source_fixture(REPO_ROOT / "examples/connectors/h4_code_source_release/fixtures/github_repository/minimal_record.json")
        normalized = importlib.import_module("archive.prototypes.legacy_runtime.connectors.h4_code_source_release.github_repository").normalize(fixture)
        limitations = normalized["source_limitations"]
        self.assertTrue(any("optional field absent or unknown" in item for item in limitations))
        self.assertEqual(normalized["release_id"], "unknown")

    def test_examples_are_valid_json(self):
        for path in (REPO_ROOT / "examples/connectors/h4_code_source_release").rglob("*.json"):
            payload = json.loads(path.read_text(encoding="utf-8"))
            self.assertIsInstance(payload, dict)


if __name__ == "__main__":
    unittest.main()
