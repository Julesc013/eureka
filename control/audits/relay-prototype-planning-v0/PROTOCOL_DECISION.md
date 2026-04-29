# Protocol Decision

Decision: the first future prototype should be local static HTTP only.

| Candidate | Status | Value | Risks | First? | Prerequisites |
| --- | --- | --- | --- | --- | --- |
| local static HTTP | future candidate | Simple read-only projection of public data and snapshots | Any listener needs bind, path, and log controls | Yes | explicit approval, localhost-only bind, allowlisted roots, path traversal tests |
| local text HTTP | future later | Simple text views for old clients | Still opens a listener | Not first separately | local static HTTP plan and text projection tests |
| local file tree HTTP | future later | Manifest/checksum browsing | Directory escape risk | Not first separately | allowlisted file-tree roots and traversal tests |
| read-only FTP-style mirror | future deferred | Useful for older clients | Insecure transport and credential confusion | No | protocol threat model and public-only root policy |
| WebDAV read-only | future deferred | File-manager integration | Complex write semantics and auth expectations | No | threat model and write-blocking proof |
| SMB read-only | future deferred | LAN file sharing | Permission, platform, and credential risks | No | platform review and LAN security policy |
| AFP read-only | future deferred | Legacy Mac access | Legacy protocol and operator complexity | No | lab host and protocol-specific review |
| NFS read-only | future deferred | Unix-style export | Export-root and LAN trust risks | No | export-root threat model |
| Gopher experimental | future research | Very old-client friendly text/file index | Niche protocol and implementation risk | No | separate research approval |
| native sidecar | future deferred | Tight native client integration | Private data and lifecycle risks | No | native client implementation and privacy policy review |
| snapshot mount | future deferred | Offline snapshot browsing | Mount permissions and authenticity claims | No | snapshot consumer implementation and signature policy |

Local static HTTP is only a planning decision here. No server, socket, route,
or protocol code is added.
