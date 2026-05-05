# GitHub Releases Review

Status summary: approval pack present, connector contract present, inventory
present, runtime planning present, approval pending. A recorded fixture adapter
exists under `runtime/connectors/github_releases/`, but it is deterministic local
fixture code and not live GitHub API runtime.

Major gates:

- GitHub API/source-policy review is policy_gated.
- Owner/repo identity review is required.
- Token/auth review is required; tokens are disabled now.
- Private and token-required repositories are rejected.
- User-Agent/contact, rate-limit, timeout, retry/backoff, and circuit breaker are operator_gated.
- Source-cache/evidence-ledger authoritative destinations remain dependency_gated.

Forbidden capabilities: no GitHub API calls, no repository clone, no release
asset/source archive download, no raw blob fetch, no token use, no public-search
fanout, no mutation, no credentials, no telemetry.

Next safe action: explicitly separate the existing recorded fixture adapter from
any future live GitHub metadata connector, then complete operator approval.
