from __future__ import annotations

from pathlib import Path
import tempfile
import unittest

from evals.hard_queries.metadata_fallback_smoke.ia_00.loader import (
    _build_demo_normalized_catalog,
    _build_service,
    load_fixture_payload,
    policy_for_case,
    provider_for_case,
)
from runtime.engine.interfaces.public import DeterministicSearchRunRequest
from runtime.engine.resolution_runs import ResolutionRunFallbackPolicy


REPO_ROOT = Path(__file__).resolve().parents[2]


class IAMetadataProviderFallbackTests(unittest.TestCase):
    def setUp(self) -> None:
        self.catalog = _build_demo_normalized_catalog()
        self.fixtures = load_fixture_payload()

    def test_local_reviewed_result_path_unchanged_and_provider_not_called(self) -> None:
        provider = provider_for_case("candidate_sound_blaster_manual", self.fixtures)
        run = self._run(
            "synthetic",
            provider,
            ResolutionRunFallbackPolicy(enabled=True, allowed_source_families=("internet_archive",)),
        )

        self.assertIsNotNone(run.result_summary)
        self.assertIsNone(run.fallback_summary)
        self.assertEqual(_provider_call_count(provider), 0)

    def test_local_miss_triggers_ia_provider_only_when_policy_permits(self) -> None:
        provider = provider_for_case("candidate_sound_blaster_manual", self.fixtures)
        run = self._run("manual for Sound Blaster CT1740", provider, policy_for_case("candidate_sound_blaster_manual"))
        fallback = run.fallback_summary or {}

        self.assertEqual(_provider_call_count(provider), 1)
        self.assertEqual(fallback["status"], "candidate")
        self.assertEqual(fallback["trigger"], "local_lookup_no_results")
        self.assertEqual(fallback["source_id"], "internet_archive_metadata")
        self.assertEqual(fallback["source_family"], "internet_archive")
        self.assertEqual(fallback["candidate_count"], 1)
        self.assertFalse(fallback["accepted_truth"])
        self.assertFalse(fallback["verified"])
        self.assertFalse(fallback["reviewed_record_created"])
        self.assertFalse(fallback["reviewed_index_mutated"])
        self.assertFalse(fallback["public_index_mutated"])
        self.assertFalse(fallback["master_index_mutated"])
        self.assertFalse(fallback["source_observation"]["download_performed"])
        self.assertFalse(fallback["source_observation"]["extraction_executed"])

    def test_fallback_disabled_returns_policy_blocked_without_provider_call(self) -> None:
        provider = provider_for_case("policy_blocked_disabled", self.fixtures)
        run = self._run("manual for Sound Blaster CT1740", provider, policy_for_case("policy_blocked_disabled"))
        fallback = run.fallback_summary or {}

        self.assertEqual(_provider_call_count(provider), 0)
        self.assertEqual(fallback["status"], "policy_blocked")
        self.assertIn("fallback_disabled", fallback["reason_codes"])

    def test_source_disabled_returns_policy_blocked_without_provider_call(self) -> None:
        provider = provider_for_case("candidate_sound_blaster_manual", self.fixtures)
        run = self._run(
            "manual for Sound Blaster CT1740",
            provider,
            ResolutionRunFallbackPolicy(enabled=True, disabled_source_families=("internet_archive",)),
        )
        fallback = run.fallback_summary or {}

        self.assertEqual(_provider_call_count(provider), 0)
        self.assertEqual(fallback["status"], "policy_blocked")
        self.assertIn("source_family_disabled", fallback["reason_codes"])

    def test_source_not_allowlisted_returns_policy_blocked_without_provider_call(self) -> None:
        provider = provider_for_case("candidate_sound_blaster_manual", self.fixtures)
        run = self._run(
            "manual for Sound Blaster CT1740",
            provider,
            ResolutionRunFallbackPolicy(enabled=True, allowed_source_families=("software_heritage",)),
        )
        fallback = run.fallback_summary or {}

        self.assertEqual(_provider_call_count(provider), 0)
        self.assertEqual(fallback["status"], "policy_blocked")
        self.assertIn("source_family_not_allowlisted", fallback["reason_codes"])

    def test_malformed_metadata_returns_unavailable_without_truth_promotion(self) -> None:
        provider = provider_for_case("unavailable_firefox_malformed", self.fixtures)
        run = self._run(
            "latest Firefox before XP support ended",
            provider,
            policy_for_case("unavailable_firefox_malformed"),
        )
        fallback = run.fallback_summary or {}

        self.assertEqual(_provider_call_count(provider), 1)
        self.assertEqual(fallback["status"], "unavailable")
        self.assertEqual(fallback["failure_reason"], "archive_org_error")
        self.assertFalse(fallback["accepted_truth"])
        self.assertFalse(fallback["verified"])

    def test_empty_metadata_returns_need_not_absence_proof(self) -> None:
        provider = provider_for_case("need_ray_tracing_magazine", self.fixtures)
        run = self._run(
            "article about ray tracing in a 1994 magazine",
            provider,
            policy_for_case("need_ray_tracing_magazine"),
        )
        fallback = run.fallback_summary or {}

        self.assertEqual(fallback["status"], "need")
        self.assertEqual(fallback["candidate_count"], 0)
        self.assertEqual(fallback["need_count"], 1)
        self.assertFalse(fallback["verified"])

    def test_near_miss_provider_status_is_preserved(self) -> None:
        provider = provider_for_case("near_miss_blue_ftp_client", self.fixtures)
        run = self._run("old blue FTP client for XP", provider, policy_for_case("near_miss_blue_ftp_client"))
        fallback = run.fallback_summary or {}

        self.assertEqual(_provider_call_count(provider), 1)
        self.assertEqual(fallback["status"], "near_miss")
        self.assertEqual(fallback["failure_reason"], "metadata_near_miss")
        self.assertIn("fallback_near_miss", fallback["reason_codes"])
        self.assertEqual(fallback["need_count"], 1)
        self.assertFalse(fallback["accepted_truth"])
        self.assertFalse(fallback["verified"])

    def _run(self, query: str, provider, policy: ResolutionRunFallbackPolicy):
        with tempfile.TemporaryDirectory() as temp_root:
            service = _build_service(
                self.catalog,
                temp_root,
                fallback_provider=provider,
                fallback_policy=policy,
            )
            return service.run_deterministic_search(DeterministicSearchRunRequest.from_parts(query))


def _provider_call_count(provider) -> int:
    if hasattr(provider, "calls"):
        return len(provider.calls)
    return 1 if getattr(provider, "_cache", {}) else 0


if __name__ == "__main__":
    unittest.main()
