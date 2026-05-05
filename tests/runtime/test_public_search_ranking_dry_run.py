import unittest
from pathlib import Path

from runtime.engine.ranking.dry_run import rank_result_set_dry_run, run_public_search_ranking_dry_run
from runtime.engine.ranking.errors import RankingDryRunError
from runtime.engine.ranking.factors import compute_explicit_factor_summary


def _record():
    return {
        "result_set_id": "unit_result_set",
        "status": "synthetic_example",
        "current_order": ["weak", "strong"],
        "results": [
            {
                "result_id": "weak",
                "title": "Weak lexical result",
                "candidate_status": "candidate",
                "evidence": {"strength": "weak", "provenance_strength": "weak"},
                "source": {"posture": "weak"},
                "compatibility": {"evidence_strength": "unknown", "platform_os_match": "unknown"},
                "representation": {"availability": "weak", "member_access": "absent"},
                "gaps": ["source gap"],
                "rights_risk": {"caution": True},
                "actions": {"risky_actions_enabled": False},
            },
            {
                "result_id": "strong",
                "title": "Strong evidence result",
                "candidate_status": "reviewed",
                "evidence": {
                    "strength": "strong",
                    "provenance_strength": "strong",
                    "intrinsic_identifier_match": True,
                    "refs": ["synthetic_ref"],
                },
                "source": {"posture": "strong"},
                "compatibility": {
                    "evidence_strength": "strong",
                    "platform_os_match": "strong",
                    "architecture_match": "medium",
                },
                "representation": {"availability": "strong", "member_access": "medium"},
                "rights_risk": {"caution": True},
                "actions": {"risky_actions_enabled": False},
            },
        ],
    }


class PublicSearchRankingDryRunTests(unittest.TestCase):
    def test_run_public_search_ranking_dry_run_over_examples(self):
        report = run_public_search_ranking_dry_run([Path("examples/public_search_ranking_dry_run")])
        data = report.to_dict()
        self.assertEqual(data["mode"], "local_dry_run")
        self.assertGreaterEqual(data["result_sets_seen"], 5)
        self.assertFalse(data["hard_booleans"]["public_search_order_changed"])
        self.assertFalse(data["hard_booleans"]["source_cache_read"])

    def test_extracts_evidence_and_compatibility_factors(self):
        factors = compute_explicit_factor_summary(_record()["results"][1])
        by_type = {factor.factor_type: factor for factor in factors}
        self.assertEqual(by_type["evidence_strength"].category_value, "strong")
        self.assertEqual(by_type["compatibility_evidence"].category_value, "strong")
        self.assertEqual(by_type["platform_os_match"].category_value, "strong")

    def test_produces_deterministic_proposed_order_and_public_reasons(self):
        result = rank_result_set_dry_run(_record())
        self.assertEqual(result.current_order, ("weak", "strong"))
        self.assertEqual(result.proposed_dry_run_order, ("strong", "weak"))
        self.assertTrue(result.explanation_summaries[0].user_visible_reason)
        self.assertIn("No hidden score", result.explanation_summaries[0].user_visible_reason)

    def test_preserves_current_order_fallback(self):
        record = _record()
        record["policy"] = {"force_current_order_fallback": True}
        result = rank_result_set_dry_run(record)
        self.assertTrue(result.fallback_used)
        self.assertEqual(result.proposed_dry_run_order, tuple(record["current_order"]))

    def test_keeps_conflicts_and_gaps_visible(self):
        record = _record()
        record["results"][0]["conflicts"] = ["conflicting compatibility evidence"]
        result = rank_result_set_dry_run(record)
        caveats = set(result.explanation_summaries[0].caveats)
        self.assertIn("conflicts_visible", caveats)
        self.assertIn("gaps_visible", caveats)

    def test_rejects_private_absolute_path(self):
        record = _record()
        record["results"][0]["local_path"] = "C:\\Users\\Example\\private.dat"
        with self.assertRaises(RankingDryRunError):
            rank_result_set_dry_run(record)

    def test_rejects_url_live_source_fields(self):
        record = _record()
        record["results"][0]["source_url"] = "https://example.invalid/source"
        with self.assertRaises(RankingDryRunError):
            rank_result_set_dry_run(record)

    def test_detects_secret_like_keys(self):
        record = _record()
        record["results"][0]["api_key"] = "placeholder"
        with self.assertRaises(RankingDryRunError):
            rank_result_set_dry_run(record)

    def test_detects_telemetry_user_profile_ad_model_signals(self):
        for key in ("telemetry_signal", "user_profile_signal", "ad_signal", "model_signal"):
            record = _record()
            record["results"][0][key] = True
            with self.subTest(key=key):
                with self.assertRaises(RankingDryRunError):
                    rank_result_set_dry_run(record)

    def test_detects_result_suppression_claims(self):
        record = _record()
        record["results"][0]["suppress"] = True
        with self.assertRaises(RankingDryRunError):
            rank_result_set_dry_run(record)

    def test_detects_mutation_claims(self):
        record = _record()
        record["results"][0]["public_index_mutated"] = True
        with self.assertRaises(RankingDryRunError):
            rank_result_set_dry_run(record)


if __name__ == "__main__":
    unittest.main()
