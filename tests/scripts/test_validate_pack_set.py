from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
VALIDATOR = REPO_ROOT / "scripts" / "validate_pack_set.py"
REGISTRY = REPO_ROOT / "control" / "inventory" / "packs" / "example_packs.json"


class ValidatePackSetScriptTestCase(unittest.TestCase):
    def test_list_examples_plain_and_json(self) -> None:
        plain = subprocess.run(
            [sys.executable, str(VALIDATOR), "--list-examples"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("Pack Set Examples", plain.stdout)
        self.assertIn("source_pack", plain.stdout)
        self.assertIn("master_index_review_queue", plain.stdout)

        completed = subprocess.run(
            [sys.executable, str(VALIDATOR), "--list-examples", "--json"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["mode"], "list_examples")
        self.assertEqual(payload["summary"]["total"], 5)
        self.assertFalse(payload["import_performed"])
        self.assertFalse(payload["staging_performed"])

    def test_all_examples_plain_and_json(self) -> None:
        plain = subprocess.run(
            [sys.executable, str(VALIDATOR), "--all-examples"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("status: passed", plain.stdout)
        self.assertIn("passed=5", plain.stdout)

        completed = subprocess.run(
            [sys.executable, str(VALIDATOR), "--all-examples", "--json"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["mode"], "all_examples")
        self.assertEqual(payload["summary"], {"total": 5, "passed": 5, "failed": 0, "unavailable": 0, "unknown_type": 0})
        self.assertFalse(payload["mutation_performed"])
        self.assertFalse(payload["import_performed"])
        self.assertFalse(payload["staging_performed"])
        self.assertFalse(payload["indexing_performed"])
        self.assertFalse(payload["network_performed"])

    def test_known_examples_alias_passes(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(VALIDATOR), "--known-examples", "--json"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertTrue(payload["ok"])
        self.assertEqual(payload["mode"], "all_examples")
        self.assertEqual(payload["summary"]["total"], 5)

    def test_each_registered_example_validates_explicitly(self) -> None:
        registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        for example in registry["examples"]:
            with self.subTest(example=example["pack_id"]):
                completed = subprocess.run(
                    [
                        sys.executable,
                        str(VALIDATOR),
                        "--pack-root",
                        example["path"],
                        "--pack-type",
                        "auto",
                        "--json",
                    ],
                    cwd=REPO_ROOT,
                    check=True,
                    capture_output=True,
                    text=True,
                )
                payload = json.loads(completed.stdout)
                self.assertTrue(payload["ok"])
                self.assertEqual(payload["summary"]["passed"], 1)
                self.assertEqual(payload["pack_results"][0]["pack_type"], example["pack_type"])

    def test_unknown_pack_type_fails_without_scanning(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "unknown"
            root.mkdir()
            (root / "README.md").write_text("not a pack\n", encoding="utf-8")
            completed = subprocess.run(
                [sys.executable, str(VALIDATOR), "--pack-root", str(root), "--json"],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
            )
        self.assertNotEqual(completed.returncode, 0)
        payload = json.loads(completed.stdout)
        self.assertFalse(payload["ok"])
        self.assertEqual(payload["summary"]["unknown_type"], 1)
        self.assertEqual(payload["pack_results"][0]["status"], "unknown_type")

    def test_type_mismatch_fails_safely(self) -> None:
        completed = subprocess.run(
            [
                sys.executable,
                str(VALIDATOR),
                "--pack-root",
                "examples/source_packs/minimal_recorded_source_pack_v0",
                "--pack-type",
                "evidence_pack",
                "--json",
            ],
            cwd=REPO_ROOT,
            capture_output=True,
            text=True,
        )
        self.assertNotEqual(completed.returncode, 0)
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["pack_results"][0]["status"], "unknown_type")
        self.assertIn("detected source_pack", payload["pack_results"][0]["stderr_excerpt"])

    def test_missing_validator_can_be_reported_unavailable(self) -> None:
        module = _load_validator_module()
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "source_like"
            root.mkdir()
            (root / "SOURCE_PACK.json").write_text("{}\n", encoding="utf-8")
            configs = dict(module.PACK_TYPE_CONFIGS)
            configs["source_pack"] = dict(configs["source_pack"])
            configs["source_pack"]["validator"] = "scripts/missing_pack_validator.py"
            result = module.validate_pack_root(root, "source_pack", configs=configs)
        self.assertEqual(result["status"], "unavailable")
        self.assertIn("missing_pack_validator.py", result["stderr_excerpt"])


def _load_validator_module():
    spec = importlib.util.spec_from_file_location("validate_pack_set", VALIDATOR)
    if spec is None or spec.loader is None:
        raise AssertionError("Unable to load validate_pack_set module.")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


if __name__ == "__main__":
    unittest.main()
