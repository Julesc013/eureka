from __future__ import annotations

import unittest

from runtime.local_network import build_firewall_warning, build_lan_warning, validate_lan_mode_safe, validate_lan_read_only_route, validate_no_lan_mutation
from runtime.local_network.errors import LocalNetworkPolicyError, LocalNetworkSafetyError


class LocalNetworkSafetyTests(unittest.TestCase):
    def test_warnings_are_visible(self) -> None:
        self.assertIn("read-only", build_lan_warning())
        self.assertIn("firewall", build_firewall_warning().lower())

    def test_lan_mode_must_stay_read_only(self) -> None:
        self.assertEqual({"bind_lan": True, "read_only": True}, validate_lan_mode_safe({"bind_lan": True, "read_only": True}))
        with self.assertRaises(LocalNetworkSafetyError):
            validate_lan_mode_safe({"bind_lan": True, "read_only": False})

    def test_lan_mutations_are_rejected(self) -> None:
        with self.assertRaises(LocalNetworkPolicyError):
            validate_no_lan_mutation("POST", "/rebuild", "lan")
        validate_no_lan_mutation("POST", "/rebuild", "loopback")

    def test_lan_read_only_validation(self) -> None:
        self.assertEqual("/status", validate_lan_read_only_route("GET", "/status"))
        with self.assertRaises(LocalNetworkPolicyError):
            validate_lan_read_only_route("GET", "/review")


if __name__ == "__main__":
    unittest.main()
