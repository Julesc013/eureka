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

from scripts.mine_local_eval_observation_candidates import main as mine_main
from scripts.validate_obs_agent_local_eval_mining import (
    validate_candidate_payload,
    validate_obs_agent_local_eval_mining,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
PENDING_BATCH = REPO_ROOT / "evals/search_usefulness/external_baselines/batches/batch_0/observations/pending_batch_0_observations.json"
SLOT_MANIFEST = REPO_ROOT / "control/inventory/observations/manual_observation_batch_0_slot_manifest.json"
TRACK_B_FILES = [
    REPO_ROOT / "contracts/node/eureka_node_manifest.v0.json",
    REPO_ROOT / "contracts/node/node_policy.v0.json",
    REPO_ROOT / "contracts/schema/control/policies/node/node_capability.v0.json",
    REPO_ROOT / "contracts/schema/control/policies/node/work_unit.v0.json",
    REPO_ROOT / "contracts/schema/control/policies/node/work_unit_result.v0.json",
    REPO_ROOT / "contracts/schema/control/policies/node/local_foundry_state.v0.json",
]
OBSERVATION_DIRS = [
    REPO_ROOT / "evals/search_usefulness/external_baselines/batches/batch_0/observations",
    REPO_ROOT / "evals/search_usefulness/external_baselines/observations",
]


class ObsAgentLocalEvalMiningTest(unittest.TestCase):
    def test_mining_script_runs_on_current_repo_state(self) -> None:
        output = io.StringIO()

        result = mine_main(["--repo-root", str(REPO_ROOT)], stdout=output)

        self.assertEqual(result, 0)
        self.assertIn("candidate_count", output.getvalue())

    def test_list_inputs_output_is_non_empty(self) -> None:
        output = io.StringIO()

        result = mine_main(["--repo-root", str(REPO_ROOT), "--list-inputs"], stdout=output)

        self.assertEqual(result, 0)
        lines = [line for line in output.getvalue().splitlines() if line.strip()]
        self.assertGreater(len(lines), 5)
        self.assertIn("site/dist/data/eval_summary.json", lines)

    def test_check_passes(self) -> None:
        output = io.StringIO()

        result = mine_main(["--repo-root", str(REPO_ROOT), "--check"], stdout=output)

        self.assertEqual(result, 0)
        self.assertIn("pass", output.getvalue())

    def test_json_output_writes_deterministic_json_to_explicit_temp_path(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            first = Path(temp) / "first.json"
            second = Path(temp) / "second.json"

            self.assertEqual(mine_main(["--repo-root", str(REPO_ROOT), "--json-output", str(first)], stdout=io.StringIO()), 0)
            self.assertEqual(mine_main(["--repo-root", str(REPO_ROOT), "--json-output", str(second)], stdout=io.StringIO()), 0)

            self.assertEqual(first.read_text(encoding="utf-8"), second.read_text(encoding="utf-8"))
            payload = json.loads(first.read_text(encoding="utf-8"))
            self.assertEqual(payload["candidate_count"], 5)

    def test_markdown_output_writes_deterministic_summary_to_explicit_temp_path(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            first = Path(temp) / "first.md"
            second = Path(temp) / "second.md"

            self.assertEqual(mine_main(["--repo-root", str(REPO_ROOT), "--markdown-output", str(first)], stdout=io.StringIO()), 0)
            self.assertEqual(mine_main(["--repo-root", str(REPO_ROOT), "--markdown-output", str(second)], stdout=io.StringIO()), 0)

            self.assertEqual(first.read_text(encoding="utf-8"), second.read_text(encoding="utf-8"))
            self.assertIn("Human Review Required", first.read_text(encoding="utf-8"))

    def test_validator_passes_current_repo(self) -> None:
        report = validate_obs_agent_local_eval_mining(REPO_ROOT)

        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["errors"], [])

    def test_candidate_with_observed_baseline_true_fails(self) -> None:
        candidate = _candidate()
        candidate["accepted_as_observed_baseline"] = True

        errors = validate_candidate_payload(candidate, "broken_candidate")

        self.assertTrue(any("accepted_as_observed_baseline" in error for error in errors))

    def test_candidate_with_evidence_truth_true_fails(self) -> None:
        candidate = _candidate()
        candidate["accepted_as_evidence_truth"] = True

        errors = validate_candidate_payload(candidate, "broken_candidate")

        self.assertTrue(any("accepted_as_evidence_truth" in error for error in errors))

    def test_candidate_with_master_index_mutation_true_fails(self) -> None:
        candidate = _candidate()
        candidate["master_index_mutation_allowed"] = True

        errors = validate_candidate_payload(candidate, "broken_candidate")

        self.assertTrue(any("master_index_mutation_allowed" in error for error in errors))

    def test_live_source_claim_fails(self) -> None:
        candidate = _candidate()
        candidate["candidate_summary"] = "Live source observed for this candidate."

        errors = validate_candidate_payload(candidate, "broken_candidate")

        self.assertTrue(any("live source observed" in error for error in errors))

    def test_external_observation_claim_fails(self) -> None:
        candidate = _candidate()
        candidate["product_boundary"]["performed_observations"] = True
        candidate["candidate_summary"] = "External observation performed by this record."

        errors = validate_candidate_payload(candidate, "broken_candidate")

        self.assertTrue(any("performed_observations" in error for error in errors))
        self.assertTrue(any("external observation performed" in error for error in errors))

    def test_google_scrape_claim_fails(self) -> None:
        candidate = _candidate()
        candidate["candidate_summary"] = "This record contains a scraped Google result."

        errors = validate_candidate_payload(candidate, "broken_candidate")

        self.assertTrue(any("scraped google result" in error for error in errors))

    def test_source_access_mode_approved_api_future_fails_without_explicit_approval(self) -> None:
        candidate = _candidate()
        candidate["source_access_mode"] = "approved_api_future"
        candidate["source_policy_status"] = "future_deferred"

        errors = validate_candidate_payload(candidate, "broken_candidate")

        self.assertTrue(any("source_access_mode" in error for error in errors))

    def test_script_does_not_create_observed_files(self) -> None:
        before = _observed_file_names()
        with tempfile.TemporaryDirectory() as temp:
            output_path = Path(temp) / "manifest.json"
            self.assertEqual(mine_main(["--repo-root", str(REPO_ROOT), "--json-output", str(output_path)], stdout=io.StringIO()), 0)

        self.assertEqual(before, _observed_file_names())

    def test_script_does_not_mutate_pending_observations(self) -> None:
        watched = [PENDING_BATCH, SLOT_MANIFEST]
        before = _fingerprint(watched)

        with tempfile.TemporaryDirectory() as temp:
            self.assertEqual(
                mine_main(
                    [
                        "--repo-root",
                        str(REPO_ROOT),
                        "--json-output",
                        str(Path(temp) / "manifest.json"),
                        "--markdown-output",
                        str(Path(temp) / "summary.md"),
                    ],
                    stdout=io.StringIO(),
                ),
                0,
            )

        self.assertEqual(before, _fingerprint(watched))

    def test_script_does_not_mutate_track_b_files(self) -> None:
        before = _fingerprint(TRACK_B_FILES)

        with tempfile.TemporaryDirectory() as temp:
            self.assertEqual(mine_main(["--repo-root", str(REPO_ROOT), "--json-output", str(Path(temp) / "manifest.json")], stdout=io.StringIO()), 0)

        self.assertEqual(before, _fingerprint(TRACK_B_FILES))

    def test_script_does_not_call_network_api_browser_model_or_provider(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output_path = Path(temp) / "manifest.json"
            with ExitStack() as stack:
                stack.enter_context(patch.object(socket, "create_connection", side_effect=AssertionError("network call")))
                stack.enter_context(patch.object(socket, "socket", side_effect=AssertionError("socket call")))
                stack.enter_context(patch.object(urllib.request, "urlopen", side_effect=AssertionError("urlopen call")))
                stack.enter_context(patch.object(webbrowser, "open", side_effect=AssertionError("browser call")))
                stack.enter_context(patch.object(subprocess, "run", side_effect=AssertionError("external command call")))
                result = mine_main(["--repo-root", str(REPO_ROOT), "--json-output", str(output_path), "--check"], stdout=io.StringIO())

        self.assertEqual(result, 0)


def _candidate() -> dict:
    return deepcopy(_read_json(REPO_ROOT / "examples/observation_candidates/local_eval_source_gap_candidate_v0.json"))


def _read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _fingerprint(paths: list[Path]) -> list[tuple[str, str]]:
    return sorted((str(path), hashlib.sha256(path.read_bytes()).hexdigest()) for path in paths)


def _observed_file_names() -> list[str]:
    names: list[str] = []
    for directory in OBSERVATION_DIRS:
        if directory.is_dir():
            names.extend(str(path.relative_to(REPO_ROOT)) for path in directory.glob("*.json") if path.name.lower().startswith(("observed", "accepted")))
    return sorted(names)


if __name__ == "__main__":
    unittest.main()
