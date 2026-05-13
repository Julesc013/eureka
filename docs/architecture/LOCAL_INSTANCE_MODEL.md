# Local Instance Model

LOCAL-01 introduces an explicit local appliance instance root. The root is the only place where bootstrap commands may write local appliance state, and it must be passed with `--instance`.

## Model

The local instance is a disposable filesystem tree owned by the operator. It is portable, inspectable, and safe to delete. Eureka must not infer a hidden state root from the home directory, `.cache`, `.local`, `.aide.local`, or the repo root.

The instance has these layers:

- `config/` stores instance identity and local mode flags.
- `db/` stores file-backed SQLite stores for source cache, evidence ledger, review queue, and reviewed public index.
- `logs/` stores local logs only.
- `run/` stores process/status files only.
- `tmp/`, `exports/`, and `imports/` are explicit local work areas and are not committed.

LOCAL-01 initializes empty store schemas through the existing R0 runtime store APIs. It does not add product runtime behavior and does not alter runtime code.

## Boundaries

- No HTTP server exists in LOCAL-01.
- No HTML workbench exists in LOCAL-01.
- No WorkUnit runtime exists in LOCAL-01.
- LAN remains disabled.
- Deployment is not performed.
- Production readiness is not claimed.
- Public launch readiness is not claimed.

## Next

LOCAL-02 adds governed instance configuration and migration guards before any service or workbench work begins.
