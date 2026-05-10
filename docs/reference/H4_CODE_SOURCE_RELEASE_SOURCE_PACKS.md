# H4 Code Source Release Source Packs


    H4 is the code/source/release host wave. It extends the Source OS after H3 by
    recording policy-pack-only metadata posture for source hosts, repository
    hosts, archival identity hosts, and release hosts.

    Current scope is planning only. H4-BUNDLE-01 does not enable live calls,
    repository cloning, source archive downloads, release asset downloads, git
    commands, build tools, installs, execution, source sync, public index
    mutation, master index mutation, evidence acceptance, candidate acceptance,
    source identity truth, release identity truth, or source-to-binary
    provenance truth.

Selected sources cover Software Heritage, major hosted repository/release metadata, preservation metadata, generic Git metadata, and generic release-host metadata. Optional future hosts such as Bitbucket, Codeberg/Forgejo/Gitea, Savannah, KDE Invent, GNOME GitLab, Apache mirrors, kernel.org-style trees, and vendor portals remain deferred.

The current artifacts are source records, source policy packs, coverage previews, scorecard previews, and source-pack manifests. Future H4-BUNDLE-02 may add committed fixtures and normalizers. Future H4-BUNDLE-03 may add approval-gated bounded metadata-only live probes.

Validation: `python scripts/validate_h4_code_source_release_policy_packs.py` and `python scripts/summarize_h4_code_source_release_sources.py --check`.
