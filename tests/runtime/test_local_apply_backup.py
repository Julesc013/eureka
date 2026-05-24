from __future__ import annotations

import unittest

from runtime.local.apply import APPLY_CONFIRMATION, run_local_apply
from tests.runtime.test_local_apply_gate import make_instance


class LocalApplyBackupTests(unittest.TestCase):
    def test_backup_created_before_mutation(self) -> None:
        tmp, instance = make_instance()
        self.addCleanup(tmp.cleanup)

        result = run_local_apply(
            target_instance=instance,
            apply=True,
            operator_token="local-dev-token",
            confirmation=APPLY_CONFIRMATION,
        )

        self.assertEqual(result["status"], "pass")
        backup = result["backup_manifest"]
        self.assertTrue(result["backup_created_before_apply"])
        self.assertTrue((instance / "backups" / "local_apply" / backup["backup_id"] / "backup_manifest.json").exists())
        self.assertTrue(any(item["relative_path"] == "db/public_index.sqlite" for item in backup["files"]))


if __name__ == "__main__":
    unittest.main()
