# Staged Entity Model

Future staged entities are local candidates and diagnostics only.

Supported entity types:

- `staged_source_candidate`
- `staged_evidence_candidate`
- `staged_index_summary`
- `staged_contribution_candidate`
- `staged_ai_output_candidate`
- `staged_issue`
- `staged_decision_note`

Each entity carries privacy, rights, risk, review status, summary,
limitations, and provenance refs. Review statuses never imply accepted public
state or canonical truth. The future staged inspector should display these
entities without mutating public search, a local index, runtime source
registry, or master index.
