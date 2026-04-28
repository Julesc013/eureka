# Live Backend Error Envelope

Future live backend handoff routes under `/api/v1/` should use a consistent
error envelope. This document records the expected shape before any public
backend exists. It is not a production API.

## Shape

```json
{
  "ok": false,
  "error": {
    "code": "live_backend_unavailable",
    "message": "Live backend is not available for this static deployment.",
    "status": 503,
    "retryable": false,
    "capability_required": "live_backend",
    "docs": "docs/reference/LIVE_BACKEND_HANDOFF_CONTRACT.md"
  }
}
```

## Required Codes

- `live_backend_unavailable`
- `capability_disabled`
- `live_probes_disabled`
- `route_not_public_alpha_safe`
- `rate_limited`
- `source_disabled`
- `source_timeout`
- `bad_request`
- `not_found`
- `internal_error`

## Interpretation

The envelope is a contract draft, not implemented backend behavior. Static
clients should continue to work when every live capability is absent.
