from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]


class F0ScriptsTests(unittest.TestCase):
    def run_cmd(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, *args], cwd=REPO_ROOT, text=True, capture_output=True, check=True)

    def test_fixture_builder_check_passes(self) -> None:
        result = self.run_cmd("scripts/eureka_f0_fixture_builder.py", "--check", "--json")
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "pass")
        self.assertFalse(payload["unsafe_real_archives_built"])

    def test_manifest_script_outputs_manifest_only_packet(self) -> None:
        result = self.run_cmd("scripts/eureka_f0_manifest.py", "--fixture-manifest", "examples/f0/f0_fixture_manifest.json", "--json")
        payload = json.loads(result.stdout)
        self.assertTrue(payload["manifest_only"])
        self.assertFalse(payload["extracted_to_filesystem"])

    def test_workunit_seed_script_requires_dry_run(self) -> None:
        result = self.run_cmd("scripts/eureka_f0_workunit_seed.py", "--from-manifest", "examples/f0/safe_zip_expected_manifest.json", "--dry-run", "--json")
        payload = json.loads(result.stdout)
        self.assertTrue(payload["dry_run"])
        self.assertFalse(payload["creates_runtime_workunit"])


if __name__ == "__main__":
    unittest.main()
