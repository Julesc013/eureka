# Gate Status

| Gate | Status | Reason |
|---|---|---|
| source/snapshot full discovery | blocked | rerun 03 failed with 22 historical queue-validator drift failures |
| public alpha | blocked | reviewed corpus/artifact readiness remains below threshold |
| `dev -> main` promotion | blocked | full discovery is not green and promotion review has not run |

The next step is a focused repair of historical operation validators so they accept completed or superseded historical task states without requiring the live queue to point backward.
