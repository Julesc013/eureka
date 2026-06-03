# Workbench Run Review Projection Spec

## Purpose

Workbench is the private/operator projection of the resolver spine. It may show
more actions than public surfaces, but it must not own a different truth model.

## Workbench Must Show

- ResolutionRuns
- WorkUnits
- RunEvents
- SourceObservations
- EvidenceCandidates
- SearchNeeds
- ReviewEvents
- ReviewedRecords
- IndexBuilds
- policy blocks
- absences
- fallback states

## Gate

Every public reviewed record can be traced through Workbench-visible evidence
and review state.

