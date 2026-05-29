# Validation

The promotion-05 validator accepts the pass state only when:

- branch state supports a future fast-forward
- launch-candidate and deploy dry-run results pass
- unsafe boundary flags are false
- repo-external external full-discovery evidence exists and passes
- promotion remains bounded to fast-forward only

Full unittest discovery is not run inside AI.
