import json
import unittest

from surfaces.web.server.route_policy import PublicAlphaRoutePolicy
from surfaces.web.server.server_config import WebServerConfig
from tests.hardening.helpers import find_private_path_leaks, load_json, run_python


SENTINEL_PATH = r"D:\private\eureka-secret-root\index.sqlite3"


class PublicAlphaPathLeakageTest(unittest.TestCase):
    def test_public_alpha_smoke_json_passes(self):
        completed = run_python(["scripts/public_alpha_smoke.py", "--json"], timeout=90)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        report = json.loads(completed.stdout)
        self.assertEqual(report["status"], "passed")
        self.assertEqual(report["mode"], "public_alpha")
        self.assertEqual(report["failed_checks"], 0)

    def test_status_projection_hides_configured_private_paths(self):
        config = WebServerConfig.public_alpha(
            index_root=SENTINEL_PATH,
            run_store_root=SENTINEL_PATH,
            task_store_root=SENTINEL_PATH,
            memory_store_root=SENTINEL_PATH,
            export_store_root=SENTINEL_PATH,
        )
        status = config.to_status_dict()
        serialized = json.dumps(status, sort_keys=True)

        self.assertNotIn(SENTINEL_PATH, serialized)
        self.assertIn('"index_root": "configured"', serialized)
        self.assertIn('"run_store_root": "configured"', serialized)
        self.assertEqual(find_private_path_leaks(status), [])

    def test_blocked_response_reports_parameter_names_not_values(self):
        config = WebServerConfig.public_alpha()
        policy = PublicAlphaRoutePolicy(config)
        decision = policy.evaluate_api_request(
            "/api/index/status",
            {"index_path": [SENTINEL_PATH]},
        )

        self.assertFalse(decision.allowed)
        payload = decision.to_blocked_payload()
        serialized = json.dumps(payload, sort_keys=True)
        self.assertNotIn(SENTINEL_PATH, serialized)
        self.assertEqual(payload["blocked_parameters"], ["index_path"])
        self.assertEqual(find_private_path_leaks(payload), [])

    def test_route_inventory_never_marks_local_path_routes_safe(self):
        inventory = load_json("control/inventory/public_alpha_routes.json")
        unsafe_safe_routes = []
        for route in inventory["routes"]:
            local_path_parameters = route.get("local_path_parameters", [])
            if not local_path_parameters:
                continue
            classification = route["classification"]
            if classification == "safe_public_alpha":
                unsafe_safe_routes.append(route["route_pattern"])
            self.assertIn(
                classification,
                {"blocked_public_alpha", "local_dev_only", "review_required"},
                route["route_pattern"],
            )
            self.assertNotEqual(route["mode_behavior"]["public_alpha"], "allowed", route["route_pattern"])

        self.assertEqual(unsafe_safe_routes, [])


if __name__ == "__main__":
    unittest.main()
