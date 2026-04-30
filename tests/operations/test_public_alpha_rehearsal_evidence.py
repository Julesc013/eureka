from __future__ import annotations

from collections import Counter
import json
from pathlib import Path
import re
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
PACK_DIR = REPO_ROOT / "docs" / "operations" / "public_alpha_rehearsal_evidence_v0"
MANIFEST_PATH = PACK_DIR / "rehearsal_evidence_manifest.json"
ROUTE_INVENTORY = REPO_ROOT / "control" / "inventory" / "public_alpha_routes.json"
REQUIRED_FILES = {
    "README.md",
    "REHEARSAL_SCOPE.md",
    "COMMIT_AND_ARTIFACTS.md",
    "STATIC_SITE_EVIDENCE.md",
    "SAFE_MODE_EVIDENCE.md",
    "ROUTE_INVENTORY_EVIDENCE.md",
    "EVAL_AND_AUDIT_EVIDENCE.md",
    "EXTERNAL_BASELINE_STATUS.md",
    "OPERATOR_CHECKLIST_STATUS.md",
    "BLOCKERS_AND_LIMITATIONS.md",
    "NEXT_DEPLOYMENT_REQUIREMENTS.md",
    "SIGNOFF_TEMPLATE.md",
    "rehearsal_evidence_manifest.json",
}


class PublicAlphaRehearsalEvidenceTest(unittest.TestCase):
    def test_pack_directory_and_required_files_exist(self) -> None:
        self.assertTrue(PACK_DIR.is_dir())
        existing = {path.name for path in PACK_DIR.iterdir() if path.is_file()}
        self.assertTrue(REQUIRED_FILES.issubset(existing))

    def test_manifest_records_unsigned_no_deployment_evidence(self) -> None:
        manifest = self._manifest()
        self.assertEqual(manifest["evidence_pack_id"], "public_alpha_rehearsal_evidence_v0")
        self.assertTrue(manifest["no_deployment_performed"])
        self.assertTrue(manifest["no_external_network_required"])
        self.assertEqual(manifest["signoff_status"], "unsigned")
        self.assertRegex(manifest["commit_sha"], re.compile(r"^[0-9a-f]{40}$"))

    def test_manifest_references_current_evidence_sources(self) -> None:
        manifest = self._manifest()
        self.assertEqual(manifest["static_site_pack"]["path"], "site/dist/")
        self.assertEqual(
            manifest["static_site_pack"]["validator_command"],
            "python scripts/validate_public_static_site.py",
        )
        self.assertEqual(manifest["static_site_pack"]["validation_status"], "valid")
        self.assertEqual(
            manifest["route_inventory"]["path"],
            "control/inventory/public_alpha_routes.json",
        )
        self.assertEqual(
            manifest["public_alpha_smoke"]["command"],
            "python scripts/public_alpha_smoke.py",
        )
        self.assertEqual(manifest["public_alpha_smoke"]["status"], "passed")

    def test_manifest_route_eval_and_baseline_counts_are_honest(self) -> None:
        manifest = self._manifest()
        route_counts = manifest["route_inventory"]["route_counts"]
        inventory = json.loads(ROUTE_INVENTORY.read_text(encoding="utf-8"))
        current_counts = Counter(route["classification"] for route in inventory["routes"])
        self.assertEqual(route_counts["safe_public_alpha"], current_counts["safe_public_alpha"])
        self.assertEqual(route_counts["blocked_public_alpha"], current_counts["blocked_public_alpha"])
        self.assertEqual(route_counts["local_dev_only"], current_counts["local_dev_only"])
        self.assertEqual(route_counts["review_required"], current_counts["review_required"])
        self.assertIn("/api/export/manifest", manifest["route_inventory"]["review_required_routes"])

        archive = manifest["eval_audit"]["archive_eval_status"]
        self.assertEqual(archive["task_count"], 6)
        self.assertEqual(archive["status_counts"], {"satisfied": 6})

        search = manifest["eval_audit"]["search_usefulness_status"]
        self.assertEqual(search["query_count"], 64)
        self.assertEqual(search["status_counts"]["source_gap"], 26)
        self.assertEqual(search["status_counts"]["capability_gap"], 9)

        external = manifest["eval_audit"]["external_baseline_status"]
        self.assertEqual(external["global_pending_slots"], 192)
        self.assertEqual(external["global_observed_slots"], 0)
        self.assertEqual(external["batch_0_pending_slots"], 39)
        self.assertEqual(external["batch_0_observed_slots"], 0)

    def test_blockers_and_signoff_remain_explicit(self) -> None:
        manifest = self._manifest()
        blockers = "\n".join(manifest["limitations"]).casefold()
        for phrase in (
            "auth",
            "tls",
            "rate limiting",
            "process manager",
            "live source probes",
            "external baseline observations",
        ):
            self.assertIn(phrase, blockers)

        signoff = (PACK_DIR / "SIGNOFF_TEMPLATE.md").read_text(encoding="utf-8")
        self.assertIn("unsigned/unapproved", signoff)
        self.assertIn("does not approve deployment", signoff)

    def test_docs_do_not_claim_deployment_or_observed_external_baselines(self) -> None:
        combined = "\n".join(
            path.read_text(encoding="utf-8")
            for path in PACK_DIR.glob("*.md")
        ).casefold()
        self.assertNotIn("production ready", combined)
        self.assertNotIn("public deployment completed", combined)
        self.assertNotIn("deployed public site", combined)
        self.assertNotIn("external observations were performed", combined)
        self.assertIn("no public deployment happened", combined)
        self.assertIn("no google or internet archive observations were performed", combined)

    def _manifest(self) -> dict:
        return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
