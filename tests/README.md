# Root Tests

`tests/` is reserved for verification that crosses component boundaries.

- `integration/`: cross-component checks across contracts, runtime, and surfaces
- `end_to_end/`: higher-level product workflow checks once real behavior exists

Component-local tests stay with their owning component and should not be duplicated here.

