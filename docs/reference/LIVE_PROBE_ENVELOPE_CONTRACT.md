# Live Probe Envelope Contract

A live-probe envelope describes a requested future live operation and the policy
references needed before it can run.

The envelope itself grants no permission. H0-BUNDLE-02 examples are dry-run or
blocked only. Future live probes require source policy approval, endpoint
allowlists, User-Agent/contact decisions, rate limits, timeout/retry/cache
settings, kill switches, output path policy, review gates, fixture replay,
dry-run preflight, and post-run audit evidence.

Blocked results must use `request_count: 0` and `network_used: false`.
