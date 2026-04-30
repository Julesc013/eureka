from __future__ import annotations

import json
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
INVENTORY_DIR = REPO_ROOT / "control" / "inventory" / "generated_artifacts"
INVENTORY = INVENTORY_DIR / "generated_artifacts.json"
POLICY = INVENTORY_DIR / "drift_policy.json"
DOC = REPO_ROOT / "docs" / "operations" / "GENERATED_ARTIFACT_DRIFT_GUARD.md"
AUDIT_DIR = REPO_ROOT / "control" / "audits" / "generated-artifact-drift-guard-v0"
REPORT = AUDIT_DIR / "generated_artifact_drift_report.json"
COMMAND_MATRIX = REPO_ROOT / "control" / "inventory" / "tests" / "command_matrix.json"


REQUIRED_GROUPS = {
    "public_data_summaries",
    "compatibility_surfaces",
    "static_resolver_demos",
    "static_snapshot_example",
    "static_site_dist",
    "python_oracle_goldens",
    "public_alpha_rehearsal_evidence",
    "publication_inventory",
    "test_registry",
    "aide_metadata",
}

FORBIDDEN_COMMAND_TERMS = {
    "curl",
    "wget",
    "invoke-webrequest",
    "invoke-restmethod",
    "google_web_search",
    "internet_archive_live",
    "live-source",
    "scrape",
    "crawl",
}


class GeneratedArtifactDriftGuardTest(unittest.TestCase):
    def load_inventory(self) -> dict:
        return json.loads(INVENTORY.read_text(encoding="utf-8"))

    def test_inventory_and_policy_exist_and_parse(self) -> None:
        self.assertTrue((INVENTORY_DIR / "README.md").exists())
        inventory = self.load_inventory()
        policy = json.loads(POLICY.read_text(encoding="utf-8"))
        self.assertEqual(inventory["inventory_id"], "generated-artifacts-v0")
        self.assertEqual(policy["policy_id"], "generated-artifact-drift-policy-v0")

    def test_required_artifact_groups_are_listed(self) -> None:
        groups = {
            group["artifact_id"]
            for group in self.load_inventory()["artifact_groups"]
        }
        self.assertTrue(REQUIRED_GROUPS.issubset(groups))

    def test_each_required_artifact_has_check_command(self) -> None:
        for group in self.load_inventory()["artifact_groups"]:
            with self.subTest(artifact_id=group["artifact_id"]):
                self.assertIn("check_command", group)
                self.assertIsInstance(group["check_command"], str)
                self.assertTrue(group["check_command"].strip())

    def test_check_commands_are_repo_local_and_non_networked(self) -> None:
        for group in self.load_inventory()["artifact_groups"]:
            commands = [group["check_command"], *group.get("validator_commands", [])]
            for command in commands:
                lowered = command.lower()
                with self.subTest(artifact_id=group["artifact_id"], command=command):
                    self.assertTrue(lowered.startswith("python "))
                    self.assertFalse(
                        any(term in lowered for term in FORBIDDEN_COMMAND_TERMS),
                        command,
                    )

    def test_docs_and_audit_report_exist(self) -> None:
        self.assertTrue(DOC.exists())
        required = {
            "README.md",
            "ARTIFACT_GROUPS.md",
            "DRIFT_POLICY.md",
            "COMMANDS.md",
            "CURRENT_STATUS.md",
            "REMEDIATION.md",
            "generated_artifact_drift_report.json",
        }
        for name in required:
            with self.subTest(name=name):
                self.assertTrue((AUDIT_DIR / name).exists())

    def test_report_json_parses(self) -> None:
        report = json.loads(REPORT.read_text(encoding="utf-8"))
        self.assertEqual(report["report_id"], "generated-artifact-drift-guard-v0")
        self.assertEqual(report["status"], "validation_audit_only")
        self.assertEqual(set(report["artifact_groups_covered"]), REQUIRED_GROUPS)
        self.assertEqual(report["current_drift_status"], "no_drift_detected")

    def test_command_matrix_includes_drift_guard(self) -> None:
        matrix = json.loads(COMMAND_MATRIX.read_text(encoding="utf-8"))
        lane_commands = {
            lane["lane_id"]: set(lane["commands"])
            for lane in matrix["lanes"]
        }
        for lane in ("standard", "full", "docs_only", "publication_static_site"):
            with self.subTest(lane=lane):
                self.assertIn("generated_artifact_drift_guard", lane_commands[lane])
                self.assertIn("generated_artifact_drift_guard_tests", lane_commands[lane])


if __name__ == "__main__":
    unittest.main()

