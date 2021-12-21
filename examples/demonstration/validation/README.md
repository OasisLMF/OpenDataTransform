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
`<run-timestamp>-validation.log`). It will have the following content:

```
Validation for A
Total - a: 25.0
Total - b: 30.0
NumRows: 5
Validation for B
Total - c: 25.0
Total - d: 30.0
NumRows: 5
```

Here the validation for `A` shows a total in the `a` column of `25.0` which matches the total in the output file `c`.
Similarly, the input column `b` matches the output column `d` with a value of `30.0`. Finally, both formats have the
same number of rows (`5`).
