# Workbench Operator Model

Workbench is private Mission Control for the resolver spine. It can expose
operator-only actions, but it cannot create a separate truth model.

## Operator Responsibilities

- inspect ResolutionRuns and WorkUnits
- inspect SourceObservations and EvidenceCandidates
- review candidates and needs
- promote, reject, supersede, or request more evidence through the review ledger
- rebuild indexes after reviewed changes
- inspect policy blocks, absences, and fallback failures

## Public Boundary

Workbench state may explain public records, but Workbench actions are not
public.

