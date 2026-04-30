# Pack Result Model

Each pack result records pack root, pack type, optional pack ID/version,
validator ID and command, validation/checksum/schema/privacy/rights/risk
statuses, issue records, record counts, limitations, and recommended next
action.

Supported result types are source packs, evidence packs, index packs,
contribution packs, master-index review queues, typed AI output bundles, and
unknown inputs.

Unknown inputs are represented as validation failures or unsupported pack type
outcomes. They are not scanned recursively or imported.
