# H1 Metadata Wave Fixture Plan

H1-BUNDLE-02 is expected to add committed fixtures and fixture-only normalizers for each H1 source. H1-BUNDLE-01 only records the fixture requirements.

Each source needs:

- minimal metadata record
- typical result record
- policy-blocked record
- malformed or partial record
- pagination or cursor shape when relevant
- no-live-call evidence
- no downloaded payloads
- no credentials, cookies, tokens, or private files

## Source Notes

- Wayback / CDX / Memento needs capture metadata, Memento link shape, blocked replay-fetch shape, and malformed capture rows.
- GitHub Releases needs release metadata, pagination shape, blocked asset-download shape, and partial release metadata.
- PyPI needs package metadata, release file listing metadata without payloads, blocked package-download shape, and malformed package metadata.
- npm Registry needs package metadata, version/dist metadata without payloads, blocked tarball-download shape, and malformed package metadata.
- Software Heritage needs origin/object metadata, identifier lookup shape, blocked source archive shape, and partial metadata.
- Repology needs cross-repository project metadata, package grouping shape, blocked unbounded search shape, and partial metadata.
- OSV needs advisory metadata, package/ecosystem lookup shape, blocked vulnerability acceptance shape, and partial advisory metadata.

All fixtures remain source observations or policy examples only; none become accepted truth.
