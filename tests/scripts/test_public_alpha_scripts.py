from __future__ import annotations

import json
import importlib.util
from pathlib import Path
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]


class PublicAlphaScriptsTestCase(unittest.TestCase):
    def test_demo_http_api_public_alpha_status_mode_flag(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(REPO_ROOT / "scripts" / "demo_http_api.py"),
                "--mode",
                "public_alpha",
                "status",
            ],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)

        self.assertEqual(payload["mode"], "public_alpha")
        self.assertTrue(payload["safe_mode_enabled"])

    def test_public_alpha_smoke_internal_checks_pass(self) -> None:
        smoke = _load_public_alpha_smoke_module()

        report = smoke.run_public_alpha_smoke()

        self.assertEqual(report["status"], "passed")
        self.assertGreaterEqual(report["total_checks"], 10)
        self.assertEqual(report["failed_checks"], 0)
        check_codes = {check["code"] for check in report["checks"]}
        self.assertIn("local_path_parameters_blocked", check_codes)
        self.assertIn("route_disabled_in_public_alpha", check_codes)
        self.assertNotIn(smoke.PRIVATE_PATH_SENTINEL, json.dumps(report))

    def test_public_alpha_smoke_json_mode(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(REPO_ROOT / "scripts" / "public_alpha_smoke.py"),
                "--json",
            ],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)

        self.assertEqual(payload["status"], "passed")
        self.assertEqual(payload["mode"], "public_alpha")
        self.assertEqual(payload["failed_checks"], 0)


def _load_public_alpha_smoke_module():
    module_path = REPO_ROOT / "scripts" / "public_alpha_smoke.py"
    spec = importlib.util.spec_from_file_location("public_alpha_smoke", module_path)
    if spec is None or spec.loader is None:
        raise AssertionError(f"Could not load {module_path}")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


if __name__ == "__main__":
    unittest.main()
