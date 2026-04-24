from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from runtime.engine.interfaces.public import (
    CheckedSourceSummary,
    Notice,
    ObjectSummary,
    ResolutionMemoryRecord,
    ResolutionMemoryResultSummary,
    SourceSummary,
)
from runtime.engine.memory.resolution_memory import (
    resolution_memory_from_dict,
    resolution_memory_to_dict,
)
from runtime.engine.provenance import EvidenceSummary


class ResolutionMemorySerializationTestCase(unittest.TestCase):
    def test_round_trips_stable_json_shape(self) -> None:
        memory = ResolutionMemoryRecord(
            memory_id="memory-successful-resolution-0001",
            memory_kind="successful_resolution",
            source_run_id="run-exact-resolution-0001",
            raw_query=None,
            task_kind="exact_resolution",
            requested_value="fixture:software/synthetic-demo-app@1.0.0",
            checked_source_ids=("github-releases-recorded-fixtures", "synthetic-fixtures"),
            checked_source_families=("github_releases", "synthetic"),
            checked_sources=(
                CheckedSourceSummary(
                    source_id="synthetic-fixtures",
                    name="Synthetic Fixtures",
                    source_family="synthetic",
                    status="active_fixture",
                    trust_lane="fixture",
                ),
            ),
            result_summaries=(
                ResolutionMemoryResultSummary(
                    target_ref="fixture:software/synthetic-demo-app@1.0.0",
                    object_summary=ObjectSummary(
                        id="obj.synthetic-demo-app",
                        kind="software",
                        label="Synthetic Demo App",
                    ),
                    resolved_resource_id="obj.synthetic-demo-app",
                    source=SourceSummary(
                        family="synthetic_fixture",
                        source_id="synthetic-fixtures",
                        label="Synthetic Fixtures",
                    ),
                ),
            ),
            useful_source_ids=("synthetic-fixtures",),
            primary_resolved_resource_id="obj.synthetic-demo-app",
            evidence_summary=(
                EvidenceSummary(
                    claim_kind="version",
                    claim_value="1.0.0",
                    asserted_by_family="synthetic",
                    asserted_by_label="Synthetic Fixtures",
                    evidence_kind="fixture_record",
                    evidence_locator="fixtures/synthetic_software.json",
                ),
            ),
            created_at="2026-04-25T00:00:00+00:00",
            notices=(Notice(code="memory_created", severity="info", message="Created."),),
            created_by_slice="resolution_memory_v0",
            invalidation_hints={"created_from_run": "run-exact-resolution-0001"},
        )

        with tempfile.TemporaryDirectory() as temp_dir:
            source_path = Path(temp_dir) / "memory.json"
            source_path.write_text(
                '{"note":"not used"}\n',
                encoding="utf-8",
            )
            restored = resolution_memory_from_dict(
                resolution_memory_to_dict(memory),
                source_path=source_path,
            )

        self.assertEqual(restored.memory_id, memory.memory_id)
        self.assertEqual(restored.memory_kind, "successful_resolution")
        self.assertEqual(restored.result_summaries[0].object_summary.label, "Synthetic Demo App")
        self.assertEqual(restored.evidence_summary[0].claim_value, "1.0.0")
        self.assertEqual(restored.invalidation_hints, {"created_from_run": "run-exact-resolution-0001"})


if __name__ == "__main__":
    unittest.main()
