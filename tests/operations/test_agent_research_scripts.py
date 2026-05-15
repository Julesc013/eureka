import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class AgentResearchScriptsTests(unittest.TestCase):
    def test_validator_demo_and_schema_cli_pass(self):
        validator = subprocess.run(
            [sys.executable, "scripts/validate_agent_research_task_contract.py", "--json"],
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
                    "scripts/demo_agent_research_task.py",
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
        schema = subprocess.run(
            [sys.executable, "scripts/eureka_agent_research_task.py", "report-schema", "--json"],
            text=True,
            capture_output=True,
            check=False,
            timeout=120,
        )
        self.assertEqual(schema.returncode, 0, schema.stderr + schema.stdout)


if __name__ == "__main__":
    unittest.main()
