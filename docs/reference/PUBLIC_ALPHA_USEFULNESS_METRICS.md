# Public Alpha Usefulness Metrics

Metrics are calculated from committed snapshot-refresh examples.

Required metrics:

- reviewed record count
- candidate count
- candidate-to-reviewed ratio
- known need count
- absence summary count
- represented domains
- reviewed domain count
- seed batch count
- query count
- queries with reviewed results
- queries with candidate results
- queries with need or absence evidence
- web routes smoked
- API routes smoked
- launch blockers and warnings

Candidate, need, and absence evidence improves internal review usefulness but
does not create reviewed truth.

`PUBLIC-ALPHA-REASSESS-01` adds:

- fixture candidate count
- live metadata candidate count
- total candidate count
- live metadata candidate ratio
- public search view-model availability
- live metadata review needs

Live metadata candidates are counted as candidates, not reviewed records.

`PUBLIC-ALPHA-REASSESS-02` adds:

- reviewed metadata record preview count
- reviewed source lead preview count
- useful lead count
- needs-more-evidence count
- rejected-or-duplicate count
- preview-to-reviewed ratio
- queries with review preview
- local-apply need

Review previews are counted separately from reviewed records.
