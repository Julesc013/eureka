from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "validate_repository_layout.py"


def load_validator():
    spec = importlib.util.spec_from_file_location("validate_repository_layout", SCRIPT)
    if spec is None or spec.loader is None:
        raise ImportError(f"Unable to load {SCRIPT}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class RepositoryLayoutValidatorScriptTest(unittest.TestCase):
    def test_validator_plain_passes(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT)],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("status: valid", completed.stdout)
        self.assertIn("static_artifact_root: site/dist", completed.stdout)
        self.assertIn("generated_artifact_id: static_site_dist", completed.stdout)

    def test_validator_json_parses(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), "--json"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "valid")
        self.assertEqual(payload["static_artifact_root"], "site/dist")
        self.assertEqual(payload["external_root"], "external")
        self.assertEqual(payload["generated_artifact_id"], "static_site_dist")
        self.assertEqual(payload["active_legacy_reference_hits"], [])

    def test_validator_strict_passes(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), "--strict", "--json"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertEqual(json.loads(completed.stdout)["status"], "valid")

    def test_outside_material_language_is_not_retired_root_reference(self) -> None:
        module = load_validator()
        outside_hyphen = "third" + "-party"
        outside_underscore = "third" + "_party"

        self.assertTrue(module._is_allowed_legacy_reference_line(f"{outside_hyphen} materials"))
        self.assertTrue(module._is_allowed_legacy_reference_line(f"{outside_hyphen} notices"))
        self.assertFalse(module._is_allowed_legacy_reference_line(f"{outside_hyphen} root"))
        self.assertFalse(module._is_allowed_legacy_reference_line(f"{outside_hyphen}/"))
        self.assertFalse(module._is_allowed_legacy_reference_line(f"{outside_underscore}/sample"))


if __name__ == "__main__":
    unittest.main()
