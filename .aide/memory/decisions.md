# Eureka AIDE Decisions

- Import only portable AIDE Lite artifacts needed for Eureka operation; do not copy AIDE source queue/history.
- Do not copy AIDE source generated context, reports, route decisions, cache reports, local state, raw prompts, raw responses, provider keys, or source project memory.
- Generate Eureka's own snapshot, repo map, context packet, task packet, review packet, and evidence inside this repo.
- Keep Q22 as an AIDE import and token-reduction pilot only; no Eureka product feature changes are allowed.
- Use the Q21 command dry run for validation, but apply the import manually because the command's implementation would also copy pack roots outside Q22's allowed target scope.
