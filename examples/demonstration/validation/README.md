# Validated transformation

This shows a transformation that can be used to run through one stage which also produces validation output.

## Validation files

In the forward direction. To validate the data we will take the sum of each of the columns and count the number of rows
and compare the stats from the input format (`A`) to the output format (`B`). 

For the input format the validation config will look like: 

```
entries:
  Total:
    fields:
      - a
      - b
    operator: sum
  NumRows:
    operator: count
```

And for the output format the validation config will look like: 

```
entries:
  Total:
    fields:
      - c
      - d
    operator: sum
  NumRows:
    operator: count
```

## Running

Make a local installation of the Python package.

To convert A -> B (the result saved in `B.csv`) run:

```
$> converter --config forward.yaml -v run
```

After running the transformation there will be a validation log in the log directory (named like 
`<run-timestamp>-validation.yaml`). It will have the following content:

```
- format: A
  validations:
  - entries:
    - field: a
      value: '25.0'
    - field: b
      value: '30.0'
    name: Total
    operator: sum
  - entries:
    - value: '5'
    name: NumRows
    operator: count

- format: B
  validations:
  - entries:
    - field: c
      value: '25.0'
    - field: d
      value: '30.0'
    name: Total
    operator: sum
  - entries:
    - value: '5'
    name: NumRows
    operator: count
```

Here the validation for `A` shows a total in the `a` column of `25.0` which matches the total in the output file `c`.
Similarly, the input column `b` matches the output column `d` with a value of `30.0`. Finally, both formats have the
same number of rows (`5`).
