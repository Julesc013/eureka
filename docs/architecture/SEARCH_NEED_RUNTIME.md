# SearchNeed Runtime

SearchNeeds are durable local demand records created from unresolved Search Hunt Sessions. They preserve the original query, local result posture, linked hunt, linked exhaustion report, checked layers, deferred layers, and recommended future work categories.

SearchNeeds are not truth, evidence, source approval, rights clearance, malware safety, global absence proof, or index mutation. HUNT-05 stores the need and its state history only.

The runtime store is `search_need` at `db/search_need.sqlite` under the explicit Local Appliance instance manifest. It is opened through `runtime/local/appliance` composition, not by ad hoc paths.

HUNT-05 supports creation from a hunt, list/show, and state transitions. WorkUnit creation remains disabled until HUNT-06. Source probes, extraction, sync, model/provider calls, review mutation, public index mutation, and master index mutation remain disabled.
## WorkUnit Generation Boundary

HUNT-06 adds SearchNeed-to-WorkUnit planning and persistence. SearchNeed records remain local demand records. The new pipeline creates linked WorkUnit queue records only, with execution disabled and risky future-action kinds blocked by policy.
## Workbench Smoke Integration

SearchNeeds participate in the HUNT-08 end-to-end local workflow as durable demand records between exhaustion reports and WorkUnit planning. They remain non-evidence, local-only records and do not authorize source access, extraction, model calls, downloads, or index mutation.
