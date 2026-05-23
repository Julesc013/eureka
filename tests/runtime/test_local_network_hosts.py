from __future__ import annotations

import unittest

from runtime.local.network import classify_client_scope, validate_service_host
from runtime.local.network.errors import LocalNetworkHostError


class LocalNetworkHostTests(unittest.TestCase):
    def test_default_hosts_are_loopback(self) -> None:
        self.assertEqual("127.0.0.1", validate_service_host("127.0.0.1"))
        self.assertEqual("localhost", validate_service_host("localhost"))
        self.assertEqual("loopback", classify_client_scope("127.0.0.1").value)

    def test_lan_hosts_require_explicit_bind_flag(self) -> None:
        for host in ("0.0.0.0", "::"):
            with self.assertRaises(LocalNetworkHostError):
                validate_service_host(host)
            self.assertEqual(host, validate_service_host(host, bind_lan=True))

    def test_arbitrary_hosts_are_rejected(self) -> None:
        for host in ("192.168.1.10", "10.0.0.5", "example.com", ""):
            with self.assertRaises(LocalNetworkHostError):
                validate_service_host(host)

    def test_client_hosts_are_classified(self) -> None:
        self.assertEqual("lan", classify_client_scope("192.168.1.20").value)
        self.assertEqual("lan", classify_client_scope("10.0.0.5").value)
        self.assertEqual("unknown", classify_client_scope("example.com").value)


if __name__ == "__main__":
    unittest.main()
