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
            self.assertEqual("PLAY-01", payload["task"])
            self.assertEqual("dry_run", payload["seed_mode"])
            self.assertEqual("dry_run", payload["seed_state"]["mode"])
            self.assertFalse(payload["seed_result"]["mutation_performed"])
            self.assertFalse(payload["seed_state"]["mutation_performed"])
            self.assertFalse(instance.exists())
            for section in (
                "instance",
                "seed_state",
                "search_results",
                "absence_results",
                "hunts",
                "search_needs",
                "workunits",
                "blocked_future_actions",
                "server_routes_if_checked",
                "warnings",
                "boundaries",
                "next_suggested_actions",
            ):
                self.assertIn(section, payload)

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

    def test_seed_demo_without_apply_remains_dry_run(self):
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "instances" / "default"
            completed = run_script(
                "scripts/eureka_play_session.py",
                "--instance",
                str(instance),
                "--operator-token",
                "local-dev-token",
                "--seed-demo",
                "--json",
            )
            self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertTrue(payload["seed_state"]["dry_run"])
            self.assertFalse(payload["seed_state"]["mutation_performed"])
            self.assertFalse(instance.exists())

    def test_apply_mode_requires_operator_token(self):
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "instances" / "default"
            completed = run_script(
                "scripts/eureka_play_session.py",
                "--instance",
                str(instance),
                "--apply",
                "--json",
            )
            self.assertNotEqual(0, completed.returncode)
            payload = json.loads(completed.stdout)
            self.assertEqual("fail", payload["status"])
            self.assertFalse(payload["source_probe_executed"])

    def test_help_exposes_play_01_controls(self):
        completed = run_script("scripts/eureka_play_session.py", "--help")
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        self.assertIn("--seed-demo", completed.stdout)
        self.assertIn("--apply", completed.stdout)
        self.assertIn("--query", completed.stdout)
        self.assertIn("--expect-server", completed.stdout)


if __name__ == "__main__":
    unittest.main()
