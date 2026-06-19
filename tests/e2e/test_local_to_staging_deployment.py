from __future__ import annotations

import contextlib
import hashlib
import http.client
import io
import json
from pathlib import Path
import tempfile
import threading
import unittest
from urllib.parse import quote

from runtime.local.public_alpha_service import PublicAlphaService
from runtime.local.review_materialization import accept_candidate
from runtime.local.search_index import build_local_demo_index, load_index, validate_index, write_index
from runtime.local.local_search import LocalSearchOptions, LocalSearchService
from runtime.local.staging_package import (
    MANIFEST_FILE,
    PUBLIC_INDEX_FILE,
    RUNTIME_CONFIG_FILE,
    bundle_id,
    public_index_path,
)
from scripts.eureka_staging import main as staging_main
from scripts.run_eureka_local import LocalSearchHTTPServer, _handler_for, main as run_local_main


QUERY = "manual for Sound Blaster CT1740"
FORBIDDEN_BUNDLE_MARKERS = (
    ".eureka",
    "local_review_ledger",
    "local_reviewed_records",
    "local_search_index.json",
    "local-dev-token",
    "X-Eureka-Workbench-Token",
    "C:\\",
    "D:\\",
    "/Users/",
    "\\Users\\",
)


class LocalToStagingDeploymentTests(unittest.TestCase):
    def test_package_creates_public_safe_bundle_files(self) -> None:
        with _ReviewedIndexDemo() as demo:
            result = _run_staging_main("package", "--index", str(demo.reviewed_index_path), "--out", str(demo.bundle_path))

            self.assertEqual(result.code, 0, result.stderr)
            self.assertEqual(
                sorted(path.name for path in demo.bundle_path.iterdir()),
                sorted([MANIFEST_FILE, PUBLIC_INDEX_FILE, RUNTIME_CONFIG_FILE]),
            )
            manifest = _load_json(demo.bundle_path / MANIFEST_FILE)
            public_index = load_index(demo.bundle_path / PUBLIC_INDEX_FILE)
            runtime_config = _load_json(demo.bundle_path / RUNTIME_CONFIG_FILE)

        self.assertTrue(manifest["public_alpha_mode"])
        self.assertTrue(manifest["read_only"])
        self.assertFalse(manifest["live_metadata_enabled"])
        self.assertFalse(manifest["workbench_exposed"])
        self.assertFalse(manifest["mutation_enabled"])
        self.assertEqual(manifest["document_count"], public_index["document_count"])
        self.assertEqual(manifest["artifact_verified_count"], 0)
        self.assertEqual(runtime_config["metadata_fallback"], "none")
        self.assertEqual(public_index["reviewed_records_source"], "")
        self.assertEqual(validate_index(public_index), [])
        self._assert_public_safe_bundle_text(json.dumps(manifest) + json.dumps(public_index) + json.dumps(runtime_config))

    def test_validate_rejects_missing_public_index_and_unsafe_posture(self) -> None:
        with _ReviewedIndexDemo() as demo:
            _package(demo)
            (demo.bundle_path / PUBLIC_INDEX_FILE).unlink()
            missing = _run_staging_main("validate", "--bundle", str(demo.bundle_path))
            _package(demo)
            _mutate_json(demo.bundle_path / RUNTIME_CONFIG_FILE, {"live_metadata_enabled": True})
            live = _run_staging_main("validate", "--bundle", str(demo.bundle_path))
            _package(demo)
            _mutate_json(demo.bundle_path / RUNTIME_CONFIG_FILE, {"workbench_enabled": True})
            workbench = _run_staging_main("validate", "--bundle", str(demo.bundle_path))
            _package(demo)
            _mutate_json(demo.bundle_path / RUNTIME_CONFIG_FILE, {"mutation_enabled": True})
            mutation = _run_staging_main("validate", "--bundle", str(demo.bundle_path))

        self.assertEqual(missing.code, 1)
        self.assertIn("missing required bundle file", missing.stderr)
        self.assertEqual(live.code, 1)
        self.assertIn("runtime_config.live_metadata_enabled", live.stderr)
        self.assertEqual(workbench.code, 1)
        self.assertIn("runtime_config.workbench_enabled", workbench.stderr)
        self.assertEqual(mutation.code, 1)
        self.assertIn("runtime_config.mutation_enabled", mutation.stderr)

    def test_validate_rejects_local_path_leakage(self) -> None:
        with _ReviewedIndexDemo() as demo:
            _package(demo)
            _mutate_json(demo.bundle_path / MANIFEST_FILE, {"leak": r"C:\Users\Jules\.eureka\local_reviewed_records.jsonl"})
            result = _run_staging_main("validate", "--bundle", str(demo.bundle_path))

        self.assertEqual(result.code, 1)
        self.assertIn("forbidden marker", result.stderr)

    def test_status_reports_counts_and_public_posture(self) -> None:
        with _ReviewedIndexDemo() as demo:
            _package(demo)
            result = _run_staging_main("status", "--bundle", str(demo.bundle_path), "--json")

        payload = json.loads(result.stdout)
        self.assertEqual(result.code, 0)
        self.assertEqual(payload["status"], "pass")
        self.assertTrue(payload["read_only"])
        self.assertFalse(payload["live_metadata_enabled"])
        self.assertFalse(payload["workbench_exposed"])
        self.assertFalse(payload["mutation_enabled"])
        self.assertGreaterEqual(payload["document_count"], 1)
        self.assertGreaterEqual(payload["reviewed_record_count"], 1)

    def test_staging_smoke_probes_public_routes_and_disabled_workbench(self) -> None:
        with _ReviewedIndexDemo() as demo:
            _package(demo)
            result = _run_staging_main("smoke", "--bundle", str(demo.bundle_path), "--host", "127.0.0.1", "--port", "0", "--json")

        payload = json.loads(result.stdout)
        paths = {item["path"] for item in payload["routes"]}
        self.assertEqual(result.code, 0, result.stderr)
        self.assertTrue(payload["read_only"])
        self.assertFalse(payload["live_metadata_enabled"])
        self.assertFalse(payload["public_live_fanout"])
        self.assertTrue(payload["workbench_disabled"])
        self.assertTrue(payload["hashes_unchanged"])
        self.assertIn("/", paths)
        self.assertIn("/api/status", paths)
        self.assertIn(f"/api/search?q={quote(QUERY)}", paths)
        self.assertTrue(payload["record_url"].startswith("/record/"))
        self.assertIn("/workbench", paths)
        self.assertIn("/workbench/api/status", paths)

    def test_run_local_smoke_from_staging_bundle(self) -> None:
        with _ReviewedIndexDemo() as demo:
            _package(demo)
            result = _run_local_main("--smoke", "--staging-bundle", str(demo.bundle_path))

        payload = json.loads(result.stdout)
        self.assertEqual(result.code, 0, result.stderr)
        self.assertEqual(payload["deployment_source"], "staging_bundle")
        self.assertTrue(payload["staging_bundle_loaded"])
        self.assertTrue(payload["read_only"])
        self.assertFalse(payload["live_metadata_enabled"])
        self.assertFalse(payload["workbench_exposed"])
        self.assertNotIn("index_path", payload)
        self._assert_public_safe_bundle_text(result.stdout)

    def test_running_server_from_bundle_routes_and_no_mutation(self) -> None:
        with _ReviewedIndexDemo() as demo:
            _package(demo)
            before = _sha256(public_index_path(demo.bundle_path))
            with _RunningStagingServer(demo.bundle_path) as server:
                status = json.loads(server.get("/api/status")[2])
                api_search = json.loads(server.get(f"/api/search?q={quote(QUERY)}")[2])
                record_url = api_search["results"][0]["record_url"]
                record = server.get(record_url)
                workbench = server.get("/workbench/api/status")
            after = _sha256(public_index_path(demo.bundle_path))

        self.assertEqual(status["deployment_source"], "staging_bundle")
        self.assertTrue(status["read_only"])
        self.assertFalse(status["live_metadata_enabled"])
        self.assertFalse(status["workbench_exposed"])
        self.assertEqual(api_search["results"][0]["review_state"], "accepted")
        self.assertFalse(api_search["results"][0]["artifact_verified"])
        self.assertEqual(record[0], 200)
        self.assertEqual(workbench[0], 404)
        self.assertEqual(before, after)

    def test_staging_startup_rejects_unsafe_options(self) -> None:
        with _ReviewedIndexDemo() as demo:
            _package(demo)
            cases = [
                ("--metadata-fallback", "ia_live"),
                ("--allow-live-metadata",),
                ("--enable-workbench", "--workbench-token", "local-dev-token"),
                ("--host", "0.0.0.0"),
            ]
            results = [
                _run_local_main("--smoke", "--staging-bundle", str(demo.bundle_path), *case)
                for case in cases
            ]

        self.assertEqual([result.code for result in results], [2, 2, 2, 2])

    def test_prior_public_alpha_index_smoke_still_works(self) -> None:
        with _ReviewedIndexDemo() as demo:
            result = _run_local_main(
                "--smoke",
                "--public-alpha",
                "--index",
                "local",
                "--index-path",
                str(demo.reviewed_index_path),
                "--metadata-fallback",
                "none",
            )

        self.assertEqual(result.code, 0, result.stderr)

    def _assert_public_safe_bundle_text(self, text: str) -> None:
        for marker in FORBIDDEN_BUNDLE_MARKERS:
            self.assertNotIn(marker, text)


class _ReviewedIndexDemo:
    def __enter__(self) -> "_ReviewedIndexDemo":
        self._temp_dir = tempfile.TemporaryDirectory()
        root = Path(self._temp_dir.name)
        self.index_path = root / "local_search_index.json"
        self.ledger_path = root / "local_review_ledger.jsonl"
        self.records_path = root / "local_reviewed_records.jsonl"
        self.reviewed_index_path = root / "local_search_index.reviewed.json"
        self.bundle_path = root / "public-alpha-bundle"
        write_index(self.index_path, build_local_demo_index())
        accept_candidate(
            index_path=self.index_path,
            query=QUERY,
            ledger_path=self.ledger_path,
            records_path=self.records_path,
            reviewer="local_demo",
            reason="Staging local reviewed seed",
            reviewed_at="2026-06-13T00:00:00+10:00",
        )
        write_index(self.reviewed_index_path, build_local_demo_index(reviewed_records_path=self.records_path))
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        self._temp_dir.cleanup()


class _RunningStagingServer:
    def __init__(self, bundle_path: Path) -> None:
        self._bundle_path = bundle_path
        self._httpd: LocalSearchHTTPServer | None = None
        self._thread: threading.Thread | None = None
        self.port = 0

    def __enter__(self) -> "_RunningStagingServer":
        options = LocalSearchOptions(index="local", index_path=str(public_index_path(self._bundle_path)), metadata_fallback="none")
        service = LocalSearchService()
        public_alpha = PublicAlphaService(
            search_service=service,
            search_options=options,
            deployment_source="staging_bundle",
            bundle_id=bundle_id(self._bundle_path),
        )
        self._httpd = LocalSearchHTTPServer(("127.0.0.1", 0), _handler_for(service, options, None, public_alpha))
        self._thread = threading.Thread(target=self._httpd.serve_forever, daemon=True)
        self._thread.start()
        self.port = int(self._httpd.server_address[1])
        return self

    def __exit__(self, exc_type: object, exc: object, traceback: object) -> None:
        if self._httpd is not None:
            self._httpd.shutdown()
        if self._thread is not None:
            self._thread.join(timeout=5)
        if self._httpd is not None:
            self._httpd.server_close()

    def get(self, path: str) -> tuple[int, dict[str, str], str]:
        conn = http.client.HTTPConnection("127.0.0.1", self.port, timeout=5)
        try:
            conn.request("GET", path)
            response = conn.getresponse()
            body = response.read().decode("utf-8")
            return response.status, {key.lower(): value for key, value in response.getheaders()}, body
        finally:
            conn.close()


@contextlib.contextmanager
def _patched_json(path: Path) -> Any:
    payload = _load_json(path)
    yield payload
    path.write_bytes(json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=True).encode("utf-8") + b"\n")


def _package(demo: _ReviewedIndexDemo) -> None:
    result = _run_staging_main("package", "--index", str(demo.reviewed_index_path), "--out", str(demo.bundle_path))
    if result.code != 0:
        raise AssertionError(result.stderr or result.stdout)


def _mutate_json(path: Path, updates: Mapping[str, Any]) -> None:
    with _patched_json(path) as payload:
        payload.update(updates)


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _run_staging_main(*args: str) -> "_Result":
    stdout = io.StringIO()
    stderr = io.StringIO()
    code = staging_main(list(args), stdout=stdout, stderr=stderr)
    return _Result(code=code, stdout=stdout.getvalue(), stderr=stderr.getvalue())


def _run_local_main(*args: str) -> "_Result":
    stdout = io.StringIO()
    stderr = io.StringIO()
    code = run_local_main(list(args), stdout=stdout, stderr=stderr)
    return _Result(code=code, stdout=stdout.getvalue(), stderr=stderr.getvalue())


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


class _Result:
    def __init__(self, *, code: int, stdout: str, stderr: str) -> None:
        self.code = code
        self.stdout = stdout
        self.stderr = stderr


if __name__ == "__main__":
    unittest.main()
