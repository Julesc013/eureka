# H4 Code Source Release Fixture Plan


    H4 is the code/source/release host wave. It extends the Source OS after H3 by
    recording policy-pack-only metadata posture for source hosts, repository
    hosts, archival identity hosts, and release hosts.

    Current scope is planning only. H4-BUNDLE-01 does not enable live calls,
    repository cloning, source archive downloads, release asset downloads, git
    commands, build tools, installs, execution, source sync, public index
    mutation, master index mutation, evidence acceptance, candidate acceptance,
    source identity truth, release identity truth, or source-to-binary
    provenance truth.

H4-BUNDLE-02 should add committed synthetic fixtures for each source: minimal source/project metadata, typical repository/project metadata, release metadata where applicable, tag/commit/SWHID metadata where applicable, release asset metadata where applicable, source-to-binary relation candidate metadata where applicable, license/readme/changelog metadata where applicable, policy-blocked records, malformed or partial records, no-live-call evidence, no cloned repository payloads, no downloaded source archives, no downloaded release assets, no git command output, no credentials, and no package-manager/build output.
