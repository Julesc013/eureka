# Risks And Limitations

Known limitations:

- The aggregator delegates to existing validators and does not replace them.
- It validates manifests, checksums, safety posture, and prohibited content; it
  does not prove source truth.
- It does not create a durable import report format beyond its JSON output.
- It does not stage or quarantine pack data.
- It does not compare conflicting claims across packs.
- It does not submit anything to the master-index review queue.
- It does not perform rights or malware review.

Unknown or unsupported roots return `unknown_type` rather than being scanned
recursively.

