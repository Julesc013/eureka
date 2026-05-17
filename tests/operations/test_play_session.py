import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, *args], cwd=ROOT, text=True, capture_output=True, check=False)


class PlaySessionScriptTests(unittest.TestCase):
    def test_play_session_report_passes_without_mutating_instance(self):
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "instances" / "default"
            completed = run_script(
                "scripts/eureka_play_session.py",
                "--instance",
                str(instance),
                "--operator-token",
                "local-dev-token",
                "--json",
            )
            self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual("pass", payload["status"])
            self.assertEqual("dry_run", payload["seed_mode"])
            self.assertFalse(payload["seed_result"]["mutation_performed"])
            self.assertFalse(instance.exists())

    def test_play_session_can_write_output_report(self):
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "instances" / "default"
            output = Path(tmp) / "play-session.json"
            completed = run_script(
                "scripts/eureka_play_session.py",
                "--instance",
                str(instance),
                "--operator-token",
                "local-dev-token",
                "--output",
                str(output),
                "--json",
            )
            self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
            self.assertTrue(output.is_file())
            payload = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual("pass", payload["status"])
            self.assertFalse(payload["source_probe_executed"])


if __name__ == "__main__":
    unittest.main()
