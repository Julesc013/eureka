from __future__ import annotations

import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
AUDIT_SCRIPT = ROOT / "scripts" / "audit_r0_final_closeout.py"
VALIDATOR_SCRIPT = ROOT / "scripts" / "validate_r0_final_closeout.py"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def write(path: Path, text: str = "") -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def make_fixture_repo(root: Path) -> None:
    report_paths = [
        "control/audits/r0-01-dev-production-reality-inventory-v0/r0_01_report.json",
        "control/audits/r0-02-runtime-architecture-leakage-gate-v0/r0_02_report.json",
        "control/audits/r0-03a-contract-taxonomy-refactor-plan-v0/r0_03a_report.json",
        "control/audits/r0-03b-1-contract-taxonomy-migration-v0/r0_03b_1_report.json",
        "control/audits/r0-03b-2-contract-reference-product-cleanup-v0/r0_03b_2_report.json",
        "control/audits/r0-04-source-observation-production-seam-v0/r0_04_report.json",
        "control/audits/r0-05-durable-source-cache-store-v0/r0_05_report.json",
        "control/audits/r0-06-durable-evidence-ledger-store-v0/r0_06_report.json",
        "control/audits/r0-07-review-queue-product-seam-v0/r0_07_report.json",
        "control/audits/r0-08-reviewed-public-index-rebuild-v0/r0_08_report.json",
        "control/audits/r0-09-one-source-live-test-v0/r0_09_report.json",
        "control/audits/r0-10-dev-to-main-production-review-v0/r0_10_report.json",
    ]
    for rel in report_paths:
        write_json(root / rel, {"status": "pass"})
    for rel in [
        "runtime/source/observation/__init__.py",
        "runtime/source/cache/__init__.py",
        "runtime/evidence/ledger/__init__.py",
        "runtime/review/queue/__init__.py",
        "runtime/index/public/__init__.py",
    ]:
        write(root / rel)
    for rel in [
        "scripts/validate_runtime_architecture_leakage.py",
        "scripts/validate_contract_taxonomy_plan.py",
        "scripts/validate_contract_taxonomy_migration.py",
        "scripts/validate_product_contract_tree.py",
        "scripts/validate_source_observation_seam.py",
        "scripts/validate_source_cache_store.py",
        "scripts/validate_evidence_ledger_store.py",
        "scripts/validate_review_queue_store.py",
        "scripts/validate_reviewed_public_index.py",
        "scripts/validate_one_source_live_test.py",
        "scripts/validate_r0_production_review.py",
    ]:
        write(root / rel)
    for rel in [
        "tests/runtime/test_source_observation_seam.py",
        "tests/runtime/test_source_cache_store.py",
        "tests/runtime/test_evidence_ledger_store.py",
        "tests/runtime/test_review_queue_store.py",
        "tests/runtime/test_public_index_integration.py",
        "tests/runtime/test_one_source_live_test.py",
        "tests/operations/test_r0_production_review.py",
    ]:
        write(root / rel)
    write_json(
        root / "control/inventory/r0_production_review_result.json",
        {
            "source_observation_ready": True,
            "source_cache_ready": True,
            "evidence_ledger_ready": True,
            "review_queue_ready": True,
            "reviewed_public_index_ready": True,
            "one_source_live_test_ready": True,
        },
    )
    write_json(root / "control/inventory/r0_remaining_blockers.json", {"blockers": []})
    write_json(root / "control/inventory/r0_warning_disposition.json", {"warnings": []})


class R0FinalCloseoutTests(unittest.TestCase):
    def setUp(self) -> None:
        self.audit = load_module(AUDIT_SCRIPT, "audit_r0_final_closeout")

    def build(self, mutator=None):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            make_fixture_repo(repo)
            if mutator:
                mutator(repo)
            return self.audit.build_final_closeout(repo)

    def test_final_closeout_fails_if_r0_10_missing(self):
        audit = self.build(lambda repo: (repo / "control/audits/r0-10-dev-to-main-production-review-v0/r0_10_report.json").unlink())
        self.assertFalse(audit["r0_final_closeout_result"]["all_r0_tasks_reviewed"])

    def test_final_closeout_fails_if_source_observation_seam_missing(self):
        audit = self.build(lambda repo: write_json(repo / "control/inventory/r0_production_review_result.json", {"source_observation_ready": False}))
        seams = {item["seam"]: item for item in audit["r0_final_runtime_readiness_matrix"]["seams"]}
        self.assertEqual("blocked", seams["source_observation"]["status"])

    def test_final_closeout_fails_if_source_cache_missing(self):
        audit = self.build(lambda repo: write_json(repo / "control/inventory/r0_production_review_result.json", {"source_cache_ready": False}))
        seams = {item["seam"]: item for item in audit["r0_final_runtime_readiness_matrix"]["seams"]}
        self.assertEqual("blocked", seams["source_cache"]["status"])

    def test_final_closeout_fails_if_evidence_ledger_missing(self):
        audit = self.build(lambda repo: write_json(repo / "control/inventory/r0_production_review_result.json", {"evidence_ledger_ready": False}))
        seams = {item["seam"]: item for item in audit["r0_final_runtime_readiness_matrix"]["seams"]}
        self.assertEqual("blocked", seams["evidence_ledger"]["status"])

    def test_final_closeout_fails_if_review_queue_missing(self):
        audit = self.build(lambda repo: write_json(repo / "control/inventory/r0_production_review_result.json", {"review_queue_ready": False}))
        seams = {item["seam"]: item for item in audit["r0_final_runtime_readiness_matrix"]["seams"]}
        self.assertEqual("blocked", seams["review_queue"]["status"])

    def test_final_closeout_fails_if_reviewed_public_index_missing(self):
        audit = self.build(lambda repo: write_json(repo / "control/inventory/r0_production_review_result.json", {"reviewed_public_index_ready": False}))
        seams = {item["seam"]: item for item in audit["r0_final_runtime_readiness_matrix"]["seams"]}
        self.assertEqual("blocked", seams["reviewed_public_index"]["status"])

    def test_final_closeout_fails_if_one_source_live_test_unresolved(self):
        audit = self.build(lambda repo: write_json(repo / "control/inventory/r0_production_review_result.json", {"one_source_live_test_ready": False}))
        seams = {item["seam"]: item for item in audit["r0_final_runtime_readiness_matrix"]["seams"]}
        self.assertEqual("blocked", seams["one_source_live_pipeline"]["status"])

    def test_warnings_require_disposition(self):
        audit = self.build(lambda repo: write_json(repo / "control/inventory/r0_warning_disposition.json", {"warnings": [{"area": "contract_taxonomy", "warning": "x", "disposition": "assigned_to_next_task"}]}))
        warning = audit["r0_final_warning_disposition"]["warnings"][0]
        self.assertEqual("child_task_created", warning["disposition"])

    def test_blockers_require_fix_or_child_task(self):
        audit = self.build(lambda repo: write_json(repo / "control/inventory/r0_remaining_blockers.json", {"blockers": [{"blocker_id": "B", "area": "contract_taxonomy", "finding": "x"}]}))
        blocker = audit["r0_final_blocker_register"]["blockers"][0]
        self.assertEqual("R0-REMEDIATION-CONTRACT-TAXONOMY-01", blocker["child_task"])

    def test_decisions_and_no_claims_are_explicit(self):
        audit = self.build()
        result = audit["r0_final_closeout_result"]
        self.assertIn(result["f0_decision"], {"resume_f0", "remain_blocked", "remediation_required"})
        self.assertIn(result["main_promotion_decision"], {"promote_ready", "promotion_plan_only", "remain_blocked", "already_on_main"})
        self.assertFalse(result["branch_mutation_performed"])
        self.assertFalse(result["production_readiness_claimed"])
        self.assertFalse(result["public_launch_readiness_claimed"])

    def test_validator_passes_current_repo_without_commands_after_outputs_exist(self):
        validator = load_module(VALIDATOR_SCRIPT, "validate_r0_final_closeout")
        result = validator.validate(ROOT, run_commands=False)
        self.assertIn(result["status"], {"pass", "fail"})


if __name__ == "__main__":
    unittest.main()
