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
        self.assertEqual(result.root_model.unexpected_top_level_entries, ())
        self.assertEqual(result.root_model.source, "git_ls_files")

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
                "surfaces/cli/bad_cli.py": "import runtime.engine.resolve\n",
            }
        ) as root:
            result = run_boundary_check(root)

        self.assertEqual(len(result.violations), 1)
        self.assertEqual(result.violations[0].rule_id, "surface_engine_import")
        self.assertEqual(result.violations[0].source_file, "surfaces/cli/bad_cli.py")

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

    def test_forbidden_top_level_root_fails(self) -> None:
        with temporary_repo(
            {
                "apps/web/main.py": "print('not an accepted root')\n",
            }
        ) as root:
            result = run_boundary_check(root)

        self.assertEqual(len(result.violations), 1)
        self.assertEqual(result.violations[0].rule_id, "forbidden_top_level_root")
        self.assertEqual(result.violations[0].source_file, "apps")
        self.assertEqual(result.root_model.forbidden_active_roots, ("apps",))

    def test_unexpected_top_level_root_fails(self) -> None:
        with temporary_repo(
            {
                "scratchpad/example.txt": "not classified\n",
            }
        ) as root:
            result = run_boundary_check(root)

        self.assertEqual(len(result.violations), 1)
        self.assertEqual(result.violations[0].rule_id, "unexpected_top_level_root")
        self.assertEqual(result.violations[0].source_file, "scratchpad")
        self.assertEqual(result.root_model.unexpected_top_level_entries, ("scratchpad",))

    def test_classified_top_level_exception_passes(self) -> None:
        with temporary_repo(
            {
                ".aide.local.example/README.md": "example only\n",
            }
        ) as root:
            result = run_boundary_check(root)

        self.assertEqual(result.violations, ())
        self.assertIn(".aide.local.example", result.root_model.active_roots)

    def test_license_and_notice_root_files_are_conventional(self) -> None:
        with temporary_repo(
            {
                "LICENSE.md": "custom license\n",
                "LICENSE-SUMMARY.md": "summary\n",
                "NOTICE.md": "notice\n",
            }
        ) as root:
            result = run_boundary_check(root)

        self.assertEqual(result.violations, ())
        self.assertEqual(result.root_model.unexpected_top_level_entries, ())

    def test_external_full_discovery_handoff_root_file_is_conventional(self) -> None:
        with temporary_repo(
            {
                "external_full_discovery_handoff.json": '{"schema_version": "external_full_discovery_handoff.v0"}\n',
            }
        ) as root:
            result = run_boundary_check(root)

        self.assertEqual(result.violations, ())
        self.assertEqual(result.root_model.unexpected_top_level_entries, ())

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
        self.assertEqual(payload["root_model"]["status"], "pass")
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

