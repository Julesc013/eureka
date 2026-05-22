# Run Command Bus

`run_command.v0` records control commands. In this foundation, allowed commands
are dry-run operational controls:

- `start`
- `pause`
- `resume`
- `cancel`
- `project_lanes`
- `request_ia_metadata_dry_run`

Unsafe commands remain blocked:

- live source probes
- live IA metadata
- downloads
- extraction
- execution
- model/provider calls
- store mutation
- deployment
- reviewed-record promotion
