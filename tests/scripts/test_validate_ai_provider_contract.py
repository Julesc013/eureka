from __future__ import annotations

import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = REPO_ROOT / "scripts" / "validate_ai_provider_contract.py"
EXAMPLE_PROVIDER = REPO_ROOT / "examples" / "ai_providers" / "disabled_stub_provider_v0"


class ValidateAIProviderContractScriptTestCase(unittest.TestCase):
    def test_validator_passes_plain_json_and_strict(self) -> None:
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
            [sys.executable, str(VALIDATOR), "--json"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "valid")
        self.assertEqual(payload["provider_id"], "example.disabled_stub_provider_v0")
        self.assertEqual(payload["typed_output_count"], 2)
        self.assertFalse(payload["runtime_implemented"])
        self.assertFalse(payload["model_calls_performed"])
        self.assertFalse(payload["network_performed"])
        self.assertFalse(payload["telemetry_enabled"])

        strict = subprocess.run(
            [sys.executable, str(VALIDATOR), "--strict"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("status: valid", strict.stdout)

    def test_validator_rejects_default_enabled_provider(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _copy_example(tmp, "enabled_provider")
            manifest = _read_manifest(root)
            manifest["default_enabled"] = True
            _write_manifest(root, manifest)
            _write_checksums(root)
            payload = _run_invalid(root)
        self.assertTrue(any("default_enabled must be false" in error for error in payload["errors"]))

    def test_validator_rejects_remote_provider_without_credentials(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _copy_example(tmp, "remote_without_credentials")
            manifest = _read_manifest(root)
            manifest["provider_type"] = "remote_api"
            manifest["network_required"] = True
            manifest["credential_required"] = False
            _write_manifest(root, manifest)
            _write_checksums(root)
            payload = _run_invalid(root)
        self.assertTrue(any("remote_api providers must declare credential_required true" in error for error in payload["errors"]))

    def test_validator_rejects_typed_output_without_required_review(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _copy_example(tmp, "unreviewed_output")
            output_path = root / "examples" / "typed_output_alias_candidate.json"
            output = json.loads(output_path.read_text(encoding="utf-8"))
            output["required_review"] = False
            output_path.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
            _write_checksums(root)
            payload = _run_invalid(root)
        self.assertTrue(any("required_review must be true" in error for error in payload["errors"]))

    def test_validator_rejects_typed_output_without_prohibited_uses(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _copy_example(tmp, "missing_prohibited_uses")
            output_path = root / "examples" / "typed_output_alias_candidate.json"
            output = json.loads(output_path.read_text(encoding="utf-8"))
            output["prohibited_uses"] = ["canonical_truth"]
            output_path.write_text(json.dumps(output, indent=2) + "\n", encoding="utf-8")
            _write_checksums(root)
            payload = _run_invalid(root)
        self.assertTrue(any("prohibited_uses must include" in error for error in payload["errors"]))

    def test_validator_rejects_rights_clearance_output_policy(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _copy_example(tmp, "rights_clearance_allowed")
            manifest = _read_manifest(root)
            manifest["output_policy"]["rights_clearance_allowed"] = True
            _write_manifest(root, manifest)
            _write_checksums(root)
            payload = _run_invalid(root)
        self.assertTrue(any("rights_clearance_allowed must be false" in error for error in payload["errors"]))

    def test_validator_rejects_secret_like_manifest_value(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = _copy_example(tmp, "secret_manifest")
            manifest = _read_manifest(root)
            manifest["api_key"] = "sk-testsecretvalue000"
            _write_manifest(root, manifest)
            _write_checksums(root)
            payload = _run_invalid(root)
        self.assertTrue(any("secret-like" in error.lower() or "api key" in error.lower() for error in payload["errors"]))


def _copy_example(tmp: str, name: str) -> Path:
    root = Path(tmp) / name
    shutil.copytree(EXAMPLE_PROVIDER, root)
    return root


def _read_manifest(root: Path) -> dict[str, object]:
    return json.loads((root / "AI_PROVIDER.json").read_text(encoding="utf-8"))


def _write_manifest(root: Path, manifest: dict[str, object]) -> None:
    (root / "AI_PROVIDER.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")


def _write_checksums(root: Path) -> None:
    rel_paths = [
        "AI_PROVIDER.json",
        "README.md",
        "PRIVACY_AND_SAFETY.md",
        "examples/typed_output_alias_candidate.json",
        "examples/typed_output_explanation_draft.json",
    ]
    lines = []
    for rel_path in rel_paths:
        digest = hashlib.sha256((root / rel_path).read_bytes()).hexdigest()
        lines.append(f"{digest}  {rel_path}")
    (root / "CHECKSUMS.SHA256").write_text("\n".join(lines) + "\n", encoding="utf-8")


def _run_invalid(root: Path) -> dict[str, object]:
    completed = subprocess.run(
        [sys.executable, str(VALIDATOR), "--provider-root", str(root), "--json"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )
    if completed.returncode == 0:
        raise AssertionError(f"Validator unexpectedly passed: {completed.stdout}")
    return json.loads(completed.stdout)


if __name__ == "__main__":
    unittest.main()
