# Report Generation Model

The tool emits Pack Import Report v0 documents matching
`contracts/packs/pack_import_report.v0.json`.

Reports include:

- selected input roots
- per-pack validator results
- pack type and pack id when safely available
- checksum, schema, privacy, rights, and risk status summaries
- issue records with remediation
- record-count hints from manifests where available
- provenance notes
- explicit next actions
- hard false mutation-safety fields

Local absolute paths outside the repository are redacted as
`<explicit-local-path>` or `<redacted-local-path>`.

The report validator is reused before output. A generated report is still not
import, staging, indexing, upload, runtime mutation, or master-index mutation.
