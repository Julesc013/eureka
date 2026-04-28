from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "check_rust_source_registry_parity.py"


class RustSourceRegistryParityScriptTestCase(unittest.TestCase):
    def test_script_json_output_parses(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--json"],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertIn(payload["status"], {"passed", "skipped_cargo_unavailable"})
        self.assertEqual(payload["check_id"], "rust_source_registry_parity_catch_up_v0")
        self.assertTrue(payload["python_remains_oracle"])
        self.assertFalse(payload["runtime_wiring_allowed"])
        self.assertEqual(payload["structure"]["status"], "passed")
        self.assertEqual(payload["structure"]["source_count"], 9)
        self.assertGreaterEqual(payload["structure"]["case_count"], 10)

    def test_require_cargo_reports_cargo_availability_honestly(self) -> None:
        result = subprocess.run(
            [sys.executable, str(SCRIPT), "--json", "--require-cargo"],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )

        stream = result.stdout if result.stdout.strip() else result.stderr
        payload = json.loads(stream)
        if payload["cargo"]["cargo_available"]:
            self.assertEqual(result.returncode, 0, payload["cargo"].get("stderr", ""))
            self.assertEqual(payload["cargo"]["status"], "passed")
        else:
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(payload["cargo"]["status"], "failed")
            self.assertIn("Cargo is not available", payload["cargo"]["reason"])


if __name__ == "__main__":
    unittest.main()
