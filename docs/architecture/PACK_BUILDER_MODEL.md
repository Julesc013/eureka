# Pack Builder Model

The Pack Builder model is a local drafting layer between reviewed local records
and future pack export work. It reads explicit records from the source cache,
evidence ledger, candidate store, review queue, promotion dry-runs, reviewed
public record proposals, and similar committed fixtures, then produces a pack
draft envelope.

## Request Model

A pack builder request records the requested pack type, input refs, input
summary, requested output path, review gates, truth boundary, product boundary,
no-goals, and notes. It does not grant import or submission authority.

## Draft Model

A pack draft includes `pack_draft_id`, `pack_type`, `pack_status`, input refs,
public-safe input summaries, pack contents, source/evidence/candidate/review
summaries, limitations, blocked items, review gates, validation summary, truth
boundary, product boundary, no-goals, and notes.

`index_pack_preview` remains preview-only. It does not rebuild the public index
or write index artifacts.

## Result Model

The pack builder result wraps a request summary, pack draft, validation
outcome, runtime scope, truth boundary, product boundary, and notes. It is an
audit/report envelope, not imported state.

## Boundaries

The model deliberately does not fetch sources, call APIs, call models, perform
observations, import packs, submit packs, publish packs, accept packs, accept
evidence, accept candidates, or mutate public or master indexes.
