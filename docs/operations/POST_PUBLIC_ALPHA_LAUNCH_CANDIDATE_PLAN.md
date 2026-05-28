# Post Public Alpha Launch Candidate Plan

After `PUBLIC-ALPHA-LAUNCH-CANDIDATE-00` passes:

1. Run `PUBLIC-ALPHA-DEPLOY-DRY-RUN-00`.
2. Rehearse environment, packaging, smoke checks, security headers, and
   rollback.
3. Require manual approval before any launch task.
4. Only then consider `PUBLIC-ALPHA-LAUNCH-00`.

Demand signals and source request queues remain separate follow-up work:

- `PUBLIC-DEMAND-SIGNAL-00`
- `PUBLIC-SOURCE-REQUEST-QUEUE-00`

No public launch, production claim, live source fanout, public mutation,
downloads, extraction, or model/provider calls are authorized by this plan.
