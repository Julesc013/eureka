import tempfile
import unittest
from pathlib import Path

from runtime.local_appliance import close_local_appliance, open_local_appliance
from runtime.local_operator import write_operator_token_record
from runtime.local_review import get_review_item, list_review_items, record_review_decision
from runtime.local_service import LocalServiceApp
from scripts.eureka_init_instance import initialize_instance
from scripts.validate_local_review_rebuild import TOKEN, seed_review_records


def make_runtime(tmp: str, *, token: bool = False):
    instance = Path(tmp) / "eureka-instance"
    initialize_instance(instance)
    if token:
        write_operator_token_record(instance, TOKEN)
    runtime = open_local_appliance(instance)
    seed = seed_review_records(runtime)
    return runtime, seed


class LocalReviewServiceTests(unittest.TestCase):
    def test_list_and_get_review_items(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runtime, seed = make_runtime(tmp)
            try:
                listing = list_review_items(runtime)
                detail = get_review_item(runtime, seed["accepted_review_item_id"])
            finally:
                close_local_appliance(runtime)

        self.assertEqual("pass", listing["status"])
        self.assertGreaterEqual(listing["result_count"], 3)
        self.assertEqual(seed["accepted_review_item_id"], detail["review_item"]["review_item_id"])

    def test_record_review_decision_updates_review_queue(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runtime, seed = make_runtime(tmp)
            try:
                result = record_review_decision(
                    runtime,
                    seed["accepted_review_item_id"],
                    "accept",
                    None,
                    "operator",
                    True,
                )
                detail = get_review_item(runtime, seed["accepted_review_item_id"])
            finally:
                close_local_appliance(runtime)

        self.assertEqual("accepted", result["review_status"])
        self.assertEqual("accepted", detail["review_item"]["queue_status"])

    def test_local_service_review_decision_requires_token(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            runtime, seed = make_runtime(tmp, token=True)
            try:
                app = LocalServiceApp(runtime)
                missing = app.handle("POST", f"/review/{seed['accepted_review_item_id']}/decision", body="decision=accept")
                invalid = app.handle(
                    "POST",
                    f"/review/{seed['accepted_review_item_id']}/decision",
                    body="operator_token=wrong-token&decision=accept&local_only_confirmed=on",
                )
                valid = app.handle(
                    "POST",
                    f"/review/{seed['accepted_review_item_id']}/decision",
                    body=f"operator_token={TOKEN}&decision=accept&local_only_confirmed=on",
                )
            finally:
                close_local_appliance(runtime)

        self.assertEqual(401, missing.status_code)
        self.assertEqual(401, invalid.status_code)
        self.assertEqual(200, valid.status_code)


if __name__ == "__main__":
    unittest.main()
