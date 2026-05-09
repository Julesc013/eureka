# Relay No Public Binding Report

D-BUNDLE-02 denies public binding. The server factory validates bind hosts and
allows only `127.0.0.1` and `localhost` in the current policy.

The CLI does not start a server by default. A server starts only with explicit
`--serve`, and public bind hosts are refused before server creation.

