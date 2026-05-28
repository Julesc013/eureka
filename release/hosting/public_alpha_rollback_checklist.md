# Public Alpha Rollback Checklist

- Identify the candidate commit and artifact set.
- Confirm prior reviewed snapshot/relay artifact remains available.
- Confirm route/API smoke checks before and after rollback.
- Confirm no public write or mutation state needs rollback.
- Confirm logs contain no secrets or raw live source bodies.
- Record rollback outcome in the future deploy dry-run or launch task evidence.
