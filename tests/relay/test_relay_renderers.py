import json
import unittest

from runtime.relay.profiles import load_relay_policy, load_relay_profile
from runtime.relay.renderers import render_relay_lite_html, render_relay_native_fixture_json, render_relay_text
from runtime.relay.request_response import build_relay_request, build_relay_response
from runtime.relay.snapshot_store import load_snapshot_for_relay


class RelayRendererTests(unittest.TestCase):
    def setUp(self):
        self.policy = load_relay_policy()
        self.profile = load_relay_profile("examples/relay/profiles/localhost_readonly_profile_v0.json")
        self.store = load_snapshot_for_relay("examples/snapshots/fixtures/search_snapshot_input_v0.json", self.policy)

    def response_for(self, route, profile="text"):
        request = build_relay_request("GET", route, {"format": profile}, self.profile, self.policy)
        response = build_relay_response(request, self.store, self.policy)
        response["render_profile"] = profile
        return response

    def test_render_text_route_response_works_without_server(self):
        text = render_relay_text(self.response_for("/search", "text"), self.policy)
        self.assertIn("Source posture", text)
        self.assertIn("No live access", text)

    def test_render_lite_html_route_response_works_without_server(self):
        html = render_relay_lite_html(self.response_for("/search", "lite_html"), self.policy)
        self.assertIn("<!doctype html>", html)
        self.assertIn("Evidence posture", html)
        self.assertNotIn("<script", html.casefold())

    def test_native_fixture_json_response_works_without_server(self):
        payload = json.loads(render_relay_native_fixture_json(self.response_for("/search", "native_fixture_json"), self.policy))
        self.assertTrue(payload["read_only"])
        self.assertFalse(payload["download_allowed"])
        self.assertFalse(payload["action_execution_allowed"])

    def test_no_download_upload_account_telemetry_behavior_occurs(self):
        response = self.response_for("/status", "json_manifest")
        body = response["body"]
        self.assertFalse(body["downloads_enabled"])
        self.assertFalse(body["uploads_enabled"])
        self.assertFalse(body["accounts_enabled"])
        self.assertFalse(body["telemetry_enabled"])


if __name__ == "__main__":
    unittest.main()

