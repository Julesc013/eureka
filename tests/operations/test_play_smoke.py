import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, *args], cwd=ROOT, text=True, capture_output=True, check=False)


class PlaySmokeScriptTests(unittest.TestCase):
    def test_play_smoke_passes_offline(self):
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "instances" / "default"
            completed = run_script(
                "scripts/eureka_play_smoke.py",
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
            self.assertTrue(payload["checks"]["known_hit_query"])
            self.assertTrue(payload["checks"]["known_absence_query"])
            self.assertTrue(payload["checks"]["dry_run_play_session"])
            self.assertTrue(payload["checks"]["apply_play_session_temp_instance"])
            self.assertTrue(payload["checks"]["blocked_source_probe_checked"])
            self.assertTrue(payload["checks"]["blocked_extraction_checked"])
            self.assertTrue(payload["checks"]["blocked_ai_checked"])
            self.assertFalse(payload["source_probe_executed"])
            self.assertFalse(payload["extraction_executed"])
            self.assertFalse(payload["model_provider_used"])
            self.assertFalse(instance.exists())

    def test_seed_script_defaults_to_dry_run_and_requires_apply_to_mutate(self):
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "instances" / "default"
            completed = run_script("scripts/eureka_seed_play_demo.py", "--instance", str(instance), "--json")
            self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertTrue(payload["dry_run"])
            self.assertFalse(payload["mutation_performed"])
            self.assertFalse(instance.exists())

    def test_seed_script_apply_requires_operator_token(self):
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "instances" / "default"
            completed = run_script("scripts/eureka_seed_play_demo.py", "--instance", str(instance), "--apply", "--json")
            self.assertNotEqual(0, completed.returncode)
            payload = json.loads(completed.stdout)
            self.assertEqual("fail", payload["status"])
            self.assertFalse(payload["source_probe_executed"])

    def test_play_validator_passes(self):
        completed = run_script("scripts/validate_play_seed_pack.py")
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual("pass", payload["status"])

    def test_play_session_validator_passes(self):
        completed = run_script("scripts/validate_play_session.py")
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual("pass", payload["status"])


if __name__ == "__main__":
    unittest.main()
