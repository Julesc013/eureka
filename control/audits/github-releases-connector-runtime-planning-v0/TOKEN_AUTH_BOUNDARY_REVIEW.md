# Token/Auth Boundary Review

GitHub Releases v0 remains token-free by default. No GitHub token is configured, no credentials are configured, and no authenticated repository access is planned for v0 unless a future explicit approval changes the policy. GitHub token access is not configured.

Token/auth policy is pending. Until it is approved, the future runtime must use `EUREKA_GITHUB_RELEASES_AUTH_MODE=none` and `EUREKA_GITHUB_RELEASES_TOKEN_ENABLED=0`.

Token use is not required for P89 planning and is not enabled.
