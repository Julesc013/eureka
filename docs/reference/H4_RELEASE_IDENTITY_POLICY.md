# H4 Release Identity Policy


    H4 is the code/source/release host wave. It extends the Source OS after H3 by
    recording policy-pack-only metadata posture for source hosts, repository
    hosts, archival identity hosts, and release hosts.

    Current scope is planning only. H4-BUNDLE-01 does not enable live calls,
    repository cloning, source archive downloads, release asset downloads, git
    commands, build tools, installs, execution, source sync, public index
    mutation, master index mutation, evidence acceptance, candidate acceptance,
    source identity truth, release identity truth, or source-to-binary
    provenance truth.

Release identity candidates may include release IDs, tags, names, versions, timestamps, actors, release notes refs, asset metadata, asset names, sizes, hash candidates, source archive asset candidates, binary asset candidates, signature asset candidates, SBOM asset candidates, changelog candidates, compatibility claim candidates, and advisory candidates.

Release identity candidates are not accepted release truth. Asset metadata does not grant download permission. Hash metadata does not prove malware safety. Signature metadata does not prove authenticity without future verification. Source archives do not prove build reproducibility. Release notes do not prove compatibility or installability.
