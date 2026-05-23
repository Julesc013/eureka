import json
import tempfile
import unittest
from pathlib import Path

from runtime.local.operator import (
    LocalOperatorError,
    hash_operator_token,
    load_operator_token_record,
    require_operator_token,
    verify_operator_token,
    write_operator_token_record,
)


class DummyConfig:
    def __init__(self, instance_root: Path):
        self.instance_root = instance_root


class DummyRequest:
    def __init__(self, token: str | None = None):
        self.headers = {}
        if token is not None:
            self.headers["x-eureka-operator-token"] = token
        self.params = {}
        self.body_params = {}


class LocalOperatorAuthTests(unittest.TestCase):
    def test_operator_token_hash_verifies_correct_token(self) -> None:
        token_hash = hash_operator_token("local-secret-token", "salt-value")

        self.assertTrue(verify_operator_token("local-secret-token", token_hash, "salt-value"))
        self.assertFalse(verify_operator_token("wrong-token", token_hash, "salt-value"))

    def test_raw_token_is_not_persisted(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            record = write_operator_token_record(Path(tmp), "local-secret-token")
            stored = json.loads((Path(tmp) / "config" / "operator.json").read_text(encoding="utf-8"))

        self.assertTrue(record["token_hash"])
        self.assertFalse(record["raw_token_stored"])
        self.assertNotIn("local-secret-token", json.dumps(stored))

    def test_require_operator_token_accepts_configured_token(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            write_operator_token_record(Path(tmp), "local-secret-token")
            state = require_operator_token(DummyRequest("local-secret-token"), DummyConfig(Path(tmp)))

        self.assertTrue(state.configured)

    def test_require_operator_token_rejects_missing_or_wrong_token(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            write_operator_token_record(Path(tmp), "local-secret-token")
            config = DummyConfig(Path(tmp))

            with self.assertRaises(LocalOperatorError):
                require_operator_token(DummyRequest(), config)
            with self.assertRaises(LocalOperatorError):
                require_operator_token(DummyRequest("wrong-token"), config)

    def test_load_operator_token_record_returns_none_when_unconfigured(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIsNone(load_operator_token_record(Path(tmp)))


if __name__ == "__main__":
    unittest.main()
