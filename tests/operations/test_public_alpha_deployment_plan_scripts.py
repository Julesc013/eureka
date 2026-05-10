
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


class PublicAlphaDeploymentPlanScriptTests(unittest.TestCase):
    def run_script(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, *args], cwd=REPO_ROOT, capture_output=True, text=True, check=False)

    def test_scripts_pass(self) -> None:
        commands = (
            ("scripts/validate_public_alpha_deployment_plan.py", "--json"),
            ("scripts/build_public_alpha_deployment_plan.py", "--check", "--json"),
            ("scripts/check_public_alpha_deployment_plan.py", "--input", "examples/hosting/deployment/public_alpha_deployment_plan_v0.json", "--check", "--json"),
            ("scripts/check_public_alpha_config_manifest.py", "--input", "examples/hosting/deployment/public_alpha_config_manifest_v0.json", "--check", "--json"),
            ("scripts/check_public_alpha_dns_readiness.py", "--input", "examples/hosting/deployment/public_alpha_dns_readiness_unknown_v0.json", "--check", "--json"),
            ("scripts/summarize_public_alpha_deployment_plan.py", "--input", "examples/hosting/deployment", "--check", "--json"),
        )
        for command in commands:
            result = self.run_script(*command)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(json.loads(result.stdout)["status"], "pass")

    def test_build_script_writes_no_files_by_default(self) -> None:
        before = {path.as_posix() for path in (REPO_ROOT / "examples/hosting/deployment").rglob("*")}
        result = self.run_script("scripts/build_public_alpha_deployment_plan.py", "--check")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        after = {path.as_posix() for path in (REPO_ROOT / "examples/hosting/deployment").rglob("*")}
        self.assertEqual(before, after)

    def test_scripts_write_explicit_outputs_to_temp_paths(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eureka_public_alpha_plan_") as temp_dir:
            output = Path(temp_dir) / "plan.json"
            summary = Path(temp_dir) / "summary.md"
            result = self.run_script("scripts/build_public_alpha_deployment_plan.py", "--output", str(output), "--summary-output", str(summary), "--check")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue(output.is_file())
            self.assertTrue(summary.is_file())

    def test_scripts_refuse_forbidden_roots(self) -> None:
        for forbidden in (
            "site/dist/public-alpha.json",
            "data/public_index/public-alpha.json",
            ".local/eureka/public-alpha.json",
            "provider/config.json",
            "secrets/launch.json",
            "deploy/generated.json",
        ):
            result = self.run_script("scripts/build_public_alpha_deployment_plan.py", "--output", forbidden)
            self.assertNotEqual(result.returncode, 0, forbidden)
            self.assertIn("Refusing", result.stderr + result.stdout)

    def test_validator_does_not_create_local_private_roots(self) -> None:
        result = self.run_script("scripts/validate_public_alpha_deployment_plan.py")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        for relative in (".aide.local", ".local/eureka", ".cache/eureka"):
            self.assertFalse((REPO_ROOT / relative).exists(), relative)


if __name__ == "__main__":
    unittest.main()
