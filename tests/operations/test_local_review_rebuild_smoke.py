import io
import json
import tempfile
import threading
import unittest
from pathlib import Path

from runtime.local_appliance import close_local_appliance, open_local_appliance
from runtime.local_operator import write_operator_token_record
from runtime.local_review import record_review_decision
from runtime.local_service import create_local_http_server
from scripts import eureka_local_review_smoke, validate_local_review_rebuild
from scripts.eureka_init_instance import initialize_instance
from scripts.validate_local_review_rebuild import TOKEN, seed_review_records


class LocalReviewRebuildSmokeTests(unittest.TestCase):
    def test_smoke_refuses_non_localhost_url(self) -> None:
        stdout = io.StringIO()
        code = eureka_local_review_smoke.main(
            ["--base-url", "http://example.com:8765", "--operator-token", TOKEN, "--json"],
            stdout=stdout,
            stderr=io.StringIO(),
        )

        self.assertNotEqual(0, code)
        self.assertEqual("fail", json.loads(stdout.getvalue())["status"])

    def test_smoke_passes_against_localhost_service(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "eureka-instance"
            initialize_instance(instance)
            write_operator_token_record(instance, TOKEN)
            runtime = open_local_appliance(instance)
            try:
                seed = seed_review_records(runtime)
                record_review_decision(runtime, seed["accepted_review_item_id"], "accept", None, "operator", True)
            finally:
                close_local_appliance(runtime)
            handle_holder = {}
            ready = threading.Event()

            def serve() -> None:
                handle = create_local_http_server(instance, host="127.0.0.1", port=0, operator_token=TOKEN)
                handle_holder["handle"] = handle
                ready.set()
                try:
                    handle.httpd.serve_forever()
                finally:
                    handle.close()

            thread = threading.Thread(target=serve, daemon=True)
            thread.start()
            self.assertTrue(ready.wait(timeout=10))
            handle = handle_holder["handle"]
            try:
                stdout = io.StringIO()
                code = eureka_local_review_smoke.main(
                    ["--base-url", f"http://127.0.0.1:{handle.server_port}", "--operator-token", TOKEN, "--json"],
                    stdout=stdout,
                )
            finally:
                handle.shutdown()
                thread.join(timeout=5)

        self.assertEqual(0, code, stdout.getvalue())
        self.assertTrue(json.loads(stdout.getvalue())["rebuild_with_token_passed"])

    def test_validator_passes(self) -> None:
        result = validate_local_review_rebuild.validate(Path(__file__).resolve().parents[2])

        self.assertIn(result["status"], {"pass", "pass_with_warnings"}, result["errors"])


if __name__ == "__main__":
    unittest.main()
