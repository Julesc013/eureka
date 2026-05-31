from __future__ import annotations

import unittest

from runtime.public_alpha import smoke_public_alpha_routes_from_examples


class PublicAlphaReassessRouteTests(unittest.TestCase):
    def test_route_smoke_uses_examples_only(self) -> None:
        smoke = smoke_public_alpha_routes_from_examples()

        self.assertEqual("pass", smoke["route_smoke_status"])
        self.assertEqual(6, smoke["public_routes_smoked"])
        self.assertEqual(7, smoke["public_api_routes_smoked"])
        self.assertFalse(smoke["deployment_performed"])
        self.assertFalse(smoke["live_network_used"])


if __name__ == "__main__":
    unittest.main()
