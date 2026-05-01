# Result Card Alignment

Canonical schema: `contracts/api/search_result_card.v0.json`.

P53 keeps the result card as the public result unit. Cards carry title,
summary, record kind, lane, user cost, source, identity, evidence,
compatibility, actions, rights, risk, warnings, limitations, gaps, optional
parent/member/representation/temporal details, and optional match/rank
explanations.

Allowed v0 actions are inspection/read-oriented: inspect, preview, read, cite,
view source, view provenance, view absence report, compare, and export manifest
when safe.

Blocked or future-gated actions include download, install handoff, execute,
upload, live probe, mirror, package manager handoff, and emulator handoff.
