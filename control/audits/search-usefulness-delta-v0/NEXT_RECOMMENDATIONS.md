# Next Recommendations

## Recommended Next Milestone

`Old-Platform Source Coverage Expansion v0` was the recommendation from this
delta pack and is now implemented. The recommended follow-up is
`Search Usefulness Audit Delta v1`.

## Why This Comes Next

Before Old-Platform Source Coverage Expansion v0, this delta pack reported:

- `source_gap`: 41 of 64 queries
- `source_coverage_gap`: 49 failure-mode labels
- external baselines pending/manual for every query

After Old-Platform Source Coverage Expansion v0, the current audit reports
`covered=5`, `partial=20`, `source_gap=28`, `capability_gap=9`, and
`unknown=2`. That movement is significant enough to warrant a new delta pack
before selecting the next implementation slice. Source coverage is still a
large pressure, but the next decision should be evidence-backed against the
expanded fixture corpus.

## Acceptance Criteria

- Add recorded/committed fixtures only.
- Target old-platform-compatible software and member-level discovery query
  families first.
- Keep placeholder sources distinct from active recorded-fixture sources.
- Preserve source ids, evidence, representation/access paths, compatibility
  hints, and member lineage.
- Add tests before changing expected query status.
- Keep external baselines pending unless manual observations are committed.
- Produce a new Search Usefulness Audit Delta v1 result after the source
  expansion.

## Initial Source Families To Target

1. Old Windows utility and portable-app release metadata.
2. Windows XP/2000/98 compatible browser and media-player release notes.
3. Driver/support-media records for ThinkPad, Creative/Sound Blaster, ATI, 3Com,
   and scanner-style queries.
4. Manuals/readmes/resource-kit records with platform evidence.
5. Additional bundle fixtures with member paths that can exercise member-level
   discovery without broad extraction.

## Alternatives Considered

### Search Usefulness Baseline Persistence v0

Useful, but it is a measurement infrastructure improvement. It should follow or
pair with the next source expansion so future reports have more movement to
measure. After the source expansion, the next delta pack should decide whether
baseline persistence is the right follow-up.

### Rust Query Planner Parity Candidate v0

Important for the Rust lane, but not the next usefulness bottleneck. Python
still needs more source-backed behavior before Rust parity should preserve the
current shape.

### Public Alpha Rehearsal Evidence v0

Useful for supervised demo readiness, but current demo usefulness is still
limited by source coverage.

### Compatibility Evidence Expansion v0

Useful, but broader compatibility evidence needs broader recorded source
material first.

### Live Source Expansion

Deferred. Recorded fixtures should continue to precede live source behavior so
coverage, evidence, and expected audit movement are reviewable.

## Do Not Do Next

- live crawling
- Google scraping
- Internet Archive scraping
- broad live source federation
- fuzzy/vector retrieval
- LLM planning
- production hosting
- native apps
- broad Rust rewrite
- installer automation
- arbitrary local filesystem ingestion
