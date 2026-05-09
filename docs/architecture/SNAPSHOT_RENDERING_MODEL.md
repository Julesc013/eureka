# Snapshot Rendering Model

Snapshot renderers project the same manifest into several offline forms:

- `text`: plain text summaries for search/object/source/need/action records.
- `lite_html`: static HTML fragments with escaped content and no external assets.
- `file_tree`: README/index-style tree views.
- `json_manifest`: deterministic manifest output.

All renderers preserve the required posture fields and limitations. Renderers must not fetch resources, open sockets, host content, write `site/dist`, or activate public routes.
