import json
import re
import unittest

from tests.hardening.helpers import iter_text_files, repo_path, read_text


EXTERNAL_SYSTEMS = {
    "google",
    "internet_archive_metadata",
    "internet_archive_full_text",
    "google_web_search",
    "internet_archive_metadata_search",
    "internet_archive_full_text_search",
}


class ExternalBaselineGuardsTest(unittest.TestCase):
    def test_manual_observation_records_are_required_for_observed_baselines(self):
        observations_dir = repo_path("evals/search_usefulness/observations")
        observation_files = sorted(observations_dir.glob("*.json"))
        observation_files.extend(
            sorted(
                repo_path("evals/search_usefulness/external_baselines/observations").glob("*.json")
            )
        )
        observation_files.extend(
            sorted(
                repo_path(
                    "evals/search_usefulness/external_baselines/batches"
                ).glob("*/observations/*.json")
            )
        )

        for path in observation_files:
            payload = json.loads(path.read_text(encoding="utf-8"))
            records = payload.get("observations", [payload])
            for record in records:
                system = record.get("system") or record.get("system_id")
                if system not in EXTERNAL_SYSTEMS:
                    continue
                if record.get("observation_status") != "observed":
                    continue
                self.assertTrue(record.get("operator"), path)
                self.assertTrue(record.get("observed_at") or record.get("date"), path)
                self.assertTrue(record.get("source_notes") or record.get("notes"), path)

    def test_external_baseline_pending_manifest_is_not_observed(self):
        manifest = json.loads(
            repo_path(
                "evals/search_usefulness/external_baselines/observations/pending_observations.json"
            ).read_text(encoding="utf-8")
        )

        self.assertEqual(manifest["observation_status"], "pending_manual_observation")
        self.assertEqual(len(manifest["query_ids"]), 64)
        self.assertEqual(len(manifest["required_system_ids"]), 3)
        self.assertNotIn("top_results", manifest)

    def test_batch_zero_pending_observations_are_not_observed(self):
        payload = json.loads(
            repo_path(
                "evals/search_usefulness/external_baselines/batches/batch_0/observations/pending_batch_0_observations.json"
            ).read_text(encoding="utf-8")
        )

        self.assertEqual(payload["observation_status"], "pending_manual_observation")
        self.assertEqual(len(payload["observations"]), 39)
        for record in payload["observations"]:
            self.assertEqual(record["observation_status"], "pending_manual_observation")
            self.assertEqual(record["top_results"], [])
            self.assertIsNone(record["observed_at"])
            self.assertIsNone(record["operator"])

    def test_docs_record_manual_pending_external_baseline_policy(self):
        docs = [
            "evals/search_usefulness/README.md",
            "evals/search_usefulness/external_baselines/README.md",
            "docs/evals/SEARCH_BENCHMARK_DESIGN.md",
            "control/audits/2026-04-25-comprehensive-test-eval-audit/CONTENT_COVERAGE_AUDIT.md",
        ]
        text = "\n".join(read_text(path).lower() for path in docs)
        self.assertIn("pending_manual_observation", text)
        self.assertIn("manual", text)
        self.assertTrue(
            "no google scraping" in text or "does not scrape google" in text,
            "Search usefulness docs must state Google baselines are not scraped.",
        )

    def test_scripts_and_docs_do_not_claim_google_or_archive_scraping(self):
        scanned_paths = list(
            iter_text_files(
                [
                    "evals/search_usefulness",
                    "evals/search_usefulness/external_baselines",
                    "scripts",
                    "docs/evals",
                    "control/audits/2026-04-25-comprehensive-test-eval-audit",
                ]
            )
        )
        forbidden = re.compile(
            r"(scrape|scraping|crawl|crawling)\s+(google|internet archive)"
            r"|google\s+(scrape|scraping|crawler)"
            r"|internet archive\s+(scrape|scraping|crawler)",
            re.IGNORECASE,
        )
        allowed_policy_phrases = (
            "no google scraping",
            "no automated google scraping",
            "does not scrape google",
            "do not scrape google",
            "no internet archive scraping",
            "does not scrape google, internet archive",
            "performs no google scraping",
            "no scraping",
            "do not perform google scraping",
        )

        violations = []
        for path in scanned_paths:
            for line_number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                if not forbidden.search(line):
                    continue
                lowered = line.lower()
                if any(phrase in lowered for phrase in allowed_policy_phrases):
                    continue
                if "do not scrape" in lowered or "does not scrape" in lowered:
                    continue
                if "not perform" in lowered or "no " in lowered:
                    continue
                violations.append(f"{path.relative_to(repo_path('.'))}:{line_number}: {line.strip()}")

        self.assertEqual(violations, [])


if __name__ == "__main__":
    unittest.main()
