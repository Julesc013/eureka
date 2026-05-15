# Smoke Result

The LOCAL-04 smoke script checks loopback routes only:

- `/`
- `/status`
- `/api/v1/status`
- `/api/v1/search?q=sampleproject`
- `/api/v1/absence?q=definitely-not-present-local-04`

The smoke script refuses non-localhost URLs before making a request.
