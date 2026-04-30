from __future__ import annotations

import json
from pathlib import Path
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
AUDIT_DIR = REPO_ROOT / "control" / "audits" / "public-search-rehearsal-v0"
REPORT = AUDIT_DIR / "public_search_rehearsal_report.json"


class PublicSearchRehearsalSafetyTest(unittest.TestCase):
    def test_unsafe_capabilities_remain_disabled(self) -> None:
        report = _load_json(REPORT)

        for key in (
            "live_probes_enabled",
            "downloads_enabled",
            "installs_enabled",
            "uploads_enabled",
            "local_paths_enabled",
            "telemetry_enabled",
        ):
            self.assertFalse(report[key], key)

    def test_audit_pack_does_not_claim_hosted_search(self) -> None:
        combined = _audit_text()

        for prohibited in (
            "hosted public search is live",
            "public search is hosted",
            "hosted public search deployed",
            "production-ready public search",
            "production api stability is guaranteed",
            "live probes are enabled",
            "downloads are enabled",
            "uploads are enabled",
            "telemetry is enabled",
        ):
            self.assertNotIn(prohibited, combined)

    def test_rehearsal_report_does_not_leak_private_paths(self) -> None:
        combined = REPORT.read_text(encoding="utf-8").casefold()

        for marker in (
            "c:/",
            "d:/",
            "\\users\\",
            "/users/",
            "/home/",
            "/tmp/",
            "appdata/",
            "appdata\\",
        ):
            self.assertNotIn(marker, combined)

    def test_blocked_requests_do_not_expose_stack_traces(self) -> None:
        report = _load_json(REPORT)

        for item in report["blocked_request_results"]:
            self.assertTrue(item["no_stack_trace"])
            self.assertTrue(item["no_private_path_leakage"])


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _audit_text() -> str:
    return "\n".join(
        path.read_text(encoding="utf-8", errors="replace")
        for path in AUDIT_DIR.iterdir()
        if path.is_file()
    ).casefold()


if __name__ == "__main__":
    unittest.main()
