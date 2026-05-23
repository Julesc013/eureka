from __future__ import annotations

import subprocess
import tempfile
from pathlib import Path
import unittest

from runtime.local.appliance import close_local_appliance, open_local_appliance
from runtime.search.hunt import BLOCKED_REPLAY_STEP_KINDS, SearchHuntValidationError, build_replay_fixture_from_hunt, run_hunt_replay


ROOT = Path(__file__).resolve().parents[2]
INIT = ROOT / "scripts" / "eureka_init_instance.py"


def init_instance(tmp: str) -> Path:
    instance = Path(tmp) / "eureka-instance"
    completed = subprocess.run(["python", str(INIT), "--instance", str(instance), "--json"], cwd=ROOT, text=True, capture_output=True)
    if completed.returncode != 0:
        raise AssertionError(completed.stderr)
    return instance


class HuntReplayPolicyTests(unittest.TestCase):
    def test_blocked_steps_remain_blocked_and_replay_run_requires_token_context(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runtime = open_local_appliance(init_instance(tmp))
            try:
                hunt = runtime.search_hunt.create_session_from_query("sampleproject", runtime=runtime)
                fixture = build_replay_fixture_from_hunt(runtime, hunt.id)
                blocked = {item.kind for item in fixture.blocked_steps}

                self.assertEqual(set(BLOCKED_REPLAY_STEP_KINDS), blocked)
                for step in fixture.blocked_steps:
                    self.assertEqual("blocked", step.status.value)
                    self.assertFalse(step.policy_decision["allowed"])
                    self.assertFalse(step.policy_decision["source_probe_allowed"])
                    self.assertFalse(step.policy_decision["extraction_allowed"])
                    self.assertFalse(step.policy_decision["model_provider_allowed"])
                with self.assertRaises(SearchHuntValidationError):
                    run_hunt_replay(runtime, fixture, mode="replay_local")
            finally:
                close_local_appliance(runtime)


if __name__ == "__main__":
    unittest.main()
