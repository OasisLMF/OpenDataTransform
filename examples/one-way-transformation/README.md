# One Way Transformation

This shows a transformation that runs though multiple stages using
`A->B` followed by `B->C`. It is not reversible as `B-C.yaml` does
not have a reverse transformation defined.

## Running

To convert A -> C (the result saved in `C.csv`) run:

```
$> converter --config forward.yaml -v run
```

To convert C -> A (resulting in an error) run:

```
$> converter --config reverse.yaml -v run
```
