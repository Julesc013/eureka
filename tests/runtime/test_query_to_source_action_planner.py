from __future__ import annotations

import json
from pathlib import Path
import unittest

from runtime.search.query_plan import DOMAIN_PACKS, INTENTS, SOURCE_FAMILIES, plan_query_to_source_actions


ROOT = Path(__file__).resolve().parents[2]


class QueryToSourceActionPlannerTests(unittest.TestCase):
    def test_contract_enums_match_runtime_constants(self) -> None:
        contract = json.loads(
            (ROOT / "contracts/search/query_plan/query_to_source_action_plan.v0.json").read_text(encoding="utf-8")
        )

        self.assertEqual(set(INTENTS), set(contract["properties"]["intent"]["enum"]))
        self.assertEqual(set(DOMAIN_PACKS), set(contract["properties"]["domain_pack"]["enum"]))
        self.assertEqual(set(SOURCE_FAMILIES), set(contract["properties"]["source_families"]["items"]["enum"]))

    def test_required_example_files_match_runtime_plans(self) -> None:
        for path in sorted((ROOT / "examples/query_plans").glob("*.json")):
            if path.name == "README.md":
                continue
            payload = json.loads(path.read_text(encoding="utf-8"))
            plan = plan_query_to_source_actions(payload["example_query"])

            self.assertEqual(payload["expected_intent"], plan["intent"], path.name)
            self.assertEqual(payload["expected_domain_pack"], plan["domain_pack"], path.name)
            self.assertEqual(set(payload["expected_source_families"]), set(plan["source_families"]), path.name)
            self.assertEqual(
                payload["archive_org_metadata_query"],
                plan["source_query_rewrites"]["archive_org_metadata"],
                path.name,
            )

    def test_plan_contains_source_actions_work_units_and_review_handoff(self) -> None:
        plan = plan_query_to_source_actions("DirectX SDK June 2010 offline installer")

        self.assertEqual("find_exact_artifact", plan["intent"])
        self.assertTrue(plan["source_actions"])
        self.assertTrue(plan["work_units"])
        self.assertTrue(plan["review_handoff_plans"])
        self.assertTrue(all(action["review_required"] for action in plan["source_actions"]))
        self.assertTrue(all(action["accepted_truth"] is False for action in plan["source_actions"]))


if __name__ == "__main__":
    unittest.main()
