from __future__ import annotations

import json
from urllib.parse import parse_qs
import unittest

from runtime.gateway.public_api import build_demo_public_search_public_api


PRIVATE_SENTINELS = (
    "D:/private",
    "D:\\private",
    "C:/Users",
    "/home/",
    "/tmp/",
)


class PublicSearchSafetyRuntimeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.public_api = build_demo_public_search_public_api()

    def test_public_search_output_does_not_leak_private_paths(self) -> None:
        response = self.public_api.search(parse_qs("q=windows+7+apps&limit=5"))

        self.assertEqual(response.status_code, 200)
        serialized = json.dumps(response.body, sort_keys=True)
        for sentinel in PRIVATE_SENTINELS:
            self.assertNotIn(sentinel, serialized)

    def test_blocked_inputs_do_not_echo_secret_values(self) -> None:
        response = self.public_api.search(
            {
                "q": ["archive"],
                "index_path": ["D:/private/secret/index.sqlite3"],
            }
        )

        self.assertEqual(response.status_code, 400)
        serialized = json.dumps(response.body, sort_keys=True)
        self.assertEqual(response.body["error"]["code"], "local_paths_forbidden")
        self.assertEqual(response.body["error"]["parameter"], "index_path")
        self.assertNotIn("D:/private/secret", serialized)

    def test_result_actions_do_not_allow_download_install_execute_or_upload(self) -> None:
        response = self.public_api.search(parse_qs("q=firefox+xp&limit=3"))

        self.assertEqual(response.status_code, 200)
        for card in response.body["results"]:
            allowed = {entry["action_id"] for entry in card["actions"]["allowed"]}
            blocked = {entry["action_id"] for entry in card["actions"]["blocked"]}
            self.assertFalse(allowed & {"download", "install_handoff", "execute", "upload"})
            self.assertGreaterEqual(blocked, {"download", "install_handoff", "execute", "upload"})
            self.assertIn("no_malware_scan", card["limitations"])
            self.assertIn("no_rights_clearance", card["limitations"])


if __name__ == "__main__":
    unittest.main()
