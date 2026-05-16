import json
import tempfile
import unittest
from io import StringIO
from pathlib import Path

from scripts.validate_fixture_source_observation_vertical_slice import main


class FixtureSourceObservationVerticalSliceScriptTests(unittest.TestCase):
    def test_validator_script_writes_report_and_prints_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            output = root / "report.json"
            stdout = StringIO()
            code = main(
                [
                    "--output-root",
                    str(root / "stores"),
                    "--output",
                    str(output),
                    "--json",
                ],
                stdout=stdout,
            )
            payload = json.loads(stdout.getvalue())

            self.assertEqual(0, code)
            self.assertEqual("pass", payload["status"])
            self.assertTrue(output.is_file())
            self.assertEqual(1, payload["search"]["result_count"])
            self.assertEqual(0, payload["absence"]["result_count"])
            self.assertEqual("eureka.fixture_object_absence_surface.v0", payload["surface_packets"]["schema_version"])
            self.assertEqual("Demo Project", payload["surface_packets"]["result_packet"]["results"][0]["title"])
            self.assertEqual(
                "eureka.fixture_reviewed_index_artifact.v0",
                payload["persistent_reviewed_index"]["schema_version"],
            )
            self.assertTrue(Path(payload["persistent_reviewed_index"]["artifact_path"]).is_file())

    def test_validator_rejects_product_output_root(self):
        stderr = StringIO()
        code = main(["--output-root", "runtime/q58-fixture", "--json"], stdout=StringIO(), stderr=stderr)
        self.assertEqual(2, code)
        self.assertIn("refusing", stderr.getvalue())

    def test_validator_uses_default_temp_root(self):
        stdout = StringIO()
        code = main(["--json"], stdout=stdout)
        payload = json.loads(stdout.getvalue())
        self.assertEqual(0, code)
        self.assertEqual("pass", payload["status"])
        self.assertEqual(1, payload["search"]["result_count"])
        self.assertEqual(0, payload["absence"]["result_count"])
        self.assertTrue(payload["no_live_no_mutation"]["fixture_store_root_isolated"])
        self.assertEqual("zzznomatch", payload["surface_packets"]["absence_packet"]["query"])
        self.assertEqual(1, payload["persistent_reviewed_index"]["search_from_artifact"]["result_count"])


if __name__ == "__main__":
    unittest.main()
