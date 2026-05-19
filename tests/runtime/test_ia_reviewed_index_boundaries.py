import unittest

from runtime.source_observation.internet_archive_reviewed_index import (
    build_ia_reviewed_index_boundary_report,
    build_ia_reviewed_index_rebuild_report,
    build_ia_reviewed_records_from_promotion_previews,
    load_default_ia_promotion_previews,
    load_ia_reviewed_index_policy,
    rebuild_ia_reviewed_local_index,
)


class IAReviewedIndexBoundaryTests(unittest.TestCase):
    def test_boundary_report_blocks_forbidden_mutations(self):
        policy = load_ia_reviewed_index_policy()
        records = build_ia_reviewed_records_from_promotion_previews(load_default_ia_promotion_previews(), policy)
        store_result = rebuild_ia_reviewed_local_index(None, records, dry_run=True)
        report = build_ia_reviewed_index_rebuild_report(records, True, store_result, "dry_run_no_instance_mutation")
        boundary = build_ia_reviewed_index_boundary_report(report)
        self.assertTrue(boundary["passed"])
        self.assertFalse(boundary["operator_instance_mutated"])
        self.assertFalse(boundary["committed_data_public_index_mutated"])
        self.assertFalse(boundary["master_index_mutated"])
        self.assertFalse(boundary["download_performed"])
        self.assertFalse(boundary["extraction_executed"])
        self.assertFalse(boundary["model_provider_used"])


if __name__ == "__main__":
    unittest.main()
