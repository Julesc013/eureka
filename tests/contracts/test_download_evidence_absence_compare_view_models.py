from __future__ import annotations

import copy
import json
from pathlib import Path
import unittest

from scripts.validate_download_evidence_absence_compare_view_models import (
    ABSENCE_EXAMPLE_PATHS,
    COMPARE_EXAMPLE_PATHS,
    DOWNLOAD_EXAMPLE_PATHS,
    EVIDENCE_EXAMPLE_PATHS,
    validate_download_evidence_absence_compare_view_models,
    validate_payloads,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
PUBLICATION_DIR = REPO_ROOT / "control" / "inventory" / "publication"


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def load_payloads() -> tuple[dict, dict, dict, dict, dict, dict, dict, list[dict], list[dict], list[dict], list[dict]]:
    return (
        load_json(PUBLICATION_DIR / "download_manifest_view_model_policy.json"),
        load_json(PUBLICATION_DIR / "evidence_page_view_model_policy.json"),
        load_json(PUBLICATION_DIR / "absence_page_view_model_policy.json"),
        load_json(PUBLICATION_DIR / "compare_page_view_model_policy.json"),
        load_json(PUBLICATION_DIR / "representation_profiles.json"),
        load_json(PUBLICATION_DIR / "semantic_renderer_parity_policy.json"),
        load_json(PUBLICATION_DIR / "route_view_representation_matrix.json"),
        [load_json(REPO_ROOT / relative) for relative in DOWNLOAD_EXAMPLE_PATHS],
        [load_json(REPO_ROOT / relative) for relative in EVIDENCE_EXAMPLE_PATHS],
        [load_json(REPO_ROOT / relative) for relative in ABSENCE_EXAMPLE_PATHS],
        [load_json(REPO_ROOT / relative) for relative in COMPARE_EXAMPLE_PATHS],
    )


def validate_with(
    download_policy: dict,
    evidence_policy: dict,
    absence_policy: dict,
    compare_policy: dict,
    representations: dict,
    semantic: dict,
    route_matrix: dict,
    downloads: list[dict],
    evidences: list[dict],
    absences: list[dict],
    compares: list[dict],
) -> list[str]:
    return validate_payloads(
        download_policy,
        evidence_policy,
        absence_policy,
        compare_policy,
        representations,
        semantic,
        route_matrix,
        downloads,
        evidences,
        absences,
        compares,
        source_label="unit",
    )


class DownloadEvidenceAbsenceCompareViewModelContractsTest(unittest.TestCase):
    def test_valid_download_manifest_examples_pass(self) -> None:
        report = validate_download_evidence_absence_compare_view_models(REPO_ROOT)

        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["errors"], [])
        self.assertEqual(report["download_example_count"], 3)

    def test_valid_evidence_page_examples_pass(self) -> None:
        report = validate_download_evidence_absence_compare_view_models(REPO_ROOT)

        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["errors"], [])
        self.assertEqual(report["evidence_example_count"], 4)

    def test_valid_absence_page_examples_pass(self) -> None:
        report = validate_download_evidence_absence_compare_view_models(REPO_ROOT)

        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["errors"], [])
        self.assertEqual(report["absence_example_count"], 4)

    def test_valid_compare_page_examples_pass(self) -> None:
        report = validate_download_evidence_absence_compare_view_models(REPO_ROOT)

        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["errors"], [])
        self.assertEqual(report["compare_example_count"], 4)

    def test_missing_canonical_manifest_identity_fails(self) -> None:
        download_policy, evidence_policy, absence_policy, compare_policy, representations, semantic, route_matrix, downloads, evidences, absences, compares = load_payloads()
        downloads = copy.deepcopy(downloads)
        downloads[0]["manifest_identity"]["manifest_id"] = ""

        errors = validate_with(download_policy, evidence_policy, absence_policy, compare_policy, representations, semantic, route_matrix, downloads, evidences, absences, compares)

        self.assertTrue(any("canonical manifest identity manifest_id" in error for error in errors))

    def test_missing_canonical_evidence_identity_fails(self) -> None:
        download_policy, evidence_policy, absence_policy, compare_policy, representations, semantic, route_matrix, downloads, evidences, absences, compares = load_payloads()
        evidences = copy.deepcopy(evidences)
        evidences[0]["evidence_identity"]["evidence_id"] = ""

        errors = validate_with(download_policy, evidence_policy, absence_policy, compare_policy, representations, semantic, route_matrix, downloads, evidences, absences, compares)

        self.assertTrue(any("canonical evidence identity evidence_id" in error for error in errors))

    def test_missing_canonical_absence_identity_fails(self) -> None:
        download_policy, evidence_policy, absence_policy, compare_policy, representations, semantic, route_matrix, downloads, evidences, absences, compares = load_payloads()
        absences = copy.deepcopy(absences)
        absences[0]["absence_identity"]["absence_id"] = ""

        errors = validate_with(download_policy, evidence_policy, absence_policy, compare_policy, representations, semantic, route_matrix, downloads, evidences, absences, compares)

        self.assertTrue(any("canonical absence identity absence_id" in error for error in errors))

    def test_missing_canonical_comparison_identity_fails(self) -> None:
        download_policy, evidence_policy, absence_policy, compare_policy, representations, semantic, route_matrix, downloads, evidences, absences, compares = load_payloads()
        compares = copy.deepcopy(compares)
        compares[0]["comparison_identity"]["comparison_id"] = ""

        errors = validate_with(download_policy, evidence_policy, absence_policy, compare_policy, representations, semantic, route_matrix, downloads, evidences, absences, compares)

        self.assertTrue(any("canonical comparison identity comparison_id" in error for error in errors))

    def test_invalid_representation_profile_reference_fails(self) -> None:
        download_policy, evidence_policy, absence_policy, compare_policy, representations, semantic, route_matrix, downloads, evidences, absences, compares = load_payloads()
        download_policy = copy.deepcopy(download_policy)
        download_policy["allowed_representation_profiles"].append("missing_profile")

        errors = validate_with(download_policy, evidence_policy, absence_policy, compare_policy, representations, semantic, route_matrix, downloads, evidences, absences, compares)

        self.assertTrue(any("missing_profile" in error for error in errors))

    def test_invalid_semantic_parity_policy_reference_fails(self) -> None:
        download_policy, evidence_policy, absence_policy, compare_policy, representations, semantic, route_matrix, downloads, evidences, absences, compares = load_payloads()
        evidence_policy = copy.deepcopy(evidence_policy)
        evidence_policy["required_semantic_parity_policy"] = "missing_parity_policy"

        errors = validate_with(download_policy, evidence_policy, absence_policy, compare_policy, representations, semantic, route_matrix, downloads, evidences, absences, compares)

        self.assertTrue(any("required_semantic_parity_policy" in error for error in errors))

    def test_invalid_manifest_status_fails(self) -> None:
        download_policy, evidence_policy, absence_policy, compare_policy, representations, semantic, route_matrix, downloads, evidences, absences, compares = load_payloads()
        downloads = copy.deepcopy(downloads)
        downloads[0]["manifest_identity"]["manifest_status"] = "active_download"

        errors = validate_with(download_policy, evidence_policy, absence_policy, compare_policy, representations, semantic, route_matrix, downloads, evidences, absences, compares)

        self.assertTrue(any("manifest_status" in error for error in errors))

    def test_invalid_evidence_status_fails(self) -> None:
        download_policy, evidence_policy, absence_policy, compare_policy, representations, semantic, route_matrix, downloads, evidences, absences, compares = load_payloads()
        evidences = copy.deepcopy(evidences)
        evidences[0]["evidence_status"] = "verified_now"

        errors = validate_with(download_policy, evidence_policy, absence_policy, compare_policy, representations, semantic, route_matrix, downloads, evidences, absences, compares)

        self.assertTrue(any("evidence_status" in error for error in errors))

    def test_invalid_absence_status_fails(self) -> None:
        download_policy, evidence_policy, absence_policy, compare_policy, representations, semantic, route_matrix, downloads, evidences, absences, compares = load_payloads()
        absences = copy.deepcopy(absences)
        absences[0]["absence_status"] = "globally_absent"

        errors = validate_with(download_policy, evidence_policy, absence_policy, compare_policy, representations, semantic, route_matrix, downloads, evidences, absences, compares)

        self.assertTrue(any("absence_status" in error for error in errors))

    def test_invalid_comparison_status_fails(self) -> None:
        download_policy, evidence_policy, absence_policy, compare_policy, representations, semantic, route_matrix, downloads, evidences, absences, compares = load_payloads()
        compares = copy.deepcopy(compares)
        compares[0]["comparison_status"] = "merged"

        errors = validate_with(download_policy, evidence_policy, absence_policy, compare_policy, representations, semantic, route_matrix, downloads, evidences, absences, compares)

        self.assertTrue(any("comparison_status" in error for error in errors))

    def test_download_install_execution_package_manager_claim_fails(self) -> None:
        download_policy, evidence_policy, absence_policy, compare_policy, representations, semantic, route_matrix, downloads, evidences, absences, compares = load_payloads()
        downloads = copy.deepcopy(downloads)
        access = downloads[0]["access_path_summary"]
        access["direct_download_status"] = "available"
        access["install_status"] = "available"
        access["execution_status"] = "available"
        access["package_manager_status"] = "available"

        errors = validate_with(download_policy, evidence_policy, absence_policy, compare_policy, representations, semantic, route_matrix, downloads, evidences, absences, compares)

        self.assertTrue(any("direct_download_status" in error for error in errors))
        self.assertTrue(any("install_status" in error for error in errors))
        self.assertTrue(any("execution_status" in error for error in errors))
        self.assertTrue(any("package_manager_status" in error for error in errors))

    def test_evidence_candidate_marked_accepted_truth_fails(self) -> None:
        download_policy, evidence_policy, absence_policy, compare_policy, representations, semantic, route_matrix, downloads, evidences, absences, compares = load_payloads()
        evidences = copy.deepcopy(evidences)
        evidences[0]["review_summary"]["evidence_candidate_accepted_as_truth"] = True

        errors = validate_with(download_policy, evidence_policy, absence_policy, compare_policy, representations, semantic, route_matrix, downloads, evidences, absences, compares)

        self.assertTrue(any("evidence candidate" in error for error in errors))

    def test_ai_draft_marked_evidence_truth_fails(self) -> None:
        download_policy, evidence_policy, absence_policy, compare_policy, representations, semantic, route_matrix, downloads, evidences, absences, compares = load_payloads()
        evidences = copy.deepcopy(evidences)
        evidences[0]["evidence_type"] = "ai_draft_future"
        evidences[0]["provenance_summary"]["ai_draft_marked_evidence_truth"] = True

        errors = validate_with(download_policy, evidence_policy, absence_policy, compare_policy, representations, semantic, route_matrix, downloads, evidences, absences, compares)

        self.assertTrue(any("AI draft" in error for error in errors))

    def test_absence_claiming_exhaustive_global_search_fails(self) -> None:
        download_policy, evidence_policy, absence_policy, compare_policy, representations, semantic, route_matrix, downloads, evidences, absences, compares = load_payloads()
        absences = copy.deepcopy(absences)
        absences[0]["searched_scope"]["exhaustive_global_search_claimed"] = True

        errors = validate_with(download_policy, evidence_policy, absence_policy, compare_policy, representations, semantic, route_matrix, downloads, evidences, absences, compares)

        self.assertTrue(any("exhaustive_global_search_claimed" in error for error in errors))

    def test_compare_automatic_merge_dedup_promotion_claim_fails(self) -> None:
        download_policy, evidence_policy, absence_policy, compare_policy, representations, semantic, route_matrix, downloads, evidences, absences, compares = load_payloads()
        compares = copy.deepcopy(compares)
        compares[0]["deduplication_summary"]["automatic_merge_enabled"] = True
        compares[0]["deduplication_summary"]["automatic_dedup_enabled"] = True
        compares[0]["deduplication_summary"]["automatic_promotion_enabled"] = True

        errors = validate_with(download_policy, evidence_policy, absence_policy, compare_policy, representations, semantic, route_matrix, downloads, evidences, absences, compares)

        self.assertTrue(any("automatic_merge_enabled" in error for error in errors))
        self.assertTrue(any("automatic_dedup_enabled" in error for error in errors))
        self.assertTrue(any("automatic_promotion_enabled" in error for error in errors))

    def test_current_example_claiming_runtime_capability_fails(self) -> None:
        download_policy, evidence_policy, absence_policy, compare_policy, representations, semantic, route_matrix, downloads, evidences, absences, compares = load_payloads()
        evidences = copy.deepcopy(evidences)
        summary = evidences[0]["action_summary"]
        summary["hosted_backend_claimed"] = True
        summary["live_probes_enabled"] = True
        summary["source_sync_runtime_enabled"] = True
        summary["downloads_enabled"] = True
        summary["uploads_enabled"] = True
        summary["accounts_enabled"] = True
        summary["telemetry_enabled"] = True

        errors = validate_with(download_policy, evidence_policy, absence_policy, compare_policy, representations, semantic, route_matrix, downloads, evidences, absences, compares)

        self.assertTrue(any("hosted_backend_claimed" in error for error in errors))
        self.assertTrue(any("live_probes_enabled" in error for error in errors))
        self.assertTrue(any("source_sync_runtime_enabled" in error for error in errors))
        self.assertTrue(any("downloads_enabled" in error for error in errors))
        self.assertTrue(any("uploads_enabled" in error for error in errors))
        self.assertTrue(any("accounts_enabled" in error for error in errors))
        self.assertTrue(any("telemetry_enabled" in error for error in errors))

    def test_rights_malware_installability_safe_execution_claim_fails(self) -> None:
        download_policy, evidence_policy, absence_policy, compare_policy, representations, semantic, route_matrix, downloads, evidences, absences, compares = load_payloads()
        downloads = copy.deepcopy(downloads)
        downloads[0]["rights_summary"]["rights_clearance_claimed"] = True
        downloads[0]["risk_summary"]["malware_safety_claimed"] = True
        downloads[0]["risk_summary"]["verified_installability_claimed"] = True
        downloads[0]["risk_summary"]["safe_execution_claimed"] = True

        errors = validate_with(download_policy, evidence_policy, absence_policy, compare_policy, representations, semantic, route_matrix, downloads, evidences, absences, compares)

        self.assertTrue(any("rights clearance" in error for error in errors))
        self.assertTrue(any("malware safety" in error for error in errors))
        self.assertTrue(any("verified installability" in error for error in errors))
        self.assertTrue(any("safe execution" in error for error in errors))

    def test_missing_blocked_action_for_unavailable_capability_fails(self) -> None:
        download_policy, evidence_policy, absence_policy, compare_policy, representations, semantic, route_matrix, downloads, evidences, absences, compares = load_payloads()
        compares = copy.deepcopy(compares)
        compares[0]["blocked_actions"] = [
            action
            for action in compares[0]["blocked_actions"]
            if action["action_id"] != "master_index_mutation_unavailable"
        ]

        errors = validate_with(download_policy, evidence_policy, absence_policy, compare_policy, representations, semantic, route_matrix, downloads, evidences, absences, compares)

        self.assertTrue(any("master_index_mutation_unavailable" in error for error in errors))

    def test_policy_inventories_validate(self) -> None:
        download_policy, evidence_policy, absence_policy, compare_policy, representations, semantic, route_matrix, downloads, evidences, absences, compares = load_payloads()

        errors = validate_with(download_policy, evidence_policy, absence_policy, compare_policy, representations, semantic, route_matrix, downloads, evidences, absences, compares)

        self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
