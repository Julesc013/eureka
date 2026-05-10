import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


class HostedWrapperRehearsalScriptTests(unittest.TestCase):
    def run_script(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, *args], cwd=REPO_ROOT, capture_output=True, text=True, check=False)

    def test_validators_pass(self) -> None:
        for command in (
            ("scripts/validate_hosted_wrapper_rehearsal.py", "--json"),
            ("scripts/rehearse_hosted_wrapper.py", "--input", "examples/hosting/rehearsal/hosted_wrapper_rehearsal_local_fixture_v0.json", "--check", "--json"),
            ("scripts/run_public_alpha_smoke_matrix.py", "--matrix", "examples/hosting/smoke/public_alpha_smoke_matrix_v0.json", "--check", "--json"),
            ("scripts/check_public_alpha_blocked_requests.py", "--input", "examples/hosting/blocked_requests", "--check", "--json"),
            ("scripts/check_public_launch_evidence.py", "--input", "examples/hosting/launch/public_launch_evidence_packet_required_v0.json", "--check", "--json"),
            ("scripts/audit_public_alpha_readiness.py", "--check", "--json"),
            ("scripts/summarize_public_alpha_readiness.py", "--input", "examples/hosting", "--check", "--json"),
        ):
            result = self.run_script(*command)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(json.loads(result.stdout)["status"], "pass")

    def test_scripts_write_no_files_by_default(self) -> None:
        result = self.run_script("scripts/rehearse_hosted_wrapper.py", "--check")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertFalse((REPO_ROOT / "site" / "dist" / "hosted-wrapper.json").exists())

    def test_scripts_write_explicit_outputs_to_temp_paths(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eureka_hosted_wrapper_") as temp_dir:
            output = Path(temp_dir) / "rehearsal.json"
            summary = Path(temp_dir) / "rehearsal.md"
            result = self.run_script("scripts/rehearse_hosted_wrapper.py", "--output", str(output), "--summary-output", str(summary))
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue(output.is_file())
            self.assertTrue(summary.is_file())

    def test_scripts_refuse_forbidden_roots(self) -> None:
        for forbidden in (
            "site/dist/rehearsal.json",
            "data/public_index/rehearsal.json",
            ".local/eureka/rehearsal.json",
            "contracts/hosting/generated.json",
        ):
            result = self.run_script("scripts/rehearse_hosted_wrapper.py", "--output", forbidden)
            self.assertNotEqual(result.returncode, 0, forbidden)
            self.assertIn("Refusing", result.stderr + result.stdout)

    def test_validator_does_not_create_private_roots(self) -> None:
        result = self.run_script("scripts/validate_hosted_wrapper_rehearsal.py")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        for relative in (".aide.local", ".local/eureka", ".cache/eureka"):
            self.assertFalse((REPO_ROOT / relative).exists(), relative)


if __name__ == "__main__":
    unittest.main()
