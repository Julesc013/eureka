# Secrets And Credential Policy

Secrets must not be committed. Provider credentials, API keys, private signing keys, cookies, and account tokens belong only in reviewed future secret stores with rotation and incident procedures.

Validation: `python scripts/validate_hosting_readiness.py`.
