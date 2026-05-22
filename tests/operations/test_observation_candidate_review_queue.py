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

from scripts.build_observation_candidate_review_queue import main as build_main
from scripts.summarize_observation_candidate_review_queue import main as summarize_main
from scripts.validate_observation_candidate_review_queue import (
    validate_observation_candidate_review_queue,
    validate_policy_payload,
    validate_queue_entry,
    validate_queue_payload,
    validate_triage_rules_payload,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
PENDING_BATCH = REPO_ROOT / "evals/search_usefulness/external_baselines/batches/batch_0/observations/pending_batch_0_observations.json"
SLOT_MANIFEST = REPO_ROOT / "control/inventory/observations/manual_observation_batch_0_slot_manifest.json"
TRACK_B_FILES = [
    REPO_ROOT / "contracts/node/eureka_node_manifest.v0.json",
    REPO_ROOT / "contracts/node/node_policy.v0.json",
    REPO_ROOT / "contracts/control_schemas/policies/node/node_capability.v0.json",
    REPO_ROOT / "contracts/control_schemas/policies/node/work_unit.v0.json",
    REPO_ROOT / "contracts/control_schemas/policies/node/work_unit_result.v0.json",
    REPO_ROOT / "contracts/control_schemas/policies/node/local_foundry_state.v0.json",
]
OBSERVATION_DIRS = [
    REPO_ROOT / "evals/search_usefulness/external_baselines/batches/batch_0/observations",
    REPO_ROOT / "evals/search_usefulness/external_baselines/observations",
]


class ObservationCandidateReviewQueueTest(unittest.TestCase):
    def test_review_queue_policy_validates(self) -> None:
        policy = _read_json(REPO_ROOT / "control/inventory/observations/observation_candidate_review_queue_policy.json")

        self.assertEqual(validate_policy_payload(policy, "policy"), [])

    def test_triage_rules_validate(self) -> None:
        rules = _read_json(REPO_ROOT / "control/inventory/observations/observation_candidate_triage_rules.json")

        self.assertEqual(validate_triage_rules_payload(rules, "triage"), [])

    def test_review_queue_examples_validate(self) -> None:
        for path in sorted((REPO_ROOT / "examples/observation_reviews").glob("review_queue_*_v0.json")):
            with self.subTest(path=path.name):
                self.assertEqual(validate_queue_payload(_read_json(path), str(path), REPO_ROOT), [])

    def test_builder_runs_on_current_repo_state(self) -> None:
        output = io.StringIO()

        result = build_main(["--repo-root", str(REPO_ROOT)], stdout=output)

        self.assertEqual(result, 0)
        self.assertIn("queue_entry_count", output.getvalue())

    def test_builder_list_inputs_output_is_non_empty(self) -> None:
        output = io.StringIO()

        result = build_main(["--repo-root", str(REPO_ROOT), "--list-inputs"], stdout=output)

        self.assertEqual(result, 0)
        lines = [line for line in output.getvalue().splitlines() if line.strip()]
        self.assertGreater(len(lines), 10)
        self.assertIn("contracts/control_schemas/tasks/query/observation_candidate_review_queue.v0.json", lines)

    def test_builder_check_passes(self) -> None:
        output = io.StringIO()

        result = build_main(["--repo-root", str(REPO_ROOT), "--check"], stdout=output)

        self.assertEqual(result, 0)
        self.assertIn("pass", output.getvalue())

    def test_builder_json_output_writes_deterministic_json(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            first = Path(temp) / "first.json"
            second = Path(temp) / "second.json"

            self.assertEqual(build_main(["--repo-root", str(REPO_ROOT), "--json-output", str(first)], stdout=io.StringIO()), 0)
            self.assertEqual(build_main(["--repo-root", str(REPO_ROOT), "--json-output", str(second)], stdout=io.StringIO()), 0)

            self.assertEqual(first.read_text(encoding="utf-8"), second.read_text(encoding="utf-8"))
            payload = json.loads(first.read_text(encoding="utf-8"))
            self.assertEqual(len(payload["queue_entries"]), 15)

    def test_builder_markdown_output_writes_deterministic_summary(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            first = Path(temp) / "first.md"
            second = Path(temp) / "second.md"

            self.assertEqual(build_main(["--repo-root", str(REPO_ROOT), "--markdown-output", str(first)], stdout=io.StringIO()), 0)
            self.assertEqual(build_main(["--repo-root", str(REPO_ROOT), "--markdown-output", str(second)], stdout=io.StringIO()), 0)

            self.assertEqual(first.read_text(encoding="utf-8"), second.read_text(encoding="utf-8"))
            self.assertIn("Review Boundary", first.read_text(encoding="utf-8"))

    def test_summarizer_runs_without_mutating(self) -> None:
        output = io.StringIO()

        result = summarize_main(["--repo-root", str(REPO_ROOT)], stdout=output)

        self.assertEqual(result, 0)
        self.assertIn("by_recommended_action", output.getvalue())

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
        report = validate_observation_candidate_review_queue(REPO_ROOT)

        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["errors"], [])

    def test_queue_entry_with_observed_baseline_true_fails(self) -> None:
        entry = _entry()
        entry["accepted_as_observed_baseline"] = True

        errors = validate_queue_entry(entry, "broken", REPO_ROOT)

        self.assertTrue(any("accepted_as_observed_baseline" in error for error in errors))

    def test_queue_entry_with_evidence_truth_true_fails(self) -> None:
        entry = _entry()
        entry["accepted_as_evidence_truth"] = True

        errors = validate_queue_entry(entry, "broken", REPO_ROOT)

        self.assertTrue(any("accepted_as_evidence_truth" in error for error in errors))

    def test_queue_entry_with_master_index_mutation_true_fails(self) -> None:
        entry = _entry()
        entry["master_index_mutation_allowed"] = True

        errors = validate_queue_entry(entry, "broken", REPO_ROOT)

        self.assertTrue(any("master_index_mutation_allowed" in error for error in errors))

    def test_recommended_action_outside_vocabulary_fails(self) -> None:
        entry = _entry()
        entry["recommended_review_action"] = "approve_now"

        errors = validate_queue_entry(entry, "broken", REPO_ROOT)

        self.assertTrue(any("recommended_review_action" in error for error in errors))

    def test_priority_band_outside_vocabulary_fails(self) -> None:
        entry = _entry()
        entry["priority_band"] = "urgent"

        errors = validate_queue_entry(entry, "broken", REPO_ROOT)

        self.assertTrue(any("priority_band" in error for error in errors))

    def test_source_access_approval_claim_fails(self) -> None:
        entry = _entry()
        entry["notes"] = ["source access approved"]

        errors = validate_queue_entry(entry, "broken", REPO_ROOT)

        self.assertTrue(any("source access approved" in error for error in errors))

    def test_live_source_claim_fails(self) -> None:
        entry = _entry()
        entry["notes"] = ["Live source observed for this queue entry."]

        errors = validate_queue_entry(entry, "broken", REPO_ROOT)

        self.assertTrue(any("live source observed" in error for error in errors))

    def test_external_observation_claim_fails(self) -> None:
        queue = _queue()
        queue["product_boundary"]["performed_observations"] = True
        queue["notes"] = ["External observation performed by this queue."]

        errors = validate_queue_payload(queue, "broken_queue", REPO_ROOT)

        self.assertTrue(any("performed_observations" in error for error in errors))
        self.assertTrue(any("external observation performed" in error for error in errors))

    def test_google_scrape_claim_fails(self) -> None:
        entry = _entry()
        entry["notes"] = ["Google scrape completed for this queue entry."]

        errors = validate_queue_entry(entry, "broken", REPO_ROOT)

        self.assertTrue(any("google scrape" in error for error in errors))

    def test_script_does_not_create_observed_files(self) -> None:
        before = _observed_file_names()
        with tempfile.TemporaryDirectory() as temp:
            output_path = Path(temp) / "queue.json"
            self.assertEqual(build_main(["--repo-root", str(REPO_ROOT), "--json-output", str(output_path)], stdout=io.StringIO()), 0)

        self.assertEqual(before, _observed_file_names())

    def test_scripts_do_not_mutate_pending_observations(self) -> None:
        watched = [PENDING_BATCH, SLOT_MANIFEST]
        before = _fingerprint(watched)

        with tempfile.TemporaryDirectory() as temp:
            self.assertEqual(build_main(["--repo-root", str(REPO_ROOT), "--json-output", str(Path(temp) / "queue.json")], stdout=io.StringIO()), 0)
            self.assertEqual(summarize_main(["--repo-root", str(REPO_ROOT), "--json-output", str(Path(temp) / "summary.json")], stdout=io.StringIO()), 0)

        self.assertEqual(before, _fingerprint(watched))

    def test_scripts_do_not_mutate_track_b_files(self) -> None:
        before = _fingerprint(TRACK_B_FILES)

        with tempfile.TemporaryDirectory() as temp:
            self.assertEqual(build_main(["--repo-root", str(REPO_ROOT), "--json-output", str(Path(temp) / "queue.json")], stdout=io.StringIO()), 0)
            self.assertEqual(summarize_main(["--repo-root", str(REPO_ROOT), "--markdown-output", str(Path(temp) / "summary.md")], stdout=io.StringIO()), 0)

        self.assertEqual(before, _fingerprint(TRACK_B_FILES))

    def test_scripts_do_not_call_network_api_browser_model_or_provider(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output_path = Path(temp) / "queue.json"
            with ExitStack() as stack:
                stack.enter_context(patch.object(socket, "create_connection", side_effect=AssertionError("network call")))
                stack.enter_context(patch.object(socket, "socket", side_effect=AssertionError("socket call")))
                stack.enter_context(patch.object(urllib.request, "urlopen", side_effect=AssertionError("urlopen call")))
                stack.enter_context(patch.object(webbrowser, "open", side_effect=AssertionError("browser call")))
                stack.enter_context(patch.object(subprocess, "run", side_effect=AssertionError("external command call")))
                build_result = build_main(["--repo-root", str(REPO_ROOT), "--json-output", str(output_path), "--check"], stdout=io.StringIO())
                summary_result = summarize_main(["--repo-root", str(REPO_ROOT)], stdout=io.StringIO())

        self.assertEqual(build_result, 0)
        self.assertEqual(summary_result, 0)


def _queue() -> dict:
    return deepcopy(_read_json(REPO_ROOT / "control/inventory/observations/observation_candidate_review_queue.json"))


def _entry() -> dict:
    return deepcopy(_queue()["queue_entries"][0])


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
