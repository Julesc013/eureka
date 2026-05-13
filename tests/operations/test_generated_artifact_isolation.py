from __future__ import annotations

import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
POLICY = ROOT / "control/policies/site_dist_test_isolation_policy.json"
STATIC_SITE_TEST = ROOT / "tests/scripts/test_static_site_generator.py"


class GeneratedArtifactIsolationTests(unittest.TestCase):
    def test_test_isolation_policy_requires_tempdir(self) -> None:
        policy = json.loads(POLICY.read_text(encoding="utf-8"))
        self.assertTrue(policy["ordinary_tests_must_use_tempdir"])
        self.assertTrue(policy["ordinary_tests_must_not_write_site_dist"])

    def test_static_site_json_test_uses_temp_output(self) -> None:
        text = STATIC_SITE_TEST.read_text(encoding="utf-8")
        self.assertIn("TemporaryDirectory", text)
        self.assertIn("--output", text)
        self.assertNotIn('[sys.executable, str(BUILD), "--json"]', text)

    def test_policy_disables_default_site_dist_writes(self) -> None:
        policy = json.loads(POLICY.read_text(encoding="utf-8"))
        self.assertFalse(policy["site_dist_writes_enabled_by_default"])


if __name__ == "__main__":
    unittest.main()
