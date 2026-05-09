from __future__ import annotations

import json
from pathlib import Path
import unittest

from runtime.search_quality.known_absence import (
    build_known_absence_record,
    detect_absence_overclaim,
    validate_known_absence_record,
)
from runtime.search_quality.near_miss import build_near_miss_explanation, classify_near_miss_mismatch


ROOT = Path(__file__).resolve().parents[2]


def load(rel: str):
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


class NearMissAndAbsenceTests(unittest.TestCase):
    def test_wrong_version_near_miss_classifies(self) -> None:
        record = {"result_ref": "r", "mismatch_type": "wrong_version", "why_not_exact": "wrong version"}
        self.assertEqual(classify_near_miss_mismatch(record), "wrong_version")

    def test_wrong_platform_near_miss_classifies(self) -> None:
        record = {"result_ref": "r", "mismatch_type": "wrong_platform", "why_not_exact": "wrong platform"}
        self.assertEqual(build_near_miss_explanation(record)["mismatch_type"], "wrong_platform")

    def test_source_only_near_miss_classifies(self) -> None:
        record = {"result_ref": "r", "mismatch_type": "source_only", "why_not_exact": "source only"}
        self.assertEqual(build_near_miss_explanation(record)["mismatch_type"], "source_only")

    def test_extraction_needed_near_miss_classifies(self) -> None:
        record = {"result_ref": "r", "mismatch_type": "extraction_needed", "why_not_exact": "needs extraction"}
        built = build_near_miss_explanation(record)
        self.assertEqual(built["mismatch_type"], "extraction_needed")
        self.assertFalse(built["suggested_workunit_seed_future"]["created"])

    def test_known_absence_includes_checked_and_not_checked(self) -> None:
        bundle = load("examples/search_quality/input_bundles/software_search_explanation_bundle_v0.json")
        record = build_known_absence_record(bundle)
        self.assertTrue(record["sources_checked"])
        self.assertTrue(record["sources_not_checked"])
        self.assertFalse(record["no_claims"]["global_absence_claimed"])

    def test_known_absence_cannot_claim_global_absence(self) -> None:
        record = load("examples/search_quality/known_absence/no_reviewed_result_absence_v0.json")
        record["no_claims"]["global_absence_claimed"] = True
        self.assertTrue(detect_absence_overclaim(record))
        with self.assertRaises(ValueError):
            validate_known_absence_record(record)

    def test_known_absence_cannot_claim_exhaustive_web_search(self) -> None:
        record = load("examples/search_quality/known_absence/no_reviewed_result_absence_v0.json")
        record["no_claims"]["exhaustive_web_search_claimed"] = True
        with self.assertRaises(ValueError):
            validate_known_absence_record(record)

    def test_public_index_mutation_claim_is_rejected(self) -> None:
        record = load("examples/search_quality/known_absence/no_reviewed_result_absence_v0.json")
        record["truth_boundary"]["public_index_mutated"] = True
        with self.assertRaises(ValueError):
            validate_known_absence_record(record)


if __name__ == "__main__":
    unittest.main()
