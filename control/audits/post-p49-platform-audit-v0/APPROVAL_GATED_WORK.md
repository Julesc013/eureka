# Approval Gated Work

| Work | Classification | Notes |
|---|---|---|
| Live connectors | `approval_gated` | IA metadata first only after approval pack. |
| Local staging runtime | `approval_gated` | Current staging work is contracts/plans/inspection only. |
| Native implementation | `approval_gated` | WinForms skeleton requires explicit approval. |
| Relay implementation | `approval_gated` | First candidate is local static HTTP only after approval. |
| AI runtime | `approval_gated` | No provider loading, model calls, credentials, telemetry, or public-search AI without approval. |
| Downloads/installers/uploads/accounts | `approval_gated` | Explicitly outside current platform posture. |
| Hosted contribution intake | `approval_gated` | Needs roles, moderation, security, privacy, and review policy. |
