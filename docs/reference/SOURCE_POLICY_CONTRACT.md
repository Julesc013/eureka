# Source Policy Contract

Source policy controls whether a source may be inspected, replayed from
fixtures, probed, synced, mapped to source cache, mapped to evidence previews,
or used in review outputs.

H0-BUNDLE-01 approves only policy and fixture representation. Future live access
requires explicit approval gates:

- source policy approval
- endpoint allowlist
- User-Agent/contact decision
- rate limit
- timeout
- retry budget
- cache TTL
- kill switch
- output path policy
- privacy/risk review
- rights posture
- review gates
- fixture replay
- dry-run preflight
- post-run audit

Policy records do not mutate indexes or accept truth.
