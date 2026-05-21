from __future__ import annotations

import json
import sys
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_search_hunt_track import validate
from hunt_queue_progress import current_recommended_task_id, post_hunt_current_allowed


def load_json(rel: str) -> dict:
    return json.loads((ROOT / rel).read_text(encoding="utf-8"))


class SearchHuntTrackTests(unittest.TestCase):
    def test_hunt_track_plan_includes_hunt_00_through_hunt_12(self) -> None:
        payload = load_json("control/inventory/search_hunt_track_plan.json")
        self.assertEqual("search_hunt_track_plan.v0", payload["schema_version"])
        self.assertEqual([f"HUNT-{index:02d}" for index in range(13)], [row["task_id"] for row in payload["track"]])

    def test_next_task_is_hunt_01_or_completed_post_hunt_task(self) -> None:
        decision = load_json("control/inventory/search_hunt_next_task_decision.json")
        self.assertEqual("HUNT-01 \u2014 Search Hunt Session runtime", decision["recommended_next_task"])
        queue = (ROOT / ".aide/queue/index.yaml").read_text(encoding="utf-8")
        self.assertRegex(
            queue,
            r"current_recommended_task: (HUNT-(0[1-9]|1[0-2])|SYN-00|DOMAIN-00|SCOUT-SCHEMA-00|F0-00|G0|HUNT-REMEDIATION|HUNT-TO-MAIN-PROMOTION-REVIEW|DEV-AND-IA-[A-Z0-9-]+|REPO-LAYOUT-[A-Z0-9-]+|IA-HUNT-BRIDGE-00)\b",
        )

    def test_local_appliance_and_workunit_dependencies_are_required(self) -> None:
        dependency = load_json("control/inventory/search_hunt_local_appliance_dependency.json")
        self.assertTrue(dependency["must_use_explicit_local_instance"])
        self.assertTrue(dependency["must_use_runtime_workunit_queue_for_background_tasks"])
        matrix = load_json("control/inventory/search_hunt_dependency_matrix.json")
        names = {row["dependency"] for row in matrix["dependencies"]}
        self.assertIn("Local Appliance", names)
        self.assertIn("WorkUnit queue", names)

    def test_f0_is_not_current(self) -> None:
        queue = (ROOT / ".aide/queue/index.yaml").read_text(encoding="utf-8")
        if current_recommended_task_id(ROOT) == "F0-00":
            self.assertTrue(post_hunt_current_allowed(ROOT))
        else:
            self.assertNotIn("current_recommended_task: F0-00", queue)
        decision = load_json("control/inventory/search_hunt_next_task_decision.json")
        self.assertEqual("deferred", decision["f0_current_status"])

    def test_ai_source_probe_and_sync_are_disabled(self) -> None:
        hunt = load_json("control/policies/search_hunt_policy.json")
        ai = load_json("control/policies/search_hunt_ai_boundary_policy.json")
        sync = load_json("control/policies/search_hunt_sync_policy.json")
        self.assertFalse(hunt["source_probe_execution_enabled"])
        self.assertFalse(hunt["model_provider_enabled"])
        self.assertFalse(ai["ai_model_provider_calls_enabled_current_task"])
        self.assertFalse(sync["sync_enabled_current_task"])

    def test_completion_policy_rejects_scaffold_only_implementation(self) -> None:
        payload = load_json("control/policies/search_hunt_completion_policy.json")
        self.assertFalse(payload["scaffold_only_completion_allowed"])
        self.assertEqual("planning/control proof", payload["proof_levels"]["HUNT-00"])
        self.assertEqual("runtime/session persistence proof", payload["proof_levels"]["HUNT-01"])

    def test_validator_passes_with_disposed_warnings(self) -> None:
        result = validate(ROOT)
        self.assertIn(result["status"], {"pass", "pass_with_warnings"}, result)
        self.assertFalse(result["runtime_modified"])
        self.assertFalse(result["source_probe_executed"])
        self.assertFalse(result["model_provider_used"])


if __name__ == "__main__":
    unittest.main()
