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
    def test_play_smoke_defaults_to_dry_run_without_mutating_instance(self):
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "instances" / "default"
            completed = run_script(
                "scripts/eureka_play_smoke.py",
                "--instance",
                str(instance),
                "--operator-token",
                "local-dev-token",
                "--dry-run",
                "--json",
            )
            self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertEqual("pass", payload["status"])
            self.assertEqual("PLAY-02", payload["task"])
            self.assertEqual("dry_run", payload["mode"])
            checks = payload["validation"]["checks"]
            self.assertTrue(checks["known_hit_checked"])
            self.assertTrue(checks["known_absence_checked"])
            self.assertTrue(checks["media_search_need_checked"])
            self.assertTrue(checks["extraction_search_need_checked"])
            self.assertTrue(checks["hard_source_routing_checked"])
            self.assertTrue(checks["compatibility_query_checked"])
            self.assertTrue(checks["blocked_source_probe_checked"])
            self.assertTrue(checks["blocked_extraction_checked"])
            self.assertTrue(checks["blocked_ai_checked"])
            self.assertFalse(payload["source_probe_executed"])
            self.assertFalse(payload["extraction_executed"])
            self.assertFalse(payload["model_provider_used"])
            self.assertFalse(instance.exists())

    def test_play_smoke_temp_apply_uses_temp_instance(self):
        completed = run_script(
            "scripts/eureka_play_smoke.py",
            "--use-temp-instance",
            "--apply-demo-to-temp",
            "--operator-token",
            "local-dev-token",
            "--json",
        )
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual("pass", payload["status"], payload)
        self.assertEqual("temp_apply", payload["mode"])
        self.assertTrue(payload["instance"]["temporary"])
        self.assertTrue(payload["temp_instance_smoke_passed"])
        self.assertFalse(payload["operator_instance_mutated"])
        self.assertFalse(payload["source_probe_executed"])
        self.assertFalse(payload["extraction_executed"])
        self.assertFalse(payload["model_provider_used"])

    def test_apply_demo_to_temp_cannot_target_operator_instance(self):
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "instances" / "default"
            completed = run_script(
                "scripts/eureka_play_smoke.py",
                "--instance",
                str(instance),
                "--apply-demo-to-temp",
                "--operator-token",
                "local-dev-token",
                "--json",
            )
            self.assertNotEqual(0, completed.returncode)
            payload = json.loads(completed.stdout)
            self.assertEqual("fail", payload["status"])
            self.assertFalse(payload["source_probe_executed"])

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

    def test_play_smoke_pack_validator_passes(self):
        completed = run_script("scripts/validate_play_smoke_pack.py")
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual("pass", payload["status"], payload)


if __name__ == "__main__":
    unittest.main()
