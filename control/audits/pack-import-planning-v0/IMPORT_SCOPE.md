# Import Scope

In a future milestone, import means that a user explicitly selects a validated
source pack, evidence pack, index pack, or contribution pack and asks Eureka to
inspect it through a governed local pipeline.

Future import may:

- identify the selected pack type
- validate schema and manifest fields
- validate `CHECKSUMS.SHA256`
- parse declared JSON and JSONL files
- classify privacy, rights, and risk posture
- preserve pack ID, pack version, checksum, and validation report as provenance
- stage pack metadata into a controlled local quarantine or staging area
- make staged records available for inspection
- prepare records for a later explicit local-index-candidate mode

Import does not mean:

- scanning arbitrary directories
- trusting user data as truth
- merging into the canonical source registry
- changing hosted search or static public search
- uploading to a hosted/master index
- accepting a contribution automatically
- live fetching URLs or source locators
- loading executable plugins
- importing raw SQLite databases or cache dumps
- downloading, installing, restoring, or executing anything

P39 does not implement any import behavior. It records the future boundary so a
later implementation can be checked against it.

