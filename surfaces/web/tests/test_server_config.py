from __future__ import annotations

import unittest

from surfaces.web.server import WebServerConfig


class WebServerConfigTestCase(unittest.TestCase):
    def test_local_dev_defaults_allow_local_paths(self) -> None:
        config = WebServerConfig.local_dev()

        self.assertEqual(config.mode, "local_dev")
        self.assertTrue(config.allow_local_paths)
        self.assertTrue(config.allow_write_actions)
        self.assertTrue(config.allow_bundle_path_inspection)

    def test_public_alpha_config_disables_local_paths(self) -> None:
        config = WebServerConfig.public_alpha()

        self.assertEqual(config.mode, "public_alpha")
        self.assertFalse(config.allow_local_paths)
        self.assertFalse(config.allow_write_actions)
        self.assertFalse(config.allow_bundle_path_inspection)
        self.assertTrue(config.safe_mode_enabled)

    def test_invalid_mode_is_rejected(self) -> None:
        with self.assertRaises(ValueError):
            WebServerConfig(mode="production")

    def test_public_alpha_rejects_local_path_override(self) -> None:
        with self.assertRaises(ValueError):
            WebServerConfig.public_alpha(allow_local_paths=True)

    def test_environment_construction_uses_mode(self) -> None:
        config = WebServerConfig.from_environment({"EUREKA_WEB_MODE": "public_alpha"})

        self.assertEqual(config.mode, "public_alpha")
        self.assertFalse(config.allow_local_paths)


if __name__ == "__main__":
    unittest.main()
