# Public Alpha Launch Gates

The launch path is deliberately staged:

1. Read-only public alpha foundation.
2. Hosting readiness.
3. Closeout with external full discovery.
4. Main promotion.
5. Launch-candidate gate.
6. Deploy dry run.
7. Explicit launch task with manual approval.

`launch_candidate_ready: true` means the baseline can move to a dry run. It does
not mean the service is deployed, production-ready, or public-launch-ready.

Hard blockers include:

- deployment already performed by a non-deploy task
- production or public launch readiness claimed
- public mutation enabled
- public live source fanout enabled
- downloads, extraction, or model/provider calls enabled
- missing or failing external full discovery
- missing rollback, security, privacy, or abuse documentation
