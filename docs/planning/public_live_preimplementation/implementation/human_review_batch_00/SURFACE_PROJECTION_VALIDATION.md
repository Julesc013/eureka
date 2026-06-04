# Surface Projection Validation

Task ID: `HUMAN-REVIEW-BATCH-00`

Review decisions and reviewed seed records project through:

```text
evals.hard_queries.human_reviews.batch_00.project_review_decision
evals.hard_queries.human_reviews.batch_00.project_reviewed_seed_record
runtime.surface.SurfaceKernel
runtime.surface.renderers
```

Focused tests verify:

```text
verified records remain verified
need decisions remain need
near_miss decisions remain near_miss
request_more_evidence decisions do not become verified
public posture strips operator-only actions
operator posture can retain review actions
JSON/text/html_basic/snapshot renderers preserve status and uncertainty
HTML output escapes unsafe text
snapshot output is deterministic
no test path calls source providers
no test path mutates reviewed/master/public indexes
```
