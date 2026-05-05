# Connector Runtime Integration Status

Classification: `approval_gated`.

| Connector | Approval pack | Runtime planning | Runtime implementation | Public search integration | Live calls enabled | Writes enabled | Blocker |
| --- | --- | --- | --- | --- | --- | --- | --- |
| `internet_archive_metadata` | present, approval pending | present | absent | no | false | false | approval and runtime gate |
| `wayback_cdx_memento` | present, approval pending | present | absent | no | false | false | approval and runtime gate |
| `github_releases` | present, approval pending | present | absent | no | false | false | approval and runtime gate |
| `pypi_metadata` | present, approval pending | present | absent | no | false | false | approval and runtime gate |
| `npm_metadata` | present, approval pending | present | absent | no | false | false | approval and runtime gate |
| `software_heritage` | present, approval pending | present | absent | no | false | false | approval and runtime gate |

Recorded fixture connectors under `runtime/connectors/*_recorded` are local fixture
sources for existing search/index behavior. They are not live external connector
runtimes and do not authorize public-search live fanout.

