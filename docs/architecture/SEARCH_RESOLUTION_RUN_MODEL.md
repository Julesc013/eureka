# Search Resolution Run Model

Resolution runs are resumable, steerable state machines tied to `run_id`, the request, the compiled query, and coverage reporting.

Required states: accepted, compiled, local_index_running, local_results_available, candidate_index_running, candidate_results_available, source_cache_running, source_cache_results_available, hunt_planning, hunt_running, source_workunit_queued, source_workunit_running, source_candidates_available, review_items_available, index_rebuild_available, paused, resumed, cancelled, completed, and failed.

Terminal states are completed, cancelled, and failed. Interrupted non-terminal states are paused, waiting_for_user, waiting_for_policy, waiting_for_source_quota, waiting_for_review, and waiting_for_index_rebuild.

Every state transition has a timestamp and reason. Every source-backed transition identifies source family. Every blocked transition has blocked_reason. Every output is tied to run_id. Every run has a coverage report and preserves query interpretation.
