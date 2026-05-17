import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, *args], cwd=ROOT, text=True, capture_output=True, check=False)


class InstanceLayoutScriptsTests(unittest.TestCase):
    def test_resolve_paths_default(self):
        completed = run_script("scripts/eureka_resolve_paths.py", "--json")
        self.assertEqual(0, completed.returncode, completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual("preferred_default", payload["layout_class"])
        self.assertTrue(payload["preferred_default_instance_root"].endswith(str(Path("instances") / "default")))

    def test_list_instances_detects_sibling_root(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "eureka"
            (Path(tmp) / "instances" / "default").mkdir(parents=True)
            completed = run_script("scripts/eureka_list_instances.py", "--repo-root", str(repo), "--json")
            self.assertEqual(0, completed.returncode, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertTrue(payload["instances_root_exists"])
            self.assertEqual(["default"], [item["name"] for item in payload["instances"]])

    def test_migration_dry_run_does_not_mutate(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp) / "eureka"
            source = Path(tmp) / "eureka-instance"
            target = Path(tmp) / "instances" / "default"
            source.mkdir()
            completed = run_script(
                "scripts/eureka_migrate_instance_layout.py",
                "--repo-root",
                str(repo),
                "--from",
                str(source),
                "--to",
                str(target),
                "--dry-run",
                "--json",
            )
            self.assertEqual(0, completed.returncode, completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertTrue(payload["dry_run"])
            self.assertFalse(payload["mutation_performed"])
            self.assertFalse(target.exists())

    def test_validator_passes(self):
        completed = run_script("scripts/validate_instance_layout_policy.py")
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual("pass", payload["status"])


if __name__ == "__main__":
    unittest.main()
