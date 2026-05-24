from __future__ import annotations

import json
import subprocess
import sys
import tempfile
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]


class LocalApplyScriptTests(unittest.TestCase):
    def test_apply_cli_blocks_missing_token(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eureka-local-apply-script-") as tmp:
            instance = Path(tmp) / "instance"
            self.run_json(["scripts/eureka_init_instance.py", "--instance", str(instance), "--json"])
            completed = self.run_command(
                [
                    "scripts/eureka_local_apply.py",
                    "--instance",
                    str(instance),
                    "--from-review-promote-fixture",
                    "--apply",
                    "--confirm",
                    "APPLY_TO_LOCAL_INSTANCE",
                    "--json",
                ]
            )
            self.assertNotEqual(completed.returncode, 0)
            self.assertEqual(json.loads(completed.stdout)["status"], "blocked")

    def test_apply_and_rollback_cli_pass_on_temp_instance(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eureka-local-apply-script-") as tmp:
            instance = Path(tmp) / "instance"
            self.run_json(["scripts/eureka_init_instance.py", "--instance", str(instance), "--json"])
            apply = self.run_json(
                [
                    "scripts/eureka_local_apply.py",
                    "--instance",
                    str(instance),
                    "--from-review-promote-fixture",
                    "--apply",
                    "--operator-token",
                    "local-dev-token",
                    "--confirm",
                    "APPLY_TO_LOCAL_INSTANCE",
                    "--json",
                ]
            )
            rollback_plan = Path(apply["rollback_plan"]["backup_manifest"]["backup_root"]) / "rollback_plan.json"
            rollback = self.run_json(
                [
                    "scripts/eureka_local_apply_rollback.py",
                    "--instance",
                    str(instance),
                    "--rollback-plan",
                    str(rollback_plan),
                    "--apply",
                    "--operator-token",
                    "local-dev-token",
                    "--confirm",
                    "ROLLBACK_LOCAL_INSTANCE",
                    "--json",
                ]
            )
            self.assertEqual(apply["status"], "pass")
            self.assertEqual(rollback["status"], "pass")

    def run_command(self, args: list[str]) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, *args], cwd=REPO_ROOT, text=True, capture_output=True, check=False)

    def run_json(self, args: list[str]) -> dict[str, object]:
        completed = self.run_command(args)
        if completed.returncode != 0:
            self.fail(completed.stderr or completed.stdout)
        return json.loads(completed.stdout)


if __name__ == "__main__":
    unittest.main()
