# Child Task Matrix

| Order | Task | Status | Purpose | Next |
| ---: | --- | --- | --- | --- |
| 1 | `E2E-REFERENCE-CONTRACT-00` | planned | Consolidate semantic contracts | `E2E-REFERENCE-RUNNER-00` |
| 2 | `E2E-REFERENCE-RUNNER-00` | planned | Build shared replay/synthetic/live-shadow runner | `E2E-PREVIEW-INDEX-00` |
| 3 | `E2E-PREVIEW-INDEX-00` | planned | Build status-aware preview projection | `E2E-HUNT-EXPLORATION-UI-00` |
| 4 | `E2E-HUNT-EXPLORATION-UI-00` | planned | Build private/local exploration Workbench | `SYNTHETIC-TRUTH-PATH-E2E-00` |
| 5 | `SYNTHETIC-TRUTH-PATH-E2E-00` | planned | Prove isolated synthetic truth mechanics | `AUTONOMOUS-EVAL-ORACLE-00` |
| 6 | `AUTONOMOUS-EVAL-ORACLE-00` | planned | Build E2E evaluation oracle | `PORTABLE-EUREKA-INSTANCE-00` |
| 7 | `PORTABLE-EUREKA-INSTANCE-00` | planned | Build coherent local command surface | `HUMAN-END-TO-END-ACCEPTANCE-00` |
| 8 | `HUMAN-END-TO-END-ACCEPTANCE-00` | planned | Run human product calibration | separately gated next tasks |

Each packet references `E2E-REFERENCE-SYSTEM-TRACK-00` and repeats the hard
gates because native AIDE inheritance is not currently available.

