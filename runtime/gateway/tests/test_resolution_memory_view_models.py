from __future__ import annotations

import unittest

from runtime.gateway.public_api.resolution_memory_view_models import (
    resolution_memory_envelope_to_view_model,
)


class ResolutionMemoryViewModelsTestCase(unittest.TestCase):
    def test_coerces_resolution_memory_envelope(self) -> None:
        view_model = resolution_memory_envelope_to_view_model(
            {
                "status": "available",
                "memory_count": 1,
                "selected_memory_id": "memory-successful-search-0001",
                "memories": [
                    {
                        "memory_id": "memory-successful-search-0001",
                        "memory_kind": "successful_search",
                        "source_run_id": "run-deterministic-search-0001",
                        "created_at": "2026-04-25T00:00:00+00:00",
                        "checked_source_ids": ["synthetic-fixtures"],
                        "checked_source_families": ["synthetic"],
                        "checked_sources": [
                            {
                                "source_id": "synthetic-fixtures",
                                "name": "Synthetic Fixtures",
                                "source_family": "synthetic",
                                "status": "active_fixture",
                                "trust_lane": "fixture",
                            }
                        ],
                        "result_summaries": [
                            {
                                "target_ref": "fixture:software/synthetic-demo-app@1.0.0",
                                "object": {
                                    "id": "obj.synthetic-demo-app",
                                    "kind": "software",
                                    "label": "Synthetic Demo App",
                                },
                            }
                        ],
                        "useful_source_ids": ["synthetic-fixtures"],
                        "evidence_summary": [
                            {
                                "claim_kind": "version",
                                "claim_value": "1.0.0",
                                "asserted_by_family": "synthetic",
                                "evidence_kind": "fixture_record",
                                "evidence_locator": "fixtures/synthetic_software.json",
                            }
                        ],
                        "notices": [],
                        "created_by_slice": "resolution_memory_v0",
                    }
                ],
            }
        )

        self.assertEqual(view_model["memory_count"], 1)
        self.assertEqual(view_model["memories"][0]["memory_kind"], "successful_search")


if __name__ == "__main__":
    unittest.main()
