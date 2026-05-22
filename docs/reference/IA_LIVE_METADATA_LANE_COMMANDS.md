# IA Live Metadata Lane Commands

Commands:

- `request_live_ia_metadata`
- `approve_live_ia_metadata`
- `run_live_ia_metadata_dry_run`
- `run_live_ia_metadata_mock`
- `run_live_ia_metadata_now`
- `cancel_live_ia_metadata`
- `inspect_live_ia_metadata_result`

Default posture:

- Dry-run is operator projection only and performs no source access.
- Mock-live is operator projection only and uses deterministic fixtures.
- Real live execution requires `--allow-live`, an operator token, and policy.
- Public and native read-only projections are blocked.

Command responses must include blocked reasons, lane state, boundary flags, and
projection-safe events. They must not mutate stores or commit raw IA responses.
