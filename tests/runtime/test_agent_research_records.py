import unittest

from runtime.agent_research import AgentResearchTask, validate_agent_research_task


class AgentResearchRecordsTests(unittest.TestCase):
    def test_agent_research_task_validates_required_disabled_fields(self):
        task = AgentResearchTask.new(
            search_hunt_id="shs_test",
            search_need_id="sn_test",
            exhaustion_report_id="she_test",
            query="sampleproject",
            output_schema={"schema_version": "agent_research_report_schema.v0", "candidate_only": True, "review_required": True},
        )

        validate_agent_research_task(task)
        payload = task.to_dict()
        self.assertEqual(payload["state"], "drafted")
        self.assertFalse(payload["provider_enabled"])
        self.assertFalse(payload["execution_enabled"])
        self.assertIn("accept_truth", payload["forbidden_actions"])


if __name__ == "__main__":
    unittest.main()
