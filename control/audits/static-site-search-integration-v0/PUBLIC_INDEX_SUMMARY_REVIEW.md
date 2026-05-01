# Public Index Summary Review

P56 generates `site/dist/data/public_index_summary.json` from the P55 public
index artifacts under `data/public_index`.

Current summary:

- artifact root: `data/public_index`
- document count: 584
- source count: 15
- committed artifact refs: build manifest, source coverage, index stats,
  search documents, checksums
- contains live data: false
- contains private data: false
- contains executables: false

The static site exposes a summary, not the full search runtime. The generated
public index remains controlled fixture/recorded metadata only and does not
turn GitHub Pages into a dynamic backend.
