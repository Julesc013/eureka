from __future__ import annotations

import json
from pathlib import Path
import subprocess
import tempfile
import unittest

from tools.validators.validate_path_taxonomy import validate_path_taxonomy


class PathTaxonomyValidatorTestCase(unittest.TestCase):
    def test_required_surface_family_and_forbidden_path_fail(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_policy(root / "control/policies/path_taxonomy_policy.json")
            write(root / "surfaces/web/README.md", "# Web\n")
            write(root / "release/render/render.yaml", "services: []\n")
            git_add(root)

            report = validate_path_taxonomy(root, root / "control/policies/path_taxonomy_policy.json")

        self.assertEqual(report["status"], "invalid")
        self.assertTrue(any("required taxonomy directory is missing" in item for item in report["errors"]))
        self.assertTrue(any("release/render" in item for item in report["errors"]))

    def test_known_debt_is_reported_without_failing_default_mode(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_policy(root / "control/policies/path_taxonomy_policy.json")
            for path in (
                "surfaces/api/README.md",
                "surfaces/cli/README.md",
                "surfaces/files/README.md",
                "surfaces/lite/README.md",
                "surfaces/native/README.md",
                "surfaces/text/README.md",
                "surfaces/web/README.md",
                "contracts/ai/README.md",
                "contracts/repo/root_allowlist.contract.toml",
            ):
                write(root / path, "ok\n")
            git_add(root)

            report = validate_path_taxonomy(root, root / "control/policies/path_taxonomy_policy.json")

        self.assertEqual(report["status"], "valid")
        self.assertIn("contracts/ai", report["debt_paths"])

    def test_runtime_compatibility_paths_require_marker_and_reject_code(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            payload = {
                "root_rules": {
                    "runtime": {
                        "allowed_first_level": ["source"],
                        "compatibility_first_level": ["source_cache"],
                        "compatibility_only_files": ["__init__.py", "README.md"],
                        "compatibility_required_files": ["__init__.py", "README.md"],
                    }
                },
                "forbidden_active_paths": [],
            }
            write(root / "control/policies/path_taxonomy_policy.json", json.dumps(payload))
            write(root / "runtime/source/cache/__init__.py", "ok\n")
            write(root / "runtime/source_cache/__init__.py", "shim\n")
            git_add(root)

            missing_marker = validate_path_taxonomy(root, root / "control/policies/path_taxonomy_policy.json")

            write(root / "runtime/source_cache/README.md", "compatibility shim marker\n")
            valid = validate_path_taxonomy(root, root / "control/policies/path_taxonomy_policy.json")

            write(root / "runtime/source_cache/store.py", "active implementation should not live here\n")
            offender = validate_path_taxonomy(root, root / "control/policies/path_taxonomy_policy.json")

        self.assertEqual(missing_marker["status"], "invalid")
        self.assertTrue(any("missing required marker" in item for item in missing_marker["errors"]))
        self.assertEqual(valid["status"], "valid")
        self.assertEqual(offender["status"], "invalid")
        self.assertTrue(any("non-wrapper file" in item for item in offender["errors"]))


def write_policy(path: Path) -> None:
    payload = {
        "root_rules": {
            "contracts": {
                "allowed_first_level": ["repo", "schema"],
                "known_debt_first_level": ["ai"]
            },
            "surfaces": {
                "required_first_level": ["api", "cli", "files", "lite", "native", "text", "web"],
                "allowed_first_level": ["api", "cli", "files", "lite", "native", "text", "web"],
                "known_debt_first_level": []
            }
        },
        "forbidden_active_paths": ["release/render", "surfaces/native/cli"]
    }
    write(path, json.dumps(payload))


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def git_add(root: Path) -> None:
    subprocess.run(["git", "init"], cwd=root, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    subprocess.run(["git", "add", "."], cwd=root, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
