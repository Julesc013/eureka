# Public Search Result Card

Public result cards are governed view-model records rendered by the no-JS UX MVP.

Each card carries:

- a stable title and route (`href` plus legacy `url`);
- a status and visible text badge;
- domain/source labels;
- review and accepted-truth flags;
- evidence and limitation summaries;
- an action posture that blocks downloads, file fetches, OCR, extraction, public mutation, and live fanout.

Cards must not use color alone to distinguish states. Candidate and near-miss cards show `review required`; limited reviewed metadata/source-lead cards show `limited claim`; all non-download states show no-download/no-safety/no-rights labels.
