from __future__ import annotations

import json
import subprocess
import sys
import unittest

from scripts.validate_local_public_search_runtime import validate_local_public_search_runtime


class ValidateLocalPublicSearchRuntimeScriptTest(unittest.TestCase):
    def test_validator_passes_as_imported_function(self) -> None:
        report = validate_local_public_search_runtime()

        self.assertEqual(report["status"], "valid", report["errors"])
        self.assertEqual(report["runtime_scope"], "local_prototype_backend")
        self.assertEqual(report["mode"], "local_index_only")

    def test_validator_json_cli_parses(self) -> None:
        completed = subprocess.run(
            [sys.executable, "scripts/validate_local_public_search_runtime.py", "--json"],
            check=False,
            capture_output=True,
            text=True,
            timeout=90,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr)
        report = json.loads(completed.stdout)
        self.assertEqual(report["status"], "valid", report["errors"])
        self.assertFalse(report["hosted_public_deployment"])
        self.assertFalse(report["static_search_handoff"])


if __name__ == "__main__":
    unittest.main()
