from __future__ import annotations

import json
import tempfile
from pathlib import Path
import unittest

from runtime.search.observability import (
    DiscoveryEventStore,
    export_diagnostic_bundle,
    metrics_from_events,
    sanitize_event,
)


class DiscoveryObservabilityTests(unittest.TestCase):
    def test_events_redact_provider_payload_and_hash_query(self) -> None:
        event = sanitize_event(
            {
                "event_type": "search_completed",
                "run_id": "run-1",
                "query": "operator private query",
                "url": "https://provider.example/result",
                "snippet": "restricted provider snippet",
                "provider_rank": 1,
                "raw_response": {"secret": "payload"},
                "Authorization": "Bearer secret",
                "count": 3,
            }
        )

        encoded = json.dumps(event, sort_keys=True)
        self.assertIn("query_hash", event)
        self.assertNotIn("operator private query", encoded)
        self.assertNotIn("provider.example", encoded)
        self.assertNotIn("restricted provider snippet", encoded)
        self.assertNotIn("provider_rank", encoded)
        self.assertNotIn("Bearer secret", encoded)
        self.assertEqual("search_completed", event["event_type"])

    def test_metrics_count_normalized_event_types(self) -> None:
        events = [
            sanitize_event({"event_type": "search_started", "run_id": "r"}),
            sanitize_event({"event_type": "provider_results_received", "run_id": "r", "provider": "brave", "duration_ms": 12}),
            sanitize_event({"event_type": "document_indexed", "run_id": "r"}),
            sanitize_event({"event_type": "duplicate_removed", "run_id": "r"}),
            sanitize_event({"event_type": "fetch_blocked", "run_id": "r", "code": "robots"}),
        ]

        metrics = metrics_from_events(events)

        self.assertEqual(1, metrics["search_count"])
        self.assertEqual(1, metrics["provider_requests"])
        self.assertEqual(1, metrics["preview_index_upserts"])
        self.assertEqual(1, metrics["robots_blocks"])
        self.assertFalse(metrics["provider_payload_persisted"])

    def test_store_and_export_diagnostics_are_redacted(self) -> None:
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            store = DiscoveryEventStore(root / "events.jsonl")
            store.record("search_started", run_id="r", query="private query")
            store.append({"event_type": "document_indexed", "run_id": "r", "url": "https://provider.example/item", "snippet": "nope"})

            export = export_diagnostic_bundle(
                run_id="r",
                out_dir=root / "bundle",
                events=store.read(run_id="r"),
                capability_state={"capabilities": {"live_search": {"implementation_state": "implemented"}}},
                provider_statuses=[{"provider": "brave", "credential_value": "secret", "capability_manifest": {"persist_rank": False}}],
                run_summary={"run_id": "r", "provider_results_persisted": False, "snippet": "restricted"},
            )

            self.assertEqual("pass", export["status"])
            exported_text = "\n".join(path.read_text(encoding="utf-8") for path in (root / "bundle").iterdir() if path.is_file())
            self.assertNotIn("private query", exported_text)
            self.assertNotIn("provider.example", exported_text)
            self.assertNotIn("restricted", exported_text)
            self.assertNotIn("credential_value\": \"secret", exported_text)
            self.assertIn("provider_payload_persisted", exported_text)


if __name__ == "__main__":
    unittest.main()
