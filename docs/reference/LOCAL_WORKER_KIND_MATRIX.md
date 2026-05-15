# Local Worker Kind Matrix

| Worker kind | Enabled | Store mutation | Token required |
| --- | --- | --- | --- |
| `noop_worker` | yes | none | no |
| `review_queue_checker` | yes | none | no |
| `reviewed_index_rebuild_worker` | yes | local `public_index` only | yes |
| `absence_report_worker` | yes | none | no |
| `local_status_snapshot_worker` | yes | none | no |
| `source_probe_worker` | no | none | no |
| `extraction_worker` | no | none | no |
| `agent_research_worker` | no | none | no |
| `ai_model_worker` | no | none | no |
| `download_worker` | no | none | no |
| `install_execute_worker` | no | none | no |
| `source_sync_worker` | no | none | no |
| `lan_worker` | no | none | no |
| `deployment_worker` | no | none | no |

Disabled workers fail closed before execution. They may record a blocked WorkUnit transition and an audit result, but they must not run source probes, extraction, model calls, downloads, installs, source sync, LAN actions, deployment, or master-index mutation.
