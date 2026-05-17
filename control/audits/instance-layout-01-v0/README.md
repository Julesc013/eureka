# INSTANCE-LAYOUT-01

This audit records the standardization of the sibling local instance layout:

```text
workspace_root/
  eureka/
  instances/
    default/
    smoke/
    syn/
    f0/
```

The legacy sibling `../eureka-instance` remains valid only when explicitly
supplied by an operator. This task does not move, copy, delete, or mutate
operator instance state.

The next recommended task is `PLAY-00 - Local Workbench Seed Corpus and Demo
Hunt Pack`.
