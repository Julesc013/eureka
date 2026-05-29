# Validation

The promotion-05 validator accepts this waiting state only when:

- branch state supports a future fast-forward
- launch-candidate and deploy dry-run results pass
- unsafe boundary flags are false
- a repo-external external full-discovery handoff exists
- promotion has not been performed

Full unittest discovery is not run inside AI.
