# Public Alpha Deploy Dry-Run Gates

The dry-run gate passes only when:

- launch-candidate result is PASS
- deploy manifest exists and is non-mutating
- environment checklist passes
- smoke checklist passes
- rollback rehearsal passes
- manual approval remains required
- deployment is false
- public launch is false
- production and public launch readiness claims are false
- public mutation and live source fanout are false
- downloads, extraction, and model/provider calls are false

The dry-run gate does not replace the explicit launch task.
