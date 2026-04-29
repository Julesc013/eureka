from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = REPO_ROOT / "scripts" / "validate_relay_prototype_plan.py"


class ValidateRelayPrototypePlanScriptTestCase(unittest.TestCase):
    def test_plain_validator_passes(self) -> None:
        result = subprocess.run(
            [sys.executable, str(VALIDATOR)],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("status: valid", result.stdout)
        self.assertIn("recommended_first_prototype: local_static_http_relay_prototype", result.stdout)
        self.assertIn("relay_runtime_files: 0", result.stdout)

    def test_json_validator_passes_and_parses(self) -> None:
        result = subprocess.run(
            [sys.executable, str(VALIDATOR), "--json"],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "valid")
        self.assertEqual(payload["recommended_first_prototype"], "local_static_http_relay_prototype")
        self.assertEqual(payload["first_protocol_candidate"], "local_static_http")
        self.assertFalse(payload["implementation_approved"])
        self.assertTrue(payload["human_approval_required"])
        self.assertTrue(payload["no_relay_runtime_implemented"])
        self.assertTrue(payload["no_network_sockets_opened"])
        self.assertEqual(payload["relay_runtime_file_count"], 0)


if __name__ == "__main__":
    unittest.main()
