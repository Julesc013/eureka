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
