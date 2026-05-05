# npm Metadata Review

Status summary: approval pack present, connector contract present, inventory
present, runtime planning present, approval pending, runtime planning-only.

Major gates:

- npm registry metadata source-policy review is policy_gated.
- Package-name and scoped-package review are required.
- Token/auth review is required; tokens are disabled now.
- Private scopes and credentialed registries are rejected.
- Dependency metadata and lifecycle-script risk boundaries are required.
- User-Agent/contact, rate-limit, timeout, retry/backoff, and circuit breaker are operator_gated.
- Source-cache/evidence-ledger authoritative destinations remain dependency_gated.

Forbidden capabilities: no npm registry calls, no npm/yarn/pnpm CLI calls, no
package download/install, no dependency resolution, no lifecycle script
execution, no npm audit, no public-search fanout, no mutation, no credentials, no
telemetry.

Next safe action: human/operator package scope, lifecycle-script boundary,
source-policy, User-Agent/contact, rate-limit, and cache/evidence destination
review.
