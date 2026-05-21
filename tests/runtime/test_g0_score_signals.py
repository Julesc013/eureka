import unittest

from runtime.local_eval.g0_quality import build_score_breakdown, load_quality_fixture, validate_score_signal


class G0ScoreSignalTests(unittest.TestCase):
    def test_score_breakdown_is_deterministic_and_decomposed(self) -> None:
        fixture = load_quality_fixture("examples/search_quality/sample_quality_fixture.json")
        record = fixture["records"][0]
        first = build_score_breakdown(record, fixture["query_context"], fixture["domain_context"])
        second = build_score_breakdown(record, fixture["query_context"], fixture["domain_context"])
        self.assertEqual(first, second)
        self.assertGreater(len(first["signals"]), 10)
        self.assertFalse(first["accepted_truth"])
        for signal in first["signals"]:
            self.assertEqual(validate_score_signal(signal)["status"], "valid")


if __name__ == "__main__":
    unittest.main()
