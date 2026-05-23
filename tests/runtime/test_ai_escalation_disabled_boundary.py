import tempfile
import unittest
from pathlib import Path

from runtime.ai_escalation import build_ai_escalation_preflight, validate_provider_disabled
from runtime.local.appliance import close_local_appliance, open_local_appliance
from runtime.search.hunt import build_hunt_exhaustion_report
from scripts.eureka_init_instance import initialize_instance


class AIEscalationDisabledBoundaryTests(unittest.TestCase):
    def test_preflight_records_no_forbidden_side_effects(self):
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp)
            initialize_instance(instance)
            runtime = open_local_appliance(instance)
            try:
                hunt = runtime.search_hunt.create_session_from_query("sampleproject", runtime=runtime)
                runtime.search_hunt.attach_exhaustion_report(hunt.id, build_hunt_exhaustion_report(runtime, hunt.id))
                need = runtime.search_need.create_need_from_hunt(runtime, hunt.id)
                runtime.agent_research.draft_task_from_need(runtime, need.id)
                preflight = build_ai_escalation_preflight(runtime, need_id=need.id)
                payload = preflight.to_dict()
                self.assertEqual(validate_provider_disabled()["provider_enabled"], False)
                self.assertFalse(payload["model_provider_used"])
                self.assertFalse(payload["external_network_used"])
                self.assertFalse(payload["source_probe_executed"])
                self.assertFalse(payload["extraction_executed"])
                self.assertFalse(payload["review_mutation_performed"])
                self.assertFalse(payload["master_index_mutated"])
            finally:
                close_local_appliance(runtime)


if __name__ == "__main__":
    unittest.main()
