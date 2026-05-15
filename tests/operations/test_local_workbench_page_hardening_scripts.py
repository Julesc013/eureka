from __future__ import annotations

import json
import subprocess
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = ROOT / "scripts" / "validate_local_workbench_page_hardening.py"


class LocalWorkbenchPageHardeningScriptTests(unittest.TestCase):
    def test_page_hardening_validator_passes(self) -> None:
        completed = subprocess.run(
            ["python", str(VALIDATOR), "--json"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertIn(payload["status"], {"pass", "pass_with_warnings"})
        self.assertIs(payload["home_page_hardened"], True)
        self.assertIs(payload["search_page_hardened"], True)
        self.assertIs(payload["object_page_hardened"], True)
        self.assertIs(payload["source_page_hardened"], True)
        self.assertIs(payload["absence_page_hardened"], True)
        self.assertIs(payload["status_page_hardened"], True)
        self.assertIs(payload["json_api_still_passed"], True)
        self.assertIs(payload["workbench_smoke_passed"], True)
        self.assertIs(payload["mutation_controls_found"], False)
        self.assertIs(payload["external_assets_found"], False)
        self.assertIs(payload["forbidden_claims_found"], False)


if __name__ == "__main__":
    unittest.main()
