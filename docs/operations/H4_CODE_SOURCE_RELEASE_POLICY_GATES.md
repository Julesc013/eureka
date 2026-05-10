# H4 Code Source Release Policy Gates


    H4 is the code/source/release host wave. It extends the Source OS after H3 by
    recording policy-pack-only metadata posture for source hosts, repository
    hosts, archival identity hosts, and release hosts.

    Current scope is planning only. H4-BUNDLE-01 does not enable live calls,
    repository cloning, source archive downloads, release asset downloads, git
    commands, build tools, installs, execution, source sync, public index
    mutation, master index mutation, evidence acceptance, candidate acceptance,
    source identity truth, release identity truth, or source-to-binary
    provenance truth.

Every H4 source requires source policy approval, endpoint or metadata allowlist, User-Agent/contact posture, auth/no-auth posture, rate limit, timeout, retry budget, cache TTL, kill switch, fixture replay, dry-run policy evaluation, output path policy, privacy/risk review, rights posture, repository clone prohibition review, source archive download prohibition review, release asset download prohibition review, git/build prohibition review, install/execute prohibition review, review queue gate, post-run audit, and connector scorecard.

Current approval state for every source is not_approved_for_live_access.
