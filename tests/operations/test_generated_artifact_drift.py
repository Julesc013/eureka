from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
AUDIT_SCRIPT = ROOT / "scripts" / "audit_generated_artifact_drift.py"
REPAIR_SCRIPT = ROOT / "scripts" / "repair_generated_artifact_drift.py"
VALIDATOR_SCRIPT = ROOT / "scripts" / "validate_generated_artifact_drift.py"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class GeneratedArtifactDriftTests(unittest.TestCase):
    def setUp(self) -> None:
        self.audit = load_module(AUDIT_SCRIPT, "audit_generated_artifact_drift")
        self.repair = load_module(REPAIR_SCRIPT, "repair_generated_artifact_drift")

    def test_drift_audit_classifies_site_dist_as_deployment_generated(self) -> None:
        policy = {"classifiers": [{"path": "site/dist", "artifact_class": "deployment_generated"}]}
        self.assertEqual("deployment_generated", self.audit.classify_path("site/dist/index.html", policy))

    def test_drift_audit_classifies_audit_generated_output(self) -> None:
        policy = {"classifiers": [{"path": "control/audits", "artifact_class": "audit_generated"}]}
        self.assertEqual(
            "audit_generated",
            self.audit.classify_path("control/audits/r0-remediation/generated/sample.json", policy),
        )

    def test_drift_audit_detects_modified_generated_file_from_status(self) -> None:
        policy = {"classifiers": [{"path": "site/dist", "artifact_class": "deployment_generated"}]}
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "site/dist").mkdir(parents=True)
            (root / "site/dist/index.html").write_text("x", encoding="utf-8")
            report = self.audit.build_report(
                root,
                policy,
                baseline={"site/dist/index.html": "old"},
            )
        self.assertTrue(report["drift_detected"])
        self.assertEqual("deployment_generated", report["drift_paths"][0]["artifact_class"])

    def test_repair_script_defaults_to_dry_run_payload(self) -> None:
        result = self.repair.build_repair_result({"drift_paths": []}, apply=False)
        self.assertEqual("dry_run", result["mode"])
        self.assertEqual(0, result["safe_repairs_applied"])

    def test_repair_script_refuses_forbidden_output_roots(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(SystemExit):
                self.repair.resolve_output(Path(tmp), Path("site/dist/repair.json"))

    def test_repair_script_creates_child_task_for_unsafe_class(self) -> None:
        result = self.repair.build_repair_result(
            {"drift_paths": [{"path": "generated/unknown.json", "artifact_class": "unknown"}]},
            apply=True,
        )
        self.assertEqual("partial", result["status"])
        self.assertTrue(result["child_tasks"])

    def test_validator_passes_current_repo_after_outputs_exist(self) -> None:
        validator = load_module(VALIDATOR_SCRIPT, "validate_generated_artifact_drift")
        result = validator.validate(ROOT)
        self.assertIn(result["status"], {"pass", "fail"})


if __name__ == "__main__":
    unittest.main()
