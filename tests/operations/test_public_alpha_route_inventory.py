from __future__ import annotations

import json
from pathlib import Path
import unittest

from surfaces.web.server.api_routes import build_api_index_document
from surfaces.web.server.route_policy import (
    PUBLIC_ALPHA_BLOCKED_API_ROUTES,
    PUBLIC_ALPHA_BLOCKED_WEB_ROUTES,
    UNSAFE_LOCAL_PATH_PARAMETERS,
)
from surfaces.web.server.server_config import WebServerConfig


REPO_ROOT = Path(__file__).resolve().parents[2]
INVENTORY_PATH = REPO_ROOT / "control" / "inventory" / "public_alpha_routes.json"
REQUIRED_ROUTE_FIELDS = {
    "route_pattern",
    "method",
    "surface_type",
    "classification",
    "mode_behavior",
    "reason",
    "local_path_parameters",
    "write_read_behavior",
    "notes",
    "owning_module",
}
CLASSIFICATIONS = {
    "safe_public_alpha",
    "blocked_public_alpha",
    "local_dev_only",
    "review_required",
    "deferred",
}
BLOCKED_CLASSIFICATIONS = {"blocked_public_alpha", "local_dev_only"}
KNOWN_WEB_ROUTES = {
    "/",
    "/status",
    "/absence/resolve",
    "/absence/search",
    "/compare",
    "/compatibility",
    "/decompose",
    "/evals/archive-resolution",
    "/fetch",
    "/member",
    "/query-plan",
    "/action-plan",
    "/handoff",
    "/index/build",
    "/index/search",
    "/index/status",
    "/memories",
    "/memory",
    "/memory/create",
    "/representations",
    "/task",
    "/task/run/build-local-index",
    "/task/run/query-local-index",
    "/task/run/validate-archive-resolution-evals",
    "/task/run/validate-source-registry",
    "/tasks",
    "/run",
    "/run/resolve",
    "/run/search",
    "/run/planned-search",
    "/source",
    "/sources",
    "/runs",
    "/subject",
    "/search",
    "/inspect/bundle",
    "/actions/export-resolution-manifest",
    "/actions/export-resolution-bundle",
    "/store/manifest",
    "/store/bundle",
    "/stored/artifact",
}


class PublicAlphaRouteInventoryTestCase(unittest.TestCase):
    def test_inventory_parses_and_routes_have_required_fields(self) -> None:
        inventory = _load_inventory()

        self.assertEqual(inventory["inventory_kind"], "eureka.public_alpha_routes")
        self.assertEqual(
            set(inventory["local_path_parameter_names"]),
            set(UNSAFE_LOCAL_PATH_PARAMETERS),
        )
        self.assertIsInstance(inventory["routes"], list)
        self.assertGreater(len(inventory["routes"]), 0)

        route_patterns: set[str] = set()
        for route in inventory["routes"]:
            self.assertTrue(REQUIRED_ROUTE_FIELDS.issubset(route), route)
            self.assertIn(route["classification"], CLASSIFICATIONS)
            self.assertEqual(route["method"], "GET")
            self.assertIn(route["surface_type"], {"html", "api", "status", "debug/demo"})
            self.assertIsInstance(route["local_path_parameters"], list)
            self.assertIsInstance(route["mode_behavior"], dict)
            self.assertIn(route["mode_behavior"].get("local_dev"), {"allowed", "blocked"})
            self.assertIn(route["mode_behavior"].get("public_alpha"), {"allowed", "blocked"})
            self.assertNotIn(route["route_pattern"], route_patterns)
            route_patterns.add(route["route_pattern"])

    def test_public_alpha_safe_routes_do_not_declare_local_path_parameters(self) -> None:
        for route in _load_inventory()["routes"]:
            if route["classification"] != "safe_public_alpha":
                continue
            self.assertEqual(route["mode_behavior"]["public_alpha"], "allowed")
            self.assertEqual(route["local_path_parameters"], [], route["route_pattern"])

    def test_local_path_parameter_routes_are_blocked_or_local_dev_only(self) -> None:
        unsafe_names = set(UNSAFE_LOCAL_PATH_PARAMETERS)
        for route in _load_inventory()["routes"]:
            if not (set(route["local_path_parameters"]) & unsafe_names):
                continue
            self.assertIn(route["classification"], BLOCKED_CLASSIFICATIONS, route)
            self.assertEqual(route["mode_behavior"]["public_alpha"], "blocked", route)

    def test_inventory_covers_known_policy_blocked_routes(self) -> None:
        indexed = _routes_by_base_pattern()

        for route in PUBLIC_ALPHA_BLOCKED_API_ROUTES | PUBLIC_ALPHA_BLOCKED_WEB_ROUTES:
            self.assertIn(route, indexed)
            classifications = {item["classification"] for item in indexed[route]}
            self.assertTrue(classifications <= BLOCKED_CLASSIFICATIONS, route)
            self.assertTrue(
                all(item["mode_behavior"]["public_alpha"] == "blocked" for item in indexed[route]),
                route,
            )

    def test_inventory_covers_current_api_and_html_routes(self) -> None:
        indexed = _routes_by_base_pattern()
        api_routes = {
            endpoint["path"]
            for endpoint in build_api_index_document(WebServerConfig.local_dev())["endpoints"]
        }
        api_routes.add("/api")

        for route in api_routes | KNOWN_WEB_ROUTES:
            self.assertIn(route, indexed, route)

    def test_readiness_docs_reference_inventory_and_smoke(self) -> None:
        readiness = (
            REPO_ROOT
            / "docs"
            / "operations"
            / "PUBLIC_ALPHA_READINESS_REVIEW.md"
        ).read_text(encoding="utf-8")
        checklist = (
            REPO_ROOT
            / "docs"
            / "operations"
            / "PUBLIC_ALPHA_OPERATOR_CHECKLIST.md"
        ).read_text(encoding="utf-8")

        self.assertIn("control/inventory/public_alpha_routes.json", readiness)
        self.assertIn("python scripts/public_alpha_smoke.py", readiness)
        self.assertIn("control/inventory/public_alpha_routes.json", checklist)
        self.assertIn("python scripts/public_alpha_smoke.py --json", checklist)


def _load_inventory() -> dict[str, object]:
    return json.loads(INVENTORY_PATH.read_text(encoding="utf-8"))


def _routes_by_base_pattern() -> dict[str, list[dict[str, object]]]:
    indexed: dict[str, list[dict[str, object]]] = {}
    for route in _load_inventory()["routes"]:
        if not isinstance(route, dict):
            raise AssertionError(f"Route inventory entry must be an object: {route!r}")
        base_pattern = str(route["route_pattern"]).split("?", 1)[0]
        indexed.setdefault(base_pattern, []).append(route)
    return indexed


if __name__ == "__main__":
    unittest.main()
