# Snapshot Refresh Plan Reference

The refresh plan records source batches, reviewed record refs, candidate section
refs, review queue section refs, needs/absence section refs, relay projection
refs, and public-alpha reassess refs.

Required boundary fields remain false:

- `accepted_truth_created`
- `reviewed_index_mutated`
- `public_index_mutated`

The plan is a projection plan, not a mutation or deployment plan.
