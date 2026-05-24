from __future__ import annotations

import unittest

from runtime.capabilities import build_capability_profile, validate_capability_profile


class CapabilityProfileTests(unittest.TestCase):
    def test_profiles_disable_mutating_capabilities(self) -> None:
        for profile_id in ("public_api_read_only", "native_desktop_read_only", "lite_client_read_only"):
            profile = build_capability_profile(profile_id)
            self.assertEqual(validate_capability_profile(profile)["status"], "pass")
            self.assertTrue(profile["supports_read_only_search"])
            self.assertFalse(profile["supports_live_source_actions"])
            self.assertFalse(profile["supports_mutation"])
            self.assertFalse(profile["supports_download"])
            self.assertFalse(profile["supports_extraction"])


if __name__ == "__main__":
    unittest.main()
