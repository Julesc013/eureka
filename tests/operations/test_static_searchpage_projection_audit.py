from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest

from scripts.audit_static_searchpage_projection import (
    ARTIFACT_BINDINGS,
    REQUIRED_BINDING_FIELDS,
    build_projection_audit,
    detect_critical_boundary_violations,
    main,
)


REPO_ROOT = Path(__file__).resolve().parents[2]


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class StaticSearchPageProjectionAuditTest(unittest.TestCase):
    def test_audit_script_runs_on_current_repo_state(self) -> None:
        report = build_projection_audit(REPO_ROOT)

        self.assertIn(report["status"], {"pass", "warn"})
        self.assertEqual(report["critical_boundary_violations"], [])
        self.assertEqual(len(report["artifact_bindings"]), 5)

    def test_report_json_shape_is_valid(self) -> None:
        report = build_projection_audit(REPO_ROOT)

        for key in (
            "schema_version",
            "status",
            "track",
            "task",
            "audited_view_family",
            "artifact_bindings",
            "semantic_alignment",
            "known_gaps",
            "critical_boundary_violations",
            "product_boundary",
            "next_task",
        ):
            self.assertIn(key, report)
        self.assertEqual(report["audited_view_family"], "SearchPageView")

    def test_missing_artifact_is_reported_not_created(self) -> None:
        missing_path = "site/dist/missing-a11-search-audit-fixture.txt"
        target = REPO_ROOT / missing_path
        self.assertFalse(target.exists())
        bindings = [
            {
                "artifact_path": missing_path,
                "artifact_kind": "text_static",
                "expected_representation_profile": "text",
                "expected_route_family": "text_static",
                "expected_view_family": "SearchPageView",
            }
        ]

        report = build_projection_audit(REPO_ROOT, artifact_bindings=bindings)

        self.assertFalse(report["artifact_bindings"][0]["exists"])
        self.assertFalse(target.exists())

    def test_boundary_claim_detection_on_fixture_text(self) -> None:
        text = (
            "hosted backend active. live probes enabled. downloads enabled. "
            "uploads enabled. accounts enabled. telemetry enabled."
        )

        violations = detect_critical_boundary_violations(text, "fixture.txt")

        self.assertTrue(any("enabled_hosting" in item for item in violations))
        self.assertTrue(any("enabled_live_probes" in item for item in violations))
        self.assertTrue(any("enabled_downloads" in item for item in violations))
        self.assertTrue(any("enabled_uploads" in item for item in violations))
        self.assertTrue(any("enabled_accounts" in item for item in violations))
        self.assertTrue(any("enabled_telemetry" in item for item in violations))

    def test_static_artifact_binding_records_have_required_fields(self) -> None:
        report = build_projection_audit(REPO_ROOT)

        for binding in report["artifact_bindings"]:
            self.assertTrue(REQUIRED_BINDING_FIELDS <= set(binding), binding["artifact_path"])

    def test_check_succeeds_on_current_repo_state(self) -> None:
        output = io.StringIO()

        exit_code = main(["--check"], stdout=output)

        self.assertEqual(exit_code, 0)
        self.assertIn("Static SearchPage projection audit", output.getvalue())

    def test_json_output_writes_deterministic_json(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output_path = Path(tmp) / "projection.json"

            first_exit = main(["--json-output", str(output_path)], stdout=io.StringIO())
            first = output_path.read_text(encoding="utf-8")
            second_exit = main(["--json-output", str(output_path)], stdout=io.StringIO())
            second = output_path.read_text(encoding="utf-8")

        self.assertEqual(first_exit, 0)
        self.assertEqual(second_exit, 0)
        self.assertEqual(first, second)
        self.assertEqual(json.loads(first)["task"], "TRACK-A-11")

    def test_script_does_not_mutate_site_dist(self) -> None:
        files = [REPO_ROOT / binding["artifact_path"] for binding in ARTIFACT_BINDINGS]
        before = {path.as_posix(): file_hash(path) for path in files}
        with tempfile.TemporaryDirectory() as tmp:
            exit_code = main(["--json-output", str(Path(tmp) / "projection.json")], stdout=io.StringIO())
        after = {path.as_posix(): file_hash(path) for path in files}

        self.assertEqual(exit_code, 0)
        self.assertEqual(after, before)


if __name__ == "__main__":
    unittest.main()
