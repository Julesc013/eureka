import unittest

from runtime.relay.profiles import (
    load_relay_policy,
    load_relay_profile,
    validate_old_browser_profile,
    validate_relay_profile,
    validate_terminal_profile,
)
from runtime.relay.routes import build_relay_route_table, match_relay_route, validate_relay_route
from runtime.relay.security import validate_method_allowed, validate_no_write_route


class RelayProfilesRoutesTests(unittest.TestCase):
    def setUp(self):
        self.policy = load_relay_policy()

    def test_relay_profile_validates(self):
        profile = load_relay_profile("examples/relay/profiles/localhost_readonly_profile_v0.json")
        self.assertEqual(validate_relay_profile(profile, self.policy), [])

    def test_old_browser_profile_validates(self):
        profile = load_relay_profile("examples/relay/profiles/old_browser_html32_profile_v0.json")
        self.assertEqual(validate_old_browser_profile(profile, self.policy), [])

    def test_terminal_profile_validates(self):
        profile = load_relay_profile("examples/relay/profiles/terminal_text_profile_v0.json")
        self.assertEqual(validate_terminal_profile(profile, self.policy), [])

    def test_native_fixture_profile_validates(self):
        profile = load_relay_profile("examples/relay/profiles/native_fixture_profile_v0.json")
        self.assertEqual(validate_relay_profile(profile, self.policy), [])

    def test_route_table_validates(self):
        profile = load_relay_profile("examples/relay/profiles/localhost_readonly_profile_v0.json")
        routes = build_relay_route_table(profile, self.policy)
        self.assertGreaterEqual(len(routes), 10)
        for route in routes:
            self.assertEqual(validate_relay_route(route, self.policy), [])

    def test_get_route_allowed(self):
        self.assertEqual(validate_method_allowed("GET", self.policy), [])
        route = match_relay_route("/search", self.policy)
        self.assertEqual(route["route_kind"], "search")

    def test_post_put_patch_delete_blocked(self):
        for method in ("POST", "PUT", "PATCH", "DELETE"):
            self.assertTrue(validate_method_allowed(method, self.policy))

    def test_admin_upload_download_execute_routes_blocked(self):
        for route in ("/admin", "/upload", "/download", "/execute"):
            self.assertTrue(validate_no_write_route(route, self.policy))


if __name__ == "__main__":
    unittest.main()

