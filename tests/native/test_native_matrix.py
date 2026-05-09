import json
import unittest
from pathlib import Path

from scripts.validate_native_matrix import (
    REQUIRED_FIRST_WAVE,
    REQUIRED_FUTURE,
    REQUIRED_LIBS,
    load_toml_sections,
    validate_native_matrix,
)

REPO_ROOT = Path(__file__).resolve().parents[2]


class NativeMatrixTests(unittest.TestCase):
    def test_native_matrix_exists_and_validates(self) -> None:
        report = validate_native_matrix(REPO_ROOT)
        self.assertEqual(report["status"], "pass", report)

    def test_required_lanes_exist(self) -> None:
        sections = load_toml_sections(REPO_ROOT / "native" / "matrix" / "native.toml")
        lane_ids = set(sections)
        self.assertTrue(REQUIRED_FIRST_WAVE.issubset(lane_ids))
        self.assertTrue(REQUIRED_FUTURE.issubset(lane_ids))
        self.assertTrue(REQUIRED_LIBS.issubset(lane_ids))

    def test_native_clients_do_not_list_python_runtime_in_consumes(self) -> None:
        sections = load_toml_sections(REPO_ROOT / "native" / "matrix" / "native.toml")
        for lane_id, lane in sections.items():
            self.assertNotIn("python_runtime", lane.get("consumes", []), lane_id)
            self.assertNotIn("runtime_python_internals", json.dumps(lane), lane_id)

    def test_no_current_release_artifacts_are_claimed(self) -> None:
        artifacts = load_toml_sections(REPO_ROOT / "native" / "matrix" / "artifacts.toml")
        self.assertGreater(len(artifacts), 0)
        for artifact_id, artifact in artifacts.items():
            self.assertIs(artifact.get("produced_current"), False, artifact_id)
            self.assertIs(artifact.get("production_release_current"), False, artifact_id)


if __name__ == "__main__":
    unittest.main()
