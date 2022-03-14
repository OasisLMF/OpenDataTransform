# CEDE example

This is a working example of OED <-> CEDE data transformation for use with Acc, Loc, and RI dummy data (not provided).


## Input files
To be provided by user.


## Mapping files
`AIR-OED-ACC_v3.yml`
`AIR-OED-LOC_v3.yml`
`AIR-OED-RI_v3.yml`


## Config files
`cede_test_acc.yml`
`cede_test_loc.yml`
`cede_test_ri.yml`



## Running

Make a local installation of the Python package.

Each transformation can be run separately; to convert e.g., Account files, run:

```
$> converter --config cede_test_acc.yml -v run
```


## Additional code to handle reinsurance files in OED
`adjust_run.py` provides code to execute the transformation of all three files from CEDE to OED using the mapping files. 
It then performs the necessary split of single RI CEDE file into two OED RI files (RI info and RI 
scope).

Future versions of the transformation code will aim to include this functionality built-in in to the standard code.


## Additional code to handle peril codes
Demonstrating a specific requirement for a tested portfolio, the file `adjust_run.py` includes code to transform/assign specific 'perils covered' codes for given combinations of wind and surge perils.


Future versions of the transformation code will aim to include this type of functionality built-in in to the standard code.

