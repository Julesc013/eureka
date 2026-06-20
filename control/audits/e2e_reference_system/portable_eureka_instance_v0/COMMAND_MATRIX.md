# Command Matrix

| Command | Status | Mutation scope | Notes |
| --- | --- | --- | --- |
| `bootstrap` | implemented | explicit local instance | Initializes local instance, profile, demo run, Preview Index |
| `doctor` | implemented | none | Read-only diagnostics |
| `test` | implemented | instance eval artifacts | Delegates to autonomous oracle |
| `hunt` | implemented | instance run bundle | Synthetic mode only |
| `replay` | implemented | replay report only | Validates bundle hashes/event chain |
| `serve --mode exploration` | implemented | server lock/state during runtime | Loopback-only canonical router |
| `status` | implemented | none | Aggregates local-private state |

All commands report `provider/network calls: false` except loopback HTTP smoke, which is not a provider call.
