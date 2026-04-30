from __future__ import annotations

import json
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
AUDIT_DIR = REPO_ROOT / "control" / "audits" / "public-search-rehearsal-v0"
REPORT = AUDIT_DIR / "public_search_rehearsal_report.json"
PUBLIC_ALPHA_ROUTES = REPO_ROOT / "control" / "inventory" / "public_alpha_routes.json"
PUBLIC_SEARCH_ROUTES = (
    REPO_ROOT / "control" / "inventory" / "publication" / "public_search_routes.json"
)
HANDOFF = REPO_ROOT / "control" / "inventory" / "publication" / "public_search_handoff.json"


class PublicSearchRehearsalOperationTest(unittest.TestCase):
    def test_audit_pack_exists(self) -> None:
        required = {
            "README.md",
            "REHEARSAL_SCOPE.md",
            "ROUTE_MATRIX.md",
            "SAFE_QUERY_RESULTS.md",
            "BLOCKED_REQUEST_RESULTS.md",
            "STATIC_HANDOFF_REVIEW.md",
            "PUBLIC_ALPHA_REVIEW.md",
            "CONTRACT_ALIGNMENT_REVIEW.md",
            "LIMITATIONS_AND_BLOCKERS.md",
            "NEXT_STEPS.md",
            "public_search_rehearsal_report.json",
        }
        self.assertTrue(AUDIT_DIR.is_dir())
        self.assertTrue(required.issubset({path.name for path in AUDIT_DIR.iterdir()}))

    def test_report_records_local_rehearsal_pass(self) -> None:
        report = _load_json(REPORT)

        self.assertEqual(report["report_id"], "public_search_rehearsal_v0")
        self.assertEqual(report["decision"], "local_rehearsal_passed")
        self.assertEqual(report["mode"], "local_index_only")
        self.assertEqual(report["hosted_backend_status"], "unavailable")
        self.assertTrue(report["public_search_runtime_available"])
        self.assertTrue(report["static_handoff_available"])
        self.assertEqual(report["pass_count"], 30)
        self.assertEqual(report["fail_count"], 0)
        self.assertEqual(report["unavailable_count"], 0)

    def test_route_safe_and_blocked_results_are_recorded(self) -> None:
        report = _load_json(REPORT)

        self.assertEqual(len(report["route_results"]), 6)
        self.assertEqual(len(report["safe_query_results"]), 9)
        self.assertEqual(len(report["blocked_request_results"]), 14)
        self.assertTrue(all(item["status"] == "passed" for item in report["route_results"]))
        self.assertTrue(all(item["status"] == "passed" for item in report["safe_query_results"]))
        self.assertTrue(
            all(item["status"] == "passed" for item in report["blocked_request_results"])
        )
        blocked_codes = {item["actual_error_code"] for item in report["blocked_request_results"]}
        self.assertIn("query_required", blocked_codes)
        self.assertIn("local_paths_forbidden", blocked_codes)
        self.assertIn("live_probes_disabled", blocked_codes)
        self.assertIn("downloads_disabled", blocked_codes)
        self.assertIn("installs_disabled", blocked_codes)
        self.assertIn("uploads_disabled", blocked_codes)

    def test_static_public_alpha_and_contract_reviews_pass(self) -> None:
        report = _load_json(REPORT)

        self.assertEqual(report["static_handoff_review"]["status"], "passed")
        self.assertFalse(report["static_handoff_review"]["fake_hosted_backend_claim"])
        self.assertEqual(report["public_alpha_review"]["status"], "passed")
        self.assertTrue(report["public_alpha_review"]["public_search_routes_safe_public_alpha"])
        self.assertEqual(report["contract_alignment"]["status"], "passed")
        self.assertTrue(report["contract_alignment"]["live_backend_future"])
        self.assertTrue(report["contract_alignment"]["live_probe_future"])

    def test_inventories_reference_rehearsal(self) -> None:
        routes = _load_json(PUBLIC_SEARCH_ROUTES)
        public_alpha = _load_json(PUBLIC_ALPHA_ROUTES)
        handoff = _load_json(HANDOFF)

        self.assertEqual(routes["local_rehearsal_status"], "completed")
        self.assertEqual(public_alpha["public_search_rehearsal_status"], "completed")
        self.assertEqual(handoff["local_rehearsal_status"], "completed")
        self.assertEqual(
            routes["local_rehearsal"],
            "control/audits/public-search-rehearsal-v0/public_search_rehearsal_report.json",
        )


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
