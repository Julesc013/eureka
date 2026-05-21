from __future__ import annotations

from pathlib import Path
import unittest

from runtime.extraction_safe_fixtures import build_container_descriptor_from_fixture, build_member_manifest, build_workunit_seed_suggestions


REPO_ROOT = Path(__file__).resolve().parents[2]


class F0WorkUnitSeedTests(unittest.TestCase):
    def test_workunit_seed_is_dry_run_suggestion_only(self) -> None:
        manifest = build_member_manifest(build_container_descriptor_from_fixture(REPO_ROOT / "examples/f0/safe_zip_basic.zip"))
        seed_set = build_workunit_seed_suggestions(manifest)
        self.assertTrue(seed_set["dry_run"])
        self.assertFalse(seed_set["creates_runtime_workunit"])
        self.assertFalse(seed_set["creates_evidence"])
        self.assertFalse(seed_set["seeds"][0]["allowed"])
        self.assertIn("operator_policy_required", seed_set["seeds"][0]["blocked_reasons"])


if __name__ == "__main__":
    unittest.main()
