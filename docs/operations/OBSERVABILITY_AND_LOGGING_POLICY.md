# Observability And Logging Policy

Observability must minimize data and redact credential-like values. Raw secrets, credentials, full private query history, account sessions, and private file paths are forbidden fields.

Validation: `python scripts/validate_hosting_readiness.py`.
