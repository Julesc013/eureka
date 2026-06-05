from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "validate_repo_structure_canon.py"


class RepoStructureCanonValidatorScriptTest(unittest.TestCase):
    def test_validator_plain_passes(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT)],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertIn("status: valid", completed.stdout)
        self.assertIn("native_root: canonical", completed.stdout)
        self.assertIn("known_debt_count:", completed.stdout)

    def test_validator_json_records_canon_and_resolved_debt(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), "--json"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)

        self.assertEqual(payload["status"], "valid")
        self.assertEqual(payload["errors"], [])
        self.assertEqual(payload["native_root"]["status"], "canonical")
        self.assertTrue(payload["native_root_canonical"])
        self.assertFalse(payload["surfaces_native_supersedes_native"])
        self.assertTrue(payload["tools_root_allowed"])
        self.assertTrue(payload["release_root_allowed"])
        self.assertTrue(payload["archive_root_allowed"])
        self.assertEqual(
            {"tools", "release", "archive"},
            set(payload["top_level"]["optional_roots"]),
        )

        self.assertEqual(payload["top_level"]["classified_debt"], {})

        debt_paths = {item["path"] for item in payload["known_debt"]}
        self.assertEqual(debt_paths, {"scripts"})
        script_debt = next(item for item in payload["known_debt"] if item["path"] == "scripts")
        self.assertEqual(script_debt["debt_id"], "scripts_large_tool_tree")
        self.assertEqual(script_debt["class"], "thin_wrapper_root_with_substantive_tools")

        script_wrappers = payload["naming"]["script_wrappers"]
        self.assertGreater(script_wrappers["wrapper_count"], 100)
        self.assertGreater(script_wrappers["non_wrapper_count"], 0)

        accepted = set(payload["generated_artifacts"]["accepted_exact_exceptions"])
        self.assertIn("site/dist", accepted)
        self.assertIn("snapshots/examples/static_snapshot_v0", accepted)
        self.assertIn("site/dist/data/public_index", accepted)
        self.assertIn(".aide/generated", accepted)

    def test_validator_strict_passes_after_reconcile(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), "--strict", "--json"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)

        self.assertEqual(payload["status"], "valid")
        self.assertEqual(payload["warnings"], [])

    def test_validator_rejects_unclassified_src(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(SCRIPT), "--json"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)

        self.assertEqual(payload["naming"]["unclassified_src_paths"], [])
        self.assertIn("crates/*/src/**", payload["naming"]["allowed_src_exceptions"])


if __name__ == "__main__":
    unittest.main()
