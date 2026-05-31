# Snapshot Refresh

`SNAPSHOT-REFRESH-00` projects existing reviewed records and seed-batch handoffs
into a refreshed local snapshot packet set.

The refresh includes reviewed records, candidate sections, review queue
summaries, known needs, bounded absence summaries, a read-only relay projection,
and a public-alpha reassessment input. It does not accept candidates, mutate the
reviewed/master/public indexes, write `site/dist`, deploy, publish, or claim
production or public-launch readiness.

Candidates from the frontier media and legacy software seed batches remain
review-only candidates. Promotion previews, local apply, and snapshot refresh
handoffs remain separate gates.
