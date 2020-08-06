# Multistage Transformation

This shows a transformation that runs though multiple stages using
`A->B` followed by `B->C`. It is also reversible as `A-B.yaml` and
`B-C.yaml` both have a reverse transformation defined.

## Running

To convert A -> C (the result saved in `C.csv`) run:

```
$> converter --config forward.yaml -v run
```

To convert C -> A (the result saved in `REV.csv`) run:

```
$> converter --config reverse.yaml -v run
```
