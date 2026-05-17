import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


class InstanceLayoutPolicyTests(unittest.TestCase):
    def test_policy_declares_sibling_default_and_legacy_explicit(self):
        payload = json.loads((ROOT / "control/policies/instance_layout_policy.json").read_text(encoding="utf-8"))
        self.assertEqual("instance_layout_policy.v0", payload["schema_version"])
        self.assertEqual("../instances/default", payload["preferred_default_instance_relative_to_repo"])
        self.assertTrue(payload["legacy_sibling_instance_allowed"])
        self.assertEqual("eureka-instance", payload["legacy_sibling_instance_name"])
        self.assertFalse(payload["repo_nested_instance_allowed"])
        self.assertFalse(payload["production_readiness_claimed"])
        self.assertFalse(payload["public_launch_readiness_claimed"])

    def test_runbooks_do_not_recommend_repo_nested_default(self):
        runbooks = [
            "docs/operations/LOCAL_INSTANCE_LAYOUT.md",
            "docs/operations/INSTANCE_PATH_POLICY.md",
            "docs/operations/LOCAL_INSTANCE_BOOTSTRAP.md",
            "docs/operations/LOCAL_INSTANCE_MIGRATION_POLICY.md",
            "docs/operations/LOCAL_HTTP_SERVICE_RUNBOOK.md",
            "docs/operations/LOCAL_HTML_WORKBENCH_RUNBOOK.md",
            "docs/operations/SEARCH_HUNT_RUNTIME_RUNBOOK.md",
            "docs/operations/SEARCH_HUNT_COMMAND_RUNBOOK.md",
            "docs/operations/LOCAL_APPLIANCE_TRACK.md",
        ]
        for rel in runbooks:
            text = (ROOT / rel).read_text(encoding="utf-8")
            self.assertNotIn("--instance ./eureka-instance", text, rel)
            self.assertNotIn("--instance .\\eureka-instance", text, rel)


if __name__ == "__main__":
    unittest.main()
