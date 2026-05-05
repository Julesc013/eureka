# Safe Fallback And Rollback Model

Ranking is disabled by default. Current order fallback is mandatory. Runtime flag kill switch is required. Per-request ranking timeout is future required. If ranking fails, return unranked/current-order results. If explanation fails, disable ranking or return current order. There is no partial hidden suppression. No mutation rollback is required because no mutation is allowed. Hosted rollback returns to the previous search wrapper.
