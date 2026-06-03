# Surface Kernel

The Surface Kernel sits beside the Resolution Run Kernel. It chooses how a
canonical view model should be represented without changing what the route or
entity means.

Flow:

```text
Request metadata
-> route resolution
-> canonical view-model reference
-> capability negotiation
-> renderer dispatch
-> cache key
-> surface projection
```

TSIS-00 defines the contract boundary only. A later TSIS implementation phase
should place the Surface Kernel under `runtime/surface/`:

- `kernel.py`
- `route_resolver.py`
- `capability_negotiator.py`
- `view_model_loader.py`
- `renderer_dispatch.py`
- `cache_key.py`
- `output_policy.py`
- `fallback.py`
- `renderers/`

## Responsibilities

When implemented, the Surface Kernel may:

- resolve a path to a canonical route family
- select a representation profile from route, host, query, and `Accept` hints
- dispatch to a governed renderer id
- build a cache key that includes route, entity, profile, skin, language, host,
  and policy posture
- emit boundary flags proving projection-only behavior

The Surface Kernel must not:

- query live sources
- mutate reviewed, master, or public indexes
- promote candidates
- decide policy
- hide required semantic state
- perform downloads, file fetches, OCR, extraction, execution, or model calls
- deploy or claim public launch readiness

## Route Identity

Representation negotiation is not route splitting. `/object/eu_123` remains the
same object route whether projected as text, JSON, old HTML, rich HTML, native
card JSON, or terminal output.
