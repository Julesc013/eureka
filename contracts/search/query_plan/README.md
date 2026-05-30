# Query Plan Contracts

`query_to_source_action_plan.v0.json` describes the deterministic public-search
planner packet that turns a raw query into an intent, domain pack, source-family
route, Archive.org metadata query rewrite, candidate suppressions, lane
expectations, source-action plans, WorkUnits, review handoff plans, and a
public-safe explanation packet.

The plan is candidate-only. It does not create accepted truth, mutate indexes,
enable downloads, run extraction, call model providers, or claim production or
public launch readiness.
