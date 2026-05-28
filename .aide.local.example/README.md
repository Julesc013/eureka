# AIDE Local State Example

`.aide.local.example/` shows the intended shape of machine-local AIDE runtime
state. It is safe to commit because it contains examples and documentation only.

Do not commit actual `.aide.local/` contents. The real `.aide.local/` directory
is gitignored and reserved for user-specific or machine-specific state such as
local preferences, provider key references, cache metadata, traces, local
ledgers, and temporary run artifacts.

Committed `.aide/` remains repo-operating metadata. Mutable local state,
secrets, raw prompts, raw responses, local traces, and cache blobs must stay out
of the committed repository.
