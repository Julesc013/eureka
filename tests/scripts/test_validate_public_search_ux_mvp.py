from __future__ import annotations

import unittest

from scripts.validate_public_search_ux_mvp import validate


class ValidatePublicSearchUxMvpTests(unittest.TestCase):
    def test_validator_passes(self) -> None:
        result = validate()

        self.assertEqual("pass", result["status"])
        self.assertFalse(result["deployment_performed"])
        self.assertFalse(result["public_mutation_enabled"])


if __name__ == "__main__":
    unittest.main()
