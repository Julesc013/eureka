# Command Usage

List known examples:

```bash
python scripts/validate_only_pack_import.py --list-examples
```

Validate all pack examples:

```bash
python scripts/validate_only_pack_import.py --all-examples
python scripts/validate_only_pack_import.py --all-examples --json
```

Validate one explicit pack root:

```bash
python scripts/validate_only_pack_import.py --pack-root examples/source_packs/minimal_recorded_source_pack_v0 --json
```

Include typed AI output examples without model calls:

```bash
python scripts/validate_only_pack_import.py --all-examples --include-ai-outputs --json
```

Write a report only to an explicit existing parent directory:

```bash
python scripts/validate_only_pack_import.py --all-examples --output tmp/report.json
```

The output parent must already exist. The tool does not create staging,
quarantine, import, cache, or hidden state directories.
