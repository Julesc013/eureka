# Security And Abuse Review

Future ranking runtime requires query length cap, result count cap, ranking timeout cap, no path/URL/source selector parameters, no local file access, no live source calls, no model calls, no ranking-store writes, no telemetry, adversarial query handling, and an operator kill switch. Poisoning risk remains a query-intelligence issue and must not become a ranking input.
