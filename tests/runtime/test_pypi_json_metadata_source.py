import json
import unittest
from pathlib import Path
from unittest import mock

from runtime.source_observation.sources import pypi_json_metadata as source


class FakeResponse:
    status = 200

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return None

    def read(self):
        return json.dumps(
            {
                "info": {
                    "name": "sampleproject",
                    "version": "4.0.0",
                    "summary": "A sample Python project",
                    "project_urls": {
                        "Homepage": "https://github.com/pypa/sampleproject"
                    },
                },
                "releases": {
                    "4.0.0": [
                        {
                            "filename": "sampleproject-4.0.0.tar.gz",
                            "url": "https://files.pythonhosted.org/packages/sampleproject-4.0.0.tar.gz",
                        }
                    ]
                },
                "urls": [
                    {
                        "filename": "sampleproject-4.0.0-py3-none-any.whl",
                        "url": "https://files.pythonhosted.org/packages/sampleproject-4.0.0-py3-none-any.whl",
                    }
                ],
            }
        ).encode("utf-8")

    def getcode(self):
        return 200


class PyPIJsonMetadataSourceTests(unittest.TestCase):
    def test_package_name_validation_accepts_sampleproject(self):
        self.assertEqual((), source.validate_pypi_package_name("sampleproject"))

    def test_package_name_validation_rejects_arbitrary_package(self):
        errors = source.validate_pypi_package_name("not-sampleproject")
        self.assertTrue(errors)
        with self.assertRaises(ValueError):
            source.build_pypi_metadata_request("not-sampleproject")

    def test_dry_run_does_not_call_network(self):
        request = source.build_pypi_metadata_request("sampleproject")
        with mock.patch.object(source.urllib.request, "urlopen", side_effect=AssertionError("network called")):
            response = source.fetch_pypi_metadata(
                request,
                client_contact="Eureka-test/0.1 (contact: test@example.invalid)",
                timeout_seconds=10,
                live=False,
            )
        self.assertEqual("dry_run", response.status)
        parsed = source.parse_pypi_metadata_response(response)
        self.assertEqual("sampleproject", parsed["name"])

    def test_mocked_live_fetch_performs_one_request(self):
        request = source.build_pypi_metadata_request("sampleproject")
        calls = []

        def fake_urlopen(http_request, timeout):
            calls.append((http_request, timeout))
            return FakeResponse()

        with mock.patch.object(source.urllib.request, "urlopen", side_effect=fake_urlopen):
            response = source.fetch_pypi_metadata(
                request,
                client_contact="Eureka-test/0.1 (contact: test@example.invalid)",
                timeout_seconds=10,
                live=True,
            )
        self.assertEqual(1, len(calls))
        self.assertEqual("observed", response.status)
        self.assertEqual("https://pypi.org/pypi/sampleproject/json", calls[0][0].full_url)

    def test_parser_and_normalizer_extract_metadata_without_fetching_files(self):
        request = source.build_pypi_metadata_request("sampleproject")
        with mock.patch.object(source.urllib.request, "urlopen", return_value=FakeResponse()) as urlopen:
            response = source.fetch_pypi_metadata(
                request,
                client_contact="Eureka-test/0.1 (contact: test@example.invalid)",
                timeout_seconds=10,
                live=True,
            )
        parsed = source.parse_pypi_metadata_response(response)
        normalized = source.normalize_pypi_metadata_response(response, source.build_default_source_record())
        self.assertEqual("sampleproject", parsed["name"])
        self.assertEqual("4.0.0", parsed["version"])
        self.assertEqual("A sample Python project", parsed["summary"])
        self.assertEqual(1, parsed["release_count"])
        self.assertEqual("sampleproject", normalized.normalized_fields["name"])
        self.assertEqual(1, urlopen.call_count)

    def test_source_module_does_not_resolve_dependencies_or_fetch_download_urls(self):
        request = source.build_pypi_metadata_request("sampleproject")
        self.assertFalse(request.parameters["download_files"])
        self.assertFalse(request.parameters["resolve_dependencies"])
        text = Path(source.__file__).read_text(encoding="utf-8")
        self.assertNotIn("files.pythonhosted.org", text)
        self.assertNotIn("pip install", text.lower())


if __name__ == "__main__":
    unittest.main()
