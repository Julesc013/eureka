from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
INIT = ROOT / "scripts" / "eureka_init_instance.py"
VALIDATE = ROOT / "scripts" / "eureka_validate_instance.py"
MIGRATION_STATUS = ROOT / "scripts" / "eureka_instance_migration_status.py"
LOCAL_VALIDATOR = ROOT / "scripts" / "validate_local_instance_migration_guard.py"


def run_cmd(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["python", *args], cwd=ROOT, text=True, capture_output=True, check=False)


def payload(completed: subprocess.CompletedProcess[str]) -> dict:
    return json.loads(completed.stdout)


class LocalInstanceMigrationGuardTests(unittest.TestCase):
    def test_init_writes_store_manifest_and_migration_state(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "eureka-instance"
            completed = run_cmd(str(INIT), "--instance", str(instance), "--json")
            self.assertEqual(0, completed.returncode, completed.stderr)
            self.assertTrue((instance / "config" / "store_manifest.json").is_file())
            self.assertTrue((instance / "config" / "migration_state.json").is_file())

    def test_init_writes_instance_schema_version(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "eureka-instance"
            completed = run_cmd(str(INIT), "--instance", str(instance), "--json")
            self.assertEqual(0, completed.returncode, completed.stderr)
            manifest = json.loads((instance / "config" / "instance.json").read_text(encoding="utf-8"))
            self.assertEqual(1, manifest["instance_schema_version"])

    def test_rerun_preserves_instance_id(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "eureka-instance"
            first = run_cmd(str(INIT), "--instance", str(instance), "--json")
            self.assertEqual(0, first.returncode, first.stderr)
            first_id = json.loads((instance / "config" / "instance.json").read_text(encoding="utf-8"))["instance_id"]
            second = run_cmd(str(INIT), "--instance", str(instance), "--json")
            self.assertEqual(0, second.returncode, second.stderr)
            second_id = json.loads((instance / "config" / "instance.json").read_text(encoding="utf-8"))["instance_id"]
            self.assertEqual(first_id, second_id)

    def test_validate_passes_supported_schema_version(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "eureka-instance"
            self.assertEqual(0, run_cmd(str(INIT), "--instance", str(instance), "--json").returncode)
            validate = run_cmd(str(VALIDATE), "--instance", str(instance), "--json")
            self.assertEqual(0, validate.returncode, validate.stderr)
            self.assertEqual("pass", payload(validate)["status"])

    def test_validate_fails_unsupported_schema_version(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "eureka-instance"
            self.assertEqual(0, run_cmd(str(INIT), "--instance", str(instance), "--json").returncode)
            manifest_path = instance / "config" / "instance.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["instance_schema_version"] = 999
            manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            state_path = instance / "config" / "migration_state.json"
            state = json.loads(state_path.read_text(encoding="utf-8"))
            state["current_instance_schema_version"] = 999
            state["migration_needed"] = True
            state["blockers"] = ["unsupported instance_schema_version 999"]
            state_path.write_text(json.dumps(state, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            validate = run_cmd(str(VALIDATE), "--instance", str(instance), "--json")
            self.assertNotEqual(0, validate.returncode)
            self.assertTrue(payload(validate)["unsupported_instance_schema_version"])

    def test_migration_status_is_read_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "eureka-instance"
            self.assertEqual(0, run_cmd(str(INIT), "--instance", str(instance), "--json").returncode)
            before = tree_digest(instance)
            status = run_cmd(str(MIGRATION_STATUS), "--instance", str(instance), "--json")
            self.assertEqual(0, status.returncode, status.stderr)
            after = tree_digest(instance)
            self.assertEqual(before, after)

    def test_migration_status_detects_migration_needed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "eureka-instance"
            self.assertEqual(0, run_cmd(str(INIT), "--instance", str(instance), "--json").returncode)
            manifest_path = instance / "config" / "instance.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            manifest["instance_schema_version"] = 999
            manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            status = run_cmd(str(MIGRATION_STATUS), "--instance", str(instance), "--json")
            self.assertEqual(0, status.returncode, status.stderr)
            self.assertTrue(payload(status)["migration_needed"])
            self.assertTrue(payload(status)["blockers"])

    def test_destructive_migration_is_forbidden(self) -> None:
        policy = json.loads((ROOT / "control/policies/local_instance_migration_policy.json").read_text(encoding="utf-8"))
        schema = json.loads((ROOT / "control/policies/local_instance_schema_policy.json").read_text(encoding="utf-8"))
        self.assertIs(policy["destructive_migrations_enabled"], False)
        self.assertIs(schema["destructive_migration_allowed"], False)

    def test_missing_required_store_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "eureka-instance"
            self.assertEqual(0, run_cmd(str(INIT), "--instance", str(instance), "--json").returncode)
            (instance / "db" / "source_cache.sqlite").unlink()
            validate = run_cmd(str(VALIDATE), "--instance", str(instance), "--json")
            self.assertNotEqual(0, validate.returncode)
            self.assertIn("missing required database file", "\n".join(payload(validate)["errors"]))

    def test_forbidden_roots_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            hidden = run_cmd(str(INIT), "--instance", str(Path(tmp) / ".cache" / "eureka-instance"), "--json")
            self.assertNotEqual(0, hidden.returncode)
            repo_root = run_cmd(str(INIT), "--instance", str(ROOT), "--json")
            self.assertNotEqual(0, repo_root.returncode)

    def test_no_server_lan_or_claims(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "eureka-instance"
            completed = run_cmd(str(INIT), "--instance", str(instance), "--json")
            data = payload(completed)
            self.assertIs(data["server_enabled"], False)
            self.assertIs(data["lan_enabled"], False)
            self.assertIs(data["deployment_performed"], False)
            self.assertIs(data["production_readiness_claimed"], False)
            self.assertIs(data["public_launch_readiness_claimed"], False)

    def test_local_instance_state_is_not_committed(self) -> None:
        completed = subprocess.run(["git", "ls-files", "--", "eureka-instance"], cwd=ROOT, text=True, capture_output=True, check=False)
        self.assertEqual("", completed.stdout.strip())

    def test_validator_passes_focused_tests(self) -> None:
        completed = run_cmd(str(LOCAL_VALIDATOR))
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)


def tree_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        digest.update(path.relative_to(root).as_posix().encode("utf-8"))
        digest.update(path.read_bytes())
    return digest.hexdigest()


if __name__ == "__main__":
    unittest.main()
