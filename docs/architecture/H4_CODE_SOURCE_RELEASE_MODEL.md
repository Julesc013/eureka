# H4 Code Source Release Model


    H4 is the code/source/release host wave. It extends the Source OS after H3 by
    recording policy-pack-only metadata posture for source hosts, repository
    hosts, archival identity hosts, and release hosts.

    Current scope is planning only. H4-BUNDLE-01 does not enable live calls,
    repository cloning, source archive downloads, release asset downloads, git
    commands, build tools, installs, execution, source sync, public index
    mutation, master index mutation, evidence acceptance, candidate acceptance,
    source identity truth, release identity truth, or source-to-binary
    provenance truth.

The H4 model separates source identity, release identity, and source-to-binary relation candidates. Repository metadata, tag metadata, release metadata, and archival metadata are observations that must pass review before any source cache, evidence, candidate, public index, or master index use.

This bundle reuses H0 Source OS contracts, H1 approval-only source posture, H2 package identity caution, and H3 fixture/live/review gates. H1 Software Heritage and GitHub Releases approval material remains precedent, not a live-access grant.
