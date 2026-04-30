from __future__ import annotations

import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = REPO_ROOT / "scripts" / "validate_ai_output.py"
EXAMPLE_PROVIDER = REPO_ROOT / "examples" / "ai_providers" / "disabled_stub_provider_v0"


class ValidateAIOutputScriptTestCase(unittest.TestCase):
    def test_all_examples_plain_and_json_pass(self) -> None:
        plain = subprocess.run(
            [sys.executable, str(VALIDATOR)],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("status: valid", plain.stdout)
        self.assertIn("model_calls_performed: False", plain.stdout)

        completed = subprocess.run(
            [sys.executable, str(VALIDATOR), "--all-examples", "--json"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["passed"], 4)
        self.assertEqual(payload["failed"], 0)
        self.assertFalse(payload["model_calls_performed"])
        self.assertFalse(payload["network_performed"])
        self.assertFalse(payload["mutation_performed"])
        self.assertFalse(payload["import_performed"])

    def test_single_output_and_bundle_validation_pass(self) -> None:
        single = EXAMPLE_PROVIDER / "examples" / "alias_candidate.valid.json"
        completed = subprocess.run(
            [sys.executable, str(VALIDATOR), "--output", str(single), "--json"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertEqual(json.loads(completed.stdout)["passed"], 1)

        bundle = subprocess.run(
            [sys.executable, str(VALIDATOR), "--bundle-root", str(EXAMPLE_PROVIDER), "--json"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertEqual(json.loads(bundle.stdout)["passed"], 4)

    def test_rejects_missing_required_review(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output_path = _copy_alias_output(tmp)
            payload = json.loads(output_path.read_text(encoding="utf-8"))
            payload["required_review"] = False
            output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            result = _run_invalid(output_path)
        self.assertTrue(any("required_review must be true" in error for error in result["errors"]))

    def test_rejects_rights_clearance_and_secret_claims(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output_path = _copy_alias_output(tmp)
            payload = json.loads(output_path.read_text(encoding="utf-8"))
            payload["structured_claims"][0]["claim_value"]["rights_clearance_allowed"] = True
            payload["secret"] = "sk-testsecretvalue000"
            output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            result = _run_invalid(output_path)
        joined = "\n".join(result["errors"]).lower()
        self.assertIn("secret", joined)
        self.assertIn("rights_clearance", joined)

    def test_rejects_private_path_in_public_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output_path = _copy_alias_output(tmp)
            payload = json.loads(output_path.read_text(encoding="utf-8"))
            payload["generated_text"] = r"Candidate text mentions D:\\private\\cache\\index.sqlite3"
            output_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
            result = _run_invalid(output_path)
        self.assertTrue(any("private" in error.lower() for error in result["errors"]))


def _copy_alias_output(tmp: str) -> Path:
    output_path = Path(tmp) / "candidate.json"
    shutil.copy2(EXAMPLE_PROVIDER / "examples" / "alias_candidate.valid.json", output_path)
    return output_path


def _run_invalid(output_path: Path) -> dict[str, object]:
    completed = subprocess.run(
        [sys.executable, str(VALIDATOR), "--output", str(output_path), "--json"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    if completed.returncode == 0:
        raise AssertionError(f"Validator unexpectedly passed: {completed.stdout}")
    return json.loads(completed.stdout)


if __name__ == "__main__":
    unittest.main()
