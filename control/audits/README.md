# Audit Packs

`control/audits/` holds repo-governance audit packs. These packs are evidence
and planning artifacts, not product runtime behavior and not public product
claims.

An audit pack should usually be grouped under a dated directory and should include:

- a baseline record
- commands run or intended for final verification
- structure, content, behavior, and test-gap audits
- structured findings using `control/audits/schemas/finding.schema.json`
- backlog and next-milestone recommendations
- explicit non-goals and deferred items

Audit findings should map to future-work labels and should avoid vague
"improve everything" recommendations. If a finding depends on external search
quality, mark the external observation as pending manual evidence rather than
fabricating a baseline.

Audit packs must not be used to claim production readiness. Public-alpha
material remains supervised-demo evidence only until a separate accepted
hosting decision exists.

Current packs:

- `2026-04-25-comprehensive-test-eval-audit/`: repo-wide structure, content,
  behavior, test-gap, and backlog audit.
- `search-usefulness-delta-v0/`: stable usefulness-delta report comparing
  current Search Usefulness Audit output to a historical reported aggregate
  baseline after the old-platform/member-discovery implementation sequence.
- `search-usefulness-delta-v1/`: stable usefulness-delta report comparing
  post-source-expansion audit output to the v0 delta aggregate baseline and
  recording archive-eval movement toward source-backed but still unsatisfied
  hard tasks.
- `hard-eval-satisfaction-v0/`: stable archive-resolution hard-eval report
  recording the move from `capability_gap=1, not_satisfied=5` to
  `capability_gap=1, partial=5` without weakening hard tasks or fabricating
  source evidence.
- `old-platform-result-refinement-v0/`: stable archive-resolution result-shape
  report recording the move to `capability_gap=1, partial=4, satisfied=1`
  after deterministic primary-candidate, expected-lane, and bad-result checks
  were added without weakening hard tasks or changing retrieval behavior.
- `more-source-coverage-expansion-v1/`: stable targeted source-expansion
  report recording the move to `capability_gap=1, satisfied=5` for current
  archive-resolution hard evals after tiny Firefox XP, blue FTP-client XP,
  Windows 98 registry repair, and Windows 7 utility/app fixture evidence was
  added without live source behavior, real binaries, or external baseline
  claims.
