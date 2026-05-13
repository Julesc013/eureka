# Read-Only Route Result

The LOCAL-12 probe covers:

- `/`
- `/status`
- `/health`
- `/search?q=sampleproject`
- `/absence?q=definitely-not-present-local-12`
- `/api/v1/status`
- `/api/v1/health`
- `/api/v1/search?q=sampleproject`
- `/api/v1/absence?q=definitely-not-present-local-12`

Each route must return an acceptable status, expose a local or read-only
boundary marker, avoid mutation controls, avoid external assets, and avoid
production/public launch claims.
