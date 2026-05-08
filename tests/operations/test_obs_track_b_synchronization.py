from __future__ import annotations

from contextlib import ExitStack
from copy import deepcopy
import hashlib
import io
import json
from pathlib import Path
import socket
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import urllib.request
import webbrowser

from scripts.audit_obs_track_b_synchronization import main as audit_main
from scripts.summarize_obs_track_b_handoff import main as summarize_main
from scripts.validate_obs_track_b_synchronization import (
    validate_mapping_payload,
    validate_matrix_payload,
    validate_obs_track_b_synchronization,
    validate_policy_payload,
    validate_readiness_payload,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
PENDING_BATCH = REPO_ROOT / "evals/search_usefulness/external_baselines/batches/batch_0/observations/pending_batch_0_observations.json"
SLOT_MANIFEST = REPO_ROOT / "control/inventory/observations/manual_observation_batch_0_slot_manifest.json"
TRACK_B_FILES = [
    REPO_ROOT / "contracts/node/eureka_node_manifest.v0.json",
    REPO_ROOT / "contracts/node/node_policy.v0.json",
    REPO_ROOT / "contracts/node/node_capability.v0.json",
    REPO_ROOT / "contracts/node/work_unit.v0.json",
    REPO_ROOT / "contracts/node/work_unit_result.v0.json",
    REPO_ROOT / "contracts/node/local_foundry_state.v0.json",
]
OBSERVATION_DIRS = [
    REPO_ROOT / "evals/search_usefulness/external_baselines/batches/batch_0/observations",
    REPO_ROOT / "evals/search_usefulness/external_baselines/observations",
]


class ObsTrackBSynchronizationTest(unittest.TestCase):
    def test_sync_policy_validates(self) -> None:
        policy = _read_json(REPO_ROOT / "control/inventory/observations/obs_track_b_sync_policy.json")

        self.assertEqual(validate_policy_payload(policy, "policy"), [])

    def test_sync_matrix_validates(self) -> None:
        matrix = _matrix()

        self.assertEqual(validate_matrix_payload(matrix, "matrix", REPO_ROOT), [])

    def test_handoff_readiness_validates(self) -> None:
        readiness = _read_json(REPO_ROOT / "control/inventory/observations/obs_track_b_handoff_readiness.json")

        self.assertEqual(validate_readiness_payload(readiness, "readiness"), [])

    def test_audit_script_runs_on_current_repo_state(self) -> None:
        output = io.StringIO()

        result = audit_main(["--repo-root", str(REPO_ROOT)], stdout=output)

        self.assertEqual(result, 0)
        self.assertIn("sync_mapping_count", output.getvalue())

    def test_audit_script_list_inputs_output_is_non_empty(self) -> None:
        output = io.StringIO()

        result = audit_main(["--repo-root", str(REPO_ROOT), "--list-inputs"], stdout=output)

        self.assertEqual(result, 0)
        lines = [line for line in output.getvalue().splitlines() if line.strip()]
        self.assertGreater(len(lines), 20)
        self.assertIn("contracts/node/work_unit.v0.json", lines)

    def test_audit_script_check_passes(self) -> None:
        output = io.StringIO()

        result = audit_main(["--repo-root", str(REPO_ROOT), "--check"], stdout=output)

        self.assertEqual(result, 0)
        self.assertIn("pass", output.getvalue())

    def test_json_output_writes_deterministic_json(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            first = Path(temp) / "first.json"
            second = Path(temp) / "second.json"

            self.assertEqual(audit_main(["--repo-root", str(REPO_ROOT), "--json-output", str(first)], stdout=io.StringIO()), 0)
            self.assertEqual(audit_main(["--repo-root", str(REPO_ROOT), "--json-output", str(second)], stdout=io.StringIO()), 0)

            self.assertEqual(first.read_text(encoding="utf-8"), second.read_text(encoding="utf-8"))
            payload = json.loads(first.read_text(encoding="utf-8"))
            self.assertEqual(len(payload["mappings"]), 9)

    def test_markdown_output_writes_deterministic_summary(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            first = Path(temp) / "first.md"
            second = Path(temp) / "second.md"

            self.assertEqual(audit_main(["--repo-root", str(REPO_ROOT), "--markdown-output", str(first)], stdout=io.StringIO()), 0)
            self.assertEqual(audit_main(["--repo-root", str(REPO_ROOT), "--markdown-output", str(second)], stdout=io.StringIO()), 0)

            self.assertEqual(first.read_text(encoding="utf-8"), second.read_text(encoding="utf-8"))
            self.assertIn("Handoff Matrix", first.read_text(encoding="utf-8"))

    def test_summarizer_runs_without_mutating(self) -> None:
        output = io.StringIO()

        result = summarize_main(["--repo-root", str(REPO_ROOT)], stdout=output)

        self.assertEqual(result, 0)
        self.assertIn("by_handoff_state", output.getvalue())

    def test_summarizer_explicit_outputs_are_deterministic(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            first_json = Path(temp) / "first.json"
            second_json = Path(temp) / "second.json"
            first_md = Path(temp) / "first.md"
            second_md = Path(temp) / "second.md"

            self.assertEqual(summarize_main(["--repo-root", str(REPO_ROOT), "--json-output", str(first_json), "--markdown-output", str(first_md)], stdout=io.StringIO()), 0)
            self.assertEqual(summarize_main(["--repo-root", str(REPO_ROOT), "--json-output", str(second_json), "--markdown-output", str(second_md)], stdout=io.StringIO()), 0)

            self.assertEqual(first_json.read_text(encoding="utf-8"), second_json.read_text(encoding="utf-8"))
            self.assertEqual(first_md.read_text(encoding="utf-8"), second_md.read_text(encoding="utf-8"))

    def test_validator_passes_current_repo(self) -> None:
        report = validate_obs_track_b_synchronization(REPO_ROOT)

        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["errors"], [])

    def test_mapping_with_runtime_activation_true_fails(self) -> None:
        mapping = _mapping()
        mapping["runtime_activation_allowed_now"] = True

        errors = validate_mapping_payload(mapping, "broken_matrix", REPO_ROOT)

        self.assertTrue(any("runtime_activation_allowed_now" in error for error in errors))

    def test_mapping_with_accepted_evidence_truth_true_fails(self) -> None:
        mapping = _mapping()
        mapping["accepted_as_evidence_truth"] = True

        errors = validate_mapping_payload(mapping, "broken_matrix", REPO_ROOT)

        self.assertTrue(any("accepted_as_evidence_truth" in error for error in errors))

    def test_mapping_with_master_index_mutation_true_fails(self) -> None:
        mapping = _mapping()
        mapping["master_index_mutation_allowed"] = True

        errors = validate_mapping_payload(mapping, "broken_matrix", REPO_ROOT)

        self.assertTrue(any("master_index_mutation_allowed" in error for error in errors))

    def test_mapping_with_source_access_approved_true_fails(self) -> None:
        mapping = _mapping()
        mapping["source_access_approved"] = True

        errors = validate_mapping_payload(mapping, "broken_matrix", REPO_ROOT)

        self.assertTrue(any("source_access_approved" in error for error in errors))

    def test_mapping_creating_runtime_search_need_fails(self) -> None:
        mapping = _mapping()
        mapping["creates_runtime_search_need"] = True

        errors = validate_mapping_payload(mapping, "broken_matrix", REPO_ROOT)

        self.assertTrue(any("creates_runtime_search_need" in error for error in errors))

    def test_mapping_creating_runtime_workunit_fails(self) -> None:
        mapping = _mapping()
        mapping["creates_runtime_workunit"] = True

        errors = validate_mapping_payload(mapping, "broken_matrix", REPO_ROOT)

        self.assertTrue(any("creates_runtime_workunit" in error for error in errors))

    def test_mapping_executing_workunit_fails(self) -> None:
        mapping = _mapping()
        mapping["executes_workunit"] = True

        errors = validate_mapping_payload(mapping, "broken_matrix", REPO_ROOT)

        self.assertTrue(any("executes_workunit" in error for error in errors))

    def test_external_observation_claim_fails(self) -> None:
        mapping = _mapping()
        mapping["notes"] = ["External observation performed for this mapping."]

        errors = validate_mapping_payload(mapping, "broken_matrix", REPO_ROOT)

        self.assertTrue(any("external observation performed" in error for error in errors))

    def test_live_source_claim_fails(self) -> None:
        mapping = _mapping()
        mapping["notes"] = ["Live source observed for this mapping."]

        errors = validate_mapping_payload(mapping, "broken_matrix", REPO_ROOT)

        self.assertTrue(any("live source observed" in error for error in errors))

    def test_google_scrape_claim_fails(self) -> None:
        mapping = _mapping()
        mapping["notes"] = ["Google scrape was used."]

        errors = validate_mapping_payload(mapping, "broken_matrix", REPO_ROOT)

        self.assertTrue(any("google scrape" in error for error in errors))

    def test_script_does_not_create_observed_files(self) -> None:
        before = _observed_file_names()
        with tempfile.TemporaryDirectory() as temp:
            output_path = Path(temp) / "sync.json"
            self.assertEqual(audit_main(["--repo-root", str(REPO_ROOT), "--json-output", str(output_path)], stdout=io.StringIO()), 0)

        self.assertEqual(before, _observed_file_names())

    def test_scripts_do_not_mutate_pending_observations(self) -> None:
        watched = [PENDING_BATCH, SLOT_MANIFEST]
        before = _fingerprint(watched)

        with tempfile.TemporaryDirectory() as temp:
            self.assertEqual(audit_main(["--repo-root", str(REPO_ROOT), "--json-output", str(Path(temp) / "sync.json")], stdout=io.StringIO()), 0)
            self.assertEqual(summarize_main(["--repo-root", str(REPO_ROOT), "--json-output", str(Path(temp) / "summary.json")], stdout=io.StringIO()), 0)

        self.assertEqual(before, _fingerprint(watched))

    def test_scripts_do_not_mutate_track_b_files(self) -> None:
        before = _fingerprint(TRACK_B_FILES)

        with tempfile.TemporaryDirectory() as temp:
            self.assertEqual(audit_main(["--repo-root", str(REPO_ROOT), "--json-output", str(Path(temp) / "sync.json")], stdout=io.StringIO()), 0)
            self.assertEqual(summarize_main(["--repo-root", str(REPO_ROOT), "--markdown-output", str(Path(temp) / "summary.md")], stdout=io.StringIO()), 0)

        self.assertEqual(before, _fingerprint(TRACK_B_FILES))

    def test_scripts_do_not_call_network_api_browser_model_or_provider(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output_path = Path(temp) / "sync.json"
            with ExitStack() as stack:
                stack.enter_context(patch.object(socket, "create_connection", side_effect=AssertionError("network call")))
                stack.enter_context(patch.object(socket, "socket", side_effect=AssertionError("socket call")))
                stack.enter_context(patch.object(urllib.request, "urlopen", side_effect=AssertionError("urlopen call")))
                stack.enter_context(patch.object(webbrowser, "open", side_effect=AssertionError("browser call")))
                stack.enter_context(patch.object(subprocess, "run", side_effect=AssertionError("external command call")))
                audit_result = audit_main(["--repo-root", str(REPO_ROOT), "--json-output", str(output_path), "--check"], stdout=io.StringIO())
                summary_result = summarize_main(["--repo-root", str(REPO_ROOT)], stdout=io.StringIO())

        self.assertEqual(audit_result, 0)
        self.assertEqual(summary_result, 0)


def _matrix() -> dict:
    return deepcopy(_read_json(REPO_ROOT / "control/inventory/observations/obs_track_b_sync_matrix.json"))


def _mapping() -> dict:
    return deepcopy(_matrix()["mappings"][0])


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _fingerprint(paths: list[Path]) -> dict[str, str]:
    result: dict[str, str] = {}
    for path in paths:
        if path.is_file():
            result[str(path)] = hashlib.sha256(path.read_bytes()).hexdigest()
        else:
            result[str(path)] = "<missing>"
    return result


def _observed_file_names() -> list[str]:
    names: list[str] = []
    for directory in OBSERVATION_DIRS:
        if directory.is_dir():
            names.extend(path.name for path in sorted(directory.glob("*.json")) if path.name.lower().startswith(("observed", "accepted")))
    return names


if __name__ == "__main__":
    unittest.main()
