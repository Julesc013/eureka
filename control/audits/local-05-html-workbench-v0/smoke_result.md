# Smoke Result

The workbench smoke script checks the loopback HTML routes and JSON API compatibility:

- `/`
- `/status`
- `/search?q=sampleproject`
- `/absence?q=definitely-not-present-local-05`
- `/api/v1/status`
- `/api/v1/search?q=sampleproject`

The smoke refuses non-localhost URLs before making a request.
