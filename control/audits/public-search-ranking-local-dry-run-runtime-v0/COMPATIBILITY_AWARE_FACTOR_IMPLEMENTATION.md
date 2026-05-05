# Compatibility-Aware Factor Implementation

Compatibility factors cover:

- platform, OS, and version fit
- architecture, CPU, ABI, or API fit
- runtime and dependency metadata fit
- hardware or driver hints when present
- emulator or VM feasibility as informational only
- unknown compatibility gaps
- conflicting compatibility evidence

Rules:

- No installability claim.
- No dependency-safety claim.
- No emulator or VM launch.
- Platform-name similarity alone remains weak.
- Package metadata is not installability.
- Unknown compatibility remains visible.

