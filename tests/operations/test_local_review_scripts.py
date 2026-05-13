import io
import json
import tempfile
import unittest
from pathlib import Path

from runtime.local_appliance import close_local_appliance, open_local_appliance
from scripts import eureka_rebuild_reviewed_index, eureka_review_queue, eureka_set_operator_token
from scripts.eureka_init_instance import initialize_instance
from scripts.validate_local_review_rebuild import TOKEN, seed_review_records


class LocalReviewScriptTests(unittest.TestCase):
    def make_instance(self, tmp: str) -> tuple[Path, dict[str, str]]:
        instance = Path(tmp) / "eureka-instance"
        initialize_instance(instance)
        self.assertEqual(0, eureka_set_operator_token.main(["--instance", str(instance), "--token", TOKEN, "--json"], stdout=io.StringIO()))
        runtime = open_local_appliance(instance)
        try:
            seed = seed_review_records(runtime)
        finally:
            close_local_appliance(runtime)
        return instance, seed

    def test_set_operator_token_does_not_print_raw_token(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance = Path(tmp) / "eureka-instance"
            initialize_instance(instance)
            stdout = io.StringIO()
            code = eureka_set_operator_token.main(["--instance", str(instance), "--token", TOKEN, "--json"], stdout=stdout)

        self.assertEqual(0, code)
        self.assertNotIn(TOKEN, stdout.getvalue())

    def test_review_queue_list_show_and_decide(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance, seed = self.make_instance(tmp)
            list_out = io.StringIO()
            show_out = io.StringIO()
            decide_out = io.StringIO()
            list_code = eureka_review_queue.main(["--instance", str(instance), "--json", "list"], stdout=list_out)
            show_code = eureka_review_queue.main(
                ["--instance", str(instance), "--json", "show", "--id", seed["accepted_review_item_id"]],
                stdout=show_out,
            )
            decide_code = eureka_review_queue.main(
                [
                    "--instance",
                    str(instance),
                    "--json",
                    "decide",
                    "--id",
                    seed["accepted_review_item_id"],
                    "--decision",
                    "accept",
                    "--operator-token",
                    TOKEN,
                    "--local-only-confirmed",
                ],
                stdout=decide_out,
            )

        self.assertEqual(0, list_code, list_out.getvalue())
        self.assertEqual(0, show_code, show_out.getvalue())
        self.assertEqual(0, decide_code, decide_out.getvalue())
        self.assertEqual("accepted", json.loads(decide_out.getvalue())["review_status"])

    def test_rebuild_apply_requires_token(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            instance, seed = self.make_instance(tmp)
            eureka_review_queue.main(
                [
                    "--instance",
                    str(instance),
                    "--json",
                    "decide",
                    "--id",
                    seed["accepted_review_item_id"],
                    "--decision",
                    "accept",
                    "--operator-token",
                    TOKEN,
                    "--local-only-confirmed",
                ],
                stdout=io.StringIO(),
            )
            missing = eureka_rebuild_reviewed_index.main(["--instance", str(instance), "--apply", "--json"], stdout=io.StringIO(), stderr=io.StringIO())
            apply_out = io.StringIO()
            apply_code = eureka_rebuild_reviewed_index.main(
                ["--instance", str(instance), "--operator-token", TOKEN, "--apply", "--json"],
                stdout=apply_out,
            )

        self.assertNotEqual(0, missing)
        self.assertEqual(0, apply_code, apply_out.getvalue())
        self.assertEqual(1, json.loads(apply_out.getvalue())["included_count"])


if __name__ == "__main__":
    unittest.main()
