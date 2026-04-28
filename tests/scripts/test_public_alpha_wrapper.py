from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "run_public_alpha_server.py"


class PublicAlphaWrapperScriptTest(unittest.TestCase):
    def test_check_config_accepts_safe_defaults(self) -> None:
        completed = self._run("--check-config")

        self.assertEqual(completed.returncode, 0)
        self.assertIn("status: valid", completed.stdout)
        self.assertIn("live_probes_enabled: False", completed.stdout)
        self.assertIn("production_ready: False", completed.stdout)

    def test_print_config_json_parses(self) -> None:
        completed = self._run("--print-config-json")
        payload = json.loads(completed.stdout)

        self.assertEqual(completed.returncode, 0)
        self.assertEqual(payload["status"], "valid")
        self.assertEqual(payload["mode"], "public_alpha")
        self.assertFalse(payload["downloads_enabled"])
        self.assertFalse(payload["deployment_approved"])

    def test_nonlocal_bind_is_refused_without_gate(self) -> None:
        completed = self._run("--host", "0.0.0.0", "--check-config")

        self.assertEqual(completed.returncode, 2)
        self.assertIn("nonlocal bind", completed.stdout)

    def test_nonlocal_bind_can_be_explicitly_acknowledged(self) -> None:
        completed = self._run(
            "--host",
            "0.0.0.0",
            "--allow-nonlocal-bind",
            "--check-config",
        )

        self.assertEqual(completed.returncode, 0)
        self.assertIn("status: valid", completed.stdout)
        self.assertIn("not deployment approval", completed.stdout)

    def test_unsupported_mode_is_rejected(self) -> None:
        completed = self._run("--mode", "local_dev", "--check-config")

        self.assertEqual(completed.returncode, 2)
        self.assertIn("mode must be public_alpha", completed.stdout)

    def test_live_probe_env_is_rejected(self) -> None:
        env = {"EUREKA_ALLOW_LIVE_PROBES": "1"}
        completed = self._run("--check-config", extra_env=env)

        self.assertEqual(completed.returncode, 2)
        self.assertIn("live probes", completed.stdout)

    def test_path_env_value_is_not_printed(self) -> None:
        private_path = "D:/private/eureka-index"
        completed = self._run(
            "--print-config-json",
            extra_env={"EUREKA_WEB_INDEX_ROOT": private_path},
        )
        payload = json.loads(completed.stdout)

        self.assertEqual(completed.returncode, 2)
        self.assertEqual(payload["status"], "invalid")
        self.assertIn("EUREKA_WEB_INDEX_ROOT", completed.stdout)
        self.assertNotIn(private_path, completed.stdout)

    def _run(self, *args: str, extra_env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
        env = os.environ.copy()
        for name in tuple(env):
            if name.startswith("EUREKA_"):
                env.pop(name)
        if extra_env:
            env.update(extra_env)
        return subprocess.run(
            [sys.executable, str(SCRIPT), *args],
            cwd=REPO_ROOT,
            env=env,
            capture_output=True,
            text=True,
        )


if __name__ == "__main__":
    unittest.main()
