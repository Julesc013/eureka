# Architecture and System Model

The corpus favors a layered architecture: contracts own meaning, kernels own behavior, policies own permissions, stores own persistence, and surfaces own projection. Later TSIS notes add the missing representation/surface layer beside the resolution-run layer.

## Key synthesis

Settled architectural principles include one object/evidence/action/route language, many representations, no forked product logic, and pure renderers that must not query sources, mutate indexes, decide policy, or invent facts.

## Unresolved questions

Open design questions include the exact packet/view-model contracts, the boundary between ResolutionRunKernel and SurfaceKernel, and whether Track A/TSIS should precede Workbench-visible run work.

## Contradictions or drift

One contradiction is directory drift: one loose TSIS note explored large new roots, while the later note rejects new top-level roots and places TSIS inside existing roots. The latest advisory answer favors stable roots plus contracts/runtime/surfaces.

## Implications for future work

The next architecture tasks should add doctrine and contracts before runtime behavior: semantic contracts, representation profiles, view model contracts, capability negotiation, renderer contracts, and golden cross-render tests.

## Representative source block references

SB-0069, SB-0075, SB-0080, SB-0109, SB-0113, SB-0120, SB-0125, SB-0136, SB-0155, SB-0162, SB-0166, SB-0173
