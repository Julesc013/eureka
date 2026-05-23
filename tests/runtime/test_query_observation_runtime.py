from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path
from unittest import mock
import unittest

from runtime.local.foundry.query_observation import (
    build_query_observation,
    classify_query_outcome,
    detect_poisoning_risks,
    summarize_query_observation,
    validate_query_observation,
)


ROOT = Path(__file__).resolve().parents[2]
EXAMPLES = ROOT / "examples" / "search" / "query_observations"


class QueryObservationRuntimeTests(unittest.TestCase):
    def test_build_query_observation_works_on_valid_examples(self) -> None:
        for path in sorted(EXAMPLES.glob("*_query_observation_v0.json")):
            with self.subTest(path=path.name):
                record = build_query_observation(_read_json(path))
                self.assertEqual(validate_query_observation(record), [])

    def test_empty_result_example_classifies_as_empty(self) -> None:
        record = build_query_observation(_example("empty_result_query_observation_v0.json"))

        self.assertEqual(classify_query_outcome(record), "empty_result")

    def test_useful_result_example_classifies_as_useful(self) -> None:
        record = build_query_observation(_example("useful_result_query_observation_v0.json"))

        self.assertEqual(classify_query_outcome(record), "useful_result")

    def test_policy_blocked_example_remains_blocked(self) -> None:
        record = build_query_observation(_example("policy_blocked_query_observation_v0.json"))

        self.assertEqual(record["observation_status"], "policy_blocked")
        self.assertEqual(classify_query_outcome(record), "policy_blocked")
        self.assertIn("unsupported_scraping_request", record["poisoning_guard_posture"]["risk_flags"])

    def test_privacy_filter_flags_private_path(self) -> None:
        record = build_query_observation(
            {
                "query_text": "C:\\Users\\Alice\\private.txt",
                "query_source": "explicit_test_fixture",
                "result_count": 0,
                "result_quality": "empty",
                "first_useful_result_rank": None,
                "failure_modes": ["empty_result"],
            }
        )

        self.assertEqual(record["observation_status"], "privacy_filtered")
        self.assertIn("local_path_injection", record["privacy_posture"]["privacy_risks"])
        self.assertEqual(validate_query_observation(record), [])

    def test_privacy_filter_flags_credential_like_text(self) -> None:
        record = build_query_observation(
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
                "query_text": "https://example.invalid live_probe force source",
                "notes": ["force rank result"],
            }
        )

        self.assertIn("url_injection", risks["risk_flags"])
        self.assertIn("unsupported_live_probe_request", risks["risk_flags"])
        self.assertIn("source_manipulation_attempt", risks["risk_flags"])
        self.assertIn("result_rank_manipulation_attempt", risks["risk_flags"])

    def test_product_boundary_true_claim_fails(self) -> None:
        record = build_query_observation(_example("minimal_query_observation_v0.json"))
        record["product_boundary"]["enabled_telemetry"] = True

        errors = validate_query_observation(record)

        self.assertTrue(any("enabled_telemetry" in error for error in errors))

    def test_telemetry_hosted_live_claim_fails(self) -> None:
        record = build_query_observation(_example("minimal_query_observation_v0.json"))
        record["notes"] = ["telemetry enabled for hosted query capture enabled"]

        errors = validate_query_observation(record)

        self.assertTrue(any("telemetry enabled" in error for error in errors))
        self.assertTrue(any("hosted query capture enabled" in error for error in errors))

    def test_runtime_does_not_call_network_model_or_provider(self) -> None:
        with mock.patch("socket.create_connection", side_effect=AssertionError("network call blocked")):
            record = build_query_observation(_example("minimal_query_observation_v0.json"))
            summary = summarize_query_observation(record)

        self.assertEqual(summary["query_observation_id"], "query_observation.minimal.windows_7_apps.v0")

    def test_runtime_does_not_mutate_master_index_or_private_roots(self) -> None:
        before = _private_root_state()

        record = build_query_observation(_example("minimal_query_observation_v0.json"))

        self.assertFalse(record["product_boundary"]["mutated_master_index"])
        self.assertFalse(record["truth_boundary"]["query_observation_can_mutate_master_index"])
        self.assertEqual(before, _private_root_state())


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _example(name: str) -> dict:
    return deepcopy(_read_json(EXAMPLES / name))


def _private_root_state() -> dict[str, bool]:
    return {
        ".aide.local": (ROOT / ".aide.local").exists(),
        ".local/eureka": (ROOT / ".local" / "eureka").exists(),
        ".cache/eureka": (ROOT / ".cache" / "eureka").exists(),
    }


if __name__ == "__main__":
    unittest.main()
