from __future__ import annotations

import json
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
PUBLICATION_DIR = REPO_ROOT / "control" / "inventory" / "publication"
PUBLIC_SITE = REPO_ROOT / "site/dist"

REQUIRED_PROTOCOLS = {
    "local_static_http",
    "local_text_http",
    "local_file_tree_http",
    "read_only_ftp_mirror",
    "webdav_read_only",
    "smb_read_only",
    "afp_read_only",
    "nfs_read_only",
    "gopher_experimental",
    "native_sidecar",
    "snapshot_mount",
}
SUSPECT_FILENAMES = {
    "relay_server.py",
    "ftp_server.py",
    "smb_server.py",
    "webdav_server.py",
    "gopher_server.py",
    "local_http_relay.py",
    "protocol_proxy.py",
}


def load_json(relative: str) -> dict:
    return json.loads((REPO_ROOT / relative).read_text(encoding="utf-8"))


class RelaySurfaceDesignTest(unittest.TestCase):
    def test_relay_surface_inventory_is_design_only(self) -> None:
        payload = load_json("control/inventory/publication/relay_surface.json")

        self.assertEqual(payload["status"], "design_only")
        self.assertTrue(payload["no_relay_implemented"])
        self.assertTrue(payload["no_network_services_implemented"])
        self.assertTrue(payload["no_protocol_servers_implemented"])
        self.assertTrue(payload["public_data_only_by_default"])
        self.assertTrue(payload["private_data_disabled_by_default"])
        self.assertTrue(payload["write_actions_disabled_by_default"])
        self.assertTrue(payload["live_probes_disabled_by_default"])
        self.assertTrue(payload["admin_routes_disabled_for_old_clients"])

    def test_protocol_candidates_are_future_deferred(self) -> None:
        payload = load_json("control/inventory/publication/relay_surface.json")
        candidates = {item["id"]: item for item in payload["future_protocol_candidates"]}

        self.assertLessEqual(REQUIRED_PROTOCOLS, set(candidates))
        for protocol_id, candidate in candidates.items():
            with self.subTest(protocol_id=protocol_id):
                self.assertEqual(candidate["status"], "future_deferred")
                self.assertFalse(candidate["implemented"])

    def test_relay_docs_and_operator_checklist_exist(self) -> None:
        for relative in (
            "docs/architecture/RELAY_SURFACE.md",
            "docs/reference/RELAY_SURFACE_CONTRACT.md",
            "docs/reference/RELAY_SECURITY_AND_PRIVACY.md",
            "docs/operations/RELAY_OPERATOR_CHECKLIST.md",
        ):
            with self.subTest(relative=relative):
                text = (REPO_ROOT / relative).read_text(encoding="utf-8").casefold()
                self.assertIn("relay", text)
                self.assertIn("future", text)

        checklist = (REPO_ROOT / "docs" / "operations" / "RELAY_OPERATOR_CHECKLIST.md").read_text(
            encoding="utf-8"
        ).casefold()
        self.assertIn("future/unsigned", checklist)
        self.assertIn("confirm no private data exposure", checklist)

    def test_surface_matrices_keep_relay_future(self) -> None:
        capabilities = load_json("control/inventory/publication/surface_capabilities.json")
        relay = {item["id"]: item for item in capabilities["capabilities"]}["relay"]

        self.assertIn(relay["status"], {"planned", "deferred", "blocked", "design_only"})
        self.assertFalse(relay["enabled_by_default"])
        self.assertFalse(relay["supports_live_data"])
        self.assertFalse(relay["supports_downloads"])
        self.assertFalse(relay["supports_private_user_state"])

        matrix = load_json("control/inventory/publication/surface_route_matrix.json")
        route = {item["id"]: item for item in matrix["surfaces"]}["relay"]
        self.assertFalse(route["implemented_now"])
        self.assertEqual(route["route_roots"], [])
        self.assertEqual(route["implemented_paths"], [])

    def test_static_pages_do_not_claim_relay_runtime(self) -> None:
        combined = "\n".join(
            path.read_text(encoding="utf-8").casefold()
            for path in (
                PUBLIC_SITE / "status.html",
                PUBLIC_SITE / "limitations.html",
                PUBLIC_SITE / "roadmap.html",
                PUBLIC_SITE / "lite" / "index.html",
                PUBLIC_SITE / "text" / "index.txt",
                PUBLIC_SITE / "files" / "README.txt",
            )
        )

        self.assertNotIn("relay is implemented", combined)
        self.assertNotIn("relay server is available", combined)
        self.assertNotIn("relay runtime is running", combined)

    def test_no_obvious_relay_server_scripts_are_added(self) -> None:
        for filename in SUSPECT_FILENAMES:
            with self.subTest(filename=filename):
                matches = [
                    path
                    for path in REPO_ROOT.rglob(filename)
                    if ".git" not in path.parts
                ]
                self.assertEqual(matches, [])


if __name__ == "__main__":
    unittest.main()
