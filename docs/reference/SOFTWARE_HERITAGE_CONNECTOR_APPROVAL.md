# Software Heritage Connector Approval v0

        P76 is an approval/readiness pack for a future Software Heritage identity and archive metadata connector. The live connector is not implemented, no external calls are made, no Software Heritage API calls are made, no SWHIDs are resolved live, no origins or repository identities are fetched live, and public search must not call Software Heritage or fan out from public-query parameters.

        ## Scope

        The connector scope is software identity/archive metadata-only: future SWHID metadata summary, origin metadata summary, visit metadata summary, snapshot metadata summary, release metadata summary, revision metadata summary, directory metadata summary, content identifier metadata summary, archival presence observation, and historical source identity observation after approval.

        Arbitrary origin fetch and arbitrary SWHID fetch are forbidden. Source code content fetch, content blob fetch, directory content fetch, raw file fetch, repository clone, source archive download, source file retrieval, graph crawl, origin crawl, scraping, mirroring, install, and execution are forbidden.

        SWHID, origin URL, and repository identity review are required. Example SWHID and origin values are synthetic placeholders and must not be resolved or fetched. Private and credentialed repositories must be rejected or redacted.

        ## Source Code Content Risk

        Source-code-content risk policy is required. Source identity metadata may be observed later, but source content must not be fetched, cached, published, downloaded, cloned, or executed. P76 makes no source-code safety claim, source completeness claim, license clearance claim, rights clearance claim, or malware safety claim.

        ## Source Policy

        Official Software Heritage API/source policy, API terms, automated access, rate-limit, retry-after or abuse-limit, cache, rights/access, and token policy reviews remain pending. P76 does not browse the web and does not configure source-policy values.

        User-Agent/contact remains operator pending: descriptive User-Agent and contact policy are required later, contact_value is null, user_agent_value is null, and fake contacts are forbidden. Token use is disabled for v0 unless a future explicit credential policy is approved.

        ## Runtime Boundary

        The approval pack adds no connector runtime, no source sync runtime, no source cache runtime, no evidence ledger runtime, no telemetry, no database, no queue persistence, and no public search fanout. It mutates no source cache, evidence ledger, candidate index, public index, local index, or master index.

        ## Cache And Evidence

        Future Software Heritage observations must be cache-first and evidence-attributed. Public search may read reviewed source cache outputs in the future, but public search must not call Software Heritage live and must not accept arbitrary origin URL or SWHID parameters for live fetches.

        Expected future source cache outputs are software_heritage_swhid_metadata_summary, software_heritage_origin_metadata_summary, software_heritage_visit_metadata_summary, software_heritage_snapshot_metadata_summary, software_heritage_release_metadata_summary, software_heritage_revision_metadata_summary, software_heritage_directory_metadata_summary, and software_heritage_archival_presence_summary.

        Expected future evidence ledger outputs are software identity, archival presence, origin metadata, release metadata, revision metadata, snapshot metadata, SWHID, and scoped absence observations. They require review and promotion policy and are not accepted as truth by default.

        ## Future Path

        Future implementation requires explicit approval, official source-policy review, SWHID/origin/repository identity review, source-code-content risk review, token policy review, User-Agent/contact decision, rate limit, timeout, retry/backoff, circuit breaker, cache policy, evidence attribution, and operator approval.
