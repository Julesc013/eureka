# Background Hunt Run Record

Background hunt run records are persisted in the Search Hunt store table `search_hunt_runner_runs`.

Fields:

- `run_id`: stable run identifier.
- `hunt_id`: linked Search Hunt session.
- `search_need_ids`: linked SearchNeeds represented in the plan/run.
- `workunit_ids`: WorkUnits selected or considered.
- `worker_kinds`: worker kinds selected for the run.
- `started_at` and `finished_at`: UTC timestamps.
- `status`: `planned`, `running`, `complete`, `blocked`, `skipped`, or `failed`.
- `policy_decision`: short policy decision string.
- `worker_results`: local worker result summaries.
- `blocked_workunits`: WorkUnits left blocked by policy.
- `warnings`: warnings emitted during planning or running.
- `limitations`: local-only and non-claim notes.

All records include false side-effect flags for source probes, extraction, external network, model/provider calls, acquisition actions, review mutation, master index mutation, deployment, and public launch claims.

