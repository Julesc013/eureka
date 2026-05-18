# Validation

Validation for IA-02-TLS-TRUST-01 includes:

- IA-00 policy validator
- IA-01 fixture replay validator
- IA-02 live-probe dry-run
- Python TLS trust diagnostic
- IA TLS trust validator
- IA live-probe validator
- focused TLS and live-probe tests
- architecture boundary check
- generated artifact cleanliness check
- AIDE Lite checks

The task passes with warnings because the repository guardrails are correct but
the local Python TLS trust store still blocks a verified live IA response.
