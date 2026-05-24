from __future__ import annotations

import unittest

from runtime.local.apply import APPLY_CONFIRMATION, run_local_apply
from tests.runtime.test_local_apply_gate import make_instance


BOUNDARY_FALSES = (
    "operator_instance_mutated",
    "operator_instance_mutation_enabled_by_default",
    "committed_instance_state",
    "master_index_mutated",
    "committed_data_public_index_mutated",
    "download_performed",
    "upload_performed",
    "extraction_executed",
    "model_provider_used",
    "deployment_performed",
    "production_readiness_claimed",
    "public_launch_readiness_claimed",
)


class LocalApplyBoundaryTests(unittest.TestCase):
    def test_apply_keeps_forbidden_boundary_flags_false(self) -> None:
        tmp, instance = make_instance()
        self.addCleanup(tmp.cleanup)

        result = run_local_apply(
            target_instance=instance,
            apply=True,
            operator_token="local-dev-token",
            confirmation=APPLY_CONFIRMATION,
        )

        for field in BOUNDARY_FALSES:
            self.assertIs(result[field], False, field)
            self.assertIs(result["boundary_report"][field], False, field)
        self.assertTrue(result["boundary_report"]["explicit_local_instance_mutation_performed"])


if __name__ == "__main__":
    unittest.main()
