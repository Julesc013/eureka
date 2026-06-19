# Mode Matrix

| Mode | Implemented | Default | Provider/network | Truth/index posture |
| --- | --- | --- | --- | --- |
| synthetic | yes | enabled | false | no truth or index mutation |
| replay | yes | enabled for bundles | false | validates only |
| live-shadow | represented | disabled | false | policy blocked |

`dry_run` compatibility maps to synthetic mode with the IA dry-run scheduler
adapter.
