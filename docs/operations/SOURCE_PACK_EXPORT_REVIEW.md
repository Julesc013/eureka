# Source Pack Export Review

H0 source-pack exports are draft or preview artifacts only. They may be written
under audit generated outputs, examples, or explicit temporary test
directories. They must not be imported, submitted, accepted, or used to mutate
public/master index state.

Run:

```powershell
python scripts/build_source_pack.py --input examples/packs/source/internet_archive_source_pack_manifest_v0.json --check
```
