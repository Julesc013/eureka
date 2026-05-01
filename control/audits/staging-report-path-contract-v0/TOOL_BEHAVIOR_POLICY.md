# Tool Behavior Policy

Validate-only and future staging report tools must:

- default to stdout
- require an explicit output path for file writes
- require the output parent to exist by default
- avoid hidden state writes
- avoid parent directory auto-creation by default
- reject forbidden committed/runtime/public roots
- validate reports against Pack Import Report Format v0 when applicable

This does not grant staging, import, indexing, upload, runtime mutation, or
master-index mutation behavior.
