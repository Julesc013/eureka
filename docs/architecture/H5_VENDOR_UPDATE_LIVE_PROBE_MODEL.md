# H5 Vendor/Update Live Probe Model

The model layers exact request envelopes over the H5 fixture normalizer. When a future approved live response exists, the probe wraps the metadata response in a synthetic fixture envelope so existing H5 candidate builders enforce the same truth and product boundaries.

The hard boundary is fail-closed: source approval, metadata approval, request manifest match, endpoint class allowlist, rate/cache/kill-switch decisions, and output path policy all have to pass before any network call.
