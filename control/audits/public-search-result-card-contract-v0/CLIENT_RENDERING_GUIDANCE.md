# Client Rendering Guidance

The result card is the public unit of search display. Future consumers may
render it differently, but they should preserve the same semantic order:

1. title and subtitle
2. result lane and user-cost
3. source identity and coverage
4. why it matched or ranked
5. compatibility and evidence summaries
6. allowed, blocked, and future-gated actions
7. rights, risk, warnings, limitations, and gaps

## Standard Web

The future web surface may group cards by lane and expose richer evidence and
compatibility panels. It must not hide blocked download, install, execution, or
upload status when such actions are relevant.

## API Clients

JSON clients should read `contract_id`, `schema_version`, `result_lane`,
`user_cost`, `source`, `identity`, `actions`, `rights`, `risk`, `warnings`, and
`limitations` before using optional rich fields.

## Lite HTML And Text

Lite/text clients should degrade to a compact card:

- title
- lane
- user-cost label and score
- source id and source family
- public target ref
- first evidence summary
- allowed read/inspect action, if present
- blocked unsafe actions
- warnings and limitations

They should not require JavaScript or rich debug fields.

## Native, Relay, And Snapshot Consumers

Native, relay, and snapshot consumers may read the same card shape as a future
input contract. This milestone does not implement native clients, relay
runtime, snapshot reader runtime, or local cache behavior.

Snapshot consumers should preserve cards as static metadata and should not
interpret blocked/future-gated actions as permissions.
