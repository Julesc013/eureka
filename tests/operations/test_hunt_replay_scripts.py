from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class HuntReplayScriptsTests(unittest.TestCase):
    def test_validator_demo_and_cli_pass(self) -> None:
        validator = subprocess.run(
            [sys.executable, "scripts/validate_hunt_replay.py", "--json"],
            text=True,
            capture_output=True,
            check=False,
            timeout=180,
        )
        self.assertEqual(validator.returncode, 0, validator.stderr + validator.stdout)
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp)
            self.assertEqual(subprocess.run([sys.executable, "scripts/eureka_init_instance.py", "--instance", str(instance), "--json"], check=False).returncode, 0)
            self.assertEqual(subprocess.run([sys.executable, "scripts/eureka_set_operator_token.py", "--instance", str(instance), "--token", "validator-token", "--json"], check=False).returncode, 0)
            demo = subprocess.run(
                [sys.executable, "scripts/demo_hunt_replay.py", "--instance", str(instance), "--operator-token", "validator-token", "--json"],
                text=True,
                capture_output=True,
                check=False,
                timeout=180,
            )
            self.assertEqual(demo.returncode, 0, demo.stderr + demo.stdout)
            payload = json.loads(demo.stdout)
            hunt_id = payload["hunt_id"]
            plan = subprocess.run(
                [sys.executable, "scripts/eureka_hunt_replay.py", "--instance", str(instance), "--hunt-id", hunt_id, "plan", "--json"],
                text=True,
                capture_output=True,
                check=False,
                timeout=120,
            )
            replay = subprocess.run(
                [
                    sys.executable,
                    "scripts/eureka_hunt_replay.py",
                    "--instance",
                    str(instance),
                    "--hunt-id",
                    hunt_id,
                    "--operator-token",
                    "validator-token",
                    "replay-local",
                    "--json",
                ],
                text=True,
                capture_output=True,
                check=False,
                timeout=120,
            )
            self.assertEqual(plan.returncode, 0, plan.stderr + plan.stdout)
            self.assertEqual(replay.returncode, 0, replay.stderr + replay.stdout)


if __name__ == "__main__":
    unittest.main()
