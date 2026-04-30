from __future__ import annotations

import json
import subprocess
import sys
import unittest

from scripts.validate_public_search_static_handoff import (
    validate_public_search_static_handoff,
)


class ValidatePublicSearchStaticHandoffScriptTest(unittest.TestCase):
    def test_validator_passes_as_imported_function(self) -> None:
        report = validate_public_search_static_handoff()

        self.assertEqual(report["status"], "valid", report["errors"])
        self.assertEqual(report["static_artifact"], "site/dist")
        self.assertEqual(report["hosted_backend_status"], "unavailable")
        self.assertEqual(report["default_backend_mode"], "not_configured")
        self.assertEqual(report["q_maxlength"], 160)

    def test_validator_json_cli_parses(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/validate_public_search_static_handoff.py", "--json"],
            check=False,
            capture_output=True,
            text=True,
            timeout=90,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        report = json.loads(completed.stdout)
        self.assertEqual(report["status"], "valid", report["errors"])
        self.assertIn("search.html", report["outputs"])
        self.assertIn("data/search_handoff.json", report["outputs"])


if __name__ == "__main__":
    unittest.main()
