# SearchNeed Runtime

SearchNeeds are durable local demand records created from unresolved Search Hunt Sessions. They preserve the original query, local result posture, linked hunt, linked exhaustion report, checked layers, deferred layers, and recommended future work categories.

SearchNeeds are not truth, evidence, source approval, rights clearance, malware safety, global absence proof, or index mutation. HUNT-05 stores the need and its state history only.

The runtime store is `search_need` at `db/search_need.sqlite` under the explicit Local Appliance instance manifest. It is opened through `runtime/local_appliance` composition, not by ad hoc paths.

HUNT-05 supports creation from a hunt, list/show, and state transitions. WorkUnit creation remains disabled until HUNT-06. Source probes, extraction, sync, model/provider calls, review mutation, public index mutation, and master index mutation remain disabled.
