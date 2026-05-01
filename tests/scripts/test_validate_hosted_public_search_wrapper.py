from __future__ import annotations

import json
import os
from pathlib import Path
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = REPO_ROOT / "scripts" / "validate_hosted_public_search_wrapper.py"
RUNNER = REPO_ROOT / "scripts" / "run_hosted_public_search.py"


def _safe_env(**overrides: str) -> dict[str, str]:
    env = os.environ.copy()
    env.update(
        {
            "EUREKA_PUBLIC_MODE": "1",
            "EUREKA_SEARCH_MODE": "local_index_only",
            "EUREKA_ALLOW_LIVE_PROBES": "0",
            "EUREKA_ALLOW_DOWNLOADS": "0",
            "EUREKA_ALLOW_UPLOADS": "0",
            "EUREKA_ALLOW_LOCAL_PATHS": "0",
            "EUREKA_ALLOW_ARBITRARY_URL_FETCH": "0",
            "EUREKA_ALLOW_INSTALL_ACTIONS": "0",
            "EUREKA_ALLOW_TELEMETRY": "0",
            "EUREKA_OPERATOR_KILL_SWITCH": "0",
            "EUREKA_HOSTED_DEPLOYMENT_VERIFIED": "0",
            "EUREKA_DYNAMIC_BACKEND_DEPLOYED": "0",
        }
    )
    env.update(overrides)
    return env


class ValidateHostedPublicSearchWrapperScriptTest(unittest.TestCase):
    def test_plain_validator_passes(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(VALIDATOR)],
            cwd=REPO_ROOT,
            check=True,
            text=True,
            capture_output=True,
        )
        self.assertIn("status: valid", completed.stdout)
        self.assertIn("public_search_mode: local_index_only", completed.stdout)

    def test_json_validator_passes_and_parses(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(VALIDATOR), "--json"],
            cwd=REPO_ROOT,
            check=True,
            text=True,
            capture_output=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "valid")
        self.assertEqual(payload["report_id"], "hosted_public_search_wrapper_v0")
        self.assertTrue(payload["hosted_wrapper_implemented"])
        self.assertFalse(payload["hosted_backend_deployed"])
        self.assertFalse(payload["hosted_deployment_verified"])

    def test_check_config_passes_under_safe_defaults(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(RUNNER), "--check-config", "--json"],
            cwd=REPO_ROOT,
            env=_safe_env(),
            check=True,
            text=True,
            capture_output=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "valid")
        self.assertFalse(payload["config"]["live_probes_enabled"])

    def test_check_config_refuses_prohibited_feature_flags(self) -> None:
        for env_name in (
            "EUREKA_ALLOW_LIVE_PROBES",
            "EUREKA_ALLOW_DOWNLOADS",
            "EUREKA_ALLOW_UPLOADS",
            "EUREKA_ALLOW_LOCAL_PATHS",
        ):
            with self.subTest(env_name=env_name):
                completed = subprocess.run(
                    [sys.executable, str(RUNNER), "--check-config"],
                    cwd=REPO_ROOT,
                    env=_safe_env(**{env_name: "1"}),
                    text=True,
                    capture_output=True,
                )
                self.assertNotEqual(completed.returncode, 0)
                self.assertIn("status: invalid", completed.stdout)


if __name__ == "__main__":
    unittest.main()
