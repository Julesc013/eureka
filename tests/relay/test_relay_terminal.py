import unittest

from runtime.relay.profiles import load_relay_policy
from runtime.relay.snapshot_store import load_snapshot_for_relay
from runtime.relay.terminal import build_terminal_menu, render_terminal_search_results


class RelayTerminalTests(unittest.TestCase):
    def setUp(self):
        self.policy = load_relay_policy()
        self.store = load_snapshot_for_relay("examples/snapshots/fixtures/search_snapshot_input_v0.json", self.policy)

    def test_render_terminal_menu_works_without_server(self):
        menu = build_terminal_menu(self.store, self.policy)
        self.assertIn("Eureka Relay Terminal", menu)
        self.assertIn("1. Search fixture snapshot", menu)
        self.assertIn("Blocked actions", menu)

    def test_terminal_search_results_preserve_posture_fields(self):
        text = render_terminal_search_results(self.store["records"], self.policy)
        self.assertIn("Source posture", text)
        self.assertIn("Evidence posture", text)
        self.assertIn("Rights posture", text)
        self.assertIn("Risk posture", text)
        self.assertIn("Action posture", text)


if __name__ == "__main__":
    unittest.main()

