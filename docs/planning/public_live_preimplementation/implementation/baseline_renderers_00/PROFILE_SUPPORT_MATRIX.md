# Profile Support Matrix

Task ID: `BASELINE-RENDERERS-00`

| Profile | Runtime Renderer | Media Type | Content Shape | Status |
|---|---|---|---|---|
| `json_v0` | `render_json_v0` | `application/json` | structured dict | supported |
| `text_v0` | `render_text_v0` | `text/plain; charset=utf-8` | plain text string | supported |
| `html_basic_v0` | `render_html_basic_v0` | `text/html; charset=utf-8` | escaped HTML string | supported |
| `snapshot_v0` | `render_snapshot_v0` | `application/vnd.eureka.surface.snapshot+json` | deterministic dict | supported |

## Supported Input Cases

Focused tests cover:

```text
public resolution-run fallback candidate
public resolution-run fallback need
public resolution-run policy_blocked fallback
public resolution-run unavailable fallback
unknown status fallback
unsupported profile fallback
private Workbench-shaped projection
candidate route with unsafe external/user text
```

## Deferments

Full gateway route adapter rewiring remains deferred because dependency law still makes SurfaceKernel a boundary that wraps gateway-shaped output rather than a dependency of gateway modules.
