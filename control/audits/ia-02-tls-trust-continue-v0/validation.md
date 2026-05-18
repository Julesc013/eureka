# Validation

Validation commands include:

- `python scripts/validate_ia_metadata_policy.py`
- `python scripts/validate_ia_fixture_replay.py`
- `python scripts/eureka_ia_live_metadata_probe.py --dry-run --json`
- `python scripts/diagnose_python_tls_trust.py --host archive.org --json`
- `python scripts/validate_ia_tls_trust.py`
- `python scripts/validate_ia_live_metadata_probe.py`
- focused IA live-probe and TLS diagnostic unittest modules
- architecture boundary and generated artifact cleanliness checks
- AIDE Lite checks

The approved live rerun was executed only after the verified TLS diagnostic
passed with verification enabled and no insecure context.

