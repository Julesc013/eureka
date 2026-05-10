# H5 Vendor Update Driver Policy Gates

Every H5 source is currently `not_approved_for_live_access`.

Required gates include source policy approval, endpoint or metadata allowlist, User-Agent/contact posture where applicable, auth/no-auth posture, rate limit, timeout, retry budget, cache TTL, kill switch, fixture replay, dry-run policy evaluation, output path policy, privacy/risk review, rights posture, catalog fetch prohibition review, download prohibition reviews, vendor tool prohibition review, firmware flash prohibition review, install/execute prohibition review, review queue gate, post-run audit, and connector scorecard.

Failure of any future gate must fail closed. H5-BUNDLE-01 opens none of these gates.
