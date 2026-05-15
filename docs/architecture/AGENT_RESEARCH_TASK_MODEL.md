# Agent Research Task Model

Agent research tasks are disabled local records for future escalation. They are derived from a Search Hunt exhaustion report and local context such as SearchNeeds, steering preferences, checked layers, deferred layers, and blocked policies.

Tasks are not model output, evidence, source approval, rights clearance, malware safety, ranking authority, or index mutation.

Required disabled flags:

- `provider_enabled: false`
- `execution_enabled: false`
- `source_probe_enabled: false`
- browser/network research disabled by policy

The task model exists so a later reviewed gate can reason over a stable input packet shape without changing the local hunt workflow.
