from __future__ import annotations

import json
from pathlib import Path
import unittest

from evals.hard_queries.metadata_fallback_smoke.ia_00.loader import (
    BASELINE_PROFILES,
    EXPECTED_PATH,
    FIXTURE_PATH,
    build_smoke_suite,
    load_expected_outputs,
    load_fixture_payload,
)


SMOKE_ROOT = Path(__file__).resolve().parents[2] / "evals" / "hard_queries" / "metadata_fallback_smoke" / "ia_00"


class IAMetadataFallbackSmokeEvalTests(unittest.TestCase):
    def test_expected_smoke_files_exist_and_are_valid_json(self) -> None:
        expected_files = {
            "query_inputs.json",
            "ia_metadata_fixtures.json",
            "expected_fallback_outputs.json",
            "surface_projection_fixtures.json",
            "renderer_expected_outputs.json",
        }

        for name in expected_files:
            with self.subTest(name=name):
                path = SMOKE_ROOT / name
                self.assertTrue(path.is_file(), name)
                json.loads(path.read_text(encoding="utf-8"))

    def test_smoke_suite_matches_expected_statuses_and_provider_calls(self) -> None:
        suite = build_smoke_suite()
        expected = load_expected_outputs()["expected"]

        self.assertEqual(set(suite["cases"]), set(expected))
        for case_id, row in expected.items():
            with self.subTest(case_id=case_id):
                case = suite["cases"][case_id]
                fallback = case["fallback_summary"]
                self.assertEqual(fallback["status"], row["status"])
                self.assertEqual(fallback["candidate_count"], row["candidate_count"])
                self.assertEqual(fallback["need_count"], row["need_count"])
                self.assertEqual(bool(case["provider_call_count"]), row["provider_called"])
                for reason_code in row["reason_codes"]:
                    self.assertIn(reason_code, fallback["reason_codes"])

    def test_all_baseline_renderers_are_covered(self) -> None:
        suite = build_smoke_suite()

        for case in suite["cases"].values():
            self.assertEqual(set(case["surface_projections"]), set(BASELINE_PROFILES))
            for projection in case["surface_projections"].values():
                self.assertIn("renderer_output", projection["renderer_result"])
                self.assertIn(projection["view_model"]["canonical_status"], repr(projection["renderer_result"]))

    def test_smoke_does_not_call_live_network_or_mutate_indexes(self) -> None:
        suite = build_smoke_suite()

        self.assertFalse(suite["live_network_required"])
        self.assertFalse(suite["downloads_performed"])
        self.assertFalse(suite["file_fetching_performed"])
        self.assertFalse(suite["wayback_replay_performed"])
        self.assertFalse(suite["reviewed_index_mutated"])
        self.assertFalse(suite["public_index_mutated"])
        self.assertFalse(suite["master_index_mutated"])

    def test_fixture_contract_keeps_metadata_only_boundary(self) -> None:
        fixtures = load_fixture_payload(FIXTURE_PATH)
        self.assertTrue(fixtures["metadata_only"])
        self.assertFalse(fixtures["live_network_required"])
        for case in fixtures["cases"]:
            self.assertNotIn("download", repr(case).casefold())

    def test_public_gateway_does_not_import_or_own_ia_provider(self) -> None:
        gateway_path = SMOKE_ROOT.parents[3] / "runtime" / "gateway" / "public_api" / "resolution_runs_boundary.py"
        text = gateway_path.read_text(encoding="utf-8")

        self.assertNotIn("archive_org_public_metadata", text)
        self.assertNotIn("ArchiveOrgMetadataCandidateProvider", text)


if __name__ == "__main__":
    unittest.main()
