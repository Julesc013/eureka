import unittest
from pathlib import Path

from scripts.validate_native_c89_library import (
    C99_TOKENS,
    FORBIDDEN_RUNTIME_TOKENS,
    REQUIRED_FILES,
    validate_native_c89_library,
)

REPO_ROOT = Path(__file__).resolve().parents[2]


class NativeC89LibraryTests(unittest.TestCase):
    def test_c89_validator_passes_or_warns_for_missing_compiler(self) -> None:
        report = validate_native_c89_library(REPO_ROOT)
        self.assertIn(report["status"], {"pass", "pass_with_warnings"}, report)

    def test_c89_headers_and_sources_exist(self) -> None:
        for relative in REQUIRED_FILES:
            self.assertTrue((REPO_ROOT / "native" / "lib" / "c89" / relative).is_file(), relative)

    def test_c89_files_do_not_contain_obvious_c99_only_syntax(self) -> None:
        for relative in REQUIRED_FILES:
            path = REPO_ROOT / "native" / "lib" / "c89" / relative
            text = path.read_text(encoding="utf-8")
            for token in C99_TOKENS:
                self.assertNotIn(token, text, f"{relative} contains {token}")

    def test_c89_files_do_not_call_network_download_or_execute_apis(self) -> None:
        for relative in REQUIRED_FILES:
            path = REPO_ROOT / "native" / "lib" / "c89" / relative
            text = path.read_text(encoding="utf-8")
            for token in FORBIDDEN_RUNTIME_TOKENS:
                self.assertNotIn(token, text, f"{relative} contains {token}")


if __name__ == "__main__":
    unittest.main()
