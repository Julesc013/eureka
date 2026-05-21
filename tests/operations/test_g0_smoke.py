import json
import subprocess
import sys
import unittest


class G0SmokeTests(unittest.TestCase):
    def test_smoke_all_projections(self) -> None:
        fixture = "examples/search_quality/sample_quality_fixture.json"
        for projection in ("operator_workbench", "public_web", "native_desktop_read_only"):
            completed = subprocess.run(
                [sys.executable, "scripts/eureka_g0_smoke.py", "--fixture", fixture, "--projection", projection, "--json"],
                capture_output=True,
                text=True,
                check=True,
            )
            payload = json.loads(completed.stdout)
            self.assertEqual(payload["status"], "pass")
            self.assertTrue(payload["read_only"])
            self.assertFalse(payload["model_provider_used"])


if __name__ == "__main__":
    unittest.main()
