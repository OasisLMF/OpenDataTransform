# One Way Transformation

This shows a transformation that runs though multiple stages using
`A->B` followed by `B->C`. It is not reversible as `B-C.yaml` does
not have a reverse transformation defined.

Basic maths operations are used to demonstrate the structure and operation of the files and program.


## Mapping Files
The field data types and desired transformation are described in the mapping files.
*A-B.yaml* describes the transformation of data format A into data format B.
This is denoted by 
```
input_format: A
output_format: B
```

*B-C.yaml* demonstrates transformation between data format B and data format C.


## Config Files
Config files first describe the mapping to be used. 
'Input_format' relates to the input_format value given in the mapping file. The config file reads any mapping files in the same folder to find the correct input_format.

*forward.yaml* is the config file instructing the code to convert in a forward direction. In this case, the demonstration maps from data format A to data format C (via data format B).




## Running

Make a local installation of the Python package.

To convert A -> C (the result saved in `C.csv`) run:

```
$> converter --config forward.yaml -v run
```

To convert C -> A (resulting in an error) run:

```
$> converter --config reverse.yaml -v run
```
