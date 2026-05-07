# Upstream AIDE Lite Impact

## Candidate Upstream Learnings

- Imported AIDE Lite packs need a first-class concept of target-specific golden
  tasks layered on top of generic pack selftests.
- Generated task packets should make target product boundaries explicit when a
  target repo exposes them through AGENTS or memory.
- Selftest fixtures need enough target-like metadata to keep target-specific
  golden tasks deterministic without copying product code.

## Not Upstreamed Here

This task does not mutate the AIDE source repo. It records target-repo learnings
for later upstream synchronization only.
