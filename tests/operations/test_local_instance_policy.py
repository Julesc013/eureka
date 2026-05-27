from __future__ import annotations

import json
import subprocess
from pathlib import Path
import unittest

from scripts.local_queue_progress import current_recommended_task, is_later_control_or_handoff


ROOT = Path(__file__).resolve().parents[2]


def load_json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


class LocalInstancePolicyTests(unittest.TestCase):
    def test_local_instance_policies_exist(self) -> None:
        for rel in (
            "control/policies/local_instance_policy.json",
            "control/policies/local_instance_path_policy.json",
            "control/policies/local_instance_state_policy.json",
        ):
            self.assertTrue((ROOT / rel).is_file(), rel)

    def test_local_instance_policy_defaults(self) -> None:
        payload = load_json("control/policies/local_instance_policy.json")
        self.assertIs(payload["explicit_instance_path_required"], True)
        self.assertIs(payload["hidden_state_roots_forbidden"], True)
        self.assertIs(payload["committed_instance_state_forbidden"], True)
        self.assertEqual("eureka-instance", payload["default_instance_name"])
        self.assertIs(payload["instance_init_idempotent"], True)
        self.assertIs(payload["instance_validation_required"], True)
        self.assertIs(payload["network_access_enabled"], False)
        self.assertIs(payload["server_enabled"], False)
        self.assertIs(payload["lan_enabled"], False)
        self.assertIs(payload["deployment_enabled"], False)

    def test_path_policy_forbids_hidden_and_implicit_roots(self) -> None:
        payload = load_json("control/policies/local_instance_path_policy.json")
        forbidden = set(payload["forbidden_instance_roots"])
        self.assertIn(".cache", forbidden)
        self.assertIn(".local", forbidden)
        self.assertIn(".aide.local", forbidden)
        self.assertIn("home directory implicit path", forbidden)
        self.assertIn("repo root as instance path", forbidden)
        self.assertIn("site/dist", forbidden)

    def test_state_policy_blocks_committed_state(self) -> None:
        payload = load_json("control/policies/local_instance_state_policy.json")
        self.assertIs(payload["committed_local_state_forbidden"], True)
        self.assertIs(payload["sqlite_db_files_forbidden_in_git"], True)
        self.assertIs(payload["logs_forbidden_in_git"], True)
        self.assertIs(payload["run_locks_forbidden_in_git"], True)
        self.assertIs(payload["tmp_files_forbidden_in_git"], True)
        self.assertIs(payload["exports_imports_forbidden_by_default"], True)
        self.assertIs(payload["generated_instance_state_must_be_explicit"], True)

    def test_layout_inventory_defines_required_tree(self) -> None:
        payload = load_json("control/inventory/local_instance_layout.json")
        self.assertEqual(
            ["config", "db", "logs", "run", "tmp", "exports", "imports"],
            payload["required_directories"],
        )
        self.assertIn("config/instance.json", payload["required_files"])
        self.assertIn("run/status.json", payload["required_files"])
        self.assertIn("db/source_cache.sqlite", payload["planned_database_files"])
        self.assertIn("db/public_index.sqlite", payload["planned_database_files"])

    def test_next_task_keeps_f0_deferred(self) -> None:
        payload = load_json("control/inventory/local_01_next_task_decision.json")
        self.assertEqual("LOCAL-14", payload["f0_can_resume_after"])
        self.assertEqual("deferred", payload["f0_current_status"])
        self.assertIn("LOCAL-02", payload["recommended_next_task"])
        self.assertIs(payload["server_can_start"], False)
        self.assertIs(payload["lan_can_start"], False)

    def test_queue_points_to_local_02(self) -> None:
        text = (ROOT / ".aide/queue/index.yaml").read_text(encoding="utf-8")
        current = current_recommended_task(ROOT)
        if is_later_control_or_handoff(current):
            self.assertTrue(current, text)
        else:
            self.assertIn("current_recommended_task: LOCAL-02", text)
            self.assertIn("id: LOCAL-02", text)

    def test_default_instance_root_is_ignored(self) -> None:
        completed = subprocess.run(
            ["git", "check-ignore", "eureka-instance/config/instance.json"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(0, completed.returncode, completed.stderr)

    def test_leakage_baseline_does_not_increase(self) -> None:
        payload = load_json("control/inventory/local_01_leakage_baseline.json")
        self.assertEqual(
            payload["new_unallowlisted_production_findings_before"],
            payload["new_unallowlisted_production_findings_after"],
        )
        self.assertIs(payload["local_01_increased_leakage"], False)

    def test_no_product_claims_in_report(self) -> None:
        payload = load_json("control/audits/local-01-local-instance-bootstrap-v0/local_01_report.json")
        self.assertIs(payload["server_implemented"], False)
        self.assertIs(payload["html_workbench_implemented"], False)
        self.assertIs(payload["workunit_runtime_implemented"], False)
        self.assertIs(payload["lan_enabled"], False)
        self.assertIs(payload["deployment_performed"], False)
        self.assertIs(payload["production_readiness_claimed"], False)
        self.assertIs(payload["public_launch_readiness_claimed"], False)


if __name__ == "__main__":
    unittest.main()
