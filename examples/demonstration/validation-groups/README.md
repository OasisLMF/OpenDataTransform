# Validated groups transformation

This shows a transformation that can be used to run through one stage which also produces validation output.
The validation shows how groups can be used to validate data based on the values of a set of columns. 

## Validation files

In the forward direction. To validate the data we will take the sum of each of the columns for each value of the 
grouping columns (`g1` and `g2`) as well as the totals for each pair of grouping values. We also count the number
of rows in each of these groups.

For the input format the validation config will look like: 

```
entries:
  TotalGroup1:
    fields:
      - a
      - b
    operator: sum
    group_by:
      - g1
  TotalGroup2:
    fields:
      - a
      - b
    operator: sum
    group_by:
      - g2
  NumRowsGroup1:
    operator: count
    group_by:
      - g1
  NumRowsGroup2:
    operator: count
    group_by:
      - g2
  TotalGroupedBoth:
    fields:
      - a
      - b
    operator: sum
    group_by:
      - g1
      - g2
  NumRowsGroupedBoth:
    operator: count
    group_by:
      - g1
      - g2
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
      groups:
        g1: '1.0'
      value: '10.0'
    - field: b
      groups:
        g1: '1.0'
      value: '15.0'
    - field: a
      groups:
        g1: '2.0'
      value: '18.0'
    - field: b
      groups:
        g1: '2.0'
      value: '112.0'
    - field: a
      groups:
        g1: '3.0'
      value: '17.0'
    - field: b
      groups:
        g1: '3.0'
      value: '384.0'
    - field: a
      groups:
        g1: '4.0'
      value: '10.0'
    - field: b
      groups:
        g1: '4.0'
      value: '512.0'
    name: TotalGroup1
    operator: sum
  - entries:
    - field: a
      groups:
        g2: '1.0'
      value: '25.0'
    - field: b
      groups:
        g2: '1.0'
      value: '341.0'
    - field: a
      groups:
        g2: '2.0'
      value: '30.0'
    - field: b
      groups:
        g2: '2.0'
      value: '682.0'
    name: TotalGroup2
    operator: sum
  - entries:
    - groups:
        g1: '1.0'
      value: '4'
    - groups:
        g1: '2.0'
      value: '3'
    - groups:
        g1: '3.0'
      value: '2'
    - groups:
        g1: '4.0'
      value: '1'
    name: NumRowsGroup1
    operator: count
  - entries:
    - groups:
        g2: '1.0'
      value: '5'
    - groups:
        g2: '2.0'
      value: '5'
    name: NumRowsGroup2
    operator: count
  - entries:
    - field: a
      groups:
        g1: '1.0'
        g2: '1.0'
      value: '4.0'
    - field: b
      groups:
        g1: '1.0'
        g2: '1.0'
      value: '5.0'
    - field: a
      groups:
        g1: '1.0'
        g2: '2.0'
      value: '6.0'
    - field: b
      groups:
        g1: '1.0'
        g2: '2.0'
      value: '10.0'
    - field: a
      groups:
        g1: '2.0'
        g2: '1.0'
      value: '12.0'
    - field: b
      groups:
        g1: '2.0'
        g2: '1.0'
      value: '80.0'
    - field: a
      groups:
        g1: '2.0'
        g2: '2.0'
      value: '6.0'
    - field: b
      groups:
        g1: '2.0'
        g2: '2.0'
      value: '32.0'
    - field: a
      groups:
        g1: '3.0'
        g2: '1.0'
      value: '9.0'
    - field: b
      groups:
        g1: '3.0'
        g2: '1.0'
      value: '256.0'
    - field: a
      groups:
        g1: '3.0'
        g2: '2.0'
      value: '8.0'
    - field: b
      groups:
        g1: '3.0'
        g2: '2.0'
      value: '128.0'
    - field: a
      groups:
        g1: '4.0'
        g2: '2.0'
      value: '10.0'
    - field: b
      groups:
        g1: '4.0'
        g2: '2.0'
      value: '512.0'
    name: TotalGroupedBoth
    operator: sum
  - entries:
    - groups:
        g1: '1.0'
        g2: '1.0'
      value: '2'
    - groups:
        g1: '1.0'
        g2: '2.0'
      value: '2'
    - groups:
        g1: '2.0'
        g2: '1.0'
      value: '2'
    - groups:
        g1: '2.0'
        g2: '2.0'
      value: '1'
    - groups:
        g1: '3.0'
        g2: '1.0'
      value: '1'
    - groups:
        g1: '3.0'
        g2: '2.0'
      value: '1'
    - groups:
        g1: '4.0'
        g2: '2.0'
      value: '1'
    name: NumRowsGroupedBoth
    operator: count

- format: B
  validations:
  - entries:
    - field: c
      groups:
        g1: '1.0'
      value: '10.0'
    - field: d
      groups:
        g1: '1.0'
      value: '15.0'
    - field: c
      groups:
        g1: '2.0'
      value: '18.0'
    - field: d
      groups:
        g1: '2.0'
      value: '112.0'
    - field: c
      groups:
        g1: '3.0'
      value: '17.0'
    - field: d
      groups:
        g1: '3.0'
      value: '384.0'
    - field: c
      groups:
        g1: '4.0'
      value: '10.0'
    - field: d
      groups:
        g1: '4.0'
      value: '512.0'
    name: TotalGroup1
    operator: sum
  - entries:
    - field: c
      groups:
        g2: '1.0'
      value: '25.0'
    - field: d
      groups:
        g2: '1.0'
      value: '341.0'
    - field: c
      groups:
        g2: '2.0'
      value: '30.0'
    - field: d
      groups:
        g2: '2.0'
      value: '682.0'
    name: TotalGroup2
    operator: sum
  - entries:
    - groups:
        g1: '1.0'
      value: '4'
    - groups:
        g1: '2.0'
      value: '3'
    - groups:
        g1: '3.0'
      value: '2'
    - groups:
        g1: '4.0'
      value: '1'
    name: NumRowsGroup1
    operator: count
  - entries:
    - groups:
        g2: '1.0'
      value: '5'
    - groups:
        g2: '2.0'
      value: '5'
    name: NumRowsGroup2
    operator: count
  - entries:
    - field: c
      groups:
        g1: '1.0'
        g2: '1.0'
      value: '4.0'
    - field: d
      groups:
        g1: '1.0'
        g2: '1.0'
      value: '5.0'
    - field: c
      groups:
        g1: '1.0'
        g2: '2.0'
      value: '6.0'
    - field: d
      groups:
        g1: '1.0'
        g2: '2.0'
      value: '10.0'
    - field: c
      groups:
        g1: '2.0'
        g2: '1.0'
      value: '12.0'
    - field: d
      groups:
        g1: '2.0'
        g2: '1.0'
      value: '80.0'
    - field: c
      groups:
        g1: '2.0'
        g2: '2.0'
      value: '6.0'
    - field: d
      groups:
        g1: '2.0'
        g2: '2.0'
      value: '32.0'
    - field: c
      groups:
        g1: '3.0'
        g2: '1.0'
      value: '9.0'
    - field: d
      groups:
        g1: '3.0'
        g2: '1.0'
      value: '256.0'
    - field: c
      groups:
        g1: '3.0'
        g2: '2.0'
      value: '8.0'
    - field: d
      groups:
        g1: '3.0'
        g2: '2.0'
      value: '128.0'
    - field: c
      groups:
        g1: '4.0'
        g2: '2.0'
      value: '10.0'
    - field: d
      groups:
        g1: '4.0'
        g2: '2.0'
      value: '512.0'
    name: TotalGroupedBoth
    operator: sum
  - entries:
    - groups:
        g1: '1.0'
        g2: '1.0'
      value: '2'
    - groups:
        g1: '1.0'
        g2: '2.0'
      value: '2'
    - groups:
        g1: '2.0'
        g2: '1.0'
      value: '2'
    - groups:
        g1: '2.0'
        g2: '2.0'
      value: '1'
    - groups:
        g1: '3.0'
        g2: '1.0'
      value: '1'
    - groups:
        g1: '3.0'
        g2: '2.0'
      value: '1'
    - groups:
        g1: '4.0'
        g2: '2.0'
      value: '1'
    name: NumRowsGroupedBoth
    operator: count
```
