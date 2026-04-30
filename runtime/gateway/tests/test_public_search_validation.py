from __future__ import annotations

from urllib.parse import parse_qs
import unittest

from runtime.gateway.public_api import (
    PublicSearchRequest,
    validate_public_search_query,
)


class PublicSearchValidationTestCase(unittest.TestCase):
    def test_valid_query_uses_contract_defaults(self) -> None:
        request = validate_public_search_query(parse_qs("q=windows+7+apps"))

        self.assertIsInstance(request, PublicSearchRequest)
        assert isinstance(request, PublicSearchRequest)
        self.assertEqual(request.normalized_query, "windows 7 apps")
        self.assertEqual(request.limit, 10)
        self.assertEqual(request.mode, "local_index_only")
        self.assertEqual(request.profile, "api_client")

    def test_missing_and_too_long_queries_return_governed_errors(self) -> None:
        missing = validate_public_search_query({})
        too_long = validate_public_search_query({"q": ["x" * 161]})

        self.assertEqual(missing.status_code, 400)
        self.assertFalse(missing.body["ok"])
        self.assertEqual(missing.body["error"]["code"], "query_required")
        self.assertEqual(too_long.status_code, 400)
        self.assertEqual(too_long.body["error"]["code"], "query_too_long")

    def test_forbidden_parameters_map_to_contract_error_codes(self) -> None:
        cases = {
            "index_path": "local_paths_forbidden",
            "url": "forbidden_parameter",
            "download": "downloads_disabled",
            "install": "installs_disabled",
            "upload": "uploads_disabled",
            "source_credentials": "forbidden_parameter",
            "live_probe": "live_probes_disabled",
        }
        for parameter, expected_code in cases.items():
            with self.subTest(parameter=parameter):
                response = validate_public_search_query({"q": ["archive"], parameter: ["1"]})
                self.assertEqual(response.status_code, 400)
                self.assertEqual(response.body["error"]["code"], expected_code)
                self.assertEqual(response.body["error"]["parameter"], parameter)

    def test_mode_profile_include_and_limit_are_bounded(self) -> None:
        cases = [
            ("q=archive&mode=live_probe", "live_probes_disabled"),
            ("q=archive&profile=admin", "unsupported_profile"),
            ("q=archive&include=raw_payload", "unsupported_include"),
            ("q=archive&limit=99", "limit_too_large"),
        ]
        for query_string, expected_code in cases:
            with self.subTest(query_string=query_string):
                response = validate_public_search_query(parse_qs(query_string))
                self.assertEqual(response.status_code, 400)
                self.assertEqual(response.body["error"]["code"], expected_code)


if __name__ == "__main__":
    unittest.main()
