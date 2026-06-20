from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from runtime.local.portable_instance import (
    PortableInstanceError,
    bootstrap_command,
    build_portable_paths,
    hunt_command,
    replay_command,
    serve_command,
    status_command,
    test_command,
)


class PortableEurekaInstanceE2ETests(unittest.TestCase):
    def test_hunt_replay_status_and_serve_smoke(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "portable eureka"
            bootstrap = bootstrap_command(instance=root)
            self.assertEqual(bootstrap["status"], "pass")

            hunt = hunt_command("old blue FTP client for XP", instance=root)
            self.assertEqual(hunt["status"], "pass")
            self.assertEqual(hunt["mode"], "synthetic")
            self.assertFalse(hunt["provider_network_calls"])
            self.assertTrue((build_portable_paths(root).run_bundles / hunt["run_id"]).is_dir())

            replay = replay_command(instance=root, run_id=hunt["run_id"], strict=True)
            self.assertEqual(replay["status"], "pass")
            self.assertFalse(replay["review_or_index_mutation"])

            status = status_command(instance=root)
            self.assertEqual(status["status"], "pass")
            self.assertGreaterEqual(status["run_bundles"]["valid"], 1)

            smoke = serve_command(instance=root, port=0, smoke=True, json_output=True)
            self.assertEqual(smoke["status"], "pass")
            self.assertTrue(all(item["ok"] for item in smoke["smoke"]["endpoints"]))
            self.assertFalse(build_portable_paths(root).server_lock.exists())

    def test_live_shadow_and_path_traversal_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "portable"
            bootstrap_command(instance=root, no_demo=True)
            with self.assertRaises(PortableInstanceError):
                hunt_command("query", instance=root, mode="live-shadow")
            with self.assertRaises(PortableInstanceError):
                replay_command(instance=root, run_id="../escape")

    def test_oracle_case_writes_under_instance_eval_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "portable"
            bootstrap_command(instance=root, no_demo=True)
            result = test_command(instance=root, case="boundary_privacy_canaries")
            self.assertEqual(result["status"], "pass")
            self.assertTrue(str(result["result_path"]).startswith("run/e2e-reference/eval/"))
            self.assertFalse(result["full_unittest_discovery"])
            self.assertFalse(result["oracle"]["network_provider_calls"])


if __name__ == "__main__":
    unittest.main()
