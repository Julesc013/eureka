from __future__ import annotations

import unittest

from runtime.local.network import classify_client_scope
from scripts.eureka_lan_read_only_probe import validate_base_url


class LocalLanClientScopeTests(unittest.TestCase):
    def test_localhost_and_private_base_urls_are_allowed(self) -> None:
        self.assertEqual("http://127.0.0.1:8765", validate_base_url("http://127.0.0.1:8765"))
        self.assertEqual("http://localhost:8765", validate_base_url("http://localhost:8765"))
        self.assertEqual("http://192.168.1.10:8765", validate_base_url("http://192.168.1.10:8765"))
        self.assertEqual("lan", classify_client_scope("192.168.1.10").value)

    def test_public_and_wildcard_base_urls_are_rejected(self) -> None:
        for url in ("https://127.0.0.1:8765", "http://example.com:8765", "http://0.0.0.0:8765"):
            with self.assertRaises(ValueError):
                validate_base_url(url)


if __name__ == "__main__":
    unittest.main()
