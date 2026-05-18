# Route Matrix

Optional server route checks are read-only and localhost-only.

Covered route classes:

- root page
- status page
- known-hit search page
- known-absence search page
- Hunts page
- Hunt detail if available
- SearchNeed detail if available
- WorkUnit detail/list if available
- API search
- API absence
- API Hunts if available
- API status

The smoke runner skips route checks unless `--base-url` is supplied. With
`--expect-server`, failed localhost checks fail the smoke. Without
`--expect-server`, unavailable optional routes are warnings only.
