from __future__ import annotations

import unittest

from runtime.local_loop import APPLY_CONFIRMATION, build_local_loop_plan, run_local_loop_temp_instance


class LocalLoopBoundaryTests(unittest.TestCase):
    def test_temp_apply_requires_token(self) -> None:
        result = run_local_loop_temp_instance(
            build_local_loop_plan("sampleproject", "TEMP_INSTANCE_PATH"),
            {"use_temp_instance": True, "apply_to_temp": True, "confirmation": APPLY_CONFIRMATION},
        )

        self.assertEqual(result["status"], "blocked")
        self.assertIn("operator token is required for temp apply", result["blocked_reasons"])

    def test_temp_apply_requires_confirmation(self) -> None:
        result = run_local_loop_temp_instance(
            build_local_loop_plan("sampleproject", "TEMP_INSTANCE_PATH"),
            {"use_temp_instance": True, "apply_to_temp": True, "operator_token": "local-dev-token"},
        )

        self.assertEqual(result["status"], "blocked")
        self.assertTrue(any("confirmation" in item for item in result["blocked_reasons"]))

    def test_public_and_native_apply_are_blocked(self) -> None:
        for projection in ("public_web", "native_desktop_read_only"):
            with self.subTest(projection=projection):
                result = run_local_loop_temp_instance(
                    build_local_loop_plan("sampleproject", "TEMP_INSTANCE_PATH", projection),
                    {
                        "use_temp_instance": True,
                        "apply_to_temp": True,
                        "operator_token": "local-dev-token",
                        "confirmation": APPLY_CONFIRMATION,
                        "projection_profile": projection,
                    },
                )
                self.assertEqual(result["status"], "blocked")
                self.assertFalse(result["operator_instance_mutated"])
                self.assertFalse(result["master_index_mutated"])


if __name__ == "__main__":
    unittest.main()
