
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


class MvpAlphaAuditScriptTests(unittest.TestCase):
    def run_script(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, *args], cwd=REPO_ROOT, capture_output=True, text=True, check=False)

    def test_validators_pass(self) -> None:
        for command in (
            ("scripts/validate_mvp_alpha_audit.py", "--json"),
            ("scripts/audit_mvp_alpha_readiness.py", "--check", "--json"),
            ("scripts/summarize_mvp_alpha_readiness.py", "--input", "examples/audits/mvp_alpha", "--check", "--json"),
            ("scripts/build_mvp_alpha_operator_review_packet.py", "--audit", "examples/audits/mvp_alpha/mvp_alpha_readiness_audit_v0.json", "--gate", "examples/audits/mvp_alpha/mvp_alpha_gate_decision_ready_for_operator_review_v0.json", "--check", "--json"),
        ):
            result = self.run_script(*command)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn(json.loads(result.stdout)["status"], {"pass", "pass_with_warnings"})

    def test_audit_script_writes_no_files_by_default(self) -> None:
        result = self.run_script("scripts/audit_mvp_alpha_readiness.py", "--check")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse((REPO_ROOT / "site" / "dist" / "mvp-alpha-audit.json").exists())

    def test_scripts_write_explicit_outputs_to_temp_paths(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eureka_mvp_alpha_") as temp_dir:
            output = Path(temp_dir) / "audit.json"
            matrix = Path(temp_dir) / "matrix.json"
            summary = Path(temp_dir) / "summary.md"
            result = self.run_script("scripts/audit_mvp_alpha_readiness.py", "--json-output", str(output), "--matrix-output", str(matrix), "--summary-output", str(summary))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue(output.is_file())
            self.assertTrue(matrix.is_file())
            self.assertTrue(summary.is_file())

    def test_scripts_refuse_forbidden_roots(self) -> None:
        for forbidden in (
            "site/dist/mvp-alpha.json",
            "site/dist/data/public_index/mvp-alpha.json",
            ".local/eureka/mvp-alpha.json",
            "provider/config.json",
            "secrets/launch.json",
        ):
            result = self.run_script("scripts/audit_mvp_alpha_readiness.py", "--json-output", forbidden)
            self.assertNotEqual(result.returncode, 0, forbidden)
            self.assertIn("Refusing", result.stderr + result.stdout)

    def test_operator_packet_script_does_not_infer_signoff(self) -> None:
        result = self.run_script("scripts/build_mvp_alpha_operator_review_packet.py", "--check", "--json")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        payload = json.loads(result.stdout)
        packet = payload["packet"]
        self.assertEqual(packet["review_status"], "operator_review_required")
        self.assertFalse(packet["truth_boundary"]["operator_signoff_inferred"])

    def test_validator_does_not_create_local_private_roots(self) -> None:
        result = self.run_script("scripts/validate_mvp_alpha_audit.py")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        for relative in (".aide.local", ".local/eureka", ".cache/eureka"):
            self.assertFalse((REPO_ROOT / relative).exists(), relative)


if __name__ == "__main__":
    unittest.main()
