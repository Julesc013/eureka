from __future__ import annotations

from pathlib import Path
import unittest

from runtime.extraction_safe_fixtures import load_f0_fixture_manifest, validate_f0_fixture_manifest


REPO_ROOT = Path(__file__).resolve().parents[2]


class F0FoundationTests(unittest.TestCase):
    def test_fixture_manifest_loads_and_is_example_only(self) -> None:
        manifest = load_f0_fixture_manifest(REPO_ROOT / "examples/f0/f0_fixture_manifest.json")
        report = validate_f0_fixture_manifest(manifest)
        self.assertEqual(report["status"], "valid", report["errors"])
        self.assertEqual(manifest["fixture_status"], "example_only")
        self.assertFalse(manifest["non_claims"]["fake_evidence_created"])

    def test_required_policies_block_unsafe_actions(self) -> None:
        policy = load_f0_fixture_manifest(REPO_ROOT / "control/policies/f0_extraction_policy.json")
        self.assertTrue(policy["fixture_only_foundation"])
        self.assertTrue(policy["manifest_only_enumeration_enabled"])
        self.assertFalse(policy["downloads_enabled"])
        self.assertFalse(policy["extraction_to_filesystem_enabled"])
        self.assertFalse(policy["execution_enabled"])


if __name__ == "__main__":
    unittest.main()
