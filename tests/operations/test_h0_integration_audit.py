import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]


class H0IntegrationAuditTests(unittest.TestCase):
    def test_h0_integration_audit_passes_current_repo(self):
        result = subprocess.run([sys.executable, "scripts/audit_h0_integration.py", "--check", "--json"], cwd=REPO_ROOT, check=False, capture_output=True, text=True, timeout=120)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        self.assertIn(payload["h0_exit_gate"], {"PASS", "PASS_WITH_WARNINGS"})
        self.assertIn(payload["h1_readiness"], {"READY_FOR_H1_POLICY_PACKS", "READY_WITH_WARNINGS"})

    def test_h0_integration_audit_writes_explicit_temp_outputs(self):
        with tempfile.TemporaryDirectory() as tmp:
            json_out = Path(tmp) / "h0.json"
            md_out = Path(tmp) / "h0.md"
            result = subprocess.run([sys.executable, "scripts/audit_h0_integration.py", "--json-output", str(json_out), "--summary-output", str(md_out)], cwd=REPO_ROOT, check=False, capture_output=True, text=True, timeout=120)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue(json_out.is_file())
            self.assertTrue(md_out.is_file())

    def test_h0_integration_audit_refuses_forbidden_output_root(self):
        result = subprocess.run([sys.executable, "scripts/audit_h0_integration.py", "--json-output", "site/dist/h0.json"], cwd=REPO_ROOT, check=False, capture_output=True, text=True, timeout=120)
        self.assertNotEqual(result.returncode, 0)

    def test_h0_integration_audit_does_not_import_network_or_model_provider(self):
        text = (REPO_ROOT / "scripts/audit_h0_integration.py").read_text(encoding="utf-8")
        for item in ("requests", "httpx", "aiohttp", "socket", "openai", "anthropic", "selenium", "playwright"):
            self.assertNotIn(f"import {item}", text)
            self.assertNotIn(f"from {item}", text)


if __name__ == "__main__":
    unittest.main()
