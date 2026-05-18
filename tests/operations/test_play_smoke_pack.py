import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]


def run_script(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, *args], cwd=ROOT, text=True, capture_output=True, check=False)


def load_json(relative: str) -> dict:
    return json.loads((ROOT / relative).read_text(encoding="utf-8"))


class PlaySmokePackTests(unittest.TestCase):
    def test_query_matrix_validates_required_rows(self):
        matrix = load_json("control/inventory/play_smoke_query_matrix.json")
        rows = {item["query_id"]: item for item in matrix["queries"]}
        for query_id in (
            "known_hit",
            "known_absence",
            "media_search_need",
            "extraction_search_need",
            "hard_source_routing",
            "compatibility",
        ):
            self.assertIn(query_id, rows)
            self.assertTrue(rows[query_id]["smoke_assertions"])
            self.assertIn("must_not_create", rows[query_id])

    def test_route_matrix_validates_required_rows(self):
        matrix = load_json("control/inventory/play_smoke_route_matrix.json")
        rows = {item["route_id"]: item for item in matrix["routes"]}
        for route_id in (
            "root_page",
            "status_page",
            "search_known_hit",
            "search_known_absence",
            "hunts_page",
            "hunt_detail_if_available",
            "search_need_detail_if_available",
            "workunit_detail_or_list_if_available",
            "api_search",
            "api_absence",
            "api_hunts_if_available",
            "api_status",
        ):
            self.assertIn(route_id, rows)
            self.assertEqual("GET", rows[route_id]["method"])

    def test_result_schema_sections_present(self):
        schema = load_json("control/inventory/play_smoke_result_schema.json")
        sections = {item["section"] for item in schema["sections"]}
        for section in (
            "instance",
            "seed",
            "query_results",
            "absence_results",
            "hunts",
            "search_needs",
            "workunits",
            "blocked_future_actions",
            "routes",
            "validation",
            "boundaries",
            "warnings",
            "next_actions",
        ):
            self.assertIn(section, sections)

    def test_smoke_report_sections_present(self):
        completed = run_script(
            "scripts/eureka_play_smoke.py",
            "--use-temp-instance",
            "--apply-demo-to-temp",
            "--operator-token",
            "local-dev-token",
            "--json",
        )
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        payload = json.loads(completed.stdout)
        for section in payload["required_report_sections"]:
            self.assertIn(section, payload)
        checks = payload["validation"]["checks"]
        self.assertTrue(checks["known_hit_checked"])
        self.assertTrue(checks["known_absence_checked"])
        self.assertTrue(checks["media_search_need_checked"])
        self.assertTrue(checks["extraction_search_need_checked"])
        self.assertTrue(checks["hard_source_routing_checked"])
        self.assertTrue(checks["compatibility_query_checked"])
        self.assertTrue(checks["blocked_source_probe_checked"])
        self.assertTrue(checks["blocked_extraction_checked"])
        self.assertTrue(checks["blocked_ai_checked"])

    def test_dry_run_does_not_touch_operator_instance(self):
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "instances" / "default"
            completed = run_script(
                "scripts/eureka_play_smoke.py",
                "--instance",
                str(instance),
                "--operator-token",
                "local-dev-token",
                "--dry-run",
                "--json",
            )
            self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
            payload = json.loads(completed.stdout)
            self.assertFalse(payload["operator_instance_mutated"])
            self.assertFalse(instance.exists())

    def test_validator_passes(self):
        completed = run_script("scripts/validate_play_smoke_pack.py")
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        payload = json.loads(completed.stdout)
        self.assertEqual("pass", payload["status"], payload)
        self.assertTrue(payload["temp_instance_apply_passed"])
        self.assertTrue(payload["dry_run_does_not_mutate_operator_instance"])

    def test_no_forbidden_side_effects(self):
        completed = run_script(
            "scripts/eureka_play_smoke.py",
            "--use-temp-instance",
            "--apply-demo-to-temp",
            "--operator-token",
            "local-dev-token",
            "--json",
        )
        self.assertEqual(0, completed.returncode, completed.stdout + completed.stderr)
        payload = json.loads(completed.stdout)
        for key in (
            "operator_instance_mutated",
            "instance_state_committed",
            "fake_evidence_created",
            "fake_verified_records_created",
            "live_source_call_performed",
            "source_probe_executed",
            "extraction_executed",
            "model_provider_used",
            "download_install_execute_performed",
            "deployment_performed",
            "production_readiness_claimed",
            "public_launch_readiness_claimed",
        ):
            self.assertFalse(payload[key], key)


if __name__ == "__main__":
    unittest.main()
