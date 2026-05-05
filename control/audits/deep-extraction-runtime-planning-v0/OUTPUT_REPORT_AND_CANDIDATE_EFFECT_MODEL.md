# Output Report And Candidate Effect Model

Future report fields:

- request identity
- target identity
- extraction tiers attempted
- extraction tiers skipped
- container summary
- member summaries
- manifest summaries
- text summaries
- OCR/transcription summaries
- safety decisions
- privacy decisions
- rights/risk labels
- warnings/errors
- candidate effects:
  - source-cache candidate effect
  - evidence-ledger candidate effect
  - candidate-index candidate effect
  - public-index candidate effect
- mutation summary: all false

Rules:

- Candidate effects are not writes.
- Reports are not accepted truth.
- Raw payloads are excluded.
- Raw text dumps are excluded.
- Rights clearance and malware safety are never claimed.

