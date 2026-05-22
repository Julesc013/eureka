# Workbench Review Promote

Workbench review/promote is the local operator projection for turning candidate material into a reviewed local projection through an explicit gate. It is not automatic ranking, source acquisition, or master truth creation.

The flow is:

1. A resolution run or result lane exposes a candidate.
2. The operator projection creates a review item.
3. A review decision is proposed and, when an operator token is present, recorded in local/temp scope.
4. Accepted local review decisions create a promotion preview.
5. The reviewed-index refresh proof runs only in an explicit temp instance for this foundation task.

Public and native read-only projections may inspect summaries, but they cannot submit review decisions, create previews, or refresh an index.

## Boundaries

- Promotion preview is not promotion.
- Reviewed local index refresh is not master or public index truth.
- No automatic candidate acceptance is enabled.
- No fake evidence or fake verified record is created.
- No downloads, extraction, model/provider calls, deployment, or production/public launch claim are part of this task.

The next gate is `LOCAL-APPLY-GATE-01`, which must add backup, audit, explicit operator-instance selection, and rollback before any real operator instance apply path exists.
