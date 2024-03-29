# Single Stage Transformation

This shows a transformation that can be used to run through one stage of transformation A -> B.

Basic maths operations are used to demonstrate the structure and operation of the files and program.


## Mapping Files
The field data types and desired transformation are described in the mapping files.
`A-B.yaml` describes the transformation of data format A into data format B, denoted by:
```
input_format: A
output_format: B
```


File types are defined explicitly for each field using the field name (here, 'a' and 'b'):
```
a:
  type: float
b:
  type: float
```


The data transformations are defined under 'transform:'. An operation is explicitly given for each destination field (here, 'c' and 'd', using the input field in the operation:
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
    output_format: B
```

Input file path is defined under `extractor:` and output file path under `loader:`. In this example, the input and outputs files are in the same folder as the config file, so only the file name is given:
```
extractor:
  options:
    path: A.csv
loader:
  options:
    path: B.csv
```


## Running

Make a local installation of the Python package.

To convert A -> B (the result saved in `B.csv`) run:

```
$> converter --config forward.yaml -v run
```


## Reverse transformations

Each mapping file can contain a forward and reverse transformation, to enable bi-directional conversions to be stored in the same mapping file.

Mapping file `A-B.yaml` contains a `reverse:` set of operations to enable B -> A transformation. The `reverse.yaml` config file uses `B.csv` as input to create a `REV.csv` file. The contents of `REV.csv` should match the contents of `A.csv`.

To run this reverse transformation, use:
```
$> converter --config reverse.yaml -v run
```
