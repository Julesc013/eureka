import unittest

from runtime.local.eval.g0_quality import build_quality_console_view, load_quality_fixture


class G0FoundationTests(unittest.TestCase):
    def test_fixture_loads_and_console_is_read_only(self) -> None:
        fixture = load_quality_fixture("examples/search/quality/sample_quality_fixture.json")
        self.assertEqual(fixture["schema_version"], "g0_quality_fixture.v0")
        self.assertGreaterEqual(len(fixture["records"]), 8)
        view = build_quality_console_view(fixture, "operator_workbench")
        self.assertTrue(view["read_only"])
        self.assertFalse(view["accepted_truth"])
        self.assertFalse(view["non_claims"]["model_provider_used"])


if __name__ == "__main__":
    unittest.main()
