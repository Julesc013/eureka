# Existing Command Seams

| Seam | Owner | Reuse posture |
| --- | --- | --- |
| Local instance initialization | `tools/generators/eureka_init_instance.py` | reused directly |
| Local instance validation | `tools/generators/eureka_validate_instance.py` | reused directly |
| Local instance status | `tools/generators/eureka_instance_status.py` | reused directly |
| ResolutionRun creation | `runtime/resolution_run/**` | reused directly |
| ResolutionRun replay | `runtime/resolution_run/runner.py` | reused directly |
| Preview Index build/search/validate | `runtime/index/preview/**` | reused directly |
| Exploration workspace | `runtime/local/e2e_hunt_exploration.py` | reused directly |
| Local HTTP service | `runtime/local/service/**` | reused directly |
| Autonomous oracle | `evals/e2e_reference/oracle/**` | reused directly |

Required conclusion:

```text
one canonical local instance model
one canonical local service router
one runner
one Preview Index
one oracle
no duplicated command implementation
```
