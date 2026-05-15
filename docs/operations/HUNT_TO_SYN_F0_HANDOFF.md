# HUNT To SYN/F0 Handoff

Recommended order:

1. SYN-00 - Synthetic Query Foundry planning over Local Appliance.
2. SYN-01 - Synthetic query taxonomy and contracts.
3. SYN-02 - Synthetic fixed query datasets and eval split.
4. F0-00 - Refresh F0 after Local Appliance and HUNT/SYN.

SYN should create query pressure, SearchNeed seeds, WorkUnit seeds, and eval
structure. It must not create fake evidence or verified records.

F0 can resume if the operator explicitly prioritizes extraction, but extraction
tasks must use WorkUnits where applicable and outputs must flow through source
observation, evidence, review, and index gates.
