# Token/Auth Boundary Review

PyPI Metadata v0 remains token-free by default. No PyPI token is configured, no credentials are configured, and no authenticated package index access is planned for v0 unless a future explicit approval changes the policy. PyPI token access is not configured.

Token/auth policy is pending. Until it is approved, the future runtime must use `EUREKA_PYPI_METADATA_AUTH_MODE=none` and `EUREKA_PYPI_METADATA_TOKEN_ENABLED=0`.

Token use is not required for P90 planning and is not enabled.
