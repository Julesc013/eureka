import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class ValidatePostP49PlatformAuditScriptTests(unittest.TestCase):
    def test_validator_passes(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/validate_post_p49_platform_audit.py"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        self.assertIn("validation passed", completed.stdout)

    def test_validator_json_parses(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/validate_post_p49_platform_audit.py", "--json"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "passed")
        self.assertEqual(payload["check_id"], "post_p49_platform_audit_v0")
        self.assertEqual(payload["errors"], [])


if __name__ == "__main__":
    unittest.main()
