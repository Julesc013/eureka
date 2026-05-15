# Hunt Replay Step Matrix

Enabled deterministic steps:

- create_hunt
- apply_hunt_command
- add_steering_preference
- generate_exhaustion_report
- create_search_need
- create_workunit_plan
- create_workunits
- run_safe_deterministic_worker
- draft_agent_research_task_disabled
- summarize_final_state

Blocked future steps:

- run_source_probe
- run_extraction
- run_ai_model
- run_agent_research
- download_artifact
- install_or_execute_artifact
- mutate_master_index
- deploy_service

Blocked steps are audit-visible but not replayed.
