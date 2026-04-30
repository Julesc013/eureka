from __future__ import annotations

from html.parser import HTMLParser
import json
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
PUBLICATION_DIR = REPO_ROOT / "control" / "inventory" / "publication"
PUBLIC_SITE = REPO_ROOT / "site/dist"


class _LinkParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        for key, value in attrs:
            if key.lower() in {"href", "src"} and value:
                self.links.append(value)


class CustomDomainAlternateHostReadinessTest(unittest.TestCase):
    def test_domain_plan_records_future_unsigned_state(self) -> None:
        plan = json.loads((PUBLICATION_DIR / "domain_plan.json").read_text(encoding="utf-8"))

        self.assertEqual(plan["schema_version"], "0.1.0")
        self.assertEqual(plan["status"], "planned")
        self.assertTrue(plan["no_domain_configured"])
        self.assertTrue(plan["no_dns_changes_performed"])
        self.assertTrue(plan["no_cname_file_committed"])
        self.assertEqual(plan["custom_domain_status"], "future")
        self.assertEqual(plan["custom_domain_static_status"], "future")
        self.assertTrue(plan["domain_verification_required"])
        self.assertEqual(plan["base_path_transition"]["from"], "/eureka/")
        self.assertEqual(plan["base_path_transition"]["to"], "/")
        self.assertIn("custom domain configured", plan["prohibited_claims"])

    def test_static_hosting_targets_are_future_except_project_pages(self) -> None:
        payload = json.loads((PUBLICATION_DIR / "static_hosting_targets.json").read_text(encoding="utf-8"))
        targets = {target["id"]: target for target in payload["targets"]}

        project = targets["github_pages_project"]
        self.assertEqual(project["status"], "implemented")
        self.assertEqual(project["base_path"], "/eureka/")
        self.assertEqual(project["artifact_root"], "site/dist")
        self.assertFalse(project["backend_supported"])
        self.assertFalse(project["live_probes_supported"])
        self.assertFalse(project["deployment_success_claimed"])

        custom = targets["github_pages_custom_domain"]
        self.assertEqual(custom["status"], "future")
        self.assertEqual(custom["base_path"], "/")
        self.assertTrue(custom["requires_domain_verification"])
        self.assertTrue(custom["dns_config_not_in_repo"])
        self.assertFalse(custom["provider_config_committed"])

        self.assertEqual(targets["cloudflare_pages_static"]["status"], "future")
        self.assertEqual(targets["generic_static_host"]["status"], "future")
        self.assertEqual(targets["local_file_preview"]["base_path"], "relative")

    def test_no_cname_dns_or_provider_config_exists(self) -> None:
        forbidden = [
            REPO_ROOT / "CNAME",
            PUBLIC_SITE / "CNAME",
            REPO_ROOT / "wrangler.toml",
            REPO_ROOT / "vercel.json",
            REPO_ROOT / "netlify.toml",
            REPO_ROOT / "render.yaml",
            REPO_ROOT / "fly.toml",
            REPO_ROOT / ".cloudflare",
            REPO_ROOT / ".vercel",
        ]
        for path in forbidden:
            with self.subTest(path=path):
                self.assertFalse(path.exists())

    def test_site_dist_links_remain_relative(self) -> None:
        for path in PUBLIC_SITE.rglob("*.html"):
            parser = _LinkParser()
            parser.feed(path.read_text(encoding="utf-8"))
            for link in parser.links:
                with self.subTest(path=path, link=link):
                    self.assertFalse(link.startswith("/"), link)
                    self.assertFalse(link.startswith("https://julesc013.github.io/"), link)

    def test_docs_preserve_no_configuration_claims(self) -> None:
        readiness = (REPO_ROOT / "docs" / "operations" / "CUSTOM_DOMAIN_AND_ALTERNATE_HOST_READINESS.md").read_text(encoding="utf-8").casefold()
        checklist = (REPO_ROOT / "docs" / "operations" / "CUSTOM_DOMAIN_OPERATOR_CHECKLIST.md").read_text(encoding="utf-8").casefold()
        base_path = (REPO_ROOT / "docs" / "reference" / "BASE_PATH_PORTABILITY.md").read_text(encoding="utf-8").casefold()

        for phrase in (
            "no custom domain configured",
            "no dns changes",
            "no `site/dist/cname` file",
            "no backend hosting",
            "no live source probing",
            "/eureka/",
        ):
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, readiness)
        self.assertIn("status: unsigned/future", checklist)
        self.assertIn("root-relative", base_path)
        self.assertIn("relative", base_path)


if __name__ == "__main__":
    unittest.main()
