# npm Metadata Connector Runtime Plan

Purpose: plan a future bounded, package-metadata-only, cache-first npm connector runtime without implementing it.

Readiness: `blocked_connector_approval_pending`. P75 exists, but `connector_approved_now` is false.

This is planning-only. It adds no runtime, no external calls, no npm registry API calls, no npmjs.com calls, no npm/yarn/pnpm CLI calls, no arbitrary package or registry fetch, no tarball download, no package file download, no install, no dependency resolution, no npm audit, no lifecycle script execution, no package archive inspection, no source-cache/evidence-ledger writes, no public-search fanout, no telemetry, no credentials or tokens, and no mutation.

Approval gate: P75 approval must complete before runtime implementation.

Package identity gate: package names must come from reviewed source records, reviewed search needs, source pack records, manual observations, or fixtures. Raw public query parameters, private packages, private scopes, credentialed registries, alternate registries without future approval, local paths, uploaded files, and arbitrary URLs are forbidden.

Scoped package gate: scoped package parsing and scope-name review are required; private or credentialed scopes remain rejected.

Dependency metadata caution gate: dependency metadata is metadata only. It must not trigger dependency resolution, graph expansion, package manager invocation, dependency safety claims, vulnerability claims, or installability claims.

Lifecycle-script risk gate: lifecycle script metadata may be summarized only after review. Script execution, preinstall/install/postinstall execution, npm audit, script safety claims, and package execution claims remain disabled.

Token/auth boundary: v0 remains token-free and unauthenticated unless a future explicit policy approves token use.

Future architecture plan: source sync worker, package identity guard, scoped package guard, dependency metadata guard, lifecycle-script risk guard, token/auth guard, source policy guard, source cache writer, evidence ledger writer, health reporter, and kill switch.

Future source sync flow: approved job, approval guard, package/scoped-package guard, dependency guard, lifecycle guard, token/auth guard, operator config check, bounded metadata-only request, normalization, source-cache candidate validation, evidence-ledger observation candidate, review-required output, and no public/master index mutation.

Future source-cache outputs: npm package, version, dist-tag, tarball, engines, license, dependency, lifecycle-script, deprecation, and publisher/maintainer metadata summaries.

Future evidence-ledger outputs: package metadata, version, dist-tag, tarball metadata, engines, license, dependency metadata, lifecycle script metadata, deprecation status, scoped package identity, and scoped absence observations. They are not accepted as truth and do not claim rights clearance, malware safety, dependency safety, vulnerability status, script safety, installability, or tarball safety.

Public search must not call npm live. Public search must not accept arbitrary package, scoped-package, or registry params for live fetch. Future result cards may show reviewed source-cache/evidence refs only after separate runtime and review.

Failure model: timeouts, bounded retries, retry-after/abuse-limit handling, per-source circuit breakers, per-source rate limits, no retry storms, no public-search blocking, no raw error leaks, connector disablement on policy violation, and operator-visible summaries are required.

Implementation phases remain disabled first: planning, local synthetic dry-run, approved local live metadata probe, source sync/cache/evidence candidates, reviewed public-index rebuild, and hosted worker with monitoring/rollback/quotas/kill switch.

Acceptance criteria: approval, package identity review, scoped-package review, dependency metadata review, lifecycle-script review, token/auth review, source policy, User-Agent/contact, rate limits, timeout, cache, evidence attribution, kill switch, blocked public params, and operator approval.

Next steps: P92 Software Heritage Connector Runtime Planning v0 only after approval, while operators review npm registry/source policy, decide npm User-Agent/contact policy, and decide token-free v0 policy.
