from __future__ import annotations

import json
import socket
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from runtime.local.candidate_index_refresh import MANIFEST_FILE_NAME as CANDIDATE_MANIFEST_FILE_NAME
from runtime.local.candidate_index_refresh import build_delta as build_candidate_index_delta
from runtime.local.evidence_ledger_summary import MANIFEST_FILE_NAME as EVIDENCE_MANIFEST_FILE_NAME
from runtime.local.evidence_ledger_summary import build_delta as build_evidence_summary_delta
from runtime.local.ia_candidate_review_batch import (
    DECISION_TEMPLATE_FILE_NAME,
    MANIFEST_FILE_NAME,
    REVIEW_ITEMS_FILE_NAME,
    IACandidateReviewBatchError,
    build_review_batch,
    prepare_tranche,
    record_decisions,
    validate_batch_path,
    validate_decision_file,
    validate_tranche_decision_file,
    validate_tranche_path,
)
from runtime.local.source_observation_cache import MANIFEST_FILE_NAME as SOURCE_OBSERVATION_MANIFEST_FILE_NAME
from runtime.local.source_observation_cache import build_delta as build_source_observation_delta
from runtime.review.queue import ReviewQueueStore


ROOT = Path(__file__).resolve().parents[2]
SMOKE_REPORT = ROOT / "control/audits/source_wave/ia_metadata_provider_wiring_and_smoke_v0/ia_metadata_provider_smoke_report.json"


class ReviewIACandidatesBatchTests(unittest.TestCase):
    def test_builds_prepare_batch_from_governed_deltas(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eureka-ia-review-batch-") as tmp:
            source_delta, candidate_delta, evidence_delta = _build_inputs(Path(tmp))
            result = build_review_batch(
                source="ia_metadata",
                source_observation_delta_path=source_delta,
                candidate_index_delta_path=candidate_delta,
                evidence_summary_delta_path=evidence_delta,
                out_dir=Path(tmp) / "review-batch",
            )

        manifest = result["manifest"]
        self.assertEqual("PASS_WITH_WARNINGS", result["status"])
        self.assertEqual(56, manifest["source_observation_count"])
        self.assertEqual(56, manifest["candidate_count"])
        self.assertEqual(344, manifest["evidence_summary_count"])
        self.assertEqual(56, manifest["review_item_count"])
        self.assertEqual(56, manifest["pending_review_count"])
        self.assertIn("WAITING_FOR_OPERATOR_REVIEW_DECISIONS", manifest["blockers"])
        self.assertFalse(manifest["automatic_decisions"])
        self.assertFalse(manifest["automatic_promotion"])

    def test_every_candidate_has_one_pending_review_item(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eureka-ia-review-batch-") as tmp:
            out = _build_batch(Path(tmp))
            rows = _read_jsonl(out / REVIEW_ITEMS_FILE_NAME)

        candidate_ids = [row["candidate_id"] for row in rows]
        self.assertEqual(56, len(candidate_ids))
        self.assertEqual(len(candidate_ids), len(set(candidate_ids)))
        self.assertTrue(all(row["review_status"] == "pending" for row in rows))
        self.assertTrue(all(row["decision"] is None for row in rows))
        self.assertTrue(all(row["decision_actor"] is None for row in rows))

    def test_preserves_candidate_source_evidence_and_query_refs(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eureka-ia-review-batch-") as tmp:
            out = _build_batch(Path(tmp))
            rows = _read_jsonl(out / REVIEW_ITEMS_FILE_NAME)

        self.assertTrue(all(row["candidate_id"].startswith("candidate:ia_metadata:") for row in rows))
        self.assertTrue(all(row["source_observation_refs"] for row in rows))
        self.assertTrue(all(row["evidence_summary_refs"] for row in rows))
        self.assertTrue(all(row["query_seed_refs"] for row in rows))
        self.assertTrue(all(ref.startswith("source-observation:ia_metadata:") for row in rows for ref in row["source_observation_refs"]))
        self.assertTrue(all(ref.startswith("evidence-summary:ia_metadata:") for row in rows for ref in row["evidence_summary_refs"]))

    def test_validates_input_hashes(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eureka-ia-review-batch-") as tmp:
            source_delta, candidate_delta, evidence_delta = _build_inputs(Path(tmp))
            manifest = json.loads(evidence_delta.read_text(encoding="utf-8"))
            manifest["input_candidate_index_delta_hash"] = "sha256:bogus"
            evidence_delta.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")

            with self.assertRaises(IACandidateReviewBatchError):
                build_review_batch(
                    source="ia_metadata",
                    source_observation_delta_path=source_delta,
                    candidate_index_delta_path=candidate_delta,
                    evidence_summary_delta_path=evidence_delta,
                    out_dir=Path(tmp) / "review-batch",
                )

    def test_writes_batch_manifest_packet_template_and_guide(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eureka-ia-review-batch-") as tmp:
            out = _build_batch(Path(tmp))

            self.assertTrue((out / REVIEW_ITEMS_FILE_NAME).is_file())
            self.assertTrue((out / MANIFEST_FILE_NAME).is_file())
            self.assertTrue((out / "REVIEW_BATCH_REPORT.md").is_file())
            self.assertTrue((out / "OPERATOR_REVIEW_PACKET.md").is_file())
            self.assertTrue((out / DECISION_TEMPLATE_FILE_NAME).is_file())
            self.assertTrue((out / "OPERATOR_DECISION_GUIDE.md").is_file())

    def test_strict_batch_validation_passes(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eureka-ia-review-batch-") as tmp:
            out = _build_batch(Path(tmp))
            validation = validate_batch_path(out / MANIFEST_FILE_NAME, strict=True)

        self.assertEqual("PASS", validation["status"], validation)
        self.assertEqual(56, validation["review_item_count"])
        self.assertFalse(validation["automatic_decisions"])

    def test_status_command_reports_pending_counts(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eureka-ia-review-batch-") as tmp:
            out = _build_batch(Path(tmp))
            completed = subprocess.run(
                [
                    sys.executable,
                    "scripts/eureka_ia_candidate_review.py",
                    "status",
                    "--batch",
                    str(out / MANIFEST_FILE_NAME),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=True,
            )

        self.assertIn("review_items: 56", completed.stdout)
        self.assertIn("pending_review_items: 56", completed.stdout)
        self.assertIn("automatic_decisions: false", completed.stdout)
        self.assertIn("recommended_next_action: operator_review_required", completed.stdout)

    def test_repeated_prepare_build_is_deterministic(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eureka-ia-review-batch-") as tmp:
            source_delta, candidate_delta, evidence_delta = _build_inputs(Path(tmp))
            out = Path(tmp) / "review-batch"
            build_review_batch(
                source="ia_metadata",
                source_observation_delta_path=source_delta,
                candidate_index_delta_path=candidate_delta,
                evidence_summary_delta_path=evidence_delta,
                out_dir=out,
            )
            first_manifest = (out / MANIFEST_FILE_NAME).read_text(encoding="utf-8")
            first_rows = (out / REVIEW_ITEMS_FILE_NAME).read_text(encoding="utf-8")
            first_template = (out / DECISION_TEMPLATE_FILE_NAME).read_text(encoding="utf-8")
            build_review_batch(
                source="ia_metadata",
                source_observation_delta_path=source_delta,
                candidate_index_delta_path=candidate_delta,
                evidence_summary_delta_path=evidence_delta,
                out_dir=out,
            )

            self.assertEqual(first_manifest, (out / MANIFEST_FILE_NAME).read_text(encoding="utf-8"))
            self.assertEqual(first_rows, (out / REVIEW_ITEMS_FILE_NAME).read_text(encoding="utf-8"))
            self.assertEqual(first_template, (out / DECISION_TEMPLATE_FILE_NAME).read_text(encoding="utf-8"))

    def test_grouping_and_ranking_never_sets_decisions_or_excludes_items(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eureka-ia-review-batch-") as tmp:
            out = _build_batch(Path(tmp))
            manifest = json.loads((out / MANIFEST_FILE_NAME).read_text(encoding="utf-8"))
            rows = _read_jsonl(out / REVIEW_ITEMS_FILE_NAME)

        self.assertEqual(56, len(rows))
        self.assertTrue(any(row["review_attention_band"] == "standard_attention" for row in rows))
        self.assertTrue(any(row["review_attention_band"] == "high_attention" for row in rows))
        self.assertEqual(40, manifest["insufficient_support_item_count"])
        self.assertEqual(40, manifest["absence_near_miss_item_count"])
        self.assertTrue(all(row["decision"] is None for row in rows))

    def test_blank_decision_template_has_no_actor_or_decisions_and_fails_validation(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eureka-ia-review-batch-") as tmp:
            out = _build_batch(Path(tmp))
            template = json.loads((out / DECISION_TEMPLATE_FILE_NAME).read_text(encoding="utf-8"))
            validation = validate_decision_file(
                batch_manifest_path=out / MANIFEST_FILE_NAME,
                decision_file_path=out / DECISION_TEMPLATE_FILE_NAME,
                strict=True,
            )

        self.assertEqual("OPERATOR_REQUIRED", template["actor"])
        self.assertEqual(56, len(template["decisions"]))
        self.assertTrue(all(item["decision"] is None for item in template["decisions"]))
        self.assertEqual("FAIL", validation["status"])
        self.assertTrue(any("actor is required" in error for error in validation["errors"]))

    def test_zero_result_and_unavailable_material_do_not_become_promotable_facts(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eureka-ia-review-batch-") as tmp:
            out = _build_batch(Path(tmp))
            rows = _read_jsonl(out / REVIEW_ITEMS_FILE_NAME)

        self.assertFalse(any(row.get("decision") == "promote" for row in rows))
        self.assertTrue(all(row["self_promotion_allowed"] is False for row in rows))
        self.assertFalse(any(row.get("reviewed_record_created") for row in rows))

    def test_prepare_build_makes_no_network_or_provider_call(self) -> None:
        def fail_socket(*_args: object, **_kwargs: object) -> socket.socket:
            raise AssertionError("network socket should not be opened")

        with tempfile.TemporaryDirectory(prefix="eureka-ia-review-batch-") as tmp:
            source_delta, candidate_delta, evidence_delta = _build_inputs(Path(tmp))
            with mock.patch("socket.socket", side_effect=fail_socket):
                result = build_review_batch(
                    source="ia_metadata",
                    source_observation_delta_path=source_delta,
                    candidate_index_delta_path=candidate_delta,
                    evidence_summary_delta_path=evidence_delta,
                    out_dir=Path(tmp) / "review-batch",
                )

        self.assertFalse(result["network_used"])
        self.assertFalse(result["provider_calls"])

    def test_generated_batch_does_not_write_review_ledger_or_indexes(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eureka-ia-review-batch-") as tmp:
            out = _build_batch(Path(tmp))
            manifest = json.loads((out / MANIFEST_FILE_NAME).read_text(encoding="utf-8"))

        self.assertFalse((out / "review_ledger.sqlite").exists())
        self.assertFalse((out / "reviewed_records.jsonl").exists())
        self.assertFalse((out / "public_snapshot_index.json").exists())
        self.assertFalse(manifest["reviewed_record_creation"])
        self.assertFalse(manifest["reviewed_master_mutation"])
        self.assertFalse(manifest["public_index_mutation"])
        self.assertFalse(manifest["snapshot_refresh"])

    def test_validates_supported_subset_decisions(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eureka-ia-review-batch-") as tmp:
            out = _build_batch(Path(tmp))
            rows = _read_jsonl(out / REVIEW_ITEMS_FILE_NAME)
            decision_path = Path(tmp) / "operator-decisions.json"
            _write_json(
                decision_path,
                _decision_payload(
                    out,
                    rows,
                    [
                        ("promote", 0, {"local_only_confirmed": True}),
                        ("reject", 1, {"reason": "wrong artifact family"}),
                        ("supersede", 2, {"reason": "duplicate candidate", "supersedes_review_item_id": rows[0]["review_item_id"]}),
                        ("mark_near_miss", 3, {}),
                        ("mark_need", 4, {}),
                        ("mark_policy_blocked", 5, {"reason": "policy blocked"}),
                        ("request_more_evidence", 6, {"reason": "need stronger source observation"}),
                    ],
                ),
            )
            validation = validate_decision_file(batch_manifest_path=out / MANIFEST_FILE_NAME, decision_file_path=decision_path, strict=True)

        self.assertEqual("PASS", validation["status"], validation)
        self.assertEqual(7, validation["decisions_validated"])
        self.assertTrue(validation["subset_decision_file"])
        self.assertEqual(49, validation["omitted_pending_count"])

    def test_rejects_invalid_decision_files(self) -> None:
        cases = (
            ("unsupported", lambda payload, rows: payload["decisions"][0].__setitem__("decision", "promote_all"), "unsupported decision"),
            ("duplicate", lambda payload, rows: payload["decisions"].append(dict(payload["decisions"][0])), "duplicate review item decision"),
            ("unknown", lambda payload, rows: payload["decisions"][0].__setitem__("review_item_id", "review-item:ia_metadata:missing"), "unknown review item id"),
            ("mismatch", lambda payload, rows: payload["decisions"][0].__setitem__("candidate_id", "candidate:ia_metadata:missing"), "candidate_id does not match"),
            ("missing-refs", lambda payload, rows: _clear_refs(payload["decisions"][0]), "requires refs or rationale"),
            ("reason", lambda payload, rows: (payload["decisions"][0].__setitem__("decision", "reject"), payload["decisions"][0].__setitem__("reason", None)), "reason is required"),
            ("supersede", lambda payload, rows: (payload["decisions"][0].__setitem__("decision", "supersede"), payload["decisions"][0].__setitem__("reason", "duplicate")), "supersede requires"),
            ("promote-confirm", lambda payload, rows: payload["decisions"][0].__setitem__("local_only_confirmed", False), "promote requires"),
            ("generated-actor", lambda payload, rows: payload.__setitem__("actor", "codex-agent"), "explicit human/operator"),
            ("bulk", lambda payload, rows: payload.__setitem__("bulk_decision", "promote"), "bulk or inferred"),
        )
        with tempfile.TemporaryDirectory(prefix="eureka-ia-review-batch-") as tmp:
            out = _build_batch(Path(tmp))
            rows = _read_jsonl(out / REVIEW_ITEMS_FILE_NAME)
            for name, mutator, expected in cases:
                with self.subTest(name=name):
                    payload = _decision_payload(out, rows, [("promote", 0, {"local_only_confirmed": True})])
                    mutator(payload, rows)
                    decision_path = Path(tmp) / f"{name}.json"
                    _write_json(decision_path, payload)
                    validation = validate_decision_file(batch_manifest_path=out / MANIFEST_FILE_NAME, decision_file_path=decision_path, strict=True)
                    self.assertEqual("FAIL", validation["status"], validation)
                    self.assertTrue(any(expected in error for error in validation["errors"]), validation["errors"])

    def test_record_decisions_writes_only_review_ledger_fixture_state(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eureka-ia-review-batch-") as tmp:
            out = _build_batch(Path(tmp))
            rows = _read_jsonl(out / REVIEW_ITEMS_FILE_NAME)
            decision_path = Path(tmp) / "operator-decisions.json"
            store_path = Path(tmp) / "review.sqlite"
            _write_json(
                decision_path,
                _decision_payload(
                    out,
                    rows,
                    [("request_more_evidence", 0, {"reason": "need stronger source observation"})],
                ),
            )

            result = record_decisions(
                batch_manifest_path=out / MANIFEST_FILE_NAME,
                decision_file_path=decision_path,
                review_store_path=store_path,
                strict=True,
            )
            with ReviewQueueStore.open(store_path) as store:
                store.init()
                decisions = store.list_decisions(rows[0]["review_item_id"])
                events = store.list_events(rows[0]["review_item_id"])

            with self.assertRaises(IACandidateReviewBatchError):
                record_decisions(
                    batch_manifest_path=out / MANIFEST_FILE_NAME,
                    decision_file_path=decision_path,
                    review_store_path=store_path,
                    strict=True,
                )

        self.assertEqual("PASS", result["status"])
        self.assertEqual(1, result["decisions_recorded"])
        self.assertFalse(result["reviewed_record_created"])
        self.assertFalse(result["reviewed_index_mutated"])
        self.assertFalse(result["public_index_mutated"])
        self.assertFalse(result["master_index_mutated"])
        self.assertFalse(result["snapshot_refresh"])
        self.assertEqual(1, len(decisions))
        self.assertTrue(events)

    def test_cli_prepare_validate_status_round_trip(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eureka-ia-review-batch-") as tmp:
            source_delta, candidate_delta, evidence_delta = _build_inputs(Path(tmp))
            out = Path(tmp) / "review-batch"
            build = subprocess.run(
                [
                    sys.executable,
                    "scripts/eureka_ia_candidate_review.py",
                    "prepare",
                    "--source",
                    "ia_metadata",
                    "--source-observation-delta",
                    str(source_delta),
                    "--candidate-index-delta",
                    str(candidate_delta),
                    "--evidence-summary-delta",
                    str(evidence_delta),
                    "--out",
                    str(out),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=True,
            )
            validate = subprocess.run(
                [
                    sys.executable,
                    "scripts/eureka_ia_candidate_review.py",
                    "validate-batch",
                    "--batch",
                    str(out / MANIFEST_FILE_NAME),
                    "--strict",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=True,
            )

        self.assertIn("review_items_prepared: 56", build.stdout)
        self.assertIn("status: PASS", validate.stdout)

    def test_prepare_tranche_selects_deterministic_balanced_evidence_rich_items(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eureka-ia-review-batch-") as tmp:
            batch = _build_batch(Path(tmp))
            tranche = Path(tmp) / "tranche-01"
            prepare_tranche(
                batch_manifest_path=batch / MANIFEST_FILE_NAME,
                group="evidence_rich_pending_review",
                limit=8,
                selection_policy="balanced_evidence_rich_v0",
                tranche_id="tranche-01",
                out_dir=tranche,
            )
            first_manifest = json.loads((tranche / "tranche_manifest.json").read_text(encoding="utf-8"))
            first_rows = _read_jsonl(tranche / "tranche_review_items.jsonl")
            prepare_tranche(
                batch_manifest_path=batch / MANIFEST_FILE_NAME,
                group="evidence_rich_pending_review",
                limit=8,
                selection_policy="balanced_evidence_rich_v0",
                tranche_id="tranche-01",
                out_dir=tranche,
            )
            second_manifest = json.loads((tranche / "tranche_manifest.json").read_text(encoding="utf-8"))

        self.assertEqual(first_manifest, second_manifest)
        self.assertEqual(8, first_manifest["selected_count"])
        self.assertEqual(
            {"DirectX SDK June 2010 offline installer": 4, "old blue FTP client for XP": 4},
            first_manifest["query_seed_counts"],
        )
        self.assertEqual({"evidence_rich_pending_review": 8}, first_manifest["review_group_counts"])
        self.assertTrue(all(row["review_group"] == "evidence_rich_pending_review" for row in first_rows))

    def test_tranche_items_are_fixture_only_and_promotion_ineligible(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eureka-ia-review-batch-") as tmp:
            batch = _build_batch(Path(tmp))
            tranche = _build_tranche(Path(tmp), batch)
            manifest = json.loads((tranche / "tranche_manifest.json").read_text(encoding="utf-8"))
            rows = _read_jsonl(tranche / "tranche_review_items.jsonl")

        self.assertEqual(8, manifest["fixture_derived_count"])
        self.assertEqual(0, manifest["live_derived_count"])
        self.assertEqual(0, manifest["promotion_eligible_count"])
        self.assertEqual(8, manifest["promotion_blocked_count"])
        self.assertTrue(all(row["provider_modes"] == ["fixture"] for row in rows))
        self.assertTrue(all(row["promotion_eligible"] is False for row in rows))
        self.assertTrue(all("synthetic_input_provenance" in row["promotion_blockers"] for row in rows))
        self.assertTrue(all("independent_external_evidence_missing" in row["promotion_blockers"] for row in rows))

    def test_tranche_template_is_blank_and_promote_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eureka-ia-review-batch-") as tmp:
            batch = _build_batch(Path(tmp))
            tranche = _build_tranche(Path(tmp), batch)
            template_path = tranche / "operator_decision_template.json"
            template = json.loads(template_path.read_text(encoding="utf-8"))
            original_actor = template["actor"]
            blank_validation = validate_tranche_decision_file(
                tranche_manifest_path=tranche / "tranche_manifest.json",
                decision_file_path=template_path,
                strict=True,
            )
            decision_path = Path(tmp) / "promote.json"
            template["actor"] = "operator:jules"
            template["decisions"] = [template["decisions"][0]]
            template["decisions"][0]["decision"] = "promote"
            template["decisions"][0]["local_only_confirmed"] = True
            template["decisions"][0]["reason"] = "operator inspected item"
            _write_json(decision_path, template)
            promote_validation = validate_tranche_decision_file(
                tranche_manifest_path=tranche / "tranche_manifest.json",
                decision_file_path=decision_path,
                strict=True,
            )

        self.assertEqual("OPERATOR_REQUIRED", original_actor)
        self.assertEqual("FAIL", blank_validation["status"])
        self.assertTrue(any("actor is required" in error for error in blank_validation["errors"]))
        self.assertEqual("FAIL", promote_validation["status"])
        self.assertTrue(any("promote is not allowed" in error for error in promote_validation["errors"]))

    def test_tranche_validation_and_cli_round_trip(self) -> None:
        with tempfile.TemporaryDirectory(prefix="eureka-ia-review-batch-") as tmp:
            batch = _build_batch(Path(tmp))
            tranche = Path(tmp) / "tranche-01"
            prepare = subprocess.run(
                [
                    sys.executable,
                    "scripts/eureka_ia_candidate_review.py",
                    "prepare-tranche",
                    "--batch",
                    str(batch / MANIFEST_FILE_NAME),
                    "--group",
                    "evidence_rich_pending_review",
                    "--limit",
                    "8",
                    "--selection-policy",
                    "balanced_evidence_rich_v0",
                    "--tranche-id",
                    "tranche-01",
                    "--out",
                    str(tranche),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=True,
            )
            validate = subprocess.run(
                [
                    sys.executable,
                    "scripts/eureka_ia_candidate_review.py",
                    "validate-tranche",
                    "--tranche",
                    str(tranche / "tranche_manifest.json"),
                    "--strict",
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=True,
            )
            status = subprocess.run(
                [
                    sys.executable,
                    "scripts/eureka_ia_candidate_review.py",
                    "tranche-status",
                    "--tranche",
                    str(tranche / "tranche_manifest.json"),
                ],
                cwd=ROOT,
                text=True,
                capture_output=True,
                check=True,
            )
            validation = validate_tranche_path(tranche / "tranche_manifest.json", strict=True)

        self.assertIn("selected_count: 8", prepare.stdout)
        self.assertIn("status: PASS", validate.stdout)
        self.assertIn("promotion_eligible_count: 0", status.stdout)
        self.assertEqual("PASS", validation["status"], validation)

    def test_prepare_tranche_makes_no_network_or_ledger_or_index_mutation(self) -> None:
        def fail_socket(*_args: object, **_kwargs: object) -> socket.socket:
            raise AssertionError("network socket should not be opened")

        with tempfile.TemporaryDirectory(prefix="eureka-ia-review-batch-") as tmp:
            batch = _build_batch(Path(tmp))
            with mock.patch("socket.socket", side_effect=fail_socket):
                result = prepare_tranche(
                    batch_manifest_path=batch / MANIFEST_FILE_NAME,
                    group="evidence_rich_pending_review",
                    limit=8,
                    selection_policy="balanced_evidence_rich_v0",
                    tranche_id="tranche-01",
                    out_dir=Path(tmp) / "tranche-01",
                )

        manifest = result["manifest"]
        self.assertFalse((Path(tmp) / "tranche-01" / "review_ledger.sqlite").exists())
        self.assertFalse(manifest["reviewed_records_created"])
        self.assertFalse(manifest["reviewed_master_mutation"])
        self.assertFalse(manifest["public_index_mutation"])
        self.assertFalse(manifest["network_provider_calls"])


def _build_inputs(tmp: Path) -> tuple[Path, Path, Path]:
    source_dir = tmp / "source-observation-delta"
    candidate_dir = tmp / "candidate-index-delta"
    evidence_dir = tmp / "evidence-summary-delta"
    build_source_observation_delta(source="ia_metadata", smoke_report_path=SMOKE_REPORT, out_dir=source_dir)
    source_manifest = source_dir / SOURCE_OBSERVATION_MANIFEST_FILE_NAME
    build_candidate_index_delta(source="ia_metadata", source_observation_delta_path=source_manifest, out_dir=candidate_dir)
    candidate_manifest = candidate_dir / CANDIDATE_MANIFEST_FILE_NAME
    build_evidence_summary_delta(
        source="ia_metadata",
        source_observation_delta_path=source_manifest,
        candidate_index_delta_path=candidate_manifest,
        out_dir=evidence_dir,
    )
    return source_manifest, candidate_manifest, evidence_dir / EVIDENCE_MANIFEST_FILE_NAME


def _build_batch(tmp: Path) -> Path:
    source_delta, candidate_delta, evidence_delta = _build_inputs(tmp)
    out = tmp / "review-batch"
    build_review_batch(
        source="ia_metadata",
        source_observation_delta_path=source_delta,
        candidate_index_delta_path=candidate_delta,
        evidence_summary_delta_path=evidence_delta,
        out_dir=out,
    )
    return out


def _build_tranche(tmp: Path, batch: Path) -> Path:
    out = tmp / "tranche-01"
    prepare_tranche(
        batch_manifest_path=batch / MANIFEST_FILE_NAME,
        group="evidence_rich_pending_review",
        limit=8,
        selection_policy="balanced_evidence_rich_v0",
        tranche_id="tranche-01",
        out_dir=out,
    )
    return out


def _read_jsonl(path: Path) -> list[dict[str, object]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def _write_json(path: Path, payload: dict[str, object]) -> None:
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _decision_payload(
    out: Path,
    rows: list[dict[str, object]],
    decisions: list[tuple[str, int, dict[str, object]]],
) -> dict[str, object]:
    manifest = json.loads((out / MANIFEST_FILE_NAME).read_text(encoding="utf-8"))
    payload_decisions: list[dict[str, object]] = []
    for decision, index, extra in decisions:
        row = rows[index]
        entry = {
            "review_item_id": row["review_item_id"],
            "candidate_id": row["candidate_id"],
            "decision": decision,
            "reason": extra.get("reason"),
            "evidence_refs": list(row["evidence_summary_refs"]),  # type: ignore[index]
            "source_observation_refs": list(row["source_observation_refs"]),  # type: ignore[index]
            "absence_refs": [],
            "fallback_refs": [],
            "supersedes_review_item_id": extra.get("supersedes_review_item_id"),
            "local_only_confirmed": bool(extra.get("local_only_confirmed", False)),
        }
        payload_decisions.append(entry)
    return {
        "schema_version": "eureka.ia_candidate_review_decisions.v0",
        "batch_id": manifest["batch_id"],
        "actor": "operator:jules",
        "generated_at": manifest["generated_at"],
        "decisions": payload_decisions,
    }


def _clear_refs(entry: dict[str, object]) -> None:
    entry["evidence_refs"] = []
    entry["source_observation_refs"] = []
    entry["absence_refs"] = []
    entry["fallback_refs"] = []
    entry["reason"] = None


if __name__ == "__main__":
    unittest.main()
