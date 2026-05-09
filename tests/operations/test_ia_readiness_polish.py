import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "scripts" / "validate_ia_readiness_polish.py"


def load_module():
    spec = importlib.util.spec_from_file_location("validate_ia_readiness_polish", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


validator = load_module()


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def write_json(path: Path, payload) -> None:
    write_text(path, json.dumps(payload, indent=2, sort_keys=True) + "\n")


class IAReadinessPolishTest(unittest.TestCase):
    def make_fixture(self, root: Path) -> dict:
        audit = root / "control/audits/ia-bundle-00-readiness-polish-v0"
        write_text(audit / "README.md", "IA-BUNDLE-00 readiness polish\n")
        write_text(audit / "track_b_warning_closure.md", "warnings classified\n")
        write_text(
            audit / "evidence_contract_location_decision.md",
            "Decision: create contracts/evidence/ as a minimal pointer namespace.\n",
        )
        write_text(
            audit / "ia_connector_readiness_checklist.md",
            "\n".join(
                [
                    "IA-BUNDLE-00 does not approve source access.",
                    "IA-BUNDLE-00 does not perform external calls.",
                    "IA-BUNDLE-00 does not enable a connector.",
                    "source policy approval required",
                    "User-Agent/contact decision required",
                    "metadata-only live probe pending",
                    "reviewed-index dry-run pending",
                ]
            ),
        )
        write_text(
            audit / "ia_bundle_sequence.md",
            "\n".join(
                [
                    "IA-BUNDLE-01 - IA Metadata Connector Foundation",
                    "IA-BUNDLE-02 - IA Bounded Metadata Live Probe",
                    "IA-BUNDLE-03 - IA Reviewed-Index Dry-Run And Postmortem",
                    "source family",
                    "source capability ladder",
                    "source policy gate",
                    "fixture/replay harness",
                    "live-probe envelope",
                    "source cache",
                    "evidence candidate bridge",
                    "review queue",
                    "coverage ledger future",
                    "connector scorecard future",
                ]
            ),
        )
        write_text(audit / "validation.md", "pending\n")
        write_text(
            root / ".aide/context/latest-task-packet.md",
            "\n".join(
                [
                    "# AIDE Latest Task Packet",
                    "## PHASE",
                    "IA-BUNDLE-01 - IA metadata connector foundation",
                    "## GOAL",
                    "Main lane IA-BUNDLE-01; HUMAN-OBS-REVIEW-01 is a parallel side-lane.",
                ]
            ),
        )
        write_text(root / "contracts/evidence/README.md", "pointer namespace\n")
        index = {
            "boundary": {
                "evidence_runtime_implemented": False,
                "source_cache_write_enabled": False,
                "evidence_ledger_write_enabled": False,
                "candidate_acceptance_enabled": False,
                "evidence_truth_acceptance_enabled": False,
                "public_truth_acceptance_enabled": False,
                "public_index_mutation_allowed": False,
                "master_index_mutation_allowed": False,
                "live_source_access_allowed": False,
                "telemetry_enabled": False,
                "credentials_configured": False,
            }
        }
        write_json(root / "contracts/evidence/evidence_contract_index.v0.json", index)
        report = {
            "schema_version": "ia_bundle_00_report.v0",
            "status": "pass",
            "task": "IA-BUNDLE-00",
            "track": "IA",
            "first_connector_readiness_after": "READY_FOR_IA_BUNDLE_01",
            "side_lanes": {"human_obs_review": "parallel_side_lane"},
            "warnings_closed_or_classified": [],
            "evidence_contract_location": {"decision": "created_contracts_evidence", "notes": []},
            "ia_gates": {
                "source_policy_approved": False,
                "user_agent_contact_decided": False,
                "allowed_endpoints_decided": False,
                "forbidden_endpoints_decided": False,
                "rate_limit_decided": False,
                "timeout_retry_decided": False,
                "cache_ttl_decided": False,
                "kill_switch_decided": False,
                "fixture_normalizer_implemented": False,
                "metadata_only_live_probe_approved": False,
                "live_probe_enabled": False,
                "connector_runtime_enabled": False,
            },
            "product_boundary": {
                "changed_product_behavior": False,
                "called_external_source": False,
                "enabled_live_probes": False,
                "enabled_source_sync": False,
                "enabled_source_connectors": False,
                "enabled_downloads": False,
                "enabled_uploads": False,
                "enabled_accounts": False,
                "enabled_telemetry": False,
                "enabled_hosting": False,
                "enabled_pack_import": False,
                "enabled_hosted_review": False,
                "mutated_source_cache": False,
                "mutated_evidence_ledger": False,
                "mutated_candidate_index": False,
                "mutated_public_index": False,
                "mutated_master_index": False,
            },
            "truth_boundary": {
                "accepted_evidence_truth": False,
                "accepted_candidate_truth": False,
                "accepted_public_truth": False,
                "claimed_rights_clearance": False,
                "claimed_malware_safety": False,
                "claimed_verified_installability": False,
                "claimed_exhaustive_search": False,
                "claimed_production_readiness": False,
            },
            "next_task": "IA-BUNDLE-01 - IA metadata connector foundation",
        }
        write_json(audit / "ia_bundle_00_report.json", report)
        return report

    def test_validator_passes_current_repo(self):
        result = validator.validate_repo(REPO_ROOT)
        self.assertEqual(result["status"], "valid", result["errors"])

    def test_missing_readiness_checklist_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_fixture(root)
            (root / "control/audits/ia-bundle-00-readiness-polish-v0/ia_connector_readiness_checklist.md").unlink()
            result = validator.validate_repo(root)
            self.assertEqual(result["status"], "invalid")
            self.assertTrue(any("ia_connector_readiness_checklist.md" in error for error in result["errors"]))

    def test_latest_task_packet_only_sync_baseline_fails(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_fixture(root)
            write_text(
                root / ".aide/context/latest-task-packet.md",
                "# AIDE Latest Task Packet\n## PHASE\nSYNC-BASELINE-01 - Canonical branch baseline\n## GOAL\nProceed to sync baseline\n",
            )
            result = validator.validate_repo(root)
            self.assertEqual(result["status"], "invalid")
            self.assertTrue(any("IA-BUNDLE-01" in error or "SYNC-BASELINE-01" in error for error in result["errors"]))

    def test_latest_task_packet_h0_progression_passes(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_fixture(root)
            write_text(
                root / ".aide/context/latest-task-packet.md",
                "\n".join(
                    [
                        "# AIDE Latest Task Packet",
                        "## PHASE",
                        "H0-BUNDLE-01 - Source OS registry and policy foundation",
                        "## GOAL",
                        "Main development lane proceeds to H0-BUNDLE-01 after IA-BUNDLE-03; HUMAN-OBS-REVIEW-01 is a parallel side-lane.",
                    ]
                ),
            )
            result = validator.validate_repo(root)
            self.assertEqual(result["status"], "valid", result["errors"])

    def assert_report_claim_fails(self, path_parts, value=True):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            report = self.make_fixture(root)
            target = report
            for part in path_parts[:-1]:
                target = target[part]
            target[path_parts[-1]] = value
            write_json(root / "control/audits/ia-bundle-00-readiness-polish-v0/ia_bundle_00_report.json", report)
            result = validator.validate_repo(root)
            self.assertEqual(result["status"], "invalid")
            self.assertTrue(any(path_parts[-1] in error for error in result["errors"]), result["errors"])

    def test_ia_live_access_approval_claim_fails(self):
        self.assert_report_claim_fails(["ia_gates", "source_policy_approved"])

    def test_live_probe_enabled_claim_fails(self):
        self.assert_report_claim_fails(["ia_gates", "live_probe_enabled"])

    def test_connector_runtime_enabled_claim_fails(self):
        self.assert_report_claim_fails(["ia_gates", "connector_runtime_enabled"])

    def test_public_index_mutation_claim_fails(self):
        self.assert_report_claim_fails(["product_boundary", "mutated_public_index"])

    def test_master_index_mutation_claim_fails(self):
        self.assert_report_claim_fails(["product_boundary", "mutated_master_index"])

    def test_hosted_download_upload_account_telemetry_claims_fail(self):
        for key in ("enabled_hosting", "enabled_downloads", "enabled_uploads", "enabled_accounts", "enabled_telemetry"):
            with self.subTest(key=key):
                self.assert_report_claim_fails(["product_boundary", key])

    def test_validator_does_not_call_network_model_or_provider(self):
        text = SCRIPT.read_text(encoding="utf-8")
        banned = ("requests", "urllib", "http.client", "socket", "ftplib", "smtplib", "webbrowser", "openai")
        for phrase in banned:
            self.assertNotIn(phrase, text)

    def test_validator_does_not_mutate_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.make_fixture(root)
            before = {
                path.relative_to(root).as_posix(): path.read_bytes()
                for path in root.rglob("*")
                if path.is_file()
            }
            result = validator.validate_repo(root)
            after = {
                path.relative_to(root).as_posix(): path.read_bytes()
                for path in root.rglob("*")
                if path.is_file()
            }
            self.assertEqual(result["status"], "valid", result["errors"])
            self.assertEqual(before, after)


if __name__ == "__main__":
    unittest.main()
