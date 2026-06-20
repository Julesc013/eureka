from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from runtime.index.preview import build_preview_index
from runtime.local.e2e_hunt_exploration import (
    E2EExploreOptions,
    apply_run_control,
    build_explore_workspace,
    compare_runs,
    list_run_bundles,
    load_run_detail,
    start_synthetic_hunt,
)


class E2EHuntExplorationViewModelTests(unittest.TestCase):
    def test_workspace_projects_preview_lanes_without_truth_mutation(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            preview = _build_preview(root)
            options = E2EExploreOptions(preview_index_path=Path(preview["current_path"]), runs_root=root / "runs")

            workspace = build_explore_workspace("WinFTP XP client", options=options)

        self.assertEqual("explore_workspace", workspace["endpoint"])
        self.assertFalse(workspace["accepted_truth_created"])
        self.assertFalse(workspace["reviewed_record_created"])
        self.assertFalse(workspace["public_index_mutation"])
        self.assertEqual("pass", workspace["preview_index"]["status"])
        self.assertIn("old blue FTP client for XP", workspace["example_searches"])
        candidates = next(lane for lane in workspace["lanes"] if lane["lane_id"] == "candidates")
        self.assertGreaterEqual(candidates["record_count"], 1)
        self.assertEqual("candidate_only", candidates["records"][0]["authority"])

    def test_missing_preview_index_degrades_without_creating_records(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            options = E2EExploreOptions(preview_index_path=root / "missing.json", runs_root=root / "runs")

            workspace = build_explore_workspace("sampleproject", options=options)

        self.assertEqual("degraded", workspace["preview_index"]["status"])
        self.assertEqual(0, workspace["preview_index"]["result_count"])
        self.assertFalse(workspace["network_provider_calls"])

    def test_synthetic_hunt_writes_durable_bundle_and_replays(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            root = Path(temp_dir)
            options = E2EExploreOptions(runs_root=root / "runs")

            started = start_synthetic_hunt("sampleproject", options=options)
            run_id = started["run_id"]
            listing = list_run_bundles(options.runs_root)
            detail = load_run_detail(run_id, options.runs_root)
            replay = apply_run_control(run_id, "replay", runs_root=options.runs_root)
            blocked = apply_run_control(run_id, "pause", runs_root=options.runs_root)
            compared = compare_runs(run_id, run_id, runs_root=options.runs_root)

        self.assertEqual(1, listing["run_count"])
        self.assertEqual("completed", detail["run"]["state"])
        self.assertEqual("valid", detail["validation"]["status"])
        self.assertEqual("replay_verified", replay["replay_report"]["status"])
        self.assertEqual("blocked", blocked["status"])
        self.assertFalse(compared["diff"]["event_count_delta"])
        self.assertFalse(detail["accepted_truth_created"])
        self.assertFalse(detail["network_provider_calls"])


def _build_preview(root: Path) -> dict[str, object]:
    source_dir = root / "source"
    candidate_dir = root / "candidate"
    evidence_dir = root / "evidence"
    for directory in (source_dir, candidate_dir, evidence_dir):
        directory.mkdir(parents=True)

    source_manifest = source_dir / "source_observation_delta_manifest.json"
    source_records = source_dir / "source_observations.jsonl"
    source_manifest.write_text(json.dumps({"observation_file": source_records.name}, sort_keys=True), encoding="utf-8")
    _write_jsonl(
        source_records,
        [
            {
                "observation_id": "source-observation:ia_metadata:test-001",
                "query_seed": "WinFTP XP client",
                "source_family": "ia_metadata",
                "provider_mode": "fixture",
                "normalized_metadata": {"title": "WinFTP XP client candidate"},
                "transport_status": "ok",
            }
        ],
    )

    candidate_manifest = candidate_dir / "candidate_index_delta_manifest.json"
    candidate_records = candidate_dir / "candidate_index_delta.jsonl"
    candidate_manifest.write_text(json.dumps({"candidate_file": candidate_records.name}, sort_keys=True), encoding="utf-8")
    _write_jsonl(
        candidate_records,
        [
            {
                "candidate_id": "candidate:ia_metadata:test-winftp",
                "source_family": "ia_metadata",
                "source_observation_refs": ["source-observation:ia_metadata:test-001"],
                "query_seed_refs": ["WinFTP XP client"],
                "provider_mode_refs": ["fixture"],
                "normalized_title": "WinFTP XP client candidate",
                "review_state": "unreviewed",
            }
        ],
    )

    evidence_manifest = evidence_dir / "evidence_summary_delta_manifest.json"
    evidence_records = evidence_dir / "evidence_summaries.jsonl"
    evidence_manifest.write_text(json.dumps({"evidence_summary_file": evidence_records.name}, sort_keys=True), encoding="utf-8")
    _write_jsonl(
        evidence_records,
        [
            {
                "evidence_summary_id": "evidence:ia_metadata:test-001",
                "candidate_id": "candidate:ia_metadata:test-winftp",
                "source_observation_refs": ["source-observation:ia_metadata:test-001"],
                "evidence_type": "title/name clue",
                "support_posture": "candidate_support",
                "summary": "WinFTP XP client appears in fixture metadata.",
            }
        ],
    )

    return build_preview_index(
        out_root=root / "preview",
        source_observation_delta=source_manifest,
        candidate_delta=candidate_manifest,
        evidence_delta=evidence_manifest,
    )


def _write_jsonl(path: Path, rows: list[dict[str, object]]) -> None:
    path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")


if __name__ == "__main__":
    unittest.main()
