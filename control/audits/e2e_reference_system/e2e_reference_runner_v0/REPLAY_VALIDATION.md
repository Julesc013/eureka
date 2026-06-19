# Replay Validation

Replay validates:

- manifest presence and shape;
- bundle file hashes;
- events JSONL;
- monotonic sequence;
- payload hashes;
- previous-event hash links;
- event hashes;
- reconstructed terminal state.

Strict replay fails on unknown event types. Replay never executes provider code
or writes review/index state.
