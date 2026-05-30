from __future__ import annotations

import unittest

from runtime.candidate_store import archive_org_candidate_to_record, sample_archive_org_candidate
from runtime.search.query_plan import plan_query_to_source_actions


class ArchiveOrgCandidateIngestTest(unittest.TestCase):
    def test_query_plan_fields_are_carried_into_candidate_record(self) -> None:
        plan = plan_query_to_source_actions("DirectX SDK June 2010 offline installer")
        candidate = archive_org_candidate_to_record(sample_archive_org_candidate("DirectX SDK June 2010 offline installer"), plan)

        self.assertEqual(candidate["query_plan_ref"], plan["plan_id"])
        self.assertEqual(candidate["domain_id"], plan["domain_pack"])
        self.assertEqual(candidate["source_family"], "internet_archive")
        self.assertIn("candidate_not_reviewed_truth", candidate["limitations"])
        self.assertFalse(candidate["accepted_truth"])


if __name__ == "__main__":
    unittest.main()
