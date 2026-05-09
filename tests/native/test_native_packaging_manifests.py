import json
import unittest
from pathlib import Path

from scripts.validate_native_packaging_manifests import (
    LANES,
    build_artifact_manifest,
    build_native_packaging_manifest,
    build_release_candidate_preview,
    detect_forbidden_claims,
    validate_native_packaging_manifests,
)

REPO_ROOT = Path(__file__).resolve().parents[2]


class NativePackagingManifestTests(unittest.TestCase):
    def load_json(self, relative: str) -> dict:
        return json.loads((REPO_ROOT / relative).read_text(encoding="utf-8"))

    def test_validator_passes_current_repo(self) -> None:
        report = validate_native_packaging_manifests(REPO_ROOT)
        self.assertEqual(report["status"], "pass", report)

    def test_packaging_manifest_builds_for_first_wave_lanes(self) -> None:
        for lane_id in LANES:
            manifest = build_native_packaging_manifest(lane_id)
            self.assertEqual(manifest["schema_version"], "native_packaging_manifest.v0")
            self.assertEqual(manifest["lane_id"], lane_id)
            self.assertIs(manifest["no_binary_outputs_current"], True)
            self.assertIs(manifest["production_release_current"], False)

    def test_release_candidate_previews_do_not_claim_production_release(self) -> None:
        for lane_id in LANES:
            preview = build_release_candidate_preview(lane_id)
            self.assertNotEqual(preview["release_readiness"], "ready_for_review_future")
            self.assertFalse(detect_forbidden_claims(preview), preview)

    def test_artifact_manifests_do_not_claim_produced_current(self) -> None:
        for lane_id in LANES:
            manifest = build_artifact_manifest(lane_id)
            self.assertIs(manifest["produced_current"], False)
            self.assertIs(manifest["production_release_current"], False)
            self.assertFalse(detect_forbidden_claims(manifest), manifest)

    def test_no_binary_artifacts_are_committed(self) -> None:
        suffixes = {".exe", ".dll", ".pdb", ".obj", ".o", ".a", ".lib", ".dylib", ".so", ".app", ".msi", ".pkg", ".zip"}
        offenders = [
            path.relative_to(REPO_ROOT).as_posix()
            for root in (REPO_ROOT / "native", REPO_ROOT / "examples" / "native")
            for path in root.rglob("*")
            if path.is_file() and path.suffix.casefold() in suffixes
        ]
        self.assertEqual(offenders, [])

    def test_policy_blocked_packaging_manifest_validates(self) -> None:
        manifest = self.load_json("examples/native/packaging/policy_blocked_packaging_manifest_v0.json")
        self.assertEqual(manifest["packaging_status"], "packaging_blocked")
        self.assertIs(manifest["production_release_current"], False)


if __name__ == "__main__":
    unittest.main()
