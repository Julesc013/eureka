import unittest
from pathlib import Path

from scripts.validate_native_project_boundaries import _scan_text, validate_native_project_boundaries

REPO_ROOT = Path(__file__).resolve().parents[2]


class NativeProjectBoundaryTests(unittest.TestCase):
    def test_first_wave_boundary_validator_passes(self) -> None:
        report = validate_native_project_boundaries(REPO_ROOT)
        self.assertEqual(report["status"], "pass", report)
        self.assertGreater(report["scanned_file_count"], 0)

    def test_forbidden_network_download_and_execute_tokens_are_rejected(self) -> None:
        errors: list[str] = []
        _scan_text(
            "native/win/win32/src/app/example.c",
            "http://example.invalid\nURLDownloadToFile\nCreateProcess\nsystem(",
            errors,
        )
        self.assertGreaterEqual(len(errors), 4)

    def test_python_and_connector_runtime_internals_are_rejected(self) -> None:
        errors: list[str] = []
        _scan_text(
            "native/mac/appkit/src/Contract/example.m",
            "runtime/engine\nruntime/connectors\npython_runtime\nsource_connector",
            errors,
        )
        self.assertGreaterEqual(len(errors), 4)

    def test_public_and_master_index_mutation_claims_are_rejected(self) -> None:
        errors: list[str] = []
        _scan_text(
            "native/mac/carbon/src/app/example.c",
            "public_index_mutation_allowed = true\nmaster_index_mutation_allowed = true",
            errors,
        )
        self.assertGreaterEqual(len(errors), 2)


if __name__ == "__main__":
    unittest.main()
