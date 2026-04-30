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
            if key.lower() in {"href", "src", "action"} and value:
                self.links.append(value)


class LiveBackendHandoffContractTest(unittest.TestCase):
    def test_handoff_inventory_reserves_required_endpoints(self) -> None:
        payload = json.loads((PUBLICATION_DIR / "live_backend_handoff.json").read_text(encoding="utf-8"))

        self.assertEqual(payload["schema_version"], "0.1.0")
        self.assertEqual(payload["status"], "planned")
        self.assertEqual(payload["stability"], "experimental")
        self.assertTrue(payload["no_live_backend_implemented"])
        self.assertTrue(payload["no_deployment_performed"])
        self.assertIn("/api/v1/status", payload["endpoint_prefixes_reserved"])
        self.assertIn("/api/v1/live-probe", payload["endpoint_prefixes_reserved"])
        self.assertEqual(payload["cors_policy_status"], "unresolved")
        self.assertEqual(payload["auth_policy_status"], "unresolved")
        self.assertEqual(payload["rate_limit_policy_status"], "unresolved")

    def test_endpoint_registry_keeps_api_v1_future_only(self) -> None:
        payload = json.loads((PUBLICATION_DIR / "live_backend_routes.json").read_text(encoding="utf-8"))
        routes = {route["path_template"]: route for route in payload["routes"]}

        for endpoint in (
            "/api/v1/status",
            "/api/v1/search",
            "/api/v1/query-plan",
            "/api/v1/sources",
            "/api/v1/source/{source_id}",
            "/api/v1/evidence/{evidence_id}",
            "/api/v1/object/{object_id}",
            "/api/v1/result/{result_id}",
            "/api/v1/absence",
            "/api/v1/compare",
            "/api/v1/live-probe",
        ):
            with self.subTest(endpoint=endpoint):
                self.assertIn(endpoint, routes)
                self.assertNotIn(routes[endpoint]["status"], {"implemented", "static_demo"})
                self.assertTrue(routes[endpoint]["requires_live_backend"])

        live_probe = routes["/api/v1/live-probe"]
        self.assertEqual(live_probe["status"], "blocked")
        self.assertFalse(live_probe["public_alpha_allowed"])
        self.assertFalse(live_probe["static_handoff_allowed"])
        self.assertTrue(live_probe["live_probe_related"])

    def test_surface_capabilities_keep_live_flags_disabled(self) -> None:
        payload = json.loads((PUBLICATION_DIR / "surface_capabilities.json").read_text(encoding="utf-8"))
        capabilities = {item["id"]: item for item in payload["capabilities"]}

        self.assertEqual(capabilities["static_site"]["status"], "implemented")
        self.assertTrue(capabilities["static_site"]["enabled_by_default"])
        for capability_id in (
            "live_backend",
            "live_search",
            "live_probe_gateway",
            "internet_archive_live_probe",
        ):
            with self.subTest(capability_id=capability_id):
                self.assertFalse(capabilities[capability_id]["enabled_by_default"])
                self.assertTrue(capabilities[capability_id]["requires_backend"])
                self.assertNotIn(capabilities[capability_id]["status"], {"implemented", "static_demo"})

    def test_static_pages_do_not_link_to_api_v1(self) -> None:
        for path in PUBLIC_SITE.rglob("*.html"):
            parser = _LinkParser()
            parser.feed(path.read_text(encoding="utf-8"))
            for link in parser.links:
                with self.subTest(path=path, link=link):
                    self.assertNotIn("/api/v1", link)

    def test_docs_make_contract_only_status_explicit(self) -> None:
        handoff = (REPO_ROOT / "docs" / "reference" / "LIVE_BACKEND_HANDOFF_CONTRACT.md").read_text(encoding="utf-8").casefold()
        error = (REPO_ROOT / "docs" / "reference" / "LIVE_BACKEND_ERROR_ENVELOPE.md").read_text(encoding="utf-8").casefold()
        architecture = (REPO_ROOT / "docs" / "architecture" / "LIVE_BACKEND_HANDOFF.md").read_text(encoding="utf-8").casefold()

        self.assertIn("not a production api", handoff)
        self.assertIn("does not make `/api/v1/` live", handoff)
        self.assertIn("live_backend_unavailable", error)
        self.assertIn("not implemented backend behavior", error)
        self.assertIn("static site", architecture)
        self.assertIn("future/reserved", architecture)


if __name__ == "__main__":
    unittest.main()
