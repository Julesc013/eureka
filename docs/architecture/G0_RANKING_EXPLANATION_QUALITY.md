# G0 Ranking, Explanation, And Quality

G0 defines deterministic fixture/local-eval scoring for Eureka result records. It
orders and explains candidates only inside governed packets. A score is not
evidence, an explanation is not evidence, and a high score cannot create a
reviewed record.

Inputs may include reviewed-local result fixtures, local candidates, IA metadata
candidates, source-cache hits, F0 member manifests, SCOUT discovery candidates,
DOMAIN query hints, and SYN expected-behavior cases. Each score must include a
visible decomposition, uncertainty, limitations, and blocked-action reasons.

G0 does not perform live source calls, source probes, downloads, extraction,
provider calls, public fanout, index mutation, accepted evidence creation, or
accepted identity merges. Public ranking behavior remains a future governed
task.
