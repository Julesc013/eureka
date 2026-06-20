# Degraded Mode Matrix

| State | Behavior |
| --- | --- |
| missing instance | `bootstrap_required`, exact bootstrap command |
| invalid instance | `instance_validation_failed`, no auto-repair |
| migration required | reported, no silent migration |
| missing Preview Index | `/explore` remains available with degraded/empty state |
| invalid Preview Index | search blocked for that index |
| no run bundles | status recommends `hunt` |
| corrupt run bundle | counted as corrupt |
| invalid oracle registry | `test` blocked |
| port in use | local error, no public interface fallback |
| public/live mode requested | fail closed |
