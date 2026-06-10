# Next Task Recommendation

Run:

```text
EXTERNAL-FULL-DISCOVERY-RERUN-04
```

Reason:

```text
The focused historical queue-validator drift repair is complete, but the full-discovery evidence is stale after this commit.
```

After rerun 04 reaches terminal state, run:

```text
SOURCE-SNAPSHOT-FULL-DISCOVERY-INGEST-04
```

Do not launch public alpha or promote `dev -> main` until current external full-discovery evidence is green and the corpus/artifact gates are separately satisfied.

