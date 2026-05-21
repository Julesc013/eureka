from __future__ import annotations

import json
from pathlib import Path
import unittest

from runtime.local_eval.scout_schema import REQUIRED_RELATION_TYPES, REQUIRED_WORKUNIT_SEED_TYPES


REPO_ROOT = Path(__file__).resolve().parents[2]


class ScoutRelationTests(unittest.TestCase):
    def test_required_relation_types_present(self) -> None:
        matrix = json.loads((REPO_ROOT / "control/inventory/scout_relation_type_matrix.json").read_text(encoding="utf-8"))
        relation_ids = {item["relation_type"] for item in matrix["relation_types"]}
        self.assertEqual(relation_ids, set(REQUIRED_RELATION_TYPES))

    def test_relation_types_require_evidence_and_review(self) -> None:
        matrix = json.loads((REPO_ROOT / "control/inventory/scout_relation_type_matrix.json").read_text(encoding="utf-8"))
        for relation in matrix["relation_types"]:
            with self.subTest(relation_type=relation["relation_type"]):
                self.assertTrue(relation["evidence_required"])
                self.assertIn("misleading", relation["risk"])

    def test_discovery_trail_preserves_relation_path(self) -> None:
        trail = json.loads((REPO_ROOT / "examples/scout/sample_discovery_trail.json").read_text(encoding="utf-8"))
        step_types = [step["relation_type"] for step in trail["steps"]]
        self.assertIn("same_platform", step_types)
        self.assertIn("same_collection", step_types)
        self.assertFalse(trail["accepted_truth"])

    def test_workunit_seed_suggestions_are_suggestions_only(self) -> None:
        matrix = json.loads((REPO_ROOT / "control/inventory/scout_workunit_seed_matrix.json").read_text(encoding="utf-8"))
        types = {item["suggestion_type"] for item in matrix["workunit_seed_suggestion_types"]}
        self.assertEqual(types, set(REQUIRED_WORKUNIT_SEED_TYPES))
        for item in matrix["workunit_seed_suggestion_types"]:
            self.assertFalse(item["creates_runtime_workunit"])
            self.assertTrue(item["review_required"])


if __name__ == "__main__":
    unittest.main()
