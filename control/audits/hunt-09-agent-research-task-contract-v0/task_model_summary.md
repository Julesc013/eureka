# Task Model Summary

HUNT-09 adds `runtime/agent_research` with durable local records for disabled future research tasks. A task is derived from a Search Hunt exhaustion report and optional SearchNeed context.

Every task records local query context, checked and deferred layers, blocked policies, steering preferences, research goals, forbidden actions, and a candidate-only output schema.

`provider_enabled` and `execution_enabled` are always false.
