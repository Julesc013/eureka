from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path
import unittest

from runtime.local.appliance import close_local_appliance, open_local_appliance
from runtime.search.hunt import (
    build_replay_fixture_from_hunt,
    build_replay_plan_from_hunt,
    run_hunt_replay,
    verify_existing_hunt_against_replay,
)
from scripts.eureka_hunt_workflow_smoke import run_workflow_smoke


ROOT = Path(__file__).resolve().parents[2]
INIT = ROOT / "scripts" / "eureka_init_instance.py"


def init_instance(tmp: str) -> Path:
    instance = Path(tmp) / "eureka-instance"
    completed = subprocess.run(["python", str(INIT), "--instance", str(instance), "--json"], cwd=ROOT, text=True, capture_output=True)
    if completed.returncode != 0:
        raise AssertionError(completed.stderr)
    return instance


class HuntReplayExecutionTests(unittest.TestCase):
    def test_replay_local_stores_result_and_verify_existing_compares_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runtime = open_local_appliance(init_instance(tmp))
            try:
                workflow = run_workflow_smoke(runtime, query="sampleproject", missing_query="definitely-not-present-hunt-10")
                hunt_id = workflow["hunt_id"]
                runtime.agent_research.draft_task_from_hunt(runtime, hunt_id, operator_label="test")
                fixture = build_replay_fixture_from_hunt(runtime, hunt_id)
                result = run_hunt_replay(runtime, fixture, operator_context={"authorized": True, "operator_label": "test"}, mode="replay_local")
                verify = verify_existing_hunt_against_replay(runtime, hunt_id, fixture)

                self.assertEqual("pass", result.record.status)
                self.assertEqual("pass", verify.record.status)
                self.assertTrue(result.record.diff_summary.matched)
                self.assertTrue(runtime.search_hunt.get_replay_result(result.record.replay_id))
                self.assertGreaterEqual(len(result.record.executed_steps), len(build_replay_plan_from_hunt(runtime, hunt_id).expected_steps))
                self.assertFalse(result.to_dict()["source_probe_executed"])
                self.assertFalse(result.to_dict()["extraction_executed"])
                self.assertFalse(result.to_dict()["model_provider_used"])
            finally:
                close_local_appliance(runtime)


if __name__ == "__main__":
    unittest.main()
