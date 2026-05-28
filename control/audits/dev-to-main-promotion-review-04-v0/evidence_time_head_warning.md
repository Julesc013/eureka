# Evidence Time Head Warning

At evidence intake, the external full-discovery head matched the reviewed dev
head:

```text
317092ac431d1bf2882b199f90e66d78c097e99b
```

If the promotion evidence commit advances `dev`, the allowed delta from the
external evidence head is restricted to this promotion evidence, audit pack,
validator, and focused tests. The validator checks that any such delta is
promotion-only before allowing promotion.
