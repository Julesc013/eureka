import json
import unittest
from io import StringIO
from pathlib import Path
from unittest import mock

from scripts.demo_source_observation_seam import build_demo_result, main as demo_main
from scripts.validate_source_observation_seam import validate_seam

from runtime.source.observation import (
    MetadataRequest,
    MetadataResponse,
    ResponseFingerprint,
    SourceId,
    SourceRecord,
    validate_metadata_request,
    validate_metadata_response,
    validate_no_task_vocabulary,
    validate_source_record,
)


class SourceObservationValidationTests(unittest.TestCase):
    def test_no_task_vocabulary_appears_in_serialized_outputs(self) -> None:
        result = build_demo_result()
        text = json.dumps(result, sort_keys=True)
        self.assertEqual(validate_no_task_vocabulary(text), ())

    def test_truth_boundary_field_is_rejected(self) -> None:
        self.assertTrue(validate_no_task_vocabulary({"truth_boundary": True}))

    def test_product_boundary_field_is_rejected(self) -> None:
        self.assertTrue(validate_no_task_vocabulary({"product_boundary": True}))

    def test_validation_functions_return_errors(self) -> None:
        record = SourceRecord(
            source_id=SourceId("source.example.metadata"),
            source_family="",
            trust_lane="synthetic",
            label="Synthetic metadata",
        )
        self.assertIn("source family is required", validate_source_record(record))

        request = MetadataRequest("", SourceId("source.example.metadata"), "", "")
        self.assertTrue(validate_metadata_request(request))

        response = MetadataResponse("", "", SourceId("source.example.metadata"), "", "", fingerprint=ResponseFingerprint("", ""))
        self.assertTrue(validate_metadata_response(response))

    def test_demo_runs_without_network(self) -> None:
        with mock.patch("socket.socket", side_effect=AssertionError("network disabled")):
            code = demo_main(["--json"], stdout=StringIO())
        self.assertEqual(code, 0)

    def test_validator_passes_or_warns_for_current_repo(self) -> None:
        result = validate_seam(Path(__file__).resolve().parents[2])
        self.assertIn(result["status"], {"pass", "pass_with_warnings"})
        self.assertEqual(result["h_series_dependencies"], 0)
        self.assertEqual(result["network_dependencies"], 0)

    def test_no_h_series_module_import_or_connector_dependency(self) -> None:
        root = Path(__file__).resolve().parents[2] / "runtime/source/observation"
        text = "\n".join(path.read_text(encoding="utf-8") for path in root.glob("*.py"))
        self.assertNotIn("runtime.connectors", text)
        self.assertNotIn("h1_metadata_wave", text)


if __name__ == "__main__":
    unittest.main()
