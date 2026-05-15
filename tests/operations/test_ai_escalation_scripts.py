import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class AIEscalationScriptsTests(unittest.TestCase):
    def test_validator_demo_and_cli_pass(self):
        validator = subprocess.run(
            [sys.executable, "scripts/validate_ai_escalation_gate.py", "--json"],
            text=True,
            capture_output=True,
            check=False,
            timeout=120,
        )
        self.assertEqual(validator.returncode, 0, validator.stderr + validator.stdout)
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp)
            self.assertEqual(subprocess.run([sys.executable, "scripts/eureka_init_instance.py", "--instance", str(instance), "--json"], check=False).returncode, 0)
            self.assertEqual(subprocess.run([sys.executable, "scripts/eureka_set_operator_token.py", "--instance", str(instance), "--token", "validator-token", "--json"], check=False).returncode, 0)
            demo = subprocess.run(
                [
                    sys.executable,
                    "scripts/demo_ai_escalation_gate.py",
                    "--instance",
                    str(instance),
                    "--operator-token",
                    "validator-token",
                    "--json",
                ],
                text=True,
                capture_output=True,
                check=False,
                timeout=120,
            )
            self.assertEqual(demo.returncode, 0, demo.stderr + demo.stdout)
            payload = __import__("json").loads(demo.stdout)
            hunt_id = payload["hunt"]["id"]
            cli = subprocess.run(
                [
                    sys.executable,
                    "scripts/eureka_ai_escalation_gate.py",
                    "--instance",
                    str(instance),
                    "preflight-hunt",
                    "--hunt-id",
                    hunt_id,
                    "--operator-token",
                    "validator-token",
                    "--json",
                ],
                text=True,
                capture_output=True,
                check=False,
                timeout=120,
            )
            self.assertEqual(cli.returncode, 0, cli.stderr + cli.stdout)


if __name__ == "__main__":
    unittest.main()
