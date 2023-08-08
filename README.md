# The Open Data Transformation Framework

The Open Data Transformation Framework is an industry collaboration to develop a framework for converting catastrophe model exposure data from one data format to another. 

Documentation can be found [here](https://oasislmf.github.io/OpenDataTransform/).


## Available transformations
### AIR <-> OED
Status: 2nd phase of development. Following the development of a basic transformation (location information, primary modifiers), the group is now developing and testing a more complex mapping. Further information to follow when second phase mapping published for testing.
Model References: 
AIR CEDE v8 https://unicede.air-worldwide.com/ts-tsre_all/help_ts_exposure-data_val-rules-exposure-data.html


### RMS EDM <-> OED
Status: Discovery phase. Investigating the potential for data transformation and IP considerations between EDM (proprietary) and OED.
Model references: EDM Schema is proprietary, cannot be shared openly.


### GED4ALL <-> OED
Status: Discovery phase. Investigating the potential for data transformation
Model References 
GED4ALL taxonomy https://docs.riskdatalibrary.org/exposure.html
Risk Data Library Exposure Schema https://docs.riskdatalibrary.org/exposure.html


## Documentation
* <a href="https://oasislmf.github.io/OpenDataTransform/">General documentation</a>
* <a href="https://github.com/OasisLMF/OpenDataTransform/issues">Issues</a>
* <a href="https://github.com/OasisLMF/OpenDataTransform/releases">Releases</a>
* <a href="https://oasislmf.github.io/OpenDataTransform/package/converter/index.html">Modules</a>


## Dependencies

### System

python 3.8+

## Setup

To install the database library dependencies in debian based systems run:

```
sudo apt install libpq-dev ffmpeg libsm6 libxext6 unixodbc-dev -y
```

To install the latest development version run:

```
pip install -e git+https://github.com/OasisLMF/OpenDataTransform.git#egg=converter
```


## License

The code in this project is licensed under BSD 3-clause license.
