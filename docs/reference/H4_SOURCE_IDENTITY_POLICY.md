# H4 Source Identity Policy


    H4 is the code/source/release host wave. It extends the Source OS after H3 by
    recording policy-pack-only metadata posture for source hosts, repository
    hosts, archival identity hosts, and release hosts.

    Current scope is planning only. H4-BUNDLE-01 does not enable live calls,
    repository cloning, source archive downloads, release asset downloads, git
    commands, build tools, installs, execution, source sync, public index
    mutation, master index mutation, evidence acceptance, candidate acceptance,
    source identity truth, release identity truth, or source-to-binary
    provenance truth.

Source identity candidates may include host, owner or namespace, repository or project name, repository URL candidates, origin URL candidates, Git object ID candidates, tag candidates, SWHID candidates, archived origin candidates, license claims, readme refs, changelog refs, source archive locator candidates, and repository state candidates.

A candidate is not accepted source identity truth. Git object IDs are not provenance truth without review. SWHID candidates are not object truth without review. Repository URLs do not prove official status. License fields do not prove rights clearance. Repository presence does not prove endorsement. Archived presence does not prove completeness.
