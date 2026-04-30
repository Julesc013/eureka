# Current Static Artifact

Active artifact path: `site/dist`

Source root: `site`

Generator command: `python site/build.py`

Current public data path: `site/dist/data`

Current static surfaces:

- pages: `site/dist/*.html`
- data: `site/dist/data/*.json`
- lite HTML: `site/dist/lite/`
- plain text: `site/dist/text/`
- file-tree surface: `site/dist/files/`
- resolver demos: `site/dist/demo/`
- assets: `site/dist/assets/`
- Pages marker: `site/dist/.nojekyll`

Snapshot reference status: `snapshots/examples/static_snapshot_v0/` remains a
repo-local static snapshot example that consumes generated `site/dist/data`
inputs. It is not a production signed snapshot, public download, installer, or
snapshot reader runtime.

Repository shape:

- `public_site/` exists: no
- `third_party/` exists: no
- `external/` exists: yes
- GitHub Pages workflow uploads `site/dist`: yes

The artifact is generated and owned by repository tooling. Manual edits to
`site/dist` are not allowed; source inputs should be edited and the generator
rerun instead.
