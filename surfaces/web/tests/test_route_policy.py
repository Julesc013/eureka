from __future__ import annotations

import unittest

from surfaces.web.server import PublicAlphaRoutePolicy, WebServerConfig


class RoutePolicyTestCase(unittest.TestCase):
    def test_local_dev_allows_current_local_path_routes(self) -> None:
        policy = PublicAlphaRoutePolicy(WebServerConfig.local_dev())

        decision = policy.evaluate_api_request(
            "/api/index/status",
            {"index_path": ["D:/tmp/eureka.sqlite3"]},
        )

        self.assertTrue(decision.allowed)

    def test_public_alpha_blocks_arbitrary_local_path_parameters(self) -> None:
        policy = PublicAlphaRoutePolicy(WebServerConfig.public_alpha())

        decision = policy.evaluate_api_request(
            "/api/search",
            {"q": ["archive"], "store_root": ["D:/private/store"]},
        )

        self.assertFalse(decision.allowed)
        self.assertEqual(decision.code, "local_path_parameters_blocked")
        self.assertEqual(decision.blocked_parameters, ("store_root",))

    def test_public_alpha_allows_safe_read_only_route(self) -> None:
        policy = PublicAlphaRoutePolicy(WebServerConfig.public_alpha())

        decision = policy.evaluate_api_request("/api/search", {"q": ["archive"]})

        self.assertTrue(decision.allowed)

    def test_public_alpha_blocks_local_index_route_even_without_path(self) -> None:
        policy = PublicAlphaRoutePolicy(WebServerConfig.public_alpha())

        decision = policy.evaluate_api_request("/api/index/status", {})

        self.assertFalse(decision.allowed)
        self.assertEqual(decision.code, "route_disabled_in_public_alpha")


if __name__ == "__main__":
    unittest.main()
