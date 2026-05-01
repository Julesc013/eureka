# Gitignore Review

The required local/private root protections are:

```text
.eureka-local/
.eureka-cache/
.eureka-staging/
.eureka-reports/
```

These patterns are preventive. The milestone does not create those directories
or any local report/staging runtime state.
