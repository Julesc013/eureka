from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
import unittest


REPO_ROOT = Path(__file__).resolve().parents[2]
PLAN_DIR = REPO_ROOT / "control" / "audits" / "relay-prototype-planning-v0"
PLAN_JSON = PLAN_DIR / "relay_prototype_plan.json"
VALIDATOR = REPO_ROOT / "scripts" / "validate_relay_prototype_plan.py"
RELAY_SURFACE_VALIDATOR = REPO_ROOT / "scripts" / "validate_relay_surface_design.py"

REQUIRED_FILES = {
    "README.md",
    "CURRENT_STATE.md",
    "PROTOTYPE_SCOPE.md",
    "PROTOCOL_DECISION.md",
    "INPUT_DATA_CONTRACT.md",
    "OUTPUT_SURFACE_CONTRACT.md",
    "SECURITY_PRIVACY_REVIEW.md",
    "OPERATOR_GATES.md",
    "TEST_PLAN.md",
    "RISKS.md",
    "IMPLEMENTATION_BOUNDARIES.md",
    "NEXT_IMPLEMENTATION_PROMPT_REQUIREMENTS.md",
    "relay_prototype_plan.json",
}


class RelayPrototypePlanningTestCase(unittest.TestCase):
    def test_planning_pack_exists(self) -> None:
        self.assertTrue(PLAN_DIR.is_dir())
        present = {path.name for path in PLAN_DIR.iterdir() if path.is_file()}
        self.assertTrue(REQUIRED_FILES.issubset(present))

    def test_plan_json_records_decision_and_no_implementation(self) -> None:
        payload = _load_json(PLAN_JSON)

        self.assertEqual(payload["status"], "planning_only")
        self.assertEqual(payload["decision"], "first_future_relay_prototype_should_be_local_static_http")
        self.assertEqual(payload["recommended_first_prototype"], "local_static_http_relay_prototype")
        self.assertFalse(payload["implementation_approved"])
        self.assertTrue(payload["human_approval_required"])
        self.assertTrue(payload["no_relay_runtime_implemented"])
        self.assertTrue(payload["no_network_sockets_opened"])
        self.assertTrue(payload["no_protocol_servers_implemented"])

    def test_local_static_http_is_selected_or_justified(self) -> None:
        payload = _load_json(PLAN_JSON)

        first = payload["first_protocol_candidate"]
        self.assertEqual(first["id"], "local_static_http")
        self.assertEqual(first["default_bind_scope"], "localhost_only")
        self.assertEqual(first["mode"], "read_only")
        rejected_ids = {item["id"] for item in payload["rejected_first_protocol_candidates"]}
        self.assertTrue(
            {
                "read_only_ftp_mirror",
                "webdav_read_only",
                "smb_read_only",
                "gopher_experimental",
                "native_sidecar",
                "snapshot_mount",
            }.issubset(rejected_ids)
        )

    def test_input_output_allowlists_and_prohibitions(self) -> None:
        payload = _load_json(PLAN_JSON)

        self.assertTrue(
            {
                "site/dist/data/*.json",
                "site/dist/text/*",
                "site/dist/files/*",
                "snapshots/examples/static_snapshot_v0/*",
            }.issubset(set(payload["allowed_initial_inputs"]))
        )
        self.assertTrue(
            {
                "arbitrary user directories",
                "credentials",
                "live API responses",
                "live probe outputs",
                "external URLs",
            }.issubset(set(payload["prohibited_initial_inputs"]))
        )
        self.assertTrue(
            {
                "read-only HTTP pages",
                "plain text pages",
                "JSON static summaries",
                "checksum files",
                "snapshot manifest views",
            }.issubset(set(payload["allowed_initial_outputs"]))
        )
        self.assertTrue(
            {
                "write endpoints",
                "upload endpoints",
                "live probe endpoints",
                "arbitrary file serving",
                "executable launch",
            }.issubset(set(payload["prohibited_initial_outputs"]))
        )

    def test_security_defaults_are_local_read_only_and_static(self) -> None:
        security = _load_json(PLAN_JSON)["security_defaults"]

        self.assertEqual(security["bind_scope"], "localhost_only")
        self.assertFalse(security["lan_bind_allowed"])
        self.assertFalse(security["public_internet_exposure_allowed"])
        self.assertTrue(security["read_only"])
        self.assertTrue(security["public_data_only"])
        self.assertFalse(security["private_data_allowed"])
        self.assertFalse(security["writes_allowed"])
        self.assertFalse(security["uploads_allowed"])
        self.assertFalse(security["live_backend_proxy_allowed"])
        self.assertFalse(security["live_probes_allowed"])
        self.assertFalse(security["downloads_allowed"])
        self.assertFalse(security["executable_launch_allowed"])

    def test_docs_state_planning_only_and_approval_required(self) -> None:
        text = "\n".join(path.read_text(encoding="utf-8") for path in PLAN_DIR.glob("*.md"))

        self.assertIn("planning only", text)
        self.assertIn("explicit human approval", text)
        self.assertIn("no relay runtime exists", text)
        self.assertIn("no sockets or listeners exist", text)
        self.assertIn("localhost bind only by default", text)
        self.assertIn("no private file roots", text)

    def test_no_obvious_relay_server_scripts_exist(self) -> None:
        suspicious_names = {
            "relay_server.py",
            "run_relay.py",
            "local_http_relay.py",
            "relay_runtime.py",
            "relay_proxy.py",
            "ftp_relay.py",
            "smb_relay.py",
            "webdav_relay.py",
            "gopher_relay.py",
            "snapshot_mount.py",
        }
        offenders = [
            str(path.relative_to(REPO_ROOT))
            for path in REPO_ROOT.rglob("*.py")
            if ".git" not in path.parts
            and "__pycache__" not in path.parts
            and path.name.casefold() in suspicious_names
        ]

        self.assertEqual(offenders, [])

    def test_validator_passes_and_relay_surface_validator_still_passes(self) -> None:
        result = subprocess.run(
            [sys.executable, str(VALIDATOR), "--json"],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["status"], "valid")

        relay_result = subprocess.run(
            [sys.executable, str(RELAY_SURFACE_VALIDATOR)],
            cwd=REPO_ROOT,
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(relay_result.returncode, 0, relay_result.stderr)
        self.assertIn("status: valid", relay_result.stdout)


def _load_json(path: Path) -> dict[str, object]:
    return json.loads(path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
