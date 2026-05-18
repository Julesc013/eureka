# Source Cache Record Schema

IA source-cache records contain provenance, observation kind, request policy,
endpoint class, summary hash, normalized summary, candidate fields, limitation
flags, TTL, and boundary flags.

Required invariants:

- `review_required` is true
- `accepted_truth` is false
- raw live response bodies are not committed
- evidence writes are false
- index mutation is false
- downloads are false
