import json
from pathlib import Path
import unittest

from runtime.connectors.core.coverage_ledger import (
    build_source_coverage_manifest,
    validate_source_coverage_record,
)
from runtime.connectors.core.connector_scorecard import validate_connector_scorecard
from runtime.connectors.core.source_pack import build_source_pack_export, validate_source_pack_manifest


REPO_ROOT = Path(__file__).resolve().parents[2]


def load(rel):
    return json.loads((REPO_ROOT / rel).read_text(encoding="utf-8"))


class SourceOsCoverageScorecardsTests(unittest.TestCase):
    def test_coverage_record_validates(self):
        validate_source_coverage_record(load("examples/source_coverage/minimal_source_coverage_record_v0.json"), {})

    def test_coverage_manifest_validates(self):
        records = [
            load("examples/source_coverage/minimal_source_coverage_record_v0.json"),
            load("examples/source_coverage/internet_archive_coverage_record_v0.json"),
        ]
        manifest = build_source_coverage_manifest(records, {})
        self.assertEqual(manifest["schema_version"], "source_coverage_manifest.v0")
        self.assertFalse(manifest["truth_boundary"]["coverage_manifest_is_exhaustive_global_coverage"])

    def test_ia_coverage_example_validates(self):
        record = load("examples/source_coverage/internet_archive_coverage_record_v0.json")
        validate_source_coverage_record(record, {})
        self.assertEqual(record["coverage_basis"], "local_dry_run")

    def test_h1_metadata_wave_preview_validates(self):
        record = load("examples/source_coverage/h1_metadata_wave_coverage_preview_v0.json")
        validate_source_coverage_record(record, {})
        self.assertEqual(record["coverage_status"], "example_only")

    def test_policy_blocked_coverage_validates(self):
        record = load("examples/source_coverage/policy_blocked_coverage_record_v0.json")
        validate_source_coverage_record(record, {})
        self.assertEqual(record["coverage_status"], "blocked_by_policy")

    def test_connector_scorecard_validates(self):
        validate_connector_scorecard(load("examples/connectors/core/scorecards/minimal_connector_scorecard_v0.json"), {})

    def test_ia_scorecard_validates(self):
        scorecard = load("examples/connectors/core/scorecards/internet_archive_scorecard_v0.json")
        validate_connector_scorecard(scorecard, {})
        self.assertFalse(scorecard["truth_boundary"]["scorecard_claims_production_readiness"])

    def test_package_registry_scorecard_validates(self):
        validate_connector_scorecard(load("examples/connectors/core/scorecards/package_registry_family_scorecard_v0.json"), {})

    def test_source_pack_manifest_validates(self):
        validate_source_pack_manifest(load("examples/source_packs/internet_archive_source_pack_manifest_v0.json"), {})

    def test_source_pack_export_remains_preview(self):
        pack = load("examples/source_packs/internet_archive_source_pack_manifest_v0.json")
        export = build_source_pack_export(pack, {})
        self.assertEqual(export["export_status"], "export_preview_only")
        self.assertFalse(export["truth_boundary"]["source_pack_is_accepted_truth"])

    def test_coverage_cannot_claim_exhaustive_global_coverage(self):
        record = load("examples/source_coverage/internet_archive_coverage_record_v0.json")
        record["truth_boundary"]["coverage_claims_exhaustive_global_coverage"] = True
        with self.assertRaises(ValueError):
            validate_source_coverage_record(record, {})

    def test_scorecard_cannot_claim_production_readiness(self):
        scorecard = load("examples/connectors/core/scorecards/internet_archive_scorecard_v0.json")
        scorecard["truth_boundary"]["scorecard_claims_production_readiness"] = True
        with self.assertRaises(ValueError):
            validate_connector_scorecard(scorecard, {})

    def test_scorecard_cannot_auto_approve_future_connectors(self):
        scorecard = load("examples/connectors/core/scorecards/internet_archive_scorecard_v0.json")
        scorecard["truth_boundary"]["scorecard_auto_approves_future_connectors"] = True
        with self.assertRaises(ValueError):
            validate_connector_scorecard(scorecard, {})

    def test_source_pack_cannot_claim_accepted_imported_or_submitted(self):
        pack = load("examples/source_packs/internet_archive_source_pack_manifest_v0.json")
        pack["truth_boundary"]["source_pack_is_submitted"] = True
        with self.assertRaises(ValueError):
            validate_source_pack_manifest(pack, {})

    def test_public_index_mutation_claim_fails(self):
        record = load("examples/source_coverage/internet_archive_coverage_record_v0.json")
        record["product_boundary"]["mutated_public_index"] = True
        with self.assertRaises(ValueError):
            validate_source_coverage_record(record, {})

    def test_master_index_mutation_claim_fails(self):
        scorecard = load("examples/connectors/core/scorecards/internet_archive_scorecard_v0.json")
        scorecard["truth_boundary"]["master_index_mutated"] = True
        with self.assertRaises(ValueError):
            validate_connector_scorecard(scorecard, {})

    def test_rights_malware_installability_claim_fails(self):
        pack = load("examples/source_packs/internet_archive_source_pack_manifest_v0.json")
        pack["truth_boundary"]["verified_installability_claimed"] = True
        with self.assertRaises(ValueError):
            validate_source_pack_manifest(pack, {})


if __name__ == "__main__":
    unittest.main()
