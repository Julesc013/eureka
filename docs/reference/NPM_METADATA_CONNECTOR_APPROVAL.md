# npm Metadata Connector Approval v0

        P75 is an approval/readiness pack for a future npm package metadata connector. The live connector is not implemented, no external calls are made, no npm registry API calls are made, no npm/yarn/pnpm CLI calls are made, and public search must not call npm or fan out from public-query parameters.

        ## Scope

        The connector scope is package metadata-only: future package, version, dist-tag, tarball metadata summary, engines, license, dependency metadata summary, deprecation-like status, and maintainer or publisher metadata summaries. Arbitrary package fetch is forbidden. Tarball metadata summary is allowed as future metadata; tarball download, package file download, package install, package archive inspection, npm audit, dependency resolution, and lifecycle script execution are forbidden.

        Package identity review is required for package names and scoped packages. Scoped package names may become public-safe metadata candidates only after review; private scopes are forbidden, and Eureka must not infer organization trust from a scope name.

        Dependency metadata caution is required. Dependency fields are metadata only and do not imply dependency resolution, dependency safety, vulnerability status, installability, or package health.

        Lifecycle script risk policy is required. Lifecycle script metadata may only be summarized after approval; preinstall, install, postinstall, and other package scripts must never execute, and P75 makes no script safety claim.

        ## Source Policy

        Official npm registry/source policy, API terms, automated access, rate-limit, retry-after or abuse-limit, cache, rights/access, and token policy reviews remain pending. P75 does not browse the web and does not configure source-policy values.

        User-Agent/contact remains operator pending: descriptive User-Agent and contact policy are required later, contact_value is null, user_agent_value is null, and fake contacts are forbidden. Token use is disabled for v0 unless a future explicit credential policy is approved.

        ## Runtime Boundary

        The approval pack adds no connector runtime, no source sync runtime, no source cache runtime, no evidence ledger runtime, no telemetry, no database, no queue persistence, and no public search fanout. It mutates no source cache, evidence ledger, candidate index, public index, local index, or master index.

        ## Cache And Evidence

        Future npm observations must be cache-first and evidence-attributed. Public search may read reviewed source cache outputs in the future, but public search must not call npm live and must not accept arbitrary package or registry parameters for live fetches.

        Expected future source cache outputs are npm_package_metadata_summary, npm_version_metadata_summary, npm_dist_tag_metadata_summary, npm_tarball_metadata_summary, npm_engines_metadata_summary, npm_license_metadata_summary, npm_dependency_metadata_summary, npm_lifecycle_script_metadata_summary, npm_deprecation_status_summary, and npm_publisher_maintainer_metadata_summary.

        Expected future evidence ledger outputs are package metadata, version, dist-tag, tarball metadata, engines, license, dependency metadata, deprecation status, lifecycle script metadata, scoped package identity, and scoped absence observations. They require review and promotion policy and are not accepted as truth by default.

        ## Future Path

        Future implementation requires explicit approval, official source-policy review, package and scoped package identity review, lifecycle script risk review, token policy review, User-Agent/contact decision, rate limit, timeout, retry/backoff, circuit breaker, cache policy, evidence attribution, and operator approval.

<!-- P76-SOFTWARE-HERITAGE-SUMMARY-START -->
## P76 Software Heritage Connector Approval Pack v0

Completed as an approval-only software identity/archive metadata connector pack. It adds no live Software Heritage connector runtime, no external calls, no Software Heritage API calls, no SWHID resolution, no origin/visit/snapshot/release/revision/directory/content lookup, no source code download, no repository clone, no source archive download, no source file retrieval, no public-query fanout, no telemetry, no credentials or tokens, and no source cache/evidence ledger/candidate/index mutation. It requires SWHID/origin/repository identity review, source-code-content risk policy, source policy review, User-Agent/contact decisions, and cache-first evidence outputs. Next recommended branch: P77 Public Hosted Deployment Evidence v0.
<!-- P76-SOFTWARE-HERITAGE-SUMMARY-END -->

<!-- P80-SOURCE-PAGE-CONTRACT-START -->
## P80 Source Page Contract v0

Source Page Contract v0 is contract-only and evidence-first. It defines future public source pages for source identity, status, coverage, connector posture, source policy gates, source cache/evidence posture, public search projection, query-intelligence projection, limitations, provenance caution, and rights/risk posture.

Boundary notes:

- No runtime source routes, database, persistent source-page store, connector runtime, source sync runtime, source cache runtime, evidence ledger runtime, candidate promotion, public-index mutation, local-index mutation, master-index mutation, live source fanout, downloads, mirrors, installs, execution, uploads, telemetry, accounts, rights clearance, malware safety claim, or authoritative source trust claim are added.
- Public search may reference source page links or source badges only after a future governed integration; P80 does not mutate public search result cards or the public index.
- Source pages explain source posture and limitations; they are not source API proxies, scrapers, crawlers, download pages, mirrors, or connector health dashboards.
<!-- P80-SOURCE-PAGE-CONTRACT-END -->
