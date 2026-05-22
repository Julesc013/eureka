from __future__ import annotations

import unittest

from runtime.local_service.workbench_live_run import build_command_response, create_workbench_resolution_run


class WorkbenchLiveRunBoundaryTests(unittest.TestCase):
    def test_boundaries_remain_false_and_blocked_commands_do_not_mutate(self) -> None:
        packet = create_workbench_resolution_run("sampleproject", include_ia_hunt_dry_run=True)
        for key in (
            "live_ia_call_performed",
            "source_probe_executed",
            "source_cache_write_performed",
            "evidence_write_performed",
            "candidate_index_mutated",
            "reviewed_index_mutated",
            "master_index_mutated",
            "operator_instance_mutated",
            "download_performed",
            "upload_performed",
            "extraction_executed",
            "model_provider_used",
            "deployment_performed",
        ):
            self.assertFalse(packet["boundary_report"][key], key)
        command = build_command_response(packet["run_id"], "run_live_source")
        self.assertFalse(command["allowed"])
        self.assertFalse(command["state_mutated"])
        self.assertFalse(command["store_mutation_performed"])


if __name__ == "__main__":
    unittest.main()
