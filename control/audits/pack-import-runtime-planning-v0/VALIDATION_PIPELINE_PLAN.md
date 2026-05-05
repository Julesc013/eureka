# Validation Pipeline Plan

Future phases:

1. Locate approved pack path or repo example.
2. Verify path is inside approved root.
3. Check manifest exists.
4. Check schema version and pack kind.
5. Check checksums/fixity.
6. Check forbidden fields, private paths, secrets, credentials.
7. Check payload policy.
8. Run pack-kind validator.
9. Run pack-set validator if applicable.
10. Build validate-only import report.
11. Build diff/candidate effect report.
12. Stop before mutation unless later explicit promotion runtime is approved.
