from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path
import unittest

from runtime.local_appliance import close_local_appliance, open_local_appliance
from runtime.search_hunt import (
    BLOCKED_REPLAY_STEP_KINDS,
    ENABLED_REPLAY_STEP_KINDS,
    build_replay_fixture_from_hunt,
    build_replay_plan_from_hunt,
    run_hunt_replay,
)


ROOT = Path(__file__).resolve().parents[2]
INIT = ROOT / "scripts" / "eureka_init_instance.py"


def init_instance(tmp: str) -> Path:
    instance = Path(tmp) / "eureka-instance"
    completed = subprocess.run(["python", str(INIT), "--instance", str(instance), "--json"], cwd=ROOT, text=True, capture_output=True)
    if completed.returncode != 0:
        raise AssertionError(completed.stderr)
    return instance


class HuntReplayPlanTests(unittest.TestCase):
    def test_plan_builds_from_hunt_without_persisting_replay_run(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runtime = open_local_appliance(init_instance(tmp))
            try:
                hunt = runtime.search_hunt.create_session_from_query("sampleproject", runtime=runtime)
                fixture = build_replay_fixture_from_hunt(runtime, hunt.id)
                plan = build_replay_plan_from_hunt(runtime, hunt.id)
                result = run_hunt_replay(runtime, fixture, mode="plan_only")

                self.assertEqual(len(ENABLED_REPLAY_STEP_KINDS), len(plan.expected_steps))
                self.assertEqual(len(BLOCKED_REPLAY_STEP_KINDS), len(plan.blocked_steps))
                self.assertEqual("plan_only", result.mode.value)
                self.assertEqual(0, len(runtime.search_hunt.list_replay_results(hunt_id=hunt.id, limit=10)))
                self.assertFalse(result.to_dict()["source_probe_executed"])
            finally:
                close_local_appliance(runtime)


if __name__ == "__main__":
    unittest.main()
