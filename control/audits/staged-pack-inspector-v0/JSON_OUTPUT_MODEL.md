# JSON Output Model

`--json` emits:

- `ok`
- `schema_version`
- `inspector_id`
- `mode`
- `inspected_manifests`
- `summary`
- `errors`
- hard false side-effect fields
- notes

Each inspected manifest includes:

- manifest path, ID, status, validation status, and staging mode
- validate report reference summary
- staged pack reference summary
- staged entity counts and candidate summary
- privacy/rights/risk summary
- hard no-mutation guarantees
- reset/delete/export policy
- limitations, warnings, and next safe action

The JSON output is an inspection report, not an import report, staging record,
local index candidate, contribution candidate, or master-index decision.
