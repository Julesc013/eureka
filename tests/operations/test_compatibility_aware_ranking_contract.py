import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


class CompatibilityAwareRankingContractOperationTests(unittest.TestCase):
    def test_schemas_exist_and_parse(self):
        for path in (
            ROOT / "contracts" / "search" / "compatibility_aware_ranking_assessment.v0.json",
            ROOT / "contracts" / "search" / "compatibility_target_profile.v0.json",
            ROOT / "contracts" / "search" / "compatibility_explanation.v0.json",
        ):
            self.assertTrue(path.exists(), path)
            self.assertIsInstance(json.loads(path.read_text(encoding="utf-8")), dict)

    def test_examples_exist(self):
        roots = sorted((ROOT / "examples" / "compatibility_aware_ranking").glob("*_v0"))
        self.assertEqual(len(roots), 6)
        for root in roots:
            self.assertTrue((root / "COMPATIBILITY_TARGET_PROFILE.json").exists())
            self.assertTrue((root / "COMPATIBILITY_AWARE_RANKING_ASSESSMENT.json").exists())
            self.assertTrue((root / "COMPATIBILITY_EXPLANATION.json").exists())
            self.assertTrue((root / "CHECKSUMS.SHA256").exists())

    def test_report_hard_booleans_false(self):
        report = json.loads((ROOT / "control" / "audits" / "compatibility-aware-ranking-contract-v0" / "compatibility_aware_ranking_report.json").read_text(encoding="utf-8"))
        for key in ("runtime_compatibility_ranking_implemented", "compatibility_ranking_applied_to_live_search", "public_search_order_changed", "installability_claimed", "dependency_safety_claimed", "emulator_vm_launch_enabled", "package_manager_invoked", "master_index_mutation_allowed", "source_cache_mutation_allowed", "evidence_ledger_mutation_allowed"):
            self.assertFalse(report[key], key)


if __name__ == "__main__":
    unittest.main()
