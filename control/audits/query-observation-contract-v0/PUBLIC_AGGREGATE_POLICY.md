# Public Aggregate Policy

Public aggregate learning is allowed only after privacy filtering. Individual
query observations are not public by default.

P59 allows `public_aggregate_allowed: true` only for public-safe observations
that retain no raw query and carry no sensitive/private data flags. A future
privacy and poisoning guard must define how aggregates are counted, thresholded,
retained, deleted, and published.
