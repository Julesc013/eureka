# Public Search UX Model

`PUBLIC-SEARCH-UX-MODEL-00` defines canonical view-model packets for Eureka's
search-first public surface. It does not build the final public pages.

The selected contract authority root is:

```text
contracts/view/models/public_search
```

This extends the existing `contracts/view/models` authority and does not create
a duplicate `contracts/views` root.

## Model Shape

The canonical packet flow is:

```text
snapshot refresh examples
-> ResultCardViewModel
-> SearchPageViewModel
-> Object/Candidate/Need/Source/Evidence page view models
-> public_web/operator_workbench/api_json/classic_html/text projections
```

Result states are first-class:

- verified
- candidate
- near_miss
- known_need
- absence
- source_lead

Candidate-like states are always review-required and never accepted truth.

## Boundaries

The model is read-only. It does not deploy, publish, mutate indexes, call live
sources, download, extract, use model providers, or promote candidates.
