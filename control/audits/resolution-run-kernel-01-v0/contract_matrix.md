# Contract Matrix

- `contracts/resolution/run/resolution_run.v0.json`: run packet and state.
- `contracts/resolution/run/run_event.v0.json`: append-only event record.
- `contracts/resolution/run/run_command.v0.json`: command bus packet.
- `contracts/resolution/run/run_lane_snapshot.v0.json`: projection-safe lane snapshot.
- `contracts/resolution/run/run_coverage_report.v0.json`: coverage and boundary report.

Resolution-run contracts define orchestration packets only. They do not define
source truth, evidence acceptance, reviewed records, public ranking, or
production readiness.
