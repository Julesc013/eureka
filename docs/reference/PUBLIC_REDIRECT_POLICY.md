# Public Redirect Policy

Redirect policy is registered in
`control/inventory/publication/redirects.json`.

v0 starts with an empty redirect list:

```json
{
  "redirects": []
}
```

Static hosts may not support server-side redirects. Future route moves should
prefer:

- keeping the old route during a deprecation period
- adding a static redirect or explanation page when the host supports it
- publishing canonical links when appropriate
- recording the change in the page registry

Route removals require deprecation first unless the route was never
implemented. Provider-specific redirect files are not part of this milestone.

