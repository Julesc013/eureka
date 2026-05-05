# Extraction Pipeline Plan

Future flow:

1. Receive approved extraction request.
2. Validate request schema.
3. Check sandbox, resource, privacy, and executable policies.
4. Create isolated temporary workspace.
5. Detect container type.
6. Run Tier 0 metadata summary.
7. Optionally run Tier 1 member listing.
8. Optionally run Tier 2 manifest extraction.
9. Optionally run Tier 3 selective text summary.
10. Do not run Tier 4 or Tier 5 until separate sandbox approval.
11. Build extraction result summary.
12. Build candidate effects only.
13. Clean workspace.
14. Emit report.
15. Stop before mutation.

P105 implements none of this flow.

