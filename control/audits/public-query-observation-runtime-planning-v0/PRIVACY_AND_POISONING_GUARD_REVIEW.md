# Privacy And Poisoning Guard Review

P67 privacy and poisoning guard validates as contract-only; runtime guard wiring remains deferred but is required before any observation store.

Private data must be rejected or redacted before observation. High privacy risk and high poisoning risk observations are excluded from aggregation.
