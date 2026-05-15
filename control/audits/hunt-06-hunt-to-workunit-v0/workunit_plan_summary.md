# WorkUnit Plan Summary

SearchNeeds now produce deterministic WorkUnit plans. Plans map SearchNeed kind to local-safe queued WorkUnits and policy-gated blocked WorkUnits.

Plan preview is read-only and does not persist queue records. Persistence requires the operator token through CLI or local POST routes.
