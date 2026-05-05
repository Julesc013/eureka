import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
EXAMPLE = ROOT / "examples" / "compatibility_aware_ranking" / "minimal_os_compatibility_ranking_v0" / "COMPATIBILITY_TARGET_PROFILE.json"


class CompatibilityTargetProfileValidatorTests(unittest.TestCase):
    def test_validator_passes_all_examples(self):
        completed = subprocess.run([sys.executable, "scripts/validate_compatibility_target_profile.py", "--all-examples"], cwd=ROOT, text=True, capture_output=True, check=True)
        self.assertIn("status: valid", completed.stdout)
        self.assertIn("example_count: 6", completed.stdout)

    def test_validator_json_parses(self):
        completed = subprocess.run([sys.executable, "scripts/validate_compatibility_target_profile.py", "--all-examples", "--json"], cwd=ROOT, text=True, capture_output=True, check=True)
        report = json.loads(completed.stdout)
        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["example_count"], 6)

    def test_profile_hard_fields_safe(self):
        page = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        for key in ("runtime_profile_store_implemented", "persistent_profile_store_implemented", "user_profile_tracking_enabled", "telemetry_exported", "private_path_included", "credentials_included", "local_machine_fingerprint_included"):
            self.assertFalse(page[key], key)
        self.assertFalse(page["privacy"]["contains_local_machine_fingerprint"])

    def test_negative_profile_fails(self):
        self._assert_invalid(("local_machine_fingerprint_included",), True)

    def test_negative_private_path_fails(self):
        self._assert_invalid(("notes", 0), "C:\\Users\\Example\\profile.txt")

    def _assert_invalid(self, key_path, value):
        page = json.loads(EXAMPLE.read_text(encoding="utf-8"))
        target = page
        for part in key_path[:-1]:
            target = target[part]
        target[key_path[-1]] = value
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "COMPATIBILITY_TARGET_PROFILE.json"
            path.write_text(json.dumps(page), encoding="utf-8")
            completed = subprocess.run([sys.executable, "scripts/validate_compatibility_target_profile.py", "--profile", str(path), "--json"], cwd=ROOT, text=True, capture_output=True)
        self.assertNotEqual(completed.returncode, 0)
        self.assertEqual(json.loads(completed.stdout)["status"], "invalid")


if __name__ == "__main__":
    unittest.main()
