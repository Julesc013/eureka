# Checked Scope Model

Checked scope records the bounded search area for a miss:

- checked indexes such as `public_index` and `local_index_only`
- checked source ids and source families
- checked capabilities
- checked index snapshot references
- `live_probes_attempted: false`
- `external_calls_performed: false`

Not-checked scope records sources, source families, capabilities, reasons, and
limitations outside the checked scope. Reasons include not implemented,
disabled by policy, approval gated, operator gated, and unknown.

