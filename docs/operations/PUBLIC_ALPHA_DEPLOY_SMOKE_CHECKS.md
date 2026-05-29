# Public Alpha Deploy Smoke Checks

Smoke checks are static or fixture-backed in this dry run. They do not perform
live HTTP calls or deploy anything.

Required checks:

- `/api/v1/alpha/status` route is defined
- `/api/v1/alpha/search` route is defined
- `/api/v1/alpha/object/{object_id}` route is defined
- `/alpha` web route is defined
- public write actions are disabled
- public live source fanout is disabled

The smoke result is PASS only if every check is read-only and non-mutating.
