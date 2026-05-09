import unittest
from pathlib import Path

from scripts.validate_native_first_wave_skeletons import (
    PROJECT_SUFFIXES,
    REQUIRED_FILES,
    REQUIRED_POLICIES,
    validate_native_first_wave_skeletons,
)

REPO_ROOT = Path(__file__).resolve().parents[2]


class NativeFirstWaveSkeletonTests(unittest.TestCase):
    def test_first_wave_validator_passes(self) -> None:
        report = validate_native_first_wave_skeletons(REPO_ROOT)
        self.assertEqual(report["status"], "pass", report)

    def test_required_skeleton_files_exist(self) -> None:
        for relative in REQUIRED_FILES:
            self.assertTrue((REPO_ROOT / relative).is_file(), relative)

    def test_required_first_wave_policies_exist(self) -> None:
        for relative in REQUIRED_POLICIES:
            self.assertTrue((REPO_ROOT / relative).is_file(), relative)

    def test_win32_appkit_and_carbon_project_markers_exist(self) -> None:
        self.assertTrue((REPO_ROOT / "native/win/win32/project/Eureka.dsw").is_file())
        self.assertTrue((REPO_ROOT / "native/win/win32/project/Eureka.dsp").is_file())
        self.assertTrue((REPO_ROOT / "native/mac/appkit/project/Eureka.xcodeproj/README.md").is_file())
        self.assertTrue((REPO_ROOT / "native/mac/carbon/project/Eureka.mcp.README.md").is_file())

    def test_no_future_lane_project_files_were_added(self) -> None:
        offenders = []
        for root in ("native/mac/swiftui", "native/win/win16", "native/win/winui"):
            path = REPO_ROOT / root
            if not path.exists():
                continue
            offenders.extend(
                child.relative_to(REPO_ROOT).as_posix()
                for child in path.rglob("*")
                if child.suffix.casefold() in PROJECT_SUFFIXES
            )
        self.assertEqual(offenders, [])

    def test_no_build_outputs_or_binaries_are_committed(self) -> None:
        suffixes = {".exe", ".dll", ".pdb", ".obj", ".o", ".a", ".lib", ".dylib", ".so", ".app", ".msi", ".pkg"}
        offenders = [
            path.relative_to(REPO_ROOT).as_posix()
            for path in (REPO_ROOT / "native").rglob("*")
            if path.is_file() and path.suffix.casefold() in suffixes
        ]
        self.assertEqual(offenders, [])


if __name__ == "__main__":
    unittest.main()
