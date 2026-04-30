from __future__ import annotations

import json
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]


class LocalPublicSearchRuntimeOperationTest(unittest.TestCase):
    def test_route_and_safety_inventories_record_local_runtime_only(self) -> None:
        routes = _load_json("control/inventory/publication/public_search_routes.json")
        safety = _load_json("control/inventory/publication/public_search_safety.json")

        self.assertTrue(routes["implemented_now"])
        self.assertTrue(routes["runtime_routes_implemented"])
        self.assertEqual(routes["implementation_scope"], "local_prototype_backend")
        self.assertFalse(routes["hosted_public_runtime_implemented"])
        self.assertFalse(routes["static_handoff_implemented"])
        self.assertTrue(safety["local_public_search_runtime_implemented"])
        self.assertFalse(safety["hosted_public_search_runtime_implemented"])
        self.assertFalse(safety["rate_limit_policy"]["runtime_middleware_implemented"])

    def test_public_alpha_inventory_includes_safe_v1_routes(self) -> None:
        inventory = _load_json("control/inventory/public_alpha_routes.json")
        by_path = {route["route_pattern"]: route for route in inventory["routes"]}
        for route in (
            "/search",
            "/api/v1/status",
            "/api/v1/search",
            "/api/v1/query-plan",
            "/api/v1/sources",
            "/api/v1/source/{source_id}",
        ):
            self.assertIn(route, by_path)
            self.assertEqual(by_path[route]["classification"], "safe_public_alpha")
            self.assertEqual(by_path[route]["local_path_parameters"], [])
            self.assertEqual(by_path[route]["mode_behavior"]["public_alpha"], "allowed")

    def test_docs_describe_local_not_hosted_public_search(self) -> None:
        text = (
            (REPO_ROOT / "docs/reference/PUBLIC_SEARCH_API_CONTRACT.md").read_text(encoding="utf-8")
            + "\n"
            + (REPO_ROOT / "docs/operations/PUBLIC_SEARCH_LOCAL_INDEX_ONLY_MODE.md").read_text(encoding="utf-8")
        )
        folded = text.casefold()
        self.assertIn("local public search runtime v0", folded)
        self.assertIn("local/prototype backend runtime only", folded)
        self.assertIn("not hosted public deployment", folded)
        self.assertNotIn("public search is hosted", folded)


def _load_json(relative_path: str) -> dict[str, object]:
    return json.loads((REPO_ROOT / relative_path).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
