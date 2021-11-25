# Multistage Transformation

This example shows a transformation that converts data in format A to data in format C, via multiple stages using `A->B` followed by `B->C`. 

It is also reversible as `A-B.yaml` and `B-C.yaml` both have a reverse transformation defined.

Basic maths operations are used to demonstrate the structure and operation of the files and program.



## Mapping Files
The field data types and desired transformation are described in the mapping files.
`A-B.yaml` describes the transformation of data format A into data format B, denoted by:
```
input_format: A
output_format: B
```

Mapping file `B-C.yaml` describes the transformation of data format B into data format C.



File types are defined explicitly for each field using the field name (in `A-B.yaml` as 'a' and 'b'):
```
a:
  type: float
b:
  type: float
```


The data transformations are defined under 'transform:'. An operation is explicitly given for each destination field (in `A-B.yaml` as 'c' and 'd', using the input field in the operation:
```
c:
  - transformation: a * 2
d:
  - transformation: b + 3
```




## Config Files
Config files first describe the mapping to be used. 
'Input_format' relates to the input_format value given in the mapping file. The config file reads any mapping files in the same folder to find the correct input_format.

`forward.yaml` is the config file instructing the code to convert in a forward direction. 
In this case, the demonstration maps from data format A to data format B, under the 'mapping:' section:

```
mapping:
  options:
    input_format: A
    output_format: C
```

Input file path is defined under `extractor:` and output file path under `loader:`. In this example, the input and outputs files are in the same folder as the config file, so only the file name is given:
```
extractor:
  options:
    path: A.csv
loader:
  options:
    path: C.csv
```

Both mapping files are used in the transformation but the interim file containing data in format `B` is not exported. 



## Running

Make a local installation of the Python package.

To convert A -> C (the result saved in `C.csv`) run:

```
$> converter --config forward.yaml -v run
```



## Reverse transformations

Each mapping file can contain a forward and reverse transformation, to enable bi-directional conversions to be stored in the same mapping file.

In this example, both mapping files contain a `reverse:` set of operations. The `reverse.yaml` config file uses `C.csv` as input to create a `REV.csv` file. The contents of `REV.csv` should match contents of `A.csv`.


To convert C -> A (the result saved in `REV.csv`) run:

```
$> converter --config reverse.yaml -v run
```

