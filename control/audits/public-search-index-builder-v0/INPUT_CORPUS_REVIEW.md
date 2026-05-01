# Input Corpus Review

Allowed P55 inputs:

- `control/inventory/sources/*.source.json`
- synthetic software fixtures
- GitHub Releases recorded fixtures
- Internet Archive recorded fixtures
- local bundle fixture metadata and synthetic member records
- article-scan recorded fixtures
- source expansion recorded fixtures

Forbidden inputs remain excluded: arbitrary local paths, private cache roots,
staged packs, unreviewed packs, user uploads, credentials, live API responses,
untracked archives, executable payload bytes, and raw copyrighted payload dumps.

The generated index records source coverage for 15 source records. All sources
remain fixture, recorded fixture, or placeholder/local-future metadata; live
source use is false.
