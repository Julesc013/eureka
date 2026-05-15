# Worker Matrix

| Worker | Status | Boundary |
| --- | --- | --- |
| noop_worker | enabled | WorkUnit state and worker result only |
| review_queue_checker | enabled | Local review queue count snapshot |
| absence_report_worker | enabled | Local absence summary snapshot |
| local_status_snapshot_worker | enabled | Local status snapshot |
| reviewed_index_rebuild_worker | enabled with token | Explicit local reviewed-index rebuild worker only |
| source_probe_worker | blocked | Source probes remain disabled |
| extraction_worker | blocked | Extraction remains disabled |
| agent_research_worker | blocked | Agent research remains disabled |
| ai_model_worker | blocked | Model/provider use remains disabled |
| download_worker | blocked | Acquisition remains disabled |
| install_execute_worker | blocked | Install or launch actions remain disabled |
| source_sync_worker | blocked | Source sync remains disabled |
| lan_worker | blocked | LAN worker mutation remains disabled |
| deployment_worker | blocked | Deployment remains disabled |

