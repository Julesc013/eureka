# Source Policy And Approval Model

Source policy kinds include `manual_only`, `fixture_only`,
`source_cache_only_future`, `live_metadata_probe_after_approval`, and
`local_offline_extraction_after_approval`.

`live_probe_enabled` remains false in all P63 examples. Future live-network
probe work requires source policy review, rights review, rate limits, timeout,
backoff, circuit breaker controls, operator setup, and cache before public use.
