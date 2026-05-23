from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from unittest import mock
import unittest

from runtime.local.foundry.search_miss_ledger import (
    build_search_miss_from_query_observation,
    classify_miss_failure_modes,
    detect_exhaustive_absence_overclaim,
    detect_poisoning_risks,
    summarize_search_miss,
    validate_search_miss,
)


ROOT = Path(__file__).resolve().parents[2]
QUERY_EXAMPLES = ROOT / "examples" / "search" / "query_observations"
MISS_EXAMPLES = ROOT / "examples" / "search" / "misses"


class SearchMissLedgerRuntimeTests(unittest.TestCase):
    def test_build_search_miss_from_query_observation_works_on_empty_result(self) -> None:
        record = build_search_miss_from_query_observation(_query_example("empty_result_query_observation_v0.json"))

        self.assertEqual(record["search_miss_kind"], "empty_result")
        self.assertEqual(validate_search_miss(record), [])

    def test_valid_search_miss_examples_pass(self) -> None:
        for path in sorted(MISS_EXAMPLES.glob("*_search_miss_v0.json")):
            with self.subTest(path=path.name):
                record = build_search_miss_from_query_observation(_read_json(path))
                self.assertEqual(validate_search_miss(record), [])

    def test_weak_result_example_classifies_as_weak_result(self) -> None:
        record = build_search_miss_from_query_observation(_miss_example("weak_result_search_miss_v0.json"))

        self.assertEqual(record["search_miss_kind"], "weak_result")
        self.assertIn("weak_result", classify_miss_failure_modes(record))

    def test_near_match_example_classifies_as_near_match_only(self) -> None:
        record = build_search_miss_from_query_observation(_miss_example("near_match_search_miss_v0.json"))

        self.assertEqual(record["search_miss_kind"], "near_match_only")
        self.assertIn("near_match_only", classify_miss_failure_modes(record))

    def test_policy_blocked_example_remains_policy_blocked(self) -> None:
        record = build_search_miss_from_query_observation(_miss_example("policy_blocked_search_miss_v0.json"))

        self.assertEqual(record["search_miss_status"], "policy_blocked")
        self.assertEqual(record["search_miss_kind"], "policy_blocked")
        self.assertIn("unsupported_scraping_request", record["poisoning_guard_posture"]["risk_flags"])

    def test_noisy_result_example_classifies_as_noisy_result_list(self) -> None:
        record = build_search_miss_from_query_observation(_miss_example("noisy_result_search_miss_v0.json"))

        self.assertEqual(record["search_miss_kind"], "noisy_result_list")
        self.assertIn("noisy_result_list", classify_miss_failure_modes(record))

    def test_exhaustive_absence_overclaim_is_rejected_or_flagged(self) -> None:
        record = build_search_miss_from_query_observation(_miss_example("minimal_search_miss_v0.json"))
        record["notes"] = ["whole web was searched"]

        self.assertTrue(detect_exhaustive_absence_overclaim(record))
        self.assertTrue(any("overclaim" in error for error in validate_search_miss(record)))

    def test_privacy_filter_flags_private_path(self) -> None:
        record = build_search_miss_from_query_observation(
            {
                "query_text": "C:\\Users\\Alice\\private.txt",
                "query_source": "explicit_test_fixture",
                "result_count": 0,
                "result_quality": "empty",
                "first_useful_result_rank": None,
                "failure_modes": ["empty_result"],
            }
        )

        self.assertEqual(record["search_miss_status"], "privacy_filtered")
        self.assertIn("local_path_injection", record["privacy_posture"]["privacy_risks"])
        self.assertEqual(validate_search_miss(record), [])

    def test_privacy_filter_flags_credential_like_text(self) -> None:
        record = build_search_miss_from_query_observation(
            {
                "query_text": "api_key example should be filtered",
                "query_source": "explicit_test_fixture",
                "result_count": 0,
                "result_quality": "empty",
                "first_useful_result_rank": None,
                "failure_modes": ["empty_result"],
            }
        )

        self.assertIn("credential_like_content", record["privacy_posture"]["privacy_risks"])
        self.assertIn("credential_like_content", record["poisoning_guard_posture"]["risk_flags"])

    def test_poisoning_guard_flags_url_live_probe_and_source_manipulation(self) -> None:
        risks = detect_poisoning_risks(
            {
                "query_summary": {"query_text": "https://example.invalid live_probe force source"},
                "notes": ["force rank result"],
            }
        )

        self.assertIn("url_injection", risks["risk_flags"])
        self.assertIn("unsupported_live_probe_request", risks["risk_flags"])
        self.assertIn("source_manipulation_attempt", risks["risk_flags"])
        self.assertIn("result_rank_manipulation_attempt", risks["risk_flags"])

    def test_product_boundary_true_claim_fails(self) -> None:
        record = build_search_miss_from_query_observation(_miss_example("minimal_search_miss_v0.json"))
        record["product_boundary"]["enabled_telemetry"] = True

        errors = validate_search_miss(record)

        self.assertTrue(any("enabled_telemetry" in error for error in errors))

    def test_telemetry_hosted_live_claim_fails(self) -> None:
        record = build_search_miss_from_query_observation(_miss_example("minimal_search_miss_v0.json"))
        record["notes"] = ["telemetry enabled for hosted query capture enabled"]

        errors = validate_search_miss(record)

        self.assertTrue(any("telemetry enabled" in error for error in errors))
        self.assertTrue(any("hosted query capture enabled" in error for error in errors))

    def test_runtime_does_not_call_network_model_or_provider(self) -> None:
        with mock.patch("socket.create_connection", side_effect=AssertionError("network call blocked")):
            record = build_search_miss_from_query_observation(_query_example("empty_result_query_observation_v0.json"))
            summary = summarize_search_miss(record)

        self.assertEqual(summary["search_miss_kind"], "empty_result")

    def test_runtime_does_not_mutate_master_index_or_private_roots(self) -> None:
        before = _private_root_state()

        record = build_search_miss_from_query_observation(_miss_example("minimal_search_miss_v0.json"))

        self.assertFalse(record["product_boundary"]["mutated_master_index"])
        self.assertFalse(record["truth_boundary"]["search_miss_can_mutate_master_index"])
        self.assertEqual(before, _private_root_state())


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _query_example(name: str) -> dict:
    return deepcopy(_read_json(QUERY_EXAMPLES / name))


def _miss_example(name: str) -> dict:
    return deepcopy(_read_json(MISS_EXAMPLES / name))


def _private_root_state() -> dict[str, bool]:
    return {
        ".aide.local": (ROOT / ".aide.local").exists(),
        ".local/eureka": (ROOT / ".local" / "eureka").exists(),
        ".cache/eureka": (ROOT / ".cache" / "eureka").exists(),
    }


if __name__ == "__main__":
    unittest.main()
