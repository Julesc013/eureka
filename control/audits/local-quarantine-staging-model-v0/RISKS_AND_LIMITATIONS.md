# Risks And Limitations

Main risks:

- private paths or credentials leaking into reports
- staged records being mistaken for accepted truth
- staged metadata accidentally entering public search
- raw caches or databases being copied into a private root
- staged data being exposed through relay or snapshots
- deletion/reset/export semantics being unclear

The model mitigates these by requiring local-private defaults, ignored roots,
validate-only report links, no search/master-index impact, and explicit future
delete/reset/export requirements.

This is still planning only. No staging behavior can be inferred from this
audit pack.
