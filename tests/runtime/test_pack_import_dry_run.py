import tempfile
import unittest
from pathlib import Path

from runtime.packs.dry_run import classify_pack_candidate, run_pack_import_dry_run
from runtime.packs.policy import HARD_BOOLEANS


def pack(**overrides):
    base = {
        "schema_version": "pack_import_dry_run_input.v0",
        "pack_schema_version": "source_pack.v0",
        "pack_id": "test.pack",
        "pack_kind": "source_pack",
        "title": "Test Pack",
        "privacy_status": "public_safe",
        "public_safety_status": "public_safe",
        "risk_status": "metadata_only",
        "mutation_impact": "source_cache_candidate_effect",
        "promotion_readiness": "not_ready",
    }
    base.update(overrides)
    return base


class PackImportDryRunTests(unittest.TestCase):
    def test_classifies_pack_dimensions(self):
        cases = [
            ("source_pack", "source_cache_candidate_effect"),
            ("evidence_pack", "evidence_ledger_candidate_effect"),
            ("index_pack", "public_index_candidate_effect"),
            ("contribution_pack", "candidate_index_candidate_effect"),
            ("pack_set", "candidate_index_candidate_effect"),
        ]
        for pack_kind, mutation_impact in cases:
            with self.subTest(pack_kind=pack_kind):
                summary = classify_pack_candidate(
                    pack(
                        pack_kind=pack_kind,
                        pack_schema_version=f"{pack_kind}.v0",
                        mutation_impact=mutation_impact,
                    ),
                    run_validators=False,
                )
                self.assertEqual(summary.pack_kind, pack_kind)
                self.assertEqual(summary.validation_status, "validator_not_run")
                self.assertEqual(summary.risk_status, "metadata_only")
                self.assertEqual(summary.mutation_impact, mutation_impact)
                self.assertTrue(summary.valid)

    def test_detects_policy_violations(self):
        bad_cases = [
            pack(local_path="C:/Users/private/file.json"),
            pack(source_ref="../outside"),
            pack(fetch_url="https://example.invalid/pack.json"),
            pack(api_key="secret-value"),
            pack(run_scripts=True),
            pack(source_cache_mutated=True),
            pack(promotion_decision_created=True),
        ]
        for record in bad_cases:
            with self.subTest(record=record):
                summary = classify_pack_candidate(record, run_validators=False)
                self.assertFalse(summary.valid)
                self.assertTrue(summary.errors)

    def test_run_pack_import_dry_run_over_temp_records(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for index, pack_kind in enumerate(["source_pack", "evidence_pack", "index_pack"]):
                child = root / str(index)
                child.mkdir()
                (child / "PACK_IMPORT_DRY_RUN_INPUT.json").write_text(
                    __import__("json").dumps(
                        pack(
                            pack_id=f"test.{pack_kind}",
                            pack_kind=pack_kind,
                            pack_schema_version=f"{pack_kind}.v0",
                        )
                    ),
                    encoding="utf-8",
                )
            report = run_pack_import_dry_run([root], run_validators=False, allow_temp_roots=True)
        self.assertEqual(report.packs_seen, 3)
        self.assertEqual(report.packs_valid, 3)
        self.assertEqual(report.packs_invalid, 0)
        self.assertEqual(report.pack_kinds["source_pack"], 1)
        self.assertTrue(report.hard_booleans["local_dry_run"])
        for key, value in HARD_BOOLEANS.items():
            self.assertEqual(report.hard_booleans[key], value)

    def test_deterministic_report(self):
        first = run_pack_import_dry_run(run_validators=False)
        second = run_pack_import_dry_run(run_validators=False)
        self.assertEqual(first.to_dict(), second.to_dict())


if __name__ == "__main__":
    unittest.main()
