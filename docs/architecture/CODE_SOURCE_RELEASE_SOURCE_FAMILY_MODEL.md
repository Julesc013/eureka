# Code Source Release Source Family Model


    H4 is the code/source/release host wave. It extends the Source OS after H3 by
    recording policy-pack-only metadata posture for source hosts, repository
    hosts, archival identity hosts, and release hosts.

    Current scope is planning only. H4-BUNDLE-01 does not enable live calls,
    repository cloning, source archive downloads, release asset downloads, git
    commands, build tools, installs, execution, source sync, public index
    mutation, master index mutation, evidence acceptance, candidate acceptance,
    source identity truth, release identity truth, or source-to-binary
    provenance truth.

The family covers code hosts, source archival identity hosts, repository metadata hosts, release hosts, and generic source/release metadata. The family does not own trust semantics. It records observations for later fixture replay, review, scorecards, and quality deltas.

Current index depth is D0_source_known for all H4 sources. Future target depth is D2_metadata_indexed only after fixture replay, policy review, and separately approved probe gates.
