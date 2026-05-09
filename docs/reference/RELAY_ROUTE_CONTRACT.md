# Relay Route Contract

`contracts/relay/relay_route.v0.json` describes read-only GET routes over a
fixture snapshot.

Allowed current routes are `/status`, `/snapshot`, `/search`, `/object/{id}`,
`/source/{id}`, `/need/{id}`, `/action/{id}`, `/manifest`, `/files`,
`/text/search`, `/text/object/{id}`, and `/terminal`.

Routes expose text, lite HTML, file-tree, JSON manifest, terminal, or native
fixture JSON projections. They do not accept writes, uploads, downloads, action
execution, live source fanout, public search mutation, or index mutation.

