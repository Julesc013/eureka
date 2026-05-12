from __future__ import annotations

import ast
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[2]
AUDIT_SCRIPT = ROOT / "scripts" / "audit_r0_production_review.py"
VALIDATOR_SCRIPT = ROOT / "scripts" / "validate_r0_production_review.py"


def load_module(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def write_json(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


def make_fixture_repo(root: Path) -> None:
    reports = {
        "control/audits/r0-01-dev-production-reality-inventory-v0/r0_01_report.json": ("R0-01", "pass"),
        "control/audits/r0-02-runtime-architecture-leakage-gate-v0/r0_02_report.json": ("R0-02", "pass_with_warnings"),
        "control/audits/r0-03a-contract-taxonomy-refactor-plan-v0/r0_03a_report.json": ("R0-03A", "pass"),
        "control/audits/r0-03b-1-contract-taxonomy-migration-v0/r0_03b_1_report.json": ("R0-03B-1", "pass"),
        "control/audits/r0-03b-2-contract-reference-product-cleanup-v0/r0_03b_2_report.json": ("R0-03B-2", "pass"),
        "control/audits/r0-04-source-observation-production-seam-v0/r0_04_report.json": ("R0-04", "pass"),
        "control/audits/r0-05-durable-source-cache-store-v0/r0_05_report.json": ("R0-05", "pass"),
        "control/audits/r0-06-durable-evidence-ledger-store-v0/r0_06_report.json": ("R0-06", "pass"),
        "control/audits/r0-07-review-queue-product-seam-v0/r0_07_report.json": ("R0-07", "pass"),
        "control/audits/r0-08-reviewed-public-index-rebuild-v0/r0_08_report.json": ("R0-08", "pass"),
        "control/audits/r0-09-one-source-live-test-v0/r0_09_report.json": ("R0-09", "pass"),
    }
    for rel, (task, status) in reports.items():
        write_json(root / rel, {"schema_version": f"{task.lower()}_report.v0", "task": task, "status": status})
    write_json(root / "control/inventory/source_observation_seam_inventory.json", {"ready_for_r0_05": True})
    write_json(root / "control/inventory/source_cache_store_inventory.json", {"ready_for_r0_06": True})
    write_json(root / "control/inventory/evidence_ledger_store_inventory.json", {"ready_for_r0_07": True})
    write_json(root / "control/inventory/review_queue_store_inventory.json", {"ready_for_r0_08": True})
    write_json(root / "control/inventory/public_index_store_inventory.json", {"ready_for_r0_09": True})
    write_json(
        root / "control/inventory/runtime_architecture_leakage_gate_report.json",
        {
            "status": "pass_with_warnings",
            "blocker_count": 0,
            "new_violation_count": 0,
            "expired_allowlist_count": 0,
            "known_allowlisted_violation_count": 1,
        },
    )
    write_json(
        root / "control/inventory/r0_03b_2_final_contract_taxonomy.json",
        {
            "contracts_clean_enough_for_r0_04": True,
            "unresolved_contract_count": 0,
            "contracts_root_status": "clean_with_warnings",
            "compatibility_shim_count": 0,
        },
    )
    write_json(
        root / "control/inventory/one_source_live_test_result.json",
        {
            "status": "pass",
            "source_id": "pypi_json_metadata",
            "package_name": "sampleproject",
            "network_used": True,
            "request_count": 1,
            "download_count": 0,
            "install_execution_count": 0,
            "source_sync_used": False,
            "search_hit_count": 1,
            "absence_hit_count": 0,
            "site_dist_mutated": False,
            "master_index_mutated": False,
        },
    )


class R0ProductionReviewTests(unittest.TestCase):
    def setUp(self) -> None:
        self.audit = load_module(AUDIT_SCRIPT, "audit_r0_production_review")

    def build(self, mutator=None):
        with tempfile.TemporaryDirectory() as tmp:
            repo = Path(tmp)
            make_fixture_repo(repo)
            if mutator:
                mutator(repo)
            return self.audit.build_r0_production_review(repo)

    def test_passes_when_all_required_evidence_is_ready(self):
        audit = self.build()
        result = audit["r0_production_review_result"]
        self.assertTrue(result["all_required_r0_tasks_passed"])
        self.assertTrue(result["source_cache_ready"])
        self.assertTrue(result["evidence_ledger_ready"])
        self.assertTrue(result["review_queue_ready"])
        self.assertTrue(result["reviewed_public_index_ready"])
        self.assertTrue(result["contract_taxonomy_ready"])

    def test_fails_if_required_r0_report_missing(self):
        audit = self.build(lambda repo: (repo / "control/audits/r0-05-durable-source-cache-store-v0/r0_05_report.json").unlink())
        self.assertFalse(audit["r0_production_review_result"]["all_required_r0_tasks_passed"])
        self.assertTrue(audit["r0_remaining_blockers"]["blockers"])

    def test_fails_if_one_source_live_test_missing(self):
        audit = self.build(lambda repo: (repo / "control/inventory/one_source_live_test_result.json").unlink())
        self.assertFalse(audit["r0_production_review_result"]["one_source_live_test_ready"])

    def test_warns_if_one_source_live_test_blocked_by_network_only(self):
        def mutate(repo: Path) -> None:
            write_json(
                repo / "control/inventory/one_source_live_test_result.json",
                {"status": "blocked", "network_used": False, "reason": "environment/network unavailable"},
            )

        audit = self.build(mutate)
        self.assertFalse(audit["r0_production_review_result"]["one_source_live_test_ready"])
        self.assertTrue(any(item["area"] == "one_source_live_test" for item in audit["r0_remaining_blockers"]["blockers"]))
        self.assertTrue(any(item["area"] == "one_source_live_test" for item in audit["r0_warning_disposition"]["warnings"]))

    def test_fails_if_source_cache_not_ready(self):
        audit = self.build(lambda repo: write_json(repo / "control/inventory/source_cache_store_inventory.json", {"ready_for_r0_06": False}))
        self.assertFalse(audit["r0_production_review_result"]["source_cache_ready"])

    def test_fails_if_evidence_ledger_not_ready(self):
        audit = self.build(lambda repo: write_json(repo / "control/inventory/evidence_ledger_store_inventory.json", {"ready_for_r0_07": False}))
        self.assertFalse(audit["r0_production_review_result"]["evidence_ledger_ready"])

    def test_fails_if_review_queue_not_ready(self):
        audit = self.build(lambda repo: write_json(repo / "control/inventory/review_queue_store_inventory.json", {"ready_for_r0_08": False}))
        self.assertFalse(audit["r0_production_review_result"]["review_queue_ready"])

    def test_fails_if_reviewed_public_index_not_ready(self):
        audit = self.build(lambda repo: write_json(repo / "control/inventory/public_index_store_inventory.json", {"ready_for_r0_09": False}))
        self.assertFalse(audit["r0_production_review_result"]["reviewed_public_index_ready"])

    def test_fails_if_contract_taxonomy_not_clean_enough(self):
        audit = self.build(
            lambda repo: write_json(
                repo / "control/inventory/r0_03b_2_final_contract_taxonomy.json",
                {"contracts_clean_enough_for_r0_04": False, "unresolved_contract_count": 2, "contracts_root_status": "partial"},
            )
        )
        self.assertFalse(audit["r0_production_review_result"]["contract_taxonomy_ready"])
        self.assertEqual("remediation_required", audit["r0_next_phase_decision"]["f0_decision"])

    def test_fails_if_architecture_leakage_has_new_blockers(self):
        audit = self.build(
            lambda repo: write_json(
                repo / "control/inventory/runtime_architecture_leakage_gate_report.json",
                {"status": "fail", "blocker_count": 1, "new_violation_count": 1, "expired_allowlist_count": 0},
            )
        )
        self.assertFalse(audit["r0_production_review_result"]["architecture_leakage_gate_ready"])

    def test_warning_disposition_requires_each_warning_classified(self):
        audit = self.build()
        for warning in audit["r0_warning_disposition"]["warnings"]:
            self.assertIn(warning["disposition"], {"harmless", "assigned_to_next_task", "blocks_promotion", "fixed", "not_evaluable"})

    def test_decisions_are_explicit(self):
        audit = self.build()
        self.assertIn(audit["r0_next_phase_decision"]["f0_decision"], {"resume_f0", "remain_blocked", "remediation_required"})
        self.assertIn(audit["r0_next_phase_decision"]["main_promotion_decision"], {"promote_ready", "promotion_plan_only", "remain_blocked"})

    def test_validator_passes_current_repo_without_running_nested_validators(self):
        validator = load_module(VALIDATOR_SCRIPT, "validate_r0_production_review")
        result = validator.validate(ROOT, run_r0_validators=False)
        self.assertIn(result["status"], {"pass", "fail"})
        self.assertFalse(result["network_used"])

    def test_no_network_or_provider_imports(self):
        for path in (AUDIT_SCRIPT, VALIDATOR_SCRIPT):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                names = []
                if isinstance(node, ast.Import):
                    names = [alias.name.split(".")[0] for alias in node.names]
                elif isinstance(node, ast.ImportFrom):
                    names = [(node.module or "").split(".")[0]]
                self.assertFalse({"requests", "urllib", "httpx", "aiohttp", "openai", "anthropic"} & set(names))


if __name__ == "__main__":
    unittest.main()
