from __future__ import annotations

import json
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = REPO_ROOT / ".github" / "workflows" / "pages.yml"
DEPLOYMENT_TARGETS = (
    REPO_ROOT / "control" / "inventory" / "publication" / "deployment_targets.json"
)
DOC = REPO_ROOT / "docs" / "operations" / "GITHUB_PAGES_DEPLOYMENT.md"
PUBLIC_SITE = REPO_ROOT / "site/dist"


class GitHubPagesDeploymentEnablementTest(unittest.TestCase):
    def test_workflow_exists_and_uses_pages_artifact_actions(self) -> None:
        self.assertTrue(WORKFLOW.exists())
        text = WORKFLOW.read_text(encoding="utf-8")

        self.assertIn("actions/configure-pages@", text)
        self.assertIn("actions/upload-pages-artifact@", text)
        self.assertIn("actions/deploy-pages@", text)
        self.assertIn("path: site/dist", text)
        self.assertIn("python scripts/generate_public_data_summaries.py --check", text)
        self.assertIn("python scripts/validate_publication_inventory.py", text)
        self.assertIn("python scripts/validate_public_static_site.py", text)
        self.assertIn("python scripts/check_github_pages_static_artifact.py", text)

    def test_workflow_permissions_and_triggers_are_pages_scoped(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8")

        self.assertIn("contents: read", text)
        self.assertIn("pages: write", text)
        self.assertIn("id-token: write", text)
        self.assertIn("workflow_dispatch:", text)
        self.assertIn("branches:", text)
        self.assertIn("- main", text)
        self.assertIn("concurrency:", text)
        self.assertIn("environment:", text)
        self.assertIn("github-pages", text)

    def test_workflow_does_not_build_or_deploy_backend(self) -> None:
        text = WORKFLOW.read_text(encoding="utf-8").casefold()

        forbidden = (
            "npm ",
            "node ",
            "yarn ",
            "pnpm ",
            "vite",
            "next build",
            "hugo",
            "jekyll",
            "mkdocs",
            "docker",
            "runtime/",
            "surfaces/",
            "python scripts/run_public_alpha_server.py",
        )
        for phrase in forbidden:
            with self.subTest(phrase=phrase):
                self.assertNotIn(phrase, text)

    def test_publication_deployment_target_records_static_pages_configuration(self) -> None:
        payload = json.loads(DEPLOYMENT_TARGETS.read_text(encoding="utf-8"))
        targets = {target["id"]: target for target in payload["targets"]}
        project = targets["github_pages_project"]

        self.assertEqual(project["status"], "implemented")
        self.assertEqual(project["kind"], "static")
        self.assertEqual(project["artifact_root"], "site/dist")
        self.assertEqual(project["base_path"], "/eureka/")
        self.assertEqual(project["deployment_workflow_path"], ".github/workflows/pages.yml")
        self.assertTrue(project["workflow_configured"])
        self.assertFalse(project["deployment_success_claimed"])
        self.assertEqual(
            project["deployment_status"],
            "workflow_configured_deployment_unverified",
        )
        self.assertTrue(project["no_backend"])
        self.assertTrue(project["no_live_probes"])
        self.assertTrue(project["no_secrets"])

    def test_deployment_docs_preserve_static_only_limits(self) -> None:
        text = DOC.read_text(encoding="utf-8").casefold()

        for phrase in (
            "static only",
            "site/dist/",
            "does not host the python backend",
            "does not enable live probes",
            "not production",
            "/eureka/",
            "no custom domain",
            "no deployment secrets",
            ".github/workflows/pages.yml",
            "python scripts/check_github_pages_static_artifact.py",
            "revert the bad commit",
            "disable pages",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, text)

    def test_no_custom_domain_config_was_added(self) -> None:
        forbidden_paths = [
            PUBLIC_SITE / "CNAME",
            REPO_ROOT / "CNAME",
            REPO_ROOT / ".github" / "CNAME",
        ]
        for path in forbidden_paths:
            with self.subTest(path=path):
                self.assertFalse(path.exists())

    def test_no_non_pages_provider_config_was_added(self) -> None:
        forbidden_paths = [
            REPO_ROOT / "vercel.json",
            REPO_ROOT / "netlify.toml",
            REPO_ROOT / "fly.toml",
            REPO_ROOT / "render.yaml",
            REPO_ROOT / "wrangler.toml",
            REPO_ROOT / "Dockerfile",
            REPO_ROOT / "docker-compose.yml",
        ]
        for path in forbidden_paths:
            with self.subTest(path=path):
                self.assertFalse(path.exists())

    def test_site_dist_contains_no_runtime_or_secret_files(self) -> None:
        forbidden_suffixes = {".py", ".pyc", ".pyo", ".sqlite", ".sqlite3", ".db"}
        forbidden_names = {".env", ".env.local", "package.json", "Dockerfile"}
        forbidden_dirs = {"runtime", "surfaces", "scripts", "control", "contracts", ".git"}

        for path in PUBLIC_SITE.rglob("*"):
            relative_parts = set(path.relative_to(PUBLIC_SITE).parts)
            with self.subTest(path=path):
                self.assertFalse(relative_parts & forbidden_dirs)
                self.assertNotIn(path.name, forbidden_names)
                if path.is_file():
                    self.assertNotIn(path.suffix.casefold(), forbidden_suffixes)


if __name__ == "__main__":
    unittest.main()
