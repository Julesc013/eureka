import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PY = sys.executable


class LocalMvpIterationScriptsTest(unittest.TestCase):
    def run_cmd(self, *args, check=True):
        result = subprocess.run([PY, *args], cwd=ROOT, text=True, capture_output=True)
        if check and result.returncode != 0:
            self.fail(f"Command failed: {' '.join(args)}\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}")
        return result

    def test_planner_writes_no_files_by_default(self):
        before = {p.relative_to(ROOT).as_posix() for p in (ROOT / "examples/audits/local_mvp").glob("*.json")}
        self.run_cmd("scripts/plan_local_mvp_iteration.py", "--check")
        after = {p.relative_to(ROOT).as_posix() for p in (ROOT / "examples/audits/local_mvp").glob("*.json")}
        self.assertEqual(before, after)

    def test_scripts_pass_check_mode(self):
        self.run_cmd("scripts/validate_local_mvp_iteration.py")
        self.run_cmd("scripts/plan_local_mvp_iteration.py", "--check")
        self.run_cmd("scripts/select_local_mvp_next_task.py", "--plan", "examples/audits/local_mvp/local_mvp_iteration_plan_v0.json", "--check")
        self.run_cmd("scripts/check_local_mvp_deployment_deferral.py", "--input", "examples/audits/local_mvp/local_mvp_deployment_deferral_v0.json", "--check")
        self.run_cmd("scripts/summarize_local_mvp_iteration.py", "--input", "examples/audits/local_mvp", "--check")

    def test_scripts_write_explicit_outputs_to_temp_paths(self):
        with tempfile.TemporaryDirectory() as tmp:
            base = Path(tmp)
            self.run_cmd("scripts/plan_local_mvp_iteration.py", "--output", str(base / "plan.json"), "--matrix-output", str(base / "matrix.json"), "--summary-output", str(base / "summary.md"), "--check")
            self.assertTrue((base / "plan.json").is_file())
            self.assertTrue((base / "matrix.json").is_file())
            self.assertTrue((base / "summary.md").is_file())

    def test_output_refuses_site_dist(self):
        result = self.run_cmd("scripts/plan_local_mvp_iteration.py", "--output", "site/dist/local_mvp.json", check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Refusing", result.stderr + result.stdout)

    def test_output_refuses_public_index(self):
        result = self.run_cmd("scripts/summarize_local_mvp_iteration.py", "--input", "examples/audits/local_mvp", "--output", "data/public_index/local_mvp.json", check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Refusing", result.stderr + result.stdout)

    def test_output_refuses_secret_roots(self):
        result = self.run_cmd("scripts/select_local_mvp_next_task.py", "--output", "secrets/local_mvp.json", check=False)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Refusing", result.stderr + result.stdout)


if __name__ == "__main__":
    unittest.main()
