# Side-Effect Boundary

Allowed side effects:

- Search Hunt state mutation
- Search Hunt command history append
- Search Hunt steering preference insert/deactivation

Forbidden side effects:

- WorkUnit creation
- source probes
- extraction
- external network access
- model/provider calls
- review mutation
- public/master index mutation
- deployment
