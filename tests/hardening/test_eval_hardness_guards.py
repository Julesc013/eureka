import json
import unittest
from pathlib import Path

from tests.hardening.helpers import load_json, repo_path, run_python


REQUIRED_ARCHIVE_TASK_IDS = {
    "windows_7_apps",
    "win98_registry_repair",
    "old_blue_ftp_client_xp",
    "latest_firefox_before_xp_drop",
    "driver_inside_support_cd",
    "article_inside_magazine_scan",
}

REQUIRED_SEARCH_QUERY_IDS = {
    "windows_7_apps",
    "latest_firefox_before_xp_support_ended",
    "old_blue_ftp_client_xp",
    "driver_thinkpad_t42_wifi_windows_2000",
    "article_ray_tracing_1994_magazine",
    "driver_inf_inside_support_cd",
}

REQUIRED_SEARCH_QUERY_FAMILIES = {
    "current_covered_sanity",
    "negative_absence",
    "platform_software",
    "latest_compatible_release",
    "driver_hardware_support",
    "manual_documentation",
    "article_inside_scan",
    "package_container_member",
    "vague_identity",
    "web_archive_dead_link",
    "source_code_package_release",
}


def _load_archive_tasks():
    tasks = []
    for path in sorted(repo_path("evals/archive_resolution/tasks").glob("*.yaml")):
        tasks.append(json.loads(path.read_text(encoding="utf-8")))
    return tasks


class EvalHardnessGuardsTest(unittest.TestCase):
    def test_archive_resolution_hard_tasks_remain_structured(self):
        tasks = _load_archive_tasks()
        by_id = {task["id"]: task for task in tasks}

        self.assertGreaterEqual(len(tasks), 6)
        self.assertTrue(REQUIRED_ARCHIVE_TASK_IDS.issubset(by_id))

        for task_id in REQUIRED_ARCHIVE_TASK_IDS:
            task = by_id[task_id]
            self.assertGreaterEqual(len(task.get("raw_query", "").strip()), 10, task_id)
            self.assertIn("expected_plan", task, task_id)
            self.assertIn("task_kind", task["expected_plan"], task_id)
            self.assertIn("object_type", task["expected_plan"], task_id)
            self.assertTrue(task.get("acceptable_result_patterns"), task_id)
            self.assertTrue(task.get("required_evidence"), task_id)
            self.assertTrue(task.get("bad_result_patterns"), task_id)

    def test_archive_resolution_runner_preserves_current_hard_gap_honesty(self):
        completed = run_python(["scripts/run_archive_resolution_evals.py", "--json"], timeout=90)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        report = json.loads(completed.stdout)

        summaries = {item["task_id"]: item for item in report["task_summaries"]}
        self.assertTrue(REQUIRED_ARCHIVE_TASK_IDS.issubset(summaries))
        self.assertEqual(report["total_task_count"], len(summaries))
        self.assertGreaterEqual(report["status_counts"].get("capability_gap", 0), 1)
        self.assertEqual(
            report["status_counts"].get("capability_gap", 0)
            + report["status_counts"].get("not_satisfied", 0)
            + report["status_counts"].get("partial", 0),
            report["total_task_count"],
        )
        self.assertNotIn("satisfied", report["status_counts"])

        full_tasks = {task["task_id"]: task for task in report["tasks"]}
        for task_id in REQUIRED_ARCHIVE_TASK_IDS:
            self.assertIn(
                summaries[task_id]["overall_status"],
                {"capability_gap", "not_satisfied", "partial"},
                task_id,
            )
            self.assertEqual(summaries[task_id]["planner_status"], "satisfied", task_id)
            if summaries[task_id]["overall_status"] != "capability_gap":
                self.assertGreater(full_tasks[task_id]["search_observed_result_count"], 0, task_id)
                checks = (
                    full_tasks[task_id]["satisfied_checks"]
                    + full_tasks[task_id]["partial_checks"]
                    + full_tasks[task_id]["failed_checks"]
                )
                search_checks = [
                    check for check in checks if check["name"] == "search.expected_result_hints"
                ]
                self.assertEqual(len(search_checks), 1, task_id)
                search_check = search_checks[0]
                self.assertIn(
                    search_check["status"],
                    {"satisfied", "partial", "not_satisfied"},
                    task_id,
                )
                if summaries[task_id]["overall_status"] == "partial":
                    observed = search_check.get("observed", {})
                    self.assertTrue(observed.get("source_ids"), task_id)
                    self.assertTrue(
                        observed.get("member_paths")
                        or observed.get("representation_ids")
                        or observed.get("artifact_locators"),
                        task_id,
                    )

    def test_search_usefulness_query_pack_keeps_hard_coverage(self):
        query_pack = load_json("evals/search_usefulness/queries/search_usefulness_v0.json")
        queries = query_pack["queries"]
        by_id = {query["id"]: query for query in queries}
        families = {query["query_family"] for query in queries}

        self.assertGreaterEqual(len(queries), 64)
        self.assertTrue(REQUIRED_SEARCH_QUERY_IDS.issubset(by_id))
        self.assertTrue(REQUIRED_SEARCH_QUERY_FAMILIES.issubset(families))

        for query_id in REQUIRED_SEARCH_QUERY_IDS:
            query = by_id[query_id]
            self.assertGreaterEqual(len(query.get("query", "").strip()), 10, query_id)
            self.assertIn(
                query["expected_eureka_current_status"],
                {"covered", "partial", "capability_gap", "source_gap", "unknown"},
                query_id,
            )

    def test_search_usefulness_runner_marks_external_baselines_pending(self):
        completed = run_python(["scripts/run_search_usefulness_audit.py", "--json"], timeout=120)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        report = json.loads(completed.stdout)

        self.assertEqual(report["total_query_count"], 64)
        pending_counts = report["external_baseline_pending_counts"]
        for system in ("google", "internet_archive_metadata", "internet_archive_full_text"):
            self.assertEqual(pending_counts.get(system), report["total_query_count"], system)

        for query in report["queries"]:
            external = [
                observation
                for observation in query["observations"]
                if observation["system"] != "eureka"
            ]
            self.assertTrue(external, query["query_id"])
            for observation in external:
                self.assertEqual(
                    observation["observation_status"],
                    "pending_manual_observation",
                    f"{query['query_id']}::{observation['system']}",
                )


if __name__ == "__main__":
    unittest.main()
