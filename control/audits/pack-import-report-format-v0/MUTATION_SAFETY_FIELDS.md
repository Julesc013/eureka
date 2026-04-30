# Mutation Safety Fields

Every report has these hard false fields at top level and in
`mutation_summary`:

- `import_performed`
- `staging_performed`
- `indexing_performed`
- `upload_performed`
- `master_index_mutation_performed`
- `runtime_mutation_performed`
- `network_performed`

The validator rejects reports where any of these fields is true. Example
reports also leave `mutation_summary.files_written` empty.
