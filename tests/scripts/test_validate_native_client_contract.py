from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "validate_native_client_contract.py"


class NativeClientContractValidatorTestCase(unittest.TestCase):
    def test_validator_json_output_parses(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--json"],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "valid")
        self.assertEqual(payload["created_by"], "native_client_contract_validator_v0")
        self.assertEqual(payload["first_candidate_lane"], "windows_7_x64_winforms_net48")
        self.assertEqual(payload["lane_count"], 9)
        self.assertFalse(payload["native_gui_implemented"])
        self.assertTrue(payload["cli_surface_implemented"])
        self.assertEqual(payload["project_file_count"], 0)


if __name__ == "__main__":
    unittest.main()
