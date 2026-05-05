# Source Policy Gate Status

No official source/API policy review is recorded as complete for any first-wave
connector. The gate remains `policy_gated` for each connector.

Required source-policy review:

- Internet Archive metadata: source/API policy, cache policy, rights/access/risk review.
- Wayback/CDX/Memento: CDX/Memento source policy, URI-R handling, replay/fetch boundary, cache policy.
- GitHub Releases: API policy, repository identity rules, token/no-token posture, asset/source-archive boundary.
- PyPI metadata: package metadata policy, dependency metadata caution, private/credentialed index rejection.
- npm metadata: registry metadata policy, scoped package policy, dependency metadata caution, lifecycle-script boundary.
- Software Heritage: SWHID/origin/repository policy, source-code content fetch boundary, archive/clone prohibition.

Do not fabricate official policy review. Codex cannot fabricate official policy approval. Human/operator review is still
required before connector runtime implementation or live probes.
