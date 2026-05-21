import unittest

from runtime.local_eval.g0_quality import PROJECTION_PROFILES, build_quality_console_view, load_quality_fixture


class G0WorkbenchConsoleTests(unittest.TestCase):
    def test_console_projections_are_read_only(self) -> None:
        fixture = load_quality_fixture("examples/search_quality/sample_quality_fixture.json")
        for profile in PROJECTION_PROFILES:
            view = build_quality_console_view(fixture, profile)
            self.assertTrue(view["read_only"])
            self.assertEqual(view["projection_profile"], profile)
            self.assertFalse(view["non_claims"]["operator_instance_mutated"])
            self.assertFalse(view["non_claims"]["master_index_mutated"])


if __name__ == "__main__":
    unittest.main()
