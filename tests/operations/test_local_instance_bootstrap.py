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
STATUS = ROOT / "scripts" / "eureka_instance_status.py"
LOCAL_VALIDATOR = ROOT / "scripts" / "validate_local_instance_bootstrap.py"


def run_cmd(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["python", *args],
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )


def load_json_output(completed: subprocess.CompletedProcess[str]) -> dict:
    return json.loads(completed.stdout)


class LocalInstanceBootstrapTests(unittest.TestCase):
    def test_init_refuses_missing_instance(self) -> None:
        completed = run_cmd(str(INIT), "--json")
        self.assertNotEqual(0, completed.returncode)
        self.assertEqual("fail", load_json_output(completed)["status"])

    def test_init_refuses_repo_root(self) -> None:
        completed = run_cmd(str(INIT), "--instance", str(ROOT), "--json")
        self.assertNotEqual(0, completed.returncode)
        self.assertEqual("forbidden_instance_path", load_json_output(completed)["error"])

    def test_init_refuses_hidden_roots(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            completed = run_cmd(str(INIT), "--instance", str(Path(tmp) / ".cache" / "eureka-instance"), "--json")
        self.assertNotEqual(0, completed.returncode)
        self.assertEqual("forbidden_instance_path", load_json_output(completed)["error"])

    def test_init_creates_required_directories_and_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "eureka-instance"
            completed = run_cmd(str(INIT), "--instance", str(instance), "--json")
            self.assertEqual(0, completed.returncode, completed.stderr)
            for rel in ("config", "db", "logs", "run", "tmp", "exports", "imports"):
                self.assertTrue((instance / rel).is_dir(), rel)
            for rel in (
                "config/instance.json",
                "run/status.json",
                "db/source_cache.sqlite",
                "db/evidence_ledger.sqlite",
                "db/review_queue.sqlite",
                "db/public_index.sqlite",
            ):
                self.assertTrue((instance / rel).is_file(), rel)

    def test_init_writes_config_and_status_with_safe_flags(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "eureka-instance"
            completed = run_cmd(str(INIT), "--instance", str(instance), "--json")
            self.assertEqual(0, completed.returncode, completed.stderr)
            manifest = json.loads((instance / "config" / "instance.json").read_text(encoding="utf-8"))
            status = json.loads((instance / "run" / "status.json").read_text(encoding="utf-8"))
            self.assertEqual("local", manifest["appliance_mode"])
            for payload in (manifest, status):
                self.assertIs(payload["server_enabled"], False)
                self.assertIs(payload["lan_enabled"], False)
                self.assertIs(payload["production_readiness_claimed"], False)
                self.assertIs(payload["public_launch_readiness_claimed"], False)

    def test_init_is_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "eureka-instance"
            first = run_cmd(str(INIT), "--instance", str(instance), "--json")
            self.assertEqual(0, first.returncode, first.stderr)
            first_manifest = json.loads((instance / "config" / "instance.json").read_text(encoding="utf-8"))
            second = run_cmd(str(INIT), "--instance", str(instance), "--json")
            self.assertEqual(0, second.returncode, second.stderr)
            second_manifest = json.loads((instance / "config" / "instance.json").read_text(encoding="utf-8"))
            self.assertEqual(first_manifest["instance_id"], second_manifest["instance_id"])

    def test_validate_passes_on_initialized_temp_instance(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "eureka-instance"
            init = run_cmd(str(INIT), "--instance", str(instance), "--json")
            self.assertEqual(0, init.returncode, init.stderr)
            validate = run_cmd(str(VALIDATE), "--instance", str(instance), "--json")
            self.assertEqual(0, validate.returncode, validate.stderr)
            self.assertIn(load_json_output(validate)["status"], {"pass", "pass_with_warnings"})

    def test_validate_fails_on_missing_config(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "eureka-instance"
            init = run_cmd(str(INIT), "--instance", str(instance), "--json")
            self.assertEqual(0, init.returncode, init.stderr)
            (instance / "config" / "instance.json").unlink()
            validate = run_cmd(str(VALIDATE), "--instance", str(instance), "--json")
            self.assertNotEqual(0, validate.returncode)
            self.assertEqual("fail", load_json_output(validate)["status"])

    def test_status_script_is_read_only(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "eureka-instance"
            init = run_cmd(str(INIT), "--instance", str(instance), "--json")
            self.assertEqual(0, init.returncode, init.stderr)
            before = tree_digest(instance)
            status = run_cmd(str(STATUS), "--instance", str(instance), "--json")
            self.assertEqual(0, status.returncode, status.stderr)
            after = tree_digest(instance)
            self.assertEqual(before, after)

    def test_no_server_or_lan_or_deployment_started(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "eureka-instance"
            completed = run_cmd(str(INIT), "--instance", str(instance), "--json")
            payload = load_json_output(completed)
            self.assertIs(payload["server_enabled"], False)
            self.assertIs(payload["lan_enabled"], False)
            self.assertIs(payload["deployment_performed"], False)

    def test_local_instance_state_is_not_committed(self) -> None:
        completed = subprocess.run(
            ["git", "ls-files", "--", "eureka-instance"],
            cwd=ROOT,
            text=True,
            capture_output=True,
            check=False,
        )
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
