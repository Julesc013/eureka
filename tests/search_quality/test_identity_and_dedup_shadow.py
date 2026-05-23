from __future__ import annotations

import json
from pathlib import Path
import unittest

from runtime.search.quality.dedup_shadow import build_dedup_shadow, validate_dedup_shadow
from runtime.search.quality.identity_shadow import build_identity_merge_shadow


ROOT = Path(__file__).resolve().parents[2]


def load(rel: str):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


class IdentityAndDedupShadowTests(unittest.TestCase):
    def setUp(self) -> None:
        self.items = load("examples/search/quality/ranking/input_bundle_software_v0.json")["items"]

    def test_identity_merge_shadow_preserves_conflicts(self) -> None:
        record = build_identity_merge_shadow(self.items)
        self.assertFalse(record["merge_allowed_current"])
        self.assertFalse(record["automatic_merge_allowed"])
        self.assertGreaterEqual(record["conflict_summary"]["conflict_count"], 1)

    def test_dedup_shadow_groups_duplicates_but_does_not_merge_or_delete(self) -> None:
        record = build_dedup_shadow(self.items)
        self.assertGreaterEqual(len(record["duplicate_groups_proposed"]), 1)
        self.assertFalse(record["merge_allowed_current"])
        self.assertFalse(record["delete_allowed_current"])
        self.assertFalse(record["automatic_dedup_allowed"])

    def test_public_truth_claims_are_rejected(self) -> None:
        record = build_dedup_shadow(self.items)
        record["truth_boundary"]["public_index_mutated"] = True
        with self.assertRaises(ValueError):
            validate_dedup_shadow(record)


if __name__ == "__main__":
    unittest.main()
