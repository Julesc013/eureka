from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from tools.validators.validate_archive_import_guard import validate_archive_import_guard


class ArchiveImportGuardTestCase(unittest.TestCase):
    def test_active_runtime_archive_import_fails(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root / "runtime/example.py", "from archive.prototypes import legacy_runtime\n")

            report = validate_archive_import_guard(root)

        self.assertEqual(report["status"], "invalid")
        self.assertIn("active code must not import archived module", report["errors"][0])

    def test_tools_and_archive_are_not_active_import_roots(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write(root / "tools/auditors/example.py", "from archive.prototypes import legacy_runtime\n")
            write(root / "archive/prototypes/example.py", "import archive.prototypes.example\n")
            write(root / "runtime/example.py", "ARCHIVE_PATH = 'archive/prototypes'\n")

            report = validate_archive_import_guard(root)

        self.assertEqual(report["status"], "valid")


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
