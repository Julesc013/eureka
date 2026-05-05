# Result Cache Miss Ledger Search Need Relationship

Future flow: observation -> result cache candidate; observation + no/weak result -> miss ledger candidate; repeated miss ledger entries -> search need candidate; search needs -> probe queue candidates.
None of these steps mutate the master index in P86, and none are implemented by P86.
