# SNAPSHOT-REFRESH-01

SNAPSHOT-REFRESH-01 refreshes the local snapshot and relay projection after the
bounded live metadata pilot. It packages existing reviewed records, fixture
seed-batch candidates, redacted live metadata candidates, review queue
summaries, needs, absences, relay previews, public search view-model previews,
and public alpha reassessment inputs.

This is projection only. Live metadata observations are source observations, not
reviewed truth. The live metadata candidate section keeps
`accepted_truth: false`, `review_required: true`, and
`raw_response_included: false`.

The refresh does not write `site/dist`, does not mutate reviewed, master, or
public indexes, does not download or extract files, and does not deploy or make
public launch claims.

The next gate is `PUBLIC-ALPHA-REASSESS-01`, which can use this projection to
measure usefulness without treating candidates as accepted records.
