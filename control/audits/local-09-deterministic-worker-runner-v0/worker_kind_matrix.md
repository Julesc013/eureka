# Worker Kind Matrix

Enabled:

- `noop_worker`
- `review_queue_checker`
- `reviewed_index_rebuild_worker` - operator-token gated, local public index only
- `absence_report_worker`
- `local_status_snapshot_worker`

Blocked:

- `source_probe_worker`
- `extraction_worker`
- `agent_research_worker`
- `ai_model_worker`
- `download_worker`
- `install_execute_worker`
- `source_sync_worker`
- `lan_worker`
- `deployment_worker`
