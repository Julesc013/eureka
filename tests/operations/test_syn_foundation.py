from __future__ import annotations

import json
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]


class SynFoundationOperationsTests(unittest.TestCase):
    def test_every_query_case_has_search_need_and_workunit_seed(self) -> None:
        cases = _all_query_cases()
        need_bridge = _read_json("examples/syn_foundation/synthetic_to_search_need_seeds_v0.json")
        workunit_bridge = _read_json("examples/syn_foundation/synthetic_to_workunit_seeds_v0.json")
        case_ids = {case["query_case_id"] for case in cases}

        self.assertEqual({item["query_case_id"] for item in need_bridge["mappings"]}, case_ids)
        self.assertEqual({item["query_case_id"] for item in workunit_bridge["mappings"]}, case_ids)

    def test_query_sets_keep_non_mutation_boundary(self) -> None:
        for path in _query_set_paths():
            with self.subTest(path=path):
                payload = _read_json(path)
                boundary = payload["runtime_capability_boundary"]
                self.assertFalse(any(boundary.values()))
                self.assertFalse(payload["no_claims"]["production_search_quality"])
                self.assertFalse(payload["no_claims"]["user_demand_observed"])
                self.assertFalse(payload["no_claims"]["result_truth_created"])

    def test_syn_policy_blocks_runtime_and_external_actions(self) -> None:
        policy = _read_json("control/policies/syn_foundation_policy.json")
        for flag in (
            "synthetic_generation_runtime_enabled",
            "runtime_search_need_creation_allowed",
            "runtime_workunit_creation_allowed",
            "source_probe_enabled",
            "live_ia_call_enabled",
            "download_enabled",
            "upload_enabled",
            "extraction_enabled",
            "model_provider_enabled",
            "operator_instance_mutation_allowed",
            "master_index_mutation_allowed",
            "deployment_enabled",
            "production_readiness_claimed",
            "public_launch_readiness_claimed",
        ):
            with self.subTest(flag=flag):
                self.assertFalse(policy[flag])


def _query_set_paths() -> tuple[str, ...]:
    return (
        "examples/syn_foundation/query_sets/demo_query_set_v0.json",
        "examples/syn_foundation/query_sets/hard_query_set_v0.json",
        "examples/syn_foundation/query_sets/adversarial_query_set_v0.json",
    )


def _all_query_cases() -> list[dict]:
    cases: list[dict] = []
    for path in _query_set_paths():
        cases.extend(_read_json(path)["query_cases"])
    return cases


def _read_json(path: str) -> dict:
    return json.loads((REPO_ROOT / path).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
