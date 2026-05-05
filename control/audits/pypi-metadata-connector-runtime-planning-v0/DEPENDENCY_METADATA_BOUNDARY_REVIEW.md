# Dependency Metadata Boundary Review

Dependency metadata may be summarized in the future only if present in approved package metadata.

- dependency resolution remains disabled
- dependency graph expansion remains disabled
- package manager invocation remains disabled
- dependency safety claims are forbidden
- installability claims are forbidden
- vulnerability/security claims are forbidden unless a future vulnerability policy exists
- dependency names may require review if they reveal private/internal packages
- dependency metadata must not trigger live fetches of dependencies

Metadata is not dependency resolution, installability proof, dependency safety, vulnerability status, malware safety, or package execution safety.
