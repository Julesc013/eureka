from __future__ import annotations

from io import StringIO
import json
from pathlib import Path
import tempfile
import unittest

from scripts.run_renderer_parity_harness import (
    check_output_binding,
    check_text_markers,
    detect_forbidden_text_claims,
    main,
    run_renderer_parity_harness,
)


REPO_ROOT = Path(__file__).resolve().parents[2]


class RunRendererParityHarnessTest(unittest.TestCase):
    def test_run_harness_list_works(self) -> None:
        output = StringIO()

        code = main(["--repo-root", str(REPO_ROOT), "--list"], stdout=output)

        self.assertEqual(code, 0)
        self.assertIn("search_page_static_projection_v0", output.getvalue())

    def test_run_harness_check_passes_current_outputs(self) -> None:
        output = StringIO()

        code = main(["--repo-root", str(REPO_ROOT), "--check"], stdout=output)

        self.assertEqual(code, 0)
        self.assertIn("run_renderer_parity_harness: pass", output.getvalue())

    def test_runner_report_shape_is_valid(self) -> None:
        report = run_renderer_parity_harness(REPO_ROOT)

        self.assertEqual(report["schema_version"], "track_a_16_renderer_parity_report.v0")
        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["active_cases"], ["search_page_static_projection_v0"])
        self.assertIn("object_page_projection_future_v0", report["skipped_future_cases"])

    def test_forbidden_hosted_live_download_upload_account_telemetry_detection(self) -> None:
        text = (
            "Hosted backend active. Live probes enabled. Downloads enabled. "
            "Uploads enabled. Accounts enabled. Telemetry enabled."
        )

        errors = detect_forbidden_text_claims(text, "fixture.txt")

        self.assertGreaterEqual(len(errors), 6)

    def test_forbidden_rights_malware_installability_exhaustive_auto_detection(self) -> None:
        text = (
            "Rights clearance is verified. Malware safety is verified. "
            "Verified installability. Exhaustive global search. Automatic promotion is enabled."
        )

        errors = detect_forbidden_text_claims(text, "fixture.txt")

        self.assertTrue(any("claimed_rights_clearance" in error for error in errors))
        self.assertTrue(any("claimed_malware_safety" in error for error in errors))
        self.assertTrue(any("claimed_verified_installability" in error for error in errors))
        self.assertTrue(any("claimed_exhaustive_global_search" in error for error in errors))
        self.assertTrue(any("claimed_automatic_merge_or_promotion" in error for error in errors))

    def test_missing_required_semantic_marker_fails(self) -> None:
        errors, checked = check_text_markers("Search\nQuery\n", ["Search", "Blocked Actions"], "fixture.txt")

        self.assertEqual(checked, ["Search", "Blocked Actions"])
        self.assertTrue(any("Blocked Actions" in error for error in errors))

    def test_check_output_binding_detects_temporary_broken_output(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "projection.txt"
            output.write_text("Search\nHosted backend active.\n", encoding="utf-8")
            binding = {
                "output_id": "broken",
                "output_path": str(output),
                "output_kind": "text_static",
                "representation_profile": "text",
                "design_profile": "text_only",
                "exists_required": True,
                "semantic_categories_required": [],
                "text_markers_required": ["Search", "Blocked Actions"],
                "text_markers_forbidden": [],
                "json_paths_required": [],
                "json_claims_forbidden": [],
                "degradation_allowed": [],
                "notes": [],
            }

            result = check_output_binding(binding, REPO_ROOT)

        self.assertEqual(result["status"], "fail")
        self.assertTrue(any("Hosted" in error or "hosted" in error for error in result["errors"]))
        self.assertTrue(any("Blocked Actions" in error for error in result["errors"]))

    def test_json_output_writes_deterministic_report(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "report.json"
            output = StringIO()
            code = main(["--repo-root", str(REPO_ROOT), "--json-output", str(path)], stdout=output)
            first = path.read_text(encoding="utf-8")
            code_again = main(["--repo-root", str(REPO_ROOT), "--json-output", str(path)], stdout=StringIO())
            second = path.read_text(encoding="utf-8")

        self.assertEqual(code, 0)
        self.assertEqual(code_again, 0)
        self.assertEqual(first, second)
        self.assertEqual(json.loads(first)["status"], "pass")

    def test_runner_does_not_mutate_site_dist(self) -> None:
        before = _site_dist_fingerprint()

        run_renderer_parity_harness(REPO_ROOT)

        self.assertEqual(before, _site_dist_fingerprint())


def _site_dist_fingerprint() -> list[tuple[str, int, int]]:
    root = REPO_ROOT / "site" / "dist"
    if not root.exists():
        return []
    return sorted(
        (
            str(path.relative_to(root)),
            path.stat().st_size,
            path.stat().st_mtime_ns,
        )
        for path in root.rglob("*")
        if path.is_file()
    )


if __name__ == "__main__":
    unittest.main()
