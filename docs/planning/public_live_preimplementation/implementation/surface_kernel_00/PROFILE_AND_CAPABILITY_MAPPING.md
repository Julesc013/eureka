# Profile And Capability Mapping

Supported profile IDs:

```text
json_v0
text_v0
html_basic_v0
snapshot_v0
```

Aliases:

| Existing / Request Hint | SurfaceKernel Profile |
|---|---|
| `api_client` | `json_v0` |
| `json` | `json_v0` |
| `text` | `text_v0` |
| `standard_web` | `html_basic_v0` |
| `lite_html` | `html_basic_v0` |
| `html` | `html_basic_v0` |
| `snapshot` | `snapshot_v0` |
| `native_client` | `json_v0` |

Negotiation order:

```text
explicit requested profile
Accept header hint
safe public default
```

Unsupported profile requests fall back to:

```text
html_basic_v0
```

and mark `fallback_used=true`.
