
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]


class MvpAlphaOperatorReviewScriptTests(unittest.TestCase):
    def run_script(self, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, *args], cwd=REPO_ROOT, capture_output=True, text=True, check=False)

    def test_validators_pass(self) -> None:
        commands = (
            ("scripts/validate_mvp_alpha_operator_review.py", "--json"),
            ("scripts/build_mvp_alpha_decision_packet.py", "--audit", "control/audits/mvp-alpha-audit-01-local-mvp-readiness-v0/mvp_alpha_audit_01_report.json", "--check", "--json"),
            ("scripts/check_mvp_alpha_operator_signoff.py", "--input", "examples/audits/mvp_alpha_operator/operator_signoff_packet_unsigned_v0.json", "--check", "--json"),
            ("scripts/check_mvp_alpha_public_claims.py", "--input", "examples/audits/mvp_alpha_operator", "--check", "--json"),
            ("scripts/route_mvp_alpha_next_task.py", "--decision", "examples/audits/mvp_alpha_operator/operator_decision_approve_planning_only_v0.json", "--check", "--json"),
            ("scripts/summarize_mvp_alpha_operator_review.py", "--input", "examples/audits/mvp_alpha_operator", "--check", "--json"),
        )
        for command in commands:
            result = self.run_script(*command)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertEqual(json.loads(result.stdout)["status"], "pass")

    def test_scripts_write_no_files_by_default(self) -> None:
        before = {path.as_posix() for path in (REPO_ROOT / "examples/audits/mvp_alpha_operator").rglob("*")}
        result = self.run_script("scripts/build_mvp_alpha_decision_packet.py", "--check")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        after = {path.as_posix() for path in (REPO_ROOT / "examples/audits/mvp_alpha_operator").rglob("*")}
        self.assertEqual(before, after)

    def test_scripts_write_explicit_outputs_to_temp_paths(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eureka_operator_review_") as temp_dir:
            output = Path(temp_dir) / "packet.json"
            summary = Path(temp_dir) / "summary.md"
            result = self.run_script("scripts/build_mvp_alpha_decision_packet.py", "--output", str(output), "--summary-output", str(summary), "--check")
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertTrue(output.is_file())
            self.assertTrue(summary.is_file())

    def test_scripts_refuse_forbidden_roots(self) -> None:
        for forbidden in (
            "site/dist/operator.json",
            "site/dist/data/public_index/operator.json",
            ".local/eureka/operator.json",
            "provider/config.json",
            "secrets/signoff.json",
        ):
            result = self.run_script("scripts/build_mvp_alpha_decision_packet.py", "--output", forbidden)
            self.assertNotEqual(result.returncode, 0, forbidden)
            self.assertIn("Refusing", result.stderr + result.stdout)

    def test_decision_router_maps_planning_and_remediation(self) -> None:
        planning = self.run_script("scripts/route_mvp_alpha_next_task.py", "--decision", "examples/audits/mvp_alpha_operator/operator_decision_approve_planning_only_v0.json", "--json")
        self.assertEqual(planning.returncode, 0, planning.stdout + planning.stderr)
        self.assertEqual(json.loads(planning.stdout)["next_task_id"], "PUBLIC-ALPHA-DEPLOYMENT-PLAN-01")
        remediation = self.run_script("scripts/route_mvp_alpha_next_task.py", "--decision", "examples/audits/mvp_alpha_operator/operator_decision_request_remediation_v0.json", "--json")
        self.assertEqual(remediation.returncode, 0, remediation.stdout + remediation.stderr)
        self.assertEqual(json.loads(remediation.stdout)["next_task_id"], "MVP-ALPHA-REMEDIATION-01")

    def test_validator_does_not_create_local_private_roots(self) -> None:
        result = self.run_script("scripts/validate_mvp_alpha_operator_review.py")
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        for relative in (".aide.local", ".local/eureka", ".cache/eureka"):
            self.assertFalse((REPO_ROOT / relative).exists(), relative)


if __name__ == "__main__":
    unittest.main()
