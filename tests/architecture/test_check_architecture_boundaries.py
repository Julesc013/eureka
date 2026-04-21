from __future__ import annotations

import json
from io import StringIO
from pathlib import Path
import tempfile
import unittest

from scripts.check_architecture_boundaries import main, run_boundary_check


REPO_ROOT = Path(__file__).resolve().parents[2]


class ArchitectureBoundaryCheckerTestCase(unittest.TestCase):
    def test_real_repo_imports_pass(self) -> None:
        result = run_boundary_check(REPO_ROOT)

        self.assertEqual(result.violations, ())
        self.assertGreater(result.checked_files, 0)

    def test_surface_web_engine_violation_fails(self) -> None:
        with temporary_repo(
            {
                "surfaces/web/bad_surface.py": "from runtime.engine import core\n",
            }
        ) as root:
            result = run_boundary_check(root)

        self.assertEqual(len(result.violations), 1)
        self.assertEqual(result.violations[0].rule_id, "surface_engine_import")
        self.assertEqual(result.violations[0].source_file, "surfaces/web/bad_surface.py")

    def test_surface_native_cli_engine_violation_fails(self) -> None:
        with temporary_repo(
            {
                "surfaces/native/cli/bad_cli.py": "import runtime.engine.resolve\n",
            }
        ) as root:
            result = run_boundary_check(root)

        self.assertEqual(len(result.violations), 1)
        self.assertEqual(result.violations[0].rule_id, "surface_engine_import")
        self.assertEqual(result.violations[0].source_file, "surfaces/native/cli/bad_cli.py")

    def test_gateway_public_api_surface_violation_fails(self) -> None:
        with temporary_repo(
            {
                "runtime/gateway/public_api/bad_boundary.py": "from surfaces.web import server\n",
            }
        ) as root:
            result = run_boundary_check(root)

        self.assertEqual(len(result.violations), 1)
        self.assertEqual(result.violations[0].rule_id, "gateway_public_api_surface_import")
        self.assertEqual(
            result.violations[0].source_file,
            "runtime/gateway/public_api/bad_boundary.py",
        )

    def test_checker_emits_json_when_requested(self) -> None:
        with temporary_repo(
            {
                "surfaces/web/bad_surface.py": "from runtime.engine import core\n",
            }
        ) as root:
            buffer = StringIO()
            exit_code = main(["--root", str(root), "--json"], stdout=buffer)

        payload = json.loads(buffer.getvalue())
        self.assertEqual(exit_code, 1)
        self.assertEqual(payload["root"], str(root.resolve()))
        self.assertEqual(payload["violation_count"], 1)
        self.assertEqual(payload["violations"][0]["rule_id"], "surface_engine_import")


class temporary_repo:
    def __init__(self, files: dict[str, str]) -> None:
        self._files = files
        self._temp_dir = tempfile.TemporaryDirectory()

    def __enter__(self) -> Path:
        root = Path(self._temp_dir.name)
        for relative_path, content in self._files.items():
            file_path = root / relative_path
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(content, encoding="utf-8")
        return root

    def __exit__(self, exc_type, exc, tb) -> None:
        self._temp_dir.cleanup()
