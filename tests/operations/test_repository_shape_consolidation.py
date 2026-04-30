from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
STATIC_ARTIFACT = REPO_ROOT / "site" / "dist"
EXTERNAL = REPO_ROOT / "external"
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "pages.yml"
PUBLICATION = REPO_ROOT / "control" / "inventory" / "publication"
GENERATED_ARTIFACTS = (
    REPO_ROOT / "control" / "inventory" / "generated_artifacts" / "generated_artifacts.json"
)
DRIFT_GUARD = REPO_ROOT / "scripts" / "check_generated_artifact_drift.py"
PAGES_CHECKER = REPO_ROOT / "scripts" / "check_github_pages_static_artifact.py"


class RepositoryShapeConsolidationTest(unittest.TestCase):
    def test_static_artifact_is_site_dist_only(self) -> None:
        legacy_static = REPO_ROOT / ("public" + "_site")
        self.assertTrue(STATIC_ARTIFACT.is_dir())
        self.assertTrue((STATIC_ARTIFACT / ".nojekyll").is_file())
        self.assertFalse((STATIC_ARTIFACT / "README.md").exists())
        self.assertFalse(legacy_static.exists())

    def test_external_reference_root_exists(self) -> None:
        legacy_external = REPO_ROOT / ("third" + "_party")
        self.assertTrue(EXTERNAL.is_dir())
        self.assertTrue((EXTERNAL / "README.md").is_file())
        for name in ("licenses", "specs", "upstream_snapshots", "references"):
            self.assertTrue((EXTERNAL / name).is_dir())
        self.assertFalse(legacy_external.exists())

    def test_pages_workflow_uploads_site_dist(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")
        self.assertIn("actions/upload-pages-artifact@v3", text)
        self.assertIn("path: site/dist", text)
        self.assertIn("python site/build.py", text)
        self.assertIn("python scripts/check_generated_artifact_drift.py --artifact static_site_dist", text)
        self.assertNotIn("path: " + ("public" + "_site"), text)

    def test_publication_inventory_names_site_dist(self) -> None:
        contract = json.loads((PUBLICATION / "publication_contract.json").read_text(encoding="utf-8"))
        targets = json.loads((PUBLICATION / "deployment_targets.json").read_text(encoding="utf-8"))
        registry = json.loads((PUBLICATION / "page_registry.json").read_text(encoding="utf-8"))
        project = next(target for target in targets["targets"] if target["id"] == "github_pages_project")

        self.assertEqual(contract["current_static_artifact"], "site/dist")
        self.assertEqual(contract["deploy_artifact_current"], "site/dist")
        self.assertEqual(project["artifact_root"], "site/dist")
        self.assertEqual(registry["artifact_root"], "site/dist")

    def test_generated_artifact_inventory_contains_static_site_dist(self) -> None:
        inventory = json.loads(GENERATED_ARTIFACTS.read_text(encoding="utf-8"))
        groups = {group["artifact_id"]: group for group in inventory["artifact_groups"]}
        group = groups["static_site_dist"]

        self.assertEqual(group["artifact_paths"][0], "site/dist")
        self.assertEqual(group["deployment_target"], "github_pages_project")
        self.assertFalse(group["manual_edits_allowed"])
        self.assertIn(
            "python scripts/check_github_pages_static_artifact.py --path site/dist",
            group["validator_commands"],
        )

    def test_drift_guard_supports_static_site_dist(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(DRIFT_GUARD), "--artifact", "static_site_dist"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("status: valid", completed.stdout)
        self.assertIn("static_site_dist: passed", completed.stdout)

    def test_pages_checker_defaults_to_site_dist(self) -> None:
        completed = subprocess.run(
            [sys.executable, str(PAGES_CHECKER), "--json"],
            cwd=REPO_ROOT,
            check=True,
            capture_output=True,
            text=True,
        )
        payload = json.loads(completed.stdout)
        self.assertEqual(payload["status"], "valid")
        self.assertTrue(payload["site_dir"].replace("\\", "/").endswith("site/dist"))


if __name__ == "__main__":
    unittest.main()
