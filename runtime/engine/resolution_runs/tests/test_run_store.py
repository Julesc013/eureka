from __future__ import annotations

import json
from pathlib import Path
import tempfile
import unittest

from runtime.engine.interfaces.public import (
    CheckedSourceSummary,
    Notice,
    ObjectSummary,
    ResolutionTask,
    ResolutionRunRecord,
    ResolutionRunResultItem,
    ResolutionRunResultSummary,
)
from runtime.engine.resolution_runs import LocalResolutionRunStore, ResolutionRunNotFoundError


class LocalResolutionRunStoreTestCase(unittest.TestCase):
    def test_allocate_save_load_and_list_runs(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = LocalResolutionRunStore(temp_dir)
            run_id = store.allocate_run_id("exact_resolution")
            run = ResolutionRunRecord(
                run_id=run_id,
                run_kind="exact_resolution",
                requested_value="fixture:software/synthetic-demo-app@1.0.0",
                status="completed",
                started_at="2026-04-24T00:00:00+00:00",
                completed_at="2026-04-24T00:00:00+00:00",
                checked_source_ids=("synthetic-fixtures",),
                checked_source_families=("synthetic",),
                checked_sources=(
                    CheckedSourceSummary(
                        source_id="synthetic-fixtures",
                        name="Synthetic Fixtures",
                        source_family="synthetic",
                        status="active_fixture",
                        trust_lane="fixture",
                    ),
                ),
                resolution_task=ResolutionTask(
                    raw_query="Windows 7 apps",
                    task_kind="browse_software",
                    object_type="software",
                    constraints={"platform": {"marketing_alias": "Windows 7"}},
                    prefer=("direct_software_artifact",),
                    exclude=("operating_system_image",),
                    action_hints=("inspect", "download"),
                    source_hints=("synthetic", "github_releases"),
                    planner_confidence="high",
                    planner_notes=("Stored for test.",),
                ),
                result_summary=ResolutionRunResultSummary(
                    result_kind="exact_resolution",
                    result_count=1,
                    items=(
                        ResolutionRunResultItem(
                            target_ref="fixture:software/synthetic-demo-app@1.0.0",
                            object_summary=ObjectSummary(
                                id="obj.synthetic-demo-app",
                                kind="software",
                                label="Synthetic Demo App",
                            ),
                            resolved_resource_id="resolved:sha256:demo",
                        ),
                    ),
                ),
                notices=(Notice(code="demo_notice", severity="info", message="Stored for test."),),
            )

            store.save_run(run)
            loaded = store.get_run(run_id)
            listed = store.list_runs()
            run_path = Path(temp_dir) / "resolution_runs" / "runs" / f"{run_id}.json"
            index_path = Path(temp_dir) / "resolution_runs" / "index.json"
            raw_record = json.loads(run_path.read_text(encoding="utf-8"))
            raw_index = json.loads(index_path.read_text(encoding="utf-8"))

        self.assertEqual(run_id, "run-exact-resolution-0001")
        self.assertEqual(loaded.run_id, run.run_id)
        self.assertEqual(loaded.resolution_task.task_kind if loaded.resolution_task else "", "browse_software")
        self.assertEqual(loaded.result_summary.result_count if loaded.result_summary else 0, 1)
        self.assertEqual(len(listed), 1)
        self.assertEqual(raw_record["record_kind"], "eureka.resolution_run")
        self.assertEqual(raw_index["run_ids"], [run_id])

    def test_unknown_run_id_raises_structured_not_found(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            store = LocalResolutionRunStore(temp_dir)
            with self.assertRaises(ResolutionRunNotFoundError):
                store.get_run("run-exact-resolution-9999")


if __name__ == "__main__":
    unittest.main()
