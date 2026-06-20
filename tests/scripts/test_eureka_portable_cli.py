from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
CLI = REPO_ROOT / "scripts" / "eureka.py"


class EurekaPortableCLITests(unittest.TestCase):
    def run_cli(self, *args: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
        merged = dict(os.environ)
        if env is not None:
            merged.update(env)
        return subprocess.run(
            [sys.executable, str(CLI), *args],
            cwd=REPO_ROOT,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=merged,
            check=False,
        )

    def test_help_lists_required_commands(self) -> None:
        result = self.run_cli("--help")
        self.assertEqual(result.returncode, 0, result.stderr)
        for command in ("bootstrap", "doctor", "test", "serve", "hunt", "replay", "status"):
            self.assertIn(command, result.stdout)

    def test_unknown_command_fails(self) -> None:
        result = self.run_cli("does-not-exist")
        self.assertNotEqual(result.returncode, 0)

    def test_global_instance_option_works_before_and_after_command(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            first = Path(tmp) / "instance one"
            result = self.run_cli("--instance", str(first), "bootstrap", "--no-demo", "--json")
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(Path(payload["instance_root"]).resolve(), first.resolve())

            second = Path(tmp) / "instance two"
            result = self.run_cli("bootstrap", "--instance", str(second), "--no-demo", "--json")
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(Path(payload["instance_root"]).resolve(), second.resolve())

    def test_environment_instance_is_used_when_explicit_missing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "env instance"
            result = self.run_cli("bootstrap", "--no-demo", "--json", env={"EUREKA_INSTANCE": str(root)})
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(Path(payload["instance_root"]).resolve(), root.resolve())

    def test_default_status_is_read_only(self) -> None:
        result = self.run_cli("status", "--json", env={"EUREKA_INSTANCE": ""})
        self.assertIn(result.returncode, {0, 1})
        payload = json.loads(result.stdout)
        self.assertEqual(payload["command"], "status")
        self.assertFalse(payload["mutations_performed"])


if __name__ == "__main__":
    unittest.main()
