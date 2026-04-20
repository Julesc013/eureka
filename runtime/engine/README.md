# Engine

`runtime/engine/` is the home for engine behavior and service interfaces.

Boundary notes:

- engine must not depend on `surfaces/*`
- engine owns runtime behavior, not surface presentation
- `sdk/` is reserved for a future narrow offline boundary and is intentionally empty

