from __future__ import annotations

import subprocess
import sys
import tempfile
from pathlib import Path
import unittest

from scripts.eureka_lan_smoke import run_lan_smoke


ROOT = Path(__file__).resolve().parents[2]


class LocalLanReadOnlyRouteTests(unittest.TestCase):
    def test_same_machine_lan_bind_smoke_passes_read_only_routes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            result = run_lan_smoke(
                instance=Path(tmp) / "eureka-instance",
                host="0.0.0.0",
                port=0,
                bind_lan=True,
                read_only=True,
            )
        self.assertIn(result["status"], {"pass", "pass_with_warnings"})
        self.assertTrue(result["bind_lan_used"])
        self.assertTrue(result["read_only_routes_passed"])
        self.assertTrue(result["same_machine_lan_bind_smoke_passed"])
        self.assertFalse(result["external_client_smoke_performed"])

    def test_lan_smoke_requires_bind_lan_for_lan_host(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(ValueError):
                run_lan_smoke(
                    instance=Path(tmp) / "eureka-instance",
                    host="0.0.0.0",
                    port=0,
                    bind_lan=False,
                    read_only=True,
                )


if __name__ == "__main__":
    unittest.main()
