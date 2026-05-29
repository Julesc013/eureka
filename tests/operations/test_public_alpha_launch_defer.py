from __future__ import annotations

import json
from pathlib import Path
import unittest

from scripts.validate_public_alpha_launch_defer import validate_public_alpha_launch_defer


REPO_ROOT = Path(__file__).resolve().parents[2]


class PublicAlphaLaunchDeferTests(unittest.TestCase):
    def test_defer_result_records_launch_deferral_without_deployment(self) -> None:
        result = json.loads((REPO_ROOT / "control/inventory/public_alpha_launch_defer_result.json").read_text(encoding="utf-8"))

        self.assertEqual(result["status"], "deferred")
        self.assertEqual(result["deferred_task"], "PUBLIC-ALPHA-LAUNCH-00")
        self.assertEqual(result["recommended_next_task"], "ACTIVE-DISCOVERY-AND-CANDIDATE-INTAKE-00")
        self.assertTrue(result["required_next_capability"]["must_support_archive_org_wide_metadata_search"])
        self.assertFalse(result["deployment_performed"])
        self.assertFalse(result["public_launch_performed"])
        self.assertFalse(result["production_readiness_claimed"])
        self.assertFalse(result["public_launch_readiness_claimed"])

    def test_defer_validator_passes(self) -> None:
        report = validate_public_alpha_launch_defer()

        self.assertEqual(report["status"], "pass", report["errors"])
        self.assertTrue(report["archive_org_wide_metadata_search_required"])
        self.assertFalse(report["deployment_performed"])
        self.assertFalse(report["public_launch_performed"])

    def test_defer_validator_script_passes_json_mode(self) -> None:
        import subprocess
        import sys

        completed = subprocess.run(
            [sys.executable, "scripts/validate_public_alpha_launch_defer.py", "--json"],
            cwd=REPO_ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["recommended_next_task"], "ACTIVE-DISCOVERY-AND-CANDIDATE-INTAKE-00")


if __name__ == "__main__":
    unittest.main()
