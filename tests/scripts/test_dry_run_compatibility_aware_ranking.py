import json
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class DryRunCompatibilityAwareRankingTests(unittest.TestCase):
    def test_dry_run_outputs_safe_json(self):
        completed = subprocess.run([sys.executable, "scripts/dry_run_compatibility_aware_ranking.py", "--target-os", "Windows 7 x64", "--left-title", "Strong compatibility evidence result", "--right-title", "Unknown compatibility result", "--json"], cwd=ROOT, text=True, capture_output=True, check=True)
        page = json.loads(completed.stdout)
        self.assertEqual(page["status"], "dry_run_validated")
        self.assertFalse(page["runtime_compatibility_ranking_implemented"])
        self.assertFalse(page["compatibility_ranking_applied_to_live_search"])
        self.assertFalse(page["public_search_order_changed"])
        self.assertFalse(page["live_source_called"])
        self.assertFalse(page["external_calls_performed"])
        self.assertFalse(page["package_manager_invoked"])
        self.assertFalse(page["emulator_vm_launch_enabled"])


if __name__ == "__main__":
    unittest.main()
