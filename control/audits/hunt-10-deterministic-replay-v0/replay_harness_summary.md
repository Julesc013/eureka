# Replay Harness Summary

The replay harness creates typed fixtures from an existing local Search Hunt and can produce a plan-only result, a replay-local result, and a verify-existing result. Replay-local uses the explicit local runtime and records its replay result in `search_hunt_replay_runs`.

Replay covers hunt creation, command and steering history, exhaustion reports, SearchNeeds, WorkUnit planning and creation, one safe deterministic worker run, disabled agent research task drafting, and final-state summarization.
