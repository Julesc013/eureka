from __future__ import annotations

import hashlib
import json
import subprocess
import tempfile
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
INIT = ROOT / "scripts" / "eureka_init_instance.py"
STATUS = ROOT / "scripts" / "eureka_local_runtime_status.py"
DEMO = ROOT / "scripts" / "demo_local_runtime_composition.py"
VALIDATOR = ROOT / "scripts" / "validate_local_runtime_composition.py"


def run_cmd(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(["python", *args], cwd=ROOT, text=True, capture_output=True, check=False)


def payload(completed: subprocess.CompletedProcess[str]) -> dict:
    return json.loads(completed.stdout)


class LocalRuntimeCompositionScriptTests(unittest.TestCase):
    def test_status_script_prints_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "eureka-instance"
            self.assertEqual(0, run_cmd(str(INIT), "--instance", str(instance), "--json").returncode)
            completed = run_cmd(str(STATUS), "--instance", str(instance), "--json")
            self.assertEqual(0, completed.returncode, completed.stderr)
            data = payload(completed)
            self.assertEqual("local_runtime_status.v0", data["schema_version"])
            self.assertEqual(4, data["store_count"])
            self.assertIs(data["server_enabled"], False)
            self.assertIs(data["lan_enabled"], False)

    def test_status_script_supports_read_only_mode(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "eureka-instance"
            self.assertEqual(0, run_cmd(str(INIT), "--instance", str(instance), "--json").returncode)
            completed = run_cmd(str(STATUS), "--instance", str(instance), "--read-only", "--json")
            self.assertEqual(0, completed.returncode, completed.stderr)
            self.assertIs(payload(completed)["read_only"], True)

    def test_demo_script_opens_and_closes_runtime_without_local_writes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "eureka-instance"
            self.assertEqual(0, run_cmd(str(INIT), "--instance", str(instance), "--json").returncode)
            before = tree_digest(instance)
            completed = run_cmd(str(DEMO), "--instance", str(instance), "--json")
            self.assertEqual(0, completed.returncode, completed.stderr)
            after = tree_digest(instance)
            data = payload(completed)
            self.assertEqual("pass", data["status"])
            self.assertTrue(data["stores_opened"]["source_cache"])
            self.assertEqual("pass", data["integrity"]["status"])
            self.assertEqual(before, after)

    def test_demo_requires_initialized_instance(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "eureka-instance"
            completed = run_cmd(str(DEMO), "--instance", str(instance), "--json")
            self.assertNotEqual(0, completed.returncode)
            self.assertEqual("missing_initialized_instance", payload(completed)["error"])

    def test_validator_passes(self) -> None:
        completed = run_cmd(str(VALIDATOR))
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)


def tree_digest(root: Path) -> str:
    digest = hashlib.sha256()
    for path in sorted(item for item in root.rglob("*") if item.is_file()):
        digest.update(path.relative_to(root).as_posix().encode("utf-8"))
        digest.update(path.read_bytes())
    return digest.hexdigest()


if __name__ == "__main__":
    unittest.main()
