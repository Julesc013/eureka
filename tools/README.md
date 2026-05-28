# Tools

`tools/` contains substantive implementation helpers for validators,
generators, auditors, reporters, migrations, release checks, and local
operators. `scripts/` keeps the stable command wrappers.

Use `scripts/` commands in docs and task prompts unless a tool implementation
is intentionally being developed or debugged.

Tooling must preserve current safety boundaries: no hidden deployment, no live
source fanout, no credentials, no public mutation, no full-discovery raw logs in
the repo, and no local instance state committed.
