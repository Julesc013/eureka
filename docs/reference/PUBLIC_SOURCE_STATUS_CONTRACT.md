# Public Source Status Contract

Status: governed by `contracts/api/source_status.v0.json`.

Source status records are public-safe summaries for search responses and source
routes. They identify a source family, coverage depth, limitations, and the
next coverage step without claiming live coverage.

Allowed status values are:

- `active_fixture`
- `active_recorded_fixture`
- `placeholder`
- `local_private_future`
- `live_disabled`
- `live_enabled_future`

For the current repo state, live support and live enablement remain false unless
a later approval-gated connector milestone records actual runtime evidence.
