import unittest

from runtime.local_eval.g0_quality import build_explanation_packet, build_score_breakdown, load_quality_fixture


class G0ExplanationTests(unittest.TestCase):
    def test_explanation_contains_required_why_sections(self) -> None:
        fixture = load_quality_fixture("examples/search_quality/sample_quality_fixture.json")
        record = fixture["records"][1]
        score = build_score_breakdown(record, fixture["query_context"], fixture["domain_context"])
        packet = build_explanation_packet(score, record)
        for field in (
            "why_result_appeared",
            "why_result_ranked_here",
            "why_result_is_limited",
            "why_actions_are_blocked",
            "what_would_improve_confidence",
            "what_remaining_work_exists",
            "uncertainty",
            "limitations",
        ):
            self.assertTrue(packet[field], field)
        self.assertFalse(packet["accepted_truth"])


if __name__ == "__main__":
    unittest.main()
