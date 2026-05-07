from __future__ import annotations

import hashlib
import io
import json
from pathlib import Path
import tempfile
import unittest

from scripts.generate_static_searchpage_projection import (
    DEFAULT_INPUT,
    PROJECTION_TARGETS,
    generate_projection_bundle,
    main as generator_main,
    validate_output_root,
)
from scripts.validate_static_searchpage_projection_dry_run import (
    detect_forbidden_claims,
    main as validator_main,
    validate_static_searchpage_projection_dry_run,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
SITE_DIST_ARTIFACTS = (
    "site/dist/search.html",
    "site/dist/lite/search.html",
    "site/dist/text/search.txt",
    "site/dist/files/search.README.txt",
    "site/dist/data/search_handoff.json",
)


def file_hash(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class StaticSearchPageProjectionDryRunTest(unittest.TestCase):
    def test_generator_writes_all_outputs_to_temp_root(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output_root = Path(tmp) / "generated"

            report = generate_projection_bundle(
                input_path=Path(DEFAULT_INPUT),
                output_root=output_root,
                repo_root=REPO_ROOT,
                run_check=True,
            )

            self.assertEqual(report["status"], "pass")
            for target in PROJECTION_TARGETS:
                self.assertTrue((output_root / target["filename"]).is_file())
            self.assertTrue((output_root.parent / "projection_dry_run_report.json").is_file())
            self.assertTrue((output_root.parent / "semantic_parity_report.md").is_file())

    def test_generator_refuses_site_dist_output_root(self) -> None:
        with self.assertRaises(ValueError):
            validate_output_root(REPO_ROOT / "site" / "dist" / "a13-generated", REPO_ROOT)

    def test_generated_json_handoff_is_valid(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output_root = Path(tmp) / "generated"
            generate_projection_bundle(input_path=Path(DEFAULT_INPUT), output_root=output_root, repo_root=REPO_ROOT)

            handoff = json.loads((output_root / "search_handoff.json").read_text(encoding="utf-8"))

        self.assertEqual(handoff["schema_version"], "track_a_13_search_handoff_preview.v0")
        self.assertEqual(handoff["source_view_model"]["view_model_id"], "static_projection_reference_v0")

    def test_generated_outputs_contain_required_semantic_labels(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output_root = Path(tmp) / "generated"
            generate_projection_bundle(input_path=Path(DEFAULT_INPUT), output_root=output_root, repo_root=REPO_ROOT)

            for filename in ("search.standard.html", "search.lite.html", "search.txt"):
                text = (output_root / filename).read_text(encoding="utf-8")
                for label in ("Search", "Query", "Mode/Posture", "Result Summary", "Blocked Actions"):
                    self.assertIn(label, text)

    def test_generated_outputs_preserve_false_product_boundary_booleans(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output_root = Path(tmp) / "generated"
            generate_projection_bundle(input_path=Path(DEFAULT_INPUT), output_root=output_root, repo_root=REPO_ROOT)

            handoff = json.loads((output_root / "search_handoff.json").read_text(encoding="utf-8"))

        for key in (
            "hosted_backend_claimed",
            "live_probes_enabled",
            "downloads_enabled",
            "uploads_enabled",
            "accounts_enabled",
            "telemetry_enabled",
        ):
            self.assertIs(handoff["product_boundary"][key], False)
            self.assertIs(handoff["public_runtime_posture"][key], False)

    def test_validator_passes_on_generated_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output_root = Path(tmp) / "generated"
            generate_projection_bundle(input_path=Path(DEFAULT_INPUT), output_root=output_root, repo_root=REPO_ROOT)

            report = validate_static_searchpage_projection_dry_run(repo_root=REPO_ROOT, output_root=output_root)

        self.assertEqual(report["status"], "valid", report["errors"])

    def test_hosted_live_download_upload_account_telemetry_detection(self) -> None:
        text = "hosted backend active. live probes enabled. downloads enabled. uploads enabled. accounts enabled. telemetry enabled."

        violations = detect_forbidden_claims(text, "broken.txt")

        self.assertTrue(any("enabled_hosting" in item for item in violations))
        self.assertTrue(any("enabled_live_probes" in item for item in violations))
        self.assertTrue(any("enabled_downloads" in item for item in violations))
        self.assertTrue(any("enabled_uploads" in item for item in violations))
        self.assertTrue(any("enabled_accounts" in item for item in violations))
        self.assertTrue(any("enabled_telemetry" in item for item in violations))

    def test_rights_malware_installability_exhaustive_auto_promotion_detection(self) -> None:
        text = (
            "rights clearance verified. malware safety verified. verified installability. "
            "exhaustive global search. automatic promotion enabled."
        )

        violations = detect_forbidden_claims(text, "broken.txt")

        self.assertTrue(any("claimed_rights_clearance" in item for item in violations))
        self.assertTrue(any("claimed_malware_safety" in item for item in violations))
        self.assertTrue(any("claimed_verified_installability" in item for item in violations))
        self.assertTrue(any("claimed_exhaustive_global_search" in item for item in violations))
        self.assertTrue(any("claimed_automatic_merge_or_promotion" in item for item in violations))

    def test_generator_does_not_mutate_site_dist(self) -> None:
        before = {path: file_hash(REPO_ROOT / path) for path in SITE_DIST_ARTIFACTS}
        with tempfile.TemporaryDirectory() as tmp:
            output_root = Path(tmp) / "generated"
            generate_projection_bundle(input_path=Path(DEFAULT_INPUT), output_root=output_root, repo_root=REPO_ROOT)
        after = {path: file_hash(REPO_ROOT / path) for path in SITE_DIST_ARTIFACTS}

        self.assertEqual(after, before)

    def test_json_output_is_parseable(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output_root = Path(tmp) / "generated"
            output = io.StringIO()

            exit_code = generator_main(
                ["--output-root", str(output_root), "--check", "--json"],
                stdout=output,
                stderr=io.StringIO(),
            )

        self.assertEqual(exit_code, 0)
        payload = json.loads(output.getvalue())
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["generated_count"], 5)

    def test_validator_cli_accepts_explicit_temp_output(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            output_root = Path(tmp) / "generated"
            generate_projection_bundle(input_path=Path(DEFAULT_INPUT), output_root=output_root, repo_root=REPO_ROOT)
            output = io.StringIO()

            exit_code = validator_main(["--output-root", str(output_root), "--json"], stdout=output)

        self.assertEqual(exit_code, 0)
        self.assertEqual(json.loads(output.getvalue())["status"], "valid")


if __name__ == "__main__":
    unittest.main()
