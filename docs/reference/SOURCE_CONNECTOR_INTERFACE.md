# Source Connector Interface

The source connector interface is the reusable contract layer between Source OS
source records and future connector runtimes.

It defines possible operations, required source-policy references, fixture
replay support, live-probe envelope support, and candidate output shapes. It
does not grant permission to call a source, write source cache state, accept
evidence, mutate public/master indexes, or claim rights, malware, or
installability facts.

Current H0-BUNDLE-02 behavior is fixture-only and dry-run only. Future H1/H2
connectors must pass through source records, source policy gates, connector
capability declarations, fixture replay, policy evaluation, and review gates.

Validation:

```text
python scripts/validate_connector_interface_foundation.py
```
