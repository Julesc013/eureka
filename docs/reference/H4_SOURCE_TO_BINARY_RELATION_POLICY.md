# H4 Source To Binary Relation Policy


    H4 is the code/source/release host wave. It extends the Source OS after H3 by
    recording policy-pack-only metadata posture for source hosts, repository
    hosts, archival identity hosts, and release hosts.

    Current scope is planning only. H4-BUNDLE-01 does not enable live calls,
    repository cloning, source archive downloads, release asset downloads, git
    commands, build tools, installs, execution, source sync, public index
    mutation, master index mutation, evidence acceptance, candidate acceptance,
    source identity truth, release identity truth, or source-to-binary
    provenance truth.

Relation candidates may connect source repositories, commits, tags, releases, source archives, binary assets, package assets, build artifacts, checksums, signatures, SBOMs, and future provenance refs.

Supported relation kinds are source_release_claim, release_asset_claim, tag_to_release_candidate, commit_to_release_candidate, source_archive_to_release_candidate, binary_asset_to_release_candidate, package_to_source_candidate, sbom_to_artifact_candidate, signature_to_artifact_candidate, and not_evaluable.

A relation candidate is not accepted provenance. Tag/release matches do not prove build relation. Asset presence does not prove source relationship. Checksums do not prove malware safety. SBOM and signature metadata require future verification before trust claims.
