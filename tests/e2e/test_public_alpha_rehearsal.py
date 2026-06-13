from __future__ import annotations

import copy
import io
import json
from pathlib import Path
import tempfile
import unittest

from runtime.local.review_materialization import accept_candidate
from runtime.local.search_index import build_local_demo_index, write_index
from scripts.eureka_public_alpha_rehearsal import main as rehearsal_main
from scripts.eureka_staging import main as staging_main
from scripts.run_eureka_local import main as run_local_main


QUERY = "manual for Sound Blaster CT1740"


class PublicAlphaRehearsalTests(unittest.TestCase):
    def test_rehearsal_run_writes_json_and_markdown_reports(self) -> None:
        with _StagedPublicAlphaDemo() as demo:
            result = _run_rehearsal_main(
                "run",
                "--bundle",
                str(demo.bundle_path),
                "--host",
                "127.0.0.1",
                "--port",
                "0",
                "--out",
                str(demo.rehearsal_path),
            )

            report = _load_json(demo.rehearsal_path / "rehearsal_report.json")
            markdown_exists = (demo.rehearsal_path / "REHEARSAL_REPORT.md").is_file()

        self.assertEqual(result.code, 0, result.stderr)
        self.assertEqual(report["status"], "PASS_WITH_WARNINGS")
        self.assertEqual(report["task_id"], "PUBLIC-ALPHA-REHEARSAL-00")
        self.assertTrue(markdown_exists)
        self.assertEqual(report["local_rehearsal_failures"], [])
        self.assertGreaterEqual(len(report["launch_blockers"]), 1)
        self.assertTrue(report["read_only"])
        self.assertFalse(report["live_metadata_enabled"])
        self.assertFalse(report["workbench_exposed"])
        self.assertFalse(report["public_live_fanout"])

    def test_validate_report_passes_for_valid_report(self) -> None:
        with _StagedPublicAlphaDemo() as demo:
            _write_rehearsal(demo)
            result = _run_rehearsal_main(
                "validate-report",
                "--report",
                str(demo.rehearsal_path / "rehearsal_report.json"),
            )

        self.assertEqual(result.code, 0, result.stderr)
        self.assertIn("validation passed", result.stdout)

    def test_status_prints_summary(self) -> None:
        with _StagedPublicAlphaDemo() as demo:
            _write_rehearsal(demo)
            result = _run_rehearsal_main(
                "status",
                "--report",
                str(demo.rehearsal_path / "rehearsal_report.json"),
            )

        self.assertEqual(result.code, 0, result.stderr)
        self.assertIn("status: PASS_WITH_WARNINGS", result.stdout)
        self.assertIn("launch_blockers:", result.stdout)

    def test_rehearsal_probes_public_and_blocked_routes(self) -> None:
        with _StagedPublicAlphaDemo() as demo:
            _write_rehearsal(demo)
            report = _load_json(demo.rehearsal_path / "rehearsal_report.json")

        public_routes = {(item["method"], item["path"]) for item in report["routes_probed"]}
        blocked_routes = {(item["method"], item["path"]) for item in report["blocked_routes_probed"]}
        self.assertIn(("GET", "/"), public_routes)
        self.assertIn(("GET", "/api/status"), public_routes)
        self.assertIn(("GET", "/about"), public_routes)
        self.assertIn(("GET", "/method"), public_routes)
        self.assertTrue(any(path.startswith("/api/search?q=") for _, path in public_routes))
        self.assertTrue(any(path.startswith("/record/") and path != "/record/__missing__" for _, path in public_routes))
        self.assertIn(("GET", "/record/__missing__"), public_routes)
        self.assertIn(("GET", "/record/..%2F..%2Fprivate"), public_routes)
        self.assertIn(("GET", "/workbench"), blocked_routes)
        self.assertIn(("GET", "/workbench/api/status"), blocked_routes)
        self.assertIn(("POST", "/workbench/api/review/accept"), blocked_routes)

    def test_validate_report_detects_controlled_leakage_and_mutation_flags(self) -> None:
        with _StagedPublicAlphaDemo() as demo:
            _write_rehearsal(demo)
            report = _load_json(demo.rehearsal_path / "rehearsal_report.json")
            report["leakage_checks"]["passed"] = False
            report["leakage_checks"]["failures"] = ["public response contains forbidden marker: C:\\"]
            report["mutation_checks"]["public_routes_mutated_bundle"] = True
            bad_path = demo.rehearsal_path / "bad_report.json"
            _write_json(bad_path, report)
            result = _run_rehearsal_main("validate-report", "--report", str(bad_path))

        self.assertEqual(result.code, 1)
        self.assertIn("leakage_checks.passed must be true", result.stderr)
        self.assertIn("mutation_checks.public_routes_mutated_bundle must be false", result.stderr)

    def test_rehearsal_detects_unsafe_bundle_posture(self) -> None:
        with _StagedPublicAlphaDemo() as demo:
            config_path = demo.bundle_path / "public_runtime_config.json"
            config = _load_json(config_path)
            config["live_metadata_enabled"] = True
            _write_json(config_path, config)
            result = _run_rehearsal_main(
                "run",
                "--bundle",
                str(demo.bundle_path),
                "--host",
                "127.0.0.1",
                "--port",
                "0",
                "--out",
                str(demo.rehearsal_path),
            )
            report = _load_json(demo.rehearsal_path / "rehearsal_report.json")

        self.assertEqual(result.code, 1)
        self.assertEqual(report["status"], "FAIL")
        self.assertTrue(any("runtime_config.live_metadata_enabled" in item for item in report["local_rehearsal_failures"]))

    def test_rehearsal_refuses_non_loopback_host(self) -> None:
        with _StagedPublicAlphaDemo() as demo:
            result = _run_rehearsal_main(
                "run",
                "--bundle",
                str(demo.bundle_path),
                "--host",
                "0.0.0.0",
                "--port",
                "0",
                "--out",
                str(demo.rehearsal_path),
            )
            report = _load_json(demo.rehearsal_path / "rehearsal_report.json")

        self.assertEqual(result.code, 1)
        self.assertEqual(report["status"], "FAIL")
        self.assertIn("rehearsal server host must be loopback", report["local_rehearsal_failures"])

    def test_rehearsal_reports_launch_blockers_without_failing_local_rehearsal(self) -> None:
        with _StagedPublicAlphaDemo() as demo:
            _write_rehearsal(demo)
            report = _load_json(demo.rehearsal_path / "rehearsal_report.json")

        self.assertEqual(report["status"], "PASS_WITH_WARNINGS")
        self.assertEqual(report["local_rehearsal_failures"], [])
        self.assertGreaterEqual(len(report["launch_blockers"]), 1)
        self.assertIn("production hosting is not configured", report["launch_blockers"])

    def test_run_eureka_local_staging_bundle_still_works(self) -> None:
        with _StagedPublicAlphaDemo() as demo:
            result = _run_local_main("--smoke", "--staging-bundle", str(demo.bundle_path))

        payload = json.loads(result.stdout)
        self.assertEqual(result.code, 0, result.stderr)
        self.assertEqual(payload["deployment_source"], "staging_bundle")
        self.assertTrue(payload["read_only"])
        self.assertFalse(payload["live_metadata_enabled"])
        self.assertFalse(payload["workbench_exposed"])

    def test_validate_report_rejects_missing_required_safety_fields(self) -> None:
        with _StagedPublicAlphaDemo() as demo:
            _write_rehearsal(demo)
            report = _load_json(demo.rehearsal_path / "rehearsal_report.json")
            bad_report = copy.deepcopy(report)
            bad_report.pop("blocked_routes_probed")
            bad_report["read_only"] = False
            bad_path = demo.rehearsal_path / "missing_safety_report.json"
            _write_json(bad_path, bad_report)
            result = _run_rehearsal_main("validate-report", "--report", str(bad_path))

        self.assertEqual(result.code, 1)
        self.assertIn("missing required field: blocked_routes_probed", result.stderr)


class _StagedPublicAlphaDemo:
    def __enter__(self) -> "_StagedPublicAlphaDemo":
        self._temp_dir = tempfile.TemporaryDirectory()
        root = Path(self._temp_dir.name)
        self.index_path = root / "local_search_index.json"
        self.ledger_path = root / "local_review_ledger.jsonl"
        self.records_path = root / "local_reviewed_records.jsonl"
        self.reviewed_index_path = root / "local_search_index.reviewed.json"
        self.bundle_path = root / "public-alpha-bundle"
        self.rehearsal_path = root / "rehearsal"
        write_index(self.index_path, build_local_demo_index())
        accept_candidate(
            index_path=self.index_path,
            query=QUERY,
            ledger_path=self.ledger_path,
            records_path=self.records_path,
            reviewer="local_demo",
            reason="Public alpha rehearsal test seed",
            reviewed_at="2026-06-13T00:00:00+10:00",
        )
        write_index(self.reviewed_index_path, build_local_demo_index(reviewed_records_path=self.records_path))
        package = _run_staging_main("package", "--index", str(self.reviewed_index_path), "--out", str(self.bundle_path))
        if package.code != 0:
            raise AssertionError(package.stderr or package.stdout)
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self._temp_dir.cleanup()


def _write_rehearsal(demo: _StagedPublicAlphaDemo) -> None:
    result = _run_rehearsal_main(
        "run",
        "--bundle",
        str(demo.bundle_path),
        "--host",
        "127.0.0.1",
        "--port",
        "0",
        "--out",
        str(demo.rehearsal_path),
    )
    if result.code != 0:
        raise AssertionError(result.stderr or result.stdout)


def _run_staging_main(*args: str) -> "_Result":
    stdout = io.StringIO()
    stderr = io.StringIO()
    code = staging_main(list(args), stdout=stdout, stderr=stderr)
    return _Result(code=code, stdout=stdout.getvalue(), stderr=stderr.getvalue())


def _run_rehearsal_main(*args: str) -> "_Result":
    stdout = io.StringIO()
    stderr = io.StringIO()
    code = rehearsal_main(list(args), stdout=stdout, stderr=stderr)
    return _Result(code=code, stdout=stdout.getvalue(), stderr=stderr.getvalue())


def _run_local_main(*args: str) -> "_Result":
    stdout = io.StringIO()
    stderr = io.StringIO()
    code = run_local_main(list(args), stdout=stdout, stderr=stderr)
    return _Result(code=code, stdout=stdout.getvalue(), stderr=stderr.getvalue())


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write_json(path: Path, payload: object) -> None:
    path.write_bytes(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True).encode("utf-8") + b"\n")


class _Result:
    def __init__(self, *, code: int, stdout: str, stderr: str) -> None:
        self.code = code
        self.stdout = stdout
        self.stderr = stderr


if __name__ == "__main__":
    unittest.main()
