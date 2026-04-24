# Data Model

Eureka should keep a small typed core data model and avoid hiding semantics in
unstructured blobs or source-specific ad hoc shapes.

## Core Entity Families

The long-term canonical core will likely need typed records such as:

- `source`
- `source_record`
- `object`
- `representation`
- `state`
- `agent`
- `claim`
- `evidence`
- `identifier`
- `access_path`
- `edge`
- `blob`
- `resolution_run`
- `resolution_memory`
- `invalidation_dependency`

These are conceptual record families. Current bootstrap slices only implement
bounded subsets of the overall future model.

## Data Model Principles

### Typed over implicit

If a concept crosses component boundaries or matters to user trust, it should
eventually have an explicit type rather than surviving only as incidental
implementation detail.

### Preserve disagreement

Conflicting claims should remain explicit rather than collapsing into a hidden
"best guess" too early.

### Separate identity from access

The same object may have many states, many representations, and many access
paths. Those should not be flattened into one opaque record.

### Separate strategy from truth

User strategy and host context may affect ranking and action planning, but they
must not rewrite source-backed facts.

## Access Paths and Trust Dimensions

Eureka should avoid a single early `trust_score` field that hides disagreement.
Access and trust should instead remain decomposed into dimensions such as:

- source authority
- integrity status
- rights status
- safety status
- provenance quality
- compatibility confidence
- extraction confidence

## Bootstrap Note

The current `resolved_resource_id` seam is useful and should continue to be
propagated. It is still a bootstrap deterministic seam rather than Eureka's
final global identity system.
