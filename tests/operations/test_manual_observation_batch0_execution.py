from __future__ import annotations

from copy import deepcopy
import io
import json
from pathlib import Path
import socket
import tempfile
import unittest
from unittest.mock import patch

from scripts.prepare_manual_observation_batch0_execution import (
    BATCH_PENDING,
    BATCH_ROOT,
    build_slot_manifest,
    main as prepare_main,
)
from scripts.validate_manual_observation_batch0_execution import (
    EXECUTION_INVENTORY_PATH,
    SLOT_MANIFEST_PATH,
    validate_execution_inventory,
    validate_manual_observation_batch0_execution,
    validate_slot_manifest,
)


REPO_ROOT = Path(__file__).resolve().parents[2]


class ManualObservationBatch0ExecutionTest(unittest.TestCase):
    def test_preparation_script_runs_current_repo(self) -> None:
        output = io.StringIO()

        result = prepare_main(["--repo-root", str(REPO_ROOT), "--check"], stdout=output)

        self.assertEqual(result, 0)
        self.assertIn("ready_for_manual_execution", output.getvalue())

    def test_preparation_script_writes_deterministic_json_to_explicit_temp_path(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output_path = Path(temp) / "slot_execution_manifest.json"
            args = ["--repo-root", str(REPO_ROOT), "--json-output", str(output_path)]

            self.assertEqual(prepare_main(args, stdout=io.StringIO()), 0)
            first = output_path.read_text(encoding="utf-8")
            self.assertEqual(prepare_main(args, stdout=io.StringIO()), 0)
            second = output_path.read_text(encoding="utf-8")

        self.assertEqual(first, second)
        payload = json.loads(first)
        self.assertEqual(payload["slot_count"], 39)
        self.assertEqual(payload["status_counts"], {"pending_manual_observation": 39})

    def test_preparation_script_writes_no_files_by_default(self) -> None:
        watched = [REPO_ROOT / BATCH_PENDING]
        before = _fingerprint(watched)

        prepare_main(["--repo-root", str(REPO_ROOT)], stdout=io.StringIO())

        self.assertEqual(before, _fingerprint(watched))

    def test_preparation_script_does_not_create_observed_files(self) -> None:
        before = _observed_files()

        prepare_main(["--repo-root", str(REPO_ROOT), "--check"], stdout=io.StringIO())

        self.assertEqual(before, _observed_files())

    def test_preparation_script_does_not_mutate_pending_slot_status(self) -> None:
        before = json.loads((REPO_ROOT / BATCH_PENDING).read_text(encoding="utf-8"))

        prepare_main(["--repo-root", str(REPO_ROOT), "--check"], stdout=io.StringIO())

        after = json.loads((REPO_ROOT / BATCH_PENDING).read_text(encoding="utf-8"))
        self.assertEqual(before, after)

    def test_validator_passes_current_repo(self) -> None:
        report = validate_manual_observation_batch0_execution(REPO_ROOT)

        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["errors"], [])

    def test_product_boundary_true_claim_fails(self) -> None:
        inventory = _read_json(REPO_ROOT / EXECUTION_INVENTORY_PATH)
        broken = deepcopy(inventory)
        broken["product_boundary"]["opened_browsers"] = True

        errors = validate_execution_inventory(broken, "broken_inventory", REPO_ROOT)

        self.assertTrue(any("opened_browsers" in error for error in errors))

    def test_slot_manifest_observed_missing_fields_fails(self) -> None:
        manifest = _read_json(REPO_ROOT / SLOT_MANIFEST_PATH)
        broken = deepcopy(manifest)
        broken["slots"][0]["slot_status"] = "observed"
        broken["status_counts"] = {"observed": 1, "pending_manual_observation": 38}

        errors = validate_slot_manifest(broken, "broken_manifest")

        self.assertTrue(any("observed_file_path_if_any" in error for error in errors))
        self.assertTrue(any("required_fields_status" in error for error in errors))

    def test_pending_stub_is_not_counted_as_observed(self) -> None:
        manifest = build_slot_manifest(repo_root=REPO_ROOT)
        broken = deepcopy(manifest)
        broken["slots"][0]["slot_status"] = "pending_stub"
        broken["status_counts"] = {"pending_manual_observation": 38, "pending_stub": 1}

        errors = validate_slot_manifest(broken, "pending_stub_manifest")

        self.assertFalse(any("observed" in error for error in errors))

    def test_browser_network_api_model_provider_claim_fails(self) -> None:
        inventory = _read_json(REPO_ROOT / EXECUTION_INVENTORY_PATH)
        broken = deepcopy(inventory)
        broken["forbidden_automation"].remove("external_api_call")
        broken["product_boundary"]["called_external_apis"] = True

        errors = validate_execution_inventory(broken, "broken_inventory", REPO_ROOT)

        self.assertTrue(any("external_api_call" in error for error in errors))
        self.assertTrue(any("called_external_apis" in error for error in errors))

    def test_scripts_do_not_call_network(self) -> None:
        with patch.object(socket, "create_connection", side_effect=AssertionError("network call")) as mocked:
            manifest = build_slot_manifest(repo_root=REPO_ROOT)
            report = validate_manual_observation_batch0_execution(REPO_ROOT)

        self.assertEqual(manifest["validation_status"], "ready_for_manual_execution")
        self.assertEqual(report["status"], "valid")
        mocked.assert_not_called()

    def test_scripts_do_not_mutate_product_files(self) -> None:
        watched = [REPO_ROOT / BATCH_PENDING]
        before = _fingerprint(watched)

        build_slot_manifest(repo_root=REPO_ROOT)
        validate_manual_observation_batch0_execution(REPO_ROOT)

        self.assertEqual(before, _fingerprint(watched))


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _observed_files() -> list[str]:
    observations_dir = REPO_ROOT / BATCH_ROOT / "observations"
    return sorted(path.name for path in observations_dir.glob("*.json") if not path.name.startswith("pending_"))


def _fingerprint(paths: list[Path]) -> list[tuple[str, int, int]]:
    return sorted((str(path), path.stat().st_size, path.stat().st_mtime_ns) for path in paths)


if __name__ == "__main__":
    unittest.main()
