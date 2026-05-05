# Dependency Metadata Boundary Review

Dependency metadata may be summarized in the future only if it is present in approved metadata.

Dependency resolution remains disabled. Dependency graph expansion remains disabled. npm/yarn/pnpm invocation remains disabled. Dependency safety claims are forbidden. Installability claims are forbidden. Vulnerability/security claims are forbidden unless a future vulnerability policy exists. Dependency names may require review if they reveal private/internal packages. Dependency metadata must not trigger live fetches of dependencies. Peer, optional, dev, and bundled dependencies must be labelled as metadata classes, not resolved.
