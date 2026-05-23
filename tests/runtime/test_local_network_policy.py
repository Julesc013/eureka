from __future__ import annotations

import unittest

from runtime.local.network import is_mutation_allowed_for_scope, is_route_allowed_for_scope, load_lan_policy


class LocalNetworkPolicyTests(unittest.TestCase):
    def test_policy_loads(self) -> None:
        policy = load_lan_policy()
        self.assertEqual("local_lan_route_policy.v0", policy["schema_version"])

    def test_lan_read_only_routes_are_allowed(self) -> None:
        for path in ("/", "/status", "/health", "/search", "/object/record-1", "/source/source-1", "/absence", "/api/v1/status"):
            self.assertTrue(is_route_allowed_for_scope("GET", path, "lan"), path)

    def test_lan_review_rebuild_routes_are_blocked(self) -> None:
        for method, path in (("GET", "/review"), ("GET", "/rebuild"), ("POST", "/review/rvi/decision"), ("POST", "/rebuild")):
            self.assertFalse(is_route_allowed_for_scope(method, path, "lan"), path)

    def test_lan_unsafe_route_classes_are_blocked(self) -> None:
        for path in ("/api/v1/source-probe", "/workers/run", "/api/v1/extraction", "/api/v1/download", "/api/v1/install-execute"):
            self.assertFalse(is_route_allowed_for_scope("GET", path, "lan"), path)

    def test_loopback_operator_mutations_remain_possible_for_token_gate(self) -> None:
        self.assertTrue(is_mutation_allowed_for_scope("POST", "/rebuild", "loopback"))
        self.assertTrue(is_mutation_allowed_for_scope("POST", "/review/rvi/decision", "loopback"))
        self.assertFalse(is_mutation_allowed_for_scope("POST", "/rebuild", "lan"))


if __name__ == "__main__":
    unittest.main()
