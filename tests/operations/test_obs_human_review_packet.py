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

from scripts.build_obs_human_review_packet import main as build_main
from scripts.summarize_obs_human_review_packet import main as summarize_main
from scripts.validate_obs_human_review_packet import (
    validate_decision_example_payload,
    validate_obs_human_review_packet,
    validate_packet_manifest_payload,
    validate_packet_policy_payload,
    validate_review_item_payload,
    validate_template_policy_payload,
)


REPO_ROOT = Path(__file__).resolve().parents[2]
PENDING_BATCH = REPO_ROOT / "evals/search_usefulness/external_baselines/batches/batch_0/observations/pending_batch_0_observations.json"
SLOT_MANIFEST = REPO_ROOT / "control/inventory/observations/manual_observation_batch_0_slot_manifest.json"
TRACK_B_FILES = [
    REPO_ROOT / "contracts/node/eureka_node_manifest.v0.json",
    REPO_ROOT / "contracts/node/node_policy.v0.json",
    REPO_ROOT / "control/schemas/policies/node/node_capability.v0.json",
    REPO_ROOT / "contracts/node/work_unit.v0.json",
    REPO_ROOT / "contracts/node/work_unit_result.v0.json",
    REPO_ROOT / "control/schemas/policies/node/local_foundry_state.v0.json",
]
OBSERVATION_DIRS = [
    REPO_ROOT / "evals/search_usefulness/external_baselines/batches/batch_0/observations",
    REPO_ROOT / "evals/search_usefulness/external_baselines/observations",
]


class ObsHumanReviewPacketTest(unittest.TestCase):
    def test_packet_policy_validates(self) -> None:
        policy = _read_json(REPO_ROOT / "control/inventory/observations/obs_human_review_packet_policy.json")

        self.assertEqual(validate_packet_policy_payload(policy, "policy"), [])

    def test_decision_template_policy_validates(self) -> None:
        policy = _read_json(REPO_ROOT / "control/inventory/observations/obs_review_decision_template_policy.json")

        self.assertEqual(validate_template_policy_payload(policy, "template_policy"), [])

    def test_packet_manifest_validates(self) -> None:
        manifest = _manifest()

        self.assertEqual(validate_packet_manifest_payload(manifest, "manifest", REPO_ROOT), [])

    def test_decision_examples_validate(self) -> None:
        for path in sorted((REPO_ROOT / "examples/observation_reviews").glob("human_review_decision_*_v0.json")):
            payload = _read_json(path)

            self.assertEqual(validate_decision_example_payload(payload, path.as_posix(), REPO_ROOT), [])

    def test_builder_runs_on_current_repo_state(self) -> None:
        output = io.StringIO()

        result = build_main(["--repo-root", str(REPO_ROOT)], stdout=output)

        self.assertEqual(result, 0)
        self.assertIn("review_item_count", output.getvalue())

    def test_builder_list_inputs_output_is_non_empty(self) -> None:
        output = io.StringIO()

        result = build_main(["--repo-root", str(REPO_ROOT), "--list-inputs"], stdout=output)

        self.assertEqual(result, 0)
        lines = [line for line in output.getvalue().splitlines() if line.strip()]
        self.assertGreater(len(lines), 10)
        self.assertIn("control/inventory/observations/obs_human_review_packet_policy.json", lines)

    def test_builder_check_passes(self) -> None:
        output = io.StringIO()

        result = build_main(["--repo-root", str(REPO_ROOT), "--check"], stdout=output)

        self.assertEqual(result, 0)
        self.assertIn("pass", output.getvalue())

    def test_json_output_writes_deterministic_json(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            first = Path(temp) / "first.json"
            second = Path(temp) / "second.json"

            self.assertEqual(build_main(["--repo-root", str(REPO_ROOT), "--json-output", str(first)], stdout=io.StringIO()), 0)
            self.assertEqual(build_main(["--repo-root", str(REPO_ROOT), "--json-output", str(second)], stdout=io.StringIO()), 0)

            self.assertEqual(first.read_text(encoding="utf-8"), second.read_text(encoding="utf-8"))
            payload = json.loads(first.read_text(encoding="utf-8"))
            self.assertEqual(payload["review_item_count"], 35)
            self.assertTrue(all(item["human_decision"] is None for item in payload["review_items"]))

    def test_markdown_output_writes_deterministic_markdown(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            first = Path(temp) / "first.md"
            second = Path(temp) / "second.md"

            self.assertEqual(build_main(["--repo-root", str(REPO_ROOT), "--markdown-output", str(first)], stdout=io.StringIO()), 0)
            self.assertEqual(build_main(["--repo-root", str(REPO_ROOT), "--markdown-output", str(second)], stdout=io.StringIO()), 0)

            self.assertEqual(first.read_text(encoding="utf-8"), second.read_text(encoding="utf-8"))
            self.assertIn("OBS Human Review Packet", first.read_text(encoding="utf-8"))

    def test_summarizer_runs_without_mutating(self) -> None:
        output = io.StringIO()

        result = summarize_main(["--repo-root", str(REPO_ROOT)], stdout=output)

        self.assertEqual(result, 0)
        self.assertIn("by_recommended_decision", output.getvalue())

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
        report = validate_obs_human_review_packet(REPO_ROOT)

        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["errors"], [])

    def test_review_item_with_human_decision_prefilled_fails(self) -> None:
        item = _item()
        item["human_decision"] = "approve_as_source_lead_future"

        errors = validate_review_item_payload(item, "broken_packet", REPO_ROOT, allow_synthetic=False)

        self.assertTrue(any("human_decision" in error for error in errors))

    def test_synthetic_decision_example_may_have_human_decision(self) -> None:
        example = _read_json(REPO_ROOT / "examples/observation_reviews/human_review_decision_approve_source_lead_v0.json")

        self.assertEqual(validate_decision_example_payload(example, "synthetic_example", REPO_ROOT), [])

    def test_review_item_with_source_access_approved_true_fails(self) -> None:
        item = _item()
        item["source_access_approved"] = True

        errors = validate_review_item_payload(item, "broken_packet", REPO_ROOT, allow_synthetic=False)

        self.assertTrue(any("source_access_approved" in error for error in errors))

    def test_review_item_with_observed_baseline_true_fails(self) -> None:
        item = _item()
        item["accepted_as_observed_baseline"] = True

        errors = validate_review_item_payload(item, "broken_packet", REPO_ROOT, allow_synthetic=False)

        self.assertTrue(any("accepted_as_observed_baseline" in error for error in errors))

    def test_review_item_with_evidence_truth_true_fails(self) -> None:
        item = _item()
        item["accepted_as_evidence_truth"] = True

        errors = validate_review_item_payload(item, "broken_packet", REPO_ROOT, allow_synthetic=False)

        self.assertTrue(any("accepted_as_evidence_truth" in error for error in errors))

    def test_review_item_with_runtime_activation_true_fails(self) -> None:
        item = _item()
        item["runtime_activation_allowed_now"] = True

        errors = validate_review_item_payload(item, "broken_packet", REPO_ROOT, allow_synthetic=False)

        self.assertTrue(any("runtime_activation_allowed_now" in error for error in errors))

    def test_review_item_with_master_index_mutation_true_fails(self) -> None:
        item = _item()
        item["master_index_mutation_allowed"] = True

        errors = validate_review_item_payload(item, "broken_packet", REPO_ROOT, allow_synthetic=False)

        self.assertTrue(any("master_index_mutation_allowed" in error for error in errors))

    def test_live_source_claim_fails(self) -> None:
        item = _item()
        item["notes"] = ["Live source observed for this review item."]

        errors = validate_review_item_payload(item, "broken_packet", REPO_ROOT, allow_synthetic=False)

        self.assertTrue(any("live source observed" in error for error in errors))

    def test_external_observation_claim_fails(self) -> None:
        item = _item()
        item["notes"] = ["External observation performed for this review item."]

        errors = validate_review_item_payload(item, "broken_packet", REPO_ROOT, allow_synthetic=False)

        self.assertTrue(any("external observation performed" in error for error in errors))

    def test_google_scrape_claim_fails(self) -> None:
        item = _item()
        item["notes"] = ["Google scrape was used for this review item."]

        errors = validate_review_item_payload(item, "broken_packet", REPO_ROOT, allow_synthetic=False)

        self.assertTrue(any("google scrape" in error for error in errors))

    def test_source_approval_claim_fails(self) -> None:
        item = _item()
        item["notes"] = ["Source approval granted for this item."]

        errors = validate_review_item_payload(item, "broken_packet", REPO_ROOT, allow_synthetic=False)

        self.assertTrue(any("source approval granted" in error for error in errors))

    def test_runtime_search_need_claim_fails(self) -> None:
        item = _item()
        item["notes"] = ["Runtime SearchNeed created for this item."]

        errors = validate_review_item_payload(item, "broken_packet", REPO_ROOT, allow_synthetic=False)

        self.assertTrue(any("runtime searchneed created" in error for error in errors))

    def test_runtime_workunit_claim_fails(self) -> None:
        item = _item()
        item["notes"] = ["Runtime WorkUnit created for this item."]

        errors = validate_review_item_payload(item, "broken_packet", REPO_ROOT, allow_synthetic=False)

        self.assertTrue(any("runtime workunit created" in error for error in errors))

    def test_workunit_execution_claim_fails(self) -> None:
        item = _item()
        item["notes"] = ["WorkUnit executed for this item."]

        errors = validate_review_item_payload(item, "broken_packet", REPO_ROOT, allow_synthetic=False)

        self.assertTrue(any("workunit executed" in error for error in errors))

    def test_script_does_not_create_observed_files(self) -> None:
        before = _observed_file_names()
        with tempfile.TemporaryDirectory() as temp:
            output_path = Path(temp) / "packet.json"
            self.assertEqual(build_main(["--repo-root", str(REPO_ROOT), "--json-output", str(output_path)], stdout=io.StringIO()), 0)

        self.assertEqual(before, _observed_file_names())

    def test_scripts_do_not_mutate_pending_observations(self) -> None:
        watched = [PENDING_BATCH, SLOT_MANIFEST]
        before = _fingerprint(watched)

        with tempfile.TemporaryDirectory() as temp:
            self.assertEqual(build_main(["--repo-root", str(REPO_ROOT), "--json-output", str(Path(temp) / "packet.json")], stdout=io.StringIO()), 0)
            self.assertEqual(summarize_main(["--repo-root", str(REPO_ROOT), "--json-output", str(Path(temp) / "summary.json")], stdout=io.StringIO()), 0)

        self.assertEqual(before, _fingerprint(watched))

    def test_scripts_do_not_mutate_track_b_files(self) -> None:
        before = _fingerprint(TRACK_B_FILES)

        with tempfile.TemporaryDirectory() as temp:
            self.assertEqual(build_main(["--repo-root", str(REPO_ROOT), "--json-output", str(Path(temp) / "packet.json")], stdout=io.StringIO()), 0)
            self.assertEqual(summarize_main(["--repo-root", str(REPO_ROOT), "--markdown-output", str(Path(temp) / "summary.md")], stdout=io.StringIO()), 0)

        self.assertEqual(before, _fingerprint(TRACK_B_FILES))

    def test_scripts_do_not_call_network_api_browser_model_or_provider(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output_path = Path(temp) / "packet.json"
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


def _manifest() -> dict:
    return deepcopy(_read_json(REPO_ROOT / "control/inventory/observations/obs_human_review_packet_manifest.json"))


def _item() -> dict:
    return deepcopy(_manifest()["review_items"][0])


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
