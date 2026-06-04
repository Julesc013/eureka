from __future__ import annotations

import unittest

from runtime.surface.capabilities import negotiate_surface_profile


class SurfaceCapabilityNegotiationTests(unittest.TestCase):
    def test_explicit_safe_profile_wins(self) -> None:
        decision = negotiate_surface_profile(requested_profile="text_v0")

        self.assertEqual(decision.representation_profile, "text_v0")
        self.assertFalse(decision.fallback_used)

    def test_accept_header_can_select_json(self) -> None:
        decision = negotiate_surface_profile(accept_header="application/json")

        self.assertEqual(decision.representation_profile, "json_v0")
        self.assertEqual(decision.reason, "accept_header")

    def test_unknown_profile_falls_back_to_safe_default(self) -> None:
        decision = negotiate_surface_profile(requested_profile="immersive_canvas_v9")

        self.assertEqual(decision.representation_profile, "html_basic_v0")
        self.assertTrue(decision.fallback_used)
        self.assertEqual(decision.reason, "unsupported_profile_fallback")


if __name__ == "__main__":
    unittest.main()
