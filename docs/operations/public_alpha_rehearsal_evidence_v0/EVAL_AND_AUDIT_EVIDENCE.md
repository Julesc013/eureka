# Eval And Audit Evidence

- archive eval task count: 6
- archive eval status counts: `{"satisfied": 6}`
- search usefulness query count: 64
- search usefulness status counts: `{"capability_gap": 9, "covered": 5, "partial": 22, "source_gap": 26, "unknown": 2}`
- external pending counts: `{"google": 64, "internet_archive_full_text": 64, "internet_archive_metadata": 64}`

Archive hard evals are internally satisfied against the current fixture-backed corpus. This is regression evidence, not production relevance proof.

Search Usefulness Audit still records source gaps, capability gaps, compatibility-evidence gaps, planner gaps, representation gaps, and member-access gaps.

Python oracle golden checks and hardening tests remain separate verification lanes.

