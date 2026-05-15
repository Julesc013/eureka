import unittest

from runtime.agent_research import build_agent_research_report_schema, validate_candidate_only_report


class AgentResearchReportSchemaTests(unittest.TestCase):
    def test_report_schema_validates_candidate_only_report(self):
        schema = build_agent_research_report_schema().to_dict()
        self.assertTrue(schema["candidate_only"])
        self.assertTrue(schema["review_required"])
        report = {
            "report_id": "arr_test",
            "task_id": "art_test",
            "search_hunt_id": "shs_test",
            "search_need_id": "sn_test",
            "candidate_aliases": [],
            "candidate_source_leads": [],
            "candidate_dead_urls": [],
            "candidate_wayback_paths": [],
            "candidate_extraction_targets": [],
            "candidate_workunits": [],
            "absence_explanation_draft": "",
            "confidence_notes": [],
            "limitations": [],
            "forbidden_claims_absent": True,
            "review_required": True,
            "public_index_mutation_performed": False,
            "master_index_mutation_performed": False,
        }
        self.assertIs(validate_candidate_only_report(report), report)


if __name__ == "__main__":
    unittest.main()
