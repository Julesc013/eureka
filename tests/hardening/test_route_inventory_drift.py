import re
import unittest

from surfaces.web.server.api_routes import build_api_index_document
from surfaces.web.server.route_policy import (
    PUBLIC_ALPHA_BLOCKED_API_ROUTES,
    PUBLIC_ALPHA_BLOCKED_WEB_ROUTES,
    PublicAlphaRoutePolicy,
    UNSAFE_LOCAL_PATH_PARAMETERS,
)
from surfaces.web.server.server_config import WebServerConfig
from tests.hardening.helpers import load_json, read_text


EXEMPT_API_ROUTES = set()
EXEMPT_WEB_ROUTES = {
    "/",
}


def _route_inventory_by_pattern():
    inventory = load_json("control/inventory/public_alpha_routes.json")
    return {route["route_pattern"]: route for route in inventory["routes"]}


class RouteInventoryDriftTest(unittest.TestCase):
    def test_inventory_entries_have_required_route_policy_fields(self):
        inventory = load_json("control/inventory/public_alpha_routes.json")
        classifications = {
            "safe_public_alpha",
            "blocked_public_alpha",
            "local_dev_only",
            "review_required",
            "deferred",
        }

        for entry in inventory["routes"]:
            with self.subTest(route=entry.get("route_pattern")):
                self.assertTrue(entry.get("route_pattern"))
                self.assertTrue(entry.get("method"))
                self.assertIn(entry.get("classification"), classifications)
                self.assertTrue(entry.get("surface_type"))
                self.assertIsInstance(entry.get("mode_behavior"), dict)
                self.assertIn("local_dev", entry["mode_behavior"])
                self.assertIn("public_alpha", entry["mode_behavior"])
                self.assertTrue(entry.get("reason"))

    def test_api_routes_from_index_document_are_in_inventory(self):
        config = WebServerConfig.local_dev()
        api_doc = build_api_index_document(config)
        documented_routes = {
            endpoint["path"]
            for endpoint in api_doc["endpoints"]
            if endpoint["path"].startswith("/api")
        }
        documented_routes.add("/api")
        inventory_patterns = set(_route_inventory_by_pattern())

        missing = sorted((documented_routes - inventory_patterns) - EXEMPT_API_ROUTES)
        self.assertEqual(missing, [])

    def test_static_api_route_literals_are_in_inventory(self):
        text = read_text("surfaces/web/server/api_routes.py")
        static_routes = set(re.findall(r'path\s*==\s*"(/api[^"]*)"', text))
        static_routes.update(re.findall(r'"(/api/[A-Za-z0-9_./{}-]+)"', text))
        static_routes.add("/api")
        static_routes = {route for route in static_routes if not route.endswith("/")}
        inventory_patterns = set(_route_inventory_by_pattern())

        missing = sorted((static_routes - inventory_patterns) - EXEMPT_API_ROUTES)
        self.assertEqual(missing, [])

    def test_major_web_route_literals_are_in_inventory(self):
        text = read_text("surfaces/web/server/workbench_server.py")
        web_routes = set(re.findall(r'path\s*==\s*"(/[^"]*)"', text))
        web_routes.update(re.findall(r'"(/(?:action-plan|actions|absence|compatibility|compare|decompose|evals|fetch|handoff|index|inspect|member|memories|memory|query-plan|representations|run|runs|search|source|sources|status|store|stored|subject|task|tasks)[A-Za-z0-9_./{}?-]*)"', text))
        web_routes = {route.rstrip("\\") for route in web_routes if not route.startswith("/api")}
        inventory_patterns = set(_route_inventory_by_pattern())

        missing = sorted((web_routes - inventory_patterns) - EXEMPT_WEB_ROUTES)
        self.assertEqual(missing, [])

    def test_blocked_policy_constants_match_inventory_classification(self):
        by_pattern = _route_inventory_by_pattern()

        for route in PUBLIC_ALPHA_BLOCKED_API_ROUTES:
            self.assertIn(route, by_pattern)
            self.assertIn(
                by_pattern[route]["classification"],
                {"blocked_public_alpha", "local_dev_only"},
                route,
            )

        for route in PUBLIC_ALPHA_BLOCKED_WEB_ROUTES:
            self.assertIn(route, by_pattern)
            self.assertIn(
                by_pattern[route]["classification"],
                {"blocked_public_alpha", "local_dev_only"},
                route,
            )

    def test_policy_blocks_inventory_local_path_parameters(self):
        policy = PublicAlphaRoutePolicy(WebServerConfig.public_alpha())
        inventory = load_json("control/inventory/public_alpha_routes.json")
        inventory_params = set()

        for route in inventory["routes"]:
            params = route.get("local_path_parameters", [])
            inventory_params.update(params)
            if not params or route["surface_type"] not in {"api", "status"}:
                continue
            decision = policy.evaluate_api_request(
                route["route_pattern"],
                {param: [r"D:\private\eureka-secret"] for param in params},
            )
            self.assertFalse(decision.allowed, route["route_pattern"])

        self.assertTrue(set(UNSAFE_LOCAL_PATH_PARAMETERS).issubset(inventory_params))


if __name__ == "__main__":
    unittest.main()
