from __future__ import annotations

from html.parser import HTMLParser
import json
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
PUBLICATION_DIR = REPO_ROOT / "control" / "inventory" / "publication"
PUBLIC_SITE = REPO_ROOT / "site/dist"


class _ScriptParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.script_count = 0
        self.links: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag.lower() == "script":
            self.script_count += 1
        for key, value in attrs:
            if key.lower() in {"href", "src", "action"} and value:
                self.links.append(value)


class CompatibilitySurfaceStrategyTest(unittest.TestCase):
    def test_strategy_and_policy_docs_exist(self) -> None:
        required = [
            "docs/architecture/COMPATIBILITY_SURFACES.md",
            "docs/reference/OLD_CLIENT_DEGRADATION_POLICY.md",
            "docs/reference/NATIVE_CLIENT_READINESS_POLICY.md",
            "docs/reference/SNAPSHOT_SURFACE_CONTRACT.md",
            "docs/reference/RELAY_SURFACE_CONTRACT.md",
        ]
        for relative in required:
            with self.subTest(relative=relative):
                self.assertTrue((REPO_ROOT / relative).exists())

        text = (REPO_ROOT / "docs" / "architecture" / "COMPATIBILITY_SURFACES.md").read_text(
            encoding="utf-8"
        )
        lowered = text.casefold()
        self.assertIn("same resolver truth, multiple projections", lowered)
        self.assertIn("does not implement new runtime product behavior", lowered)
        self.assertIn("do not make one modern web app serve every old client", lowered)

    def test_surface_capabilities_include_required_families(self) -> None:
        payload = json.loads((PUBLICATION_DIR / "surface_capabilities.json").read_text(encoding="utf-8"))
        capabilities = {item["id"]: item for item in payload["capabilities"]}
        required = {
            "app",
            "web",
            "lite",
            "text",
            "files",
            "data",
            "api",
            "snapshots",
            "relay",
            "cli",
            "native_client",
            "public_static_site",
            "public_alpha_wrapper",
            "live_backend",
            "live_probe_gateway",
        }

        self.assertLessEqual(required, set(capabilities))
        for surface_id in required:
            with self.subTest(surface_id=surface_id):
                surface = capabilities[surface_id]
                for field in (
                    "stability",
                    "client_profiles",
                    "implemented_paths",
                    "reserved_paths",
                    "supports_static_data",
                    "supports_live_data",
                    "supports_downloads",
                    "supports_private_user_state",
                    "current_limitations",
                    "next_step",
                ):
                    self.assertIn(field, surface)

    def test_surface_route_matrix_matches_current_public_roots(self) -> None:
        payload = json.loads((PUBLICATION_DIR / "surface_route_matrix.json").read_text(encoding="utf-8"))
        surfaces = {item["id"]: item for item in payload["surfaces"]}

        for surface_id, expected_path in {
            "lite": PUBLIC_SITE / "lite" / "index.html",
            "text": PUBLIC_SITE / "text" / "index.txt",
            "files": PUBLIC_SITE / "files" / "manifest.json",
            "data": PUBLIC_SITE / "data" / "site_manifest.json",
            "demo": PUBLIC_SITE / "demo" / "index.html",
        }.items():
            with self.subTest(surface_id=surface_id):
                self.assertTrue(expected_path.exists())
                self.assertTrue(surfaces[surface_id]["implemented_now"])
                self.assertFalse(surfaces[surface_id]["live_backend_required"])

        for surface_id in ("app", "api", "snapshots", "relay", "native_client"):
            with self.subTest(surface_id=surface_id):
                self.assertFalse(surfaces[surface_id]["implemented_now"])
                self.assertIn(surfaces[surface_id]["status"], {"planned", "deferred", "blocked"})

    def test_live_and_future_surfaces_remain_disabled_or_deferred(self) -> None:
        payload = json.loads((PUBLICATION_DIR / "surface_capabilities.json").read_text(encoding="utf-8"))
        capabilities = {item["id"]: item for item in payload["capabilities"]}

        for surface_id in ("live_backend", "live_probe_gateway", "api"):
            with self.subTest(surface_id=surface_id):
                self.assertFalse(capabilities[surface_id]["enabled_by_default"])
                self.assertTrue(capabilities[surface_id]["requires_backend"])
                self.assertFalse(capabilities[surface_id]["supports_live_data"])

        for surface_id in ("snapshots", "relay", "native_client"):
            with self.subTest(surface_id=surface_id):
                self.assertFalse(capabilities[surface_id]["enabled_by_default"])
                self.assertIn(capabilities[surface_id]["status"], {"planned", "deferred", "blocked"})

    def test_lite_text_files_do_not_require_javascript(self) -> None:
        for path in sorted((PUBLIC_SITE / "lite").glob("*.html")):
            parser = _ScriptParser()
            parser.feed(path.read_text(encoding="utf-8"))
            with self.subTest(path=path.name):
                self.assertEqual(parser.script_count, 0)
                for link in parser.links:
                    self.assertFalse(link.startswith("/"), link)

        self.assertTrue((PUBLIC_SITE / "text" / "index.txt").exists())
        self.assertTrue((PUBLIC_SITE / "files" / "SHA256SUMS").exists())

    def test_static_pages_do_not_claim_future_surfaces_implemented(self) -> None:
        combined = "\n".join(
            path.read_text(encoding="utf-8").casefold()
            for path in [
                PUBLIC_SITE / "status.html",
                PUBLIC_SITE / "limitations.html",
                PUBLIC_SITE / "roadmap.html",
                PUBLIC_SITE / "lite" / "index.html",
                PUBLIC_SITE / "text" / "index.txt",
                PUBLIC_SITE / "files" / "README.txt",
            ]
        )
        self.assertIn("compatibility surface strategy", combined)
        self.assertIn("snapshots", combined)
        self.assertIn("future", combined)
        self.assertNotIn("snapshots are implemented", combined)
        self.assertNotIn("relay is implemented", combined)
        self.assertNotIn("native clients are implemented", combined)


if __name__ == "__main__":
    unittest.main()
