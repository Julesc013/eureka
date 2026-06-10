# Discovery Summary

| Field | Value |
|---|---|
| run id | `source_snapshot_full_discovery_rerun_03` |
| command | `python -m unittest discover -s tests -t .` |
| branch | `dev` |
| head | `2549af51a4f472e6fae9a825af2275b27f8556b8` |
| status | `fail` |
| exit code | `1` |
| tests run | `5620` |
| failures | `22` |
| errors | `0` |
| duration seconds | `2902.728351` |
| working tree clean at run start | `true` |

The failures are concentrated in historical operation validators whose expectations still require old HUNT, LOCAL, or promotion queue states.
