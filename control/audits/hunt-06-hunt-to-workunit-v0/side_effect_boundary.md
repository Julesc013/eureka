# Side Effect Boundary

Allowed:

- local WorkUnit queue record creation
- local payload references from WorkUnit to SearchNeed, hunt, and exhaustion report

Forbidden:

- WorkUnit execution
- source probe execution
- extraction
- model/provider calls
- review decision mutation
- public/master index mutation
- deployment
