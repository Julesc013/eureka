# Localhost Relay Model

D-BUNDLE-02 adds a compatibility bridge over explicit fixture snapshots. The
relay consumes snapshot records and renders local read-only projections for old
browsers, terminals, and future native fixture clients.

The relay is not a hidden backend. It does not query sources, sync state,
authenticate accounts, accept uploads, download artifacts, execute actions,
mutate search, or mutate indexes.

The server factory is inert on import. A server can start only when a caller
explicitly asks the CLI to `--serve`, and the bind host must be `127.0.0.1` or
`localhost`.

