from __future__ import annotations

import unittest

from runtime.public_alpha import build_public_search_ux_model_bundle


class PublicSearchUxModelTests(unittest.TestCase):
    def test_bundle_builds_search_first_view_model(self) -> None:
        bundle = build_public_search_ux_model_bundle()

        self.assertEqual("pass", bundle["status"])
        self.assertEqual("contracts/view/models/public_search", bundle["contract_authority_root"])
        self.assertTrue(bundle["search_page"]["search_first"])
        self.assertFalse(bundle["deployment_performed"])
        self.assertFalse(bundle["public_launch_performed"])


if __name__ == "__main__":
    unittest.main()
