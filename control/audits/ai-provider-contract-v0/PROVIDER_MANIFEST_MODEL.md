# Provider Manifest Model

`AI_PROVIDER.json` describes a future provider class. It is not executable and
does not grant runtime access.

Required posture:

- `default_enabled: false`
- no private data by default
- no telemetry by default
- no credentials in the manifest
- no local filesystem access by default
- no live source access
- no output acceptance without review

Provider types cover local model, local server, remote API, browser model,
native model, development tool, and disabled stub classes.
