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

from scripts.build_search_need_seed_candidates import main as build_main
from scripts.summarize_search_need_seed_candidates import main as summarize_main
from scripts.validate_search_need_seed_candidates import (
    validate_conversion_payload,
    validate_manifest_payload,
    validate_policy_payload,
    validate_priority_model_payload,
    validate_search_need_seed_candidates,
    validate_seed_payload,
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


class SearchNeedSeedConversionTest(unittest.TestCase):
    def test_conversion_policy_validates(self) -> None:
        policy = _read_json(REPO_ROOT / "control/inventory/observations/search_need_seed_conversion_policy.json")

        self.assertEqual(validate_policy_payload(policy, "policy"), [])

    def test_priority_model_validates(self) -> None:
        model = _read_json(REPO_ROOT / "control/inventory/observations/search_need_seed_priority_model.json")

        self.assertEqual(validate_priority_model_payload(model, "priority_model"), [])

    def test_build_script_runs_on_current_repo_state(self) -> None:
        output = io.StringIO()

        result = build_main(["--repo-root", str(REPO_ROOT)], stdout=output)

        self.assertEqual(result, 0)
        self.assertIn("seed_count", output.getvalue())

    def test_build_script_list_inputs_output_is_non_empty(self) -> None:
        output = io.StringIO()

        result = build_main(["--repo-root", str(REPO_ROOT), "--list-inputs"], stdout=output)

        self.assertEqual(result, 0)
        lines = [line for line in output.getvalue().splitlines() if line.strip()]
        self.assertGreater(len(lines), 8)
        self.assertIn("contracts/query/search_need_seed.v0.json", lines)

    def test_build_script_check_passes(self) -> None:
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
            self.assertEqual(payload["seed_count"], 5)

    def test_markdown_output_writes_deterministic_summary(self) -> None:
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
        self.assertIn("by_seed_type", output.getvalue())

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
        report = validate_search_need_seed_candidates(REPO_ROOT)

        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["errors"], [])

    def test_seed_with_accepted_runtime_search_need_true_fails(self) -> None:
        seed = _seed()
        seed["accepted_as_runtime_search_need"] = True

        errors = validate_seed_payload(seed, "broken_seed", REPO_ROOT)

        self.assertTrue(any("accepted_as_runtime_search_need" in error for error in errors))

    def test_seed_with_observed_baseline_true_fails(self) -> None:
        seed = _seed()
        seed["accepted_as_observed_baseline"] = True

        errors = validate_seed_payload(seed, "broken_seed", REPO_ROOT)

        self.assertTrue(any("accepted_as_observed_baseline" in error for error in errors))

    def test_seed_with_evidence_truth_true_fails(self) -> None:
        seed = _seed()
        seed["accepted_as_evidence_truth"] = True

        errors = validate_seed_payload(seed, "broken_seed", REPO_ROOT)

        self.assertTrue(any("accepted_as_evidence_truth" in error for error in errors))

    def test_seed_with_master_index_mutation_true_fails(self) -> None:
        seed = _seed()
        seed["master_index_mutation_allowed"] = True

        errors = validate_seed_payload(seed, "broken_seed", REPO_ROOT)

        self.assertTrue(any("master_index_mutation_allowed" in error for error in errors))

    def test_conversion_accepting_runtime_need_fails(self) -> None:
        conversion = _conversion()
        conversion["accepted_as_runtime_search_need"] = True

        errors = validate_conversion_payload(conversion, "broken_conversion", REPO_ROOT)

        self.assertTrue(any("accepted_as_runtime_search_need" in error for error in errors))

    def test_conversion_accepting_evidence_truth_fails(self) -> None:
        conversion = _conversion()
        conversion["accepted_as_evidence_truth"] = True

        errors = validate_conversion_payload(conversion, "broken_conversion", REPO_ROOT)

        self.assertTrue(any("accepted_as_evidence_truth" in error for error in errors))

    def test_live_source_claim_fails(self) -> None:
        seed = _seed()
        seed["notes"] = ["Live source observed for this seed."]

        errors = validate_seed_payload(seed, "broken_seed", REPO_ROOT)

        self.assertTrue(any("live source observed" in error for error in errors))

    def test_external_observation_claim_fails(self) -> None:
        seed = _seed()
        seed["product_boundary"]["performed_observations"] = True
        seed["notes"] = ["External observation performed for this seed."]

        errors = validate_seed_payload(seed, "broken_seed", REPO_ROOT)

        self.assertTrue(any("performed_observations" in error for error in errors))
        self.assertTrue(any("external observation performed" in error for error in errors))

    def test_google_scrape_claim_fails(self) -> None:
        seed = _seed()
        seed["notes"] = ["Google scrape completed for this seed."]

        errors = validate_seed_payload(seed, "broken_seed", REPO_ROOT)

        self.assertTrue(any("google scrape" in error for error in errors))

    def test_source_approval_claim_fails(self) -> None:
        conversion = _conversion()
        conversion["notes"] = ["source access approved"]

        errors = validate_conversion_payload(conversion, "broken_conversion", REPO_ROOT)

        self.assertTrue(any("source access approved" in error for error in errors))

    def test_priority_score_outside_bounded_range_fails(self) -> None:
        manifest = _manifest()
        manifest["seed_records"][0]["proposed_priority"]["score"] = 101

        errors = validate_manifest_payload(manifest, "broken_manifest", REPO_ROOT)

        self.assertTrue(any("proposed_priority.score" in error for error in errors))

    def test_script_does_not_create_observed_files(self) -> None:
        before = _observed_file_names()
        with tempfile.TemporaryDirectory() as temp:
            output_path = Path(temp) / "seeds.json"
            self.assertEqual(build_main(["--repo-root", str(REPO_ROOT), "--json-output", str(output_path)], stdout=io.StringIO()), 0)

        self.assertEqual(before, _observed_file_names())

    def test_scripts_do_not_mutate_pending_observations(self) -> None:
        watched = [PENDING_BATCH, SLOT_MANIFEST]
        before = _fingerprint(watched)

        with tempfile.TemporaryDirectory() as temp:
            self.assertEqual(build_main(["--repo-root", str(REPO_ROOT), "--json-output", str(Path(temp) / "seeds.json")], stdout=io.StringIO()), 0)
            self.assertEqual(summarize_main(["--repo-root", str(REPO_ROOT), "--json-output", str(Path(temp) / "summary.json")], stdout=io.StringIO()), 0)

        self.assertEqual(before, _fingerprint(watched))

    def test_scripts_do_not_mutate_track_b_files(self) -> None:
        before = _fingerprint(TRACK_B_FILES)

        with tempfile.TemporaryDirectory() as temp:
            self.assertEqual(build_main(["--repo-root", str(REPO_ROOT), "--json-output", str(Path(temp) / "seeds.json")], stdout=io.StringIO()), 0)
            self.assertEqual(summarize_main(["--repo-root", str(REPO_ROOT), "--markdown-output", str(Path(temp) / "summary.md")], stdout=io.StringIO()), 0)

        self.assertEqual(before, _fingerprint(TRACK_B_FILES))

    def test_scripts_do_not_call_network_api_browser_model_or_provider(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            output_path = Path(temp) / "seeds.json"
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


def _seed() -> dict:
    return deepcopy(_read_json(REPO_ROOT / "examples/search_need_seeds/minimal_search_need_seed_v0.json"))


def _conversion() -> dict:
    return deepcopy(_read_json(REPO_ROOT / "examples/search_need_seed_conversions/minimal_candidate_to_need_conversion_v0.json"))


def _manifest() -> dict:
    return deepcopy(_read_json(REPO_ROOT / "control/inventory/observations/search_need_seed_manifest.json"))


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
