# The Open Exposure Data Transformation

The Open Exposure Data Transformation is an industry collaboration to develop a framework for converting catastrophe model exposure data from one data format to another. 

The collaboration is coordinated by The Insurance Development Forum (IDF) [Risk Modelling Steering Group (RMSG)](https://www.insdevforum.org/working-groups/rmsg/) with OASIS leading development of the framework in partnership with model vendors and users. 
The project is conducted under the IDF RMSG Interoperabilty Technical Working Group (ITWG) whose members, drawn from over 30 organisations, have collaborated in the vision and design of this framework. 

The Open Exposure Data Transformation provides an open-source, free, and model-agnostic exposure tranformation framework to improve efficiency and transparency of exposure transformations in the insurance market.


Advantages of the Open Exposure Data Transformation include:
* Mapping files can be trusted. They provide 'industry accepted' transformations between model formats. They are developed, reviewed and tested through collaboration of model vendors and experts users, and are peer reviewed by members of the ITWG. 
* The mapping files are easy-to-read so they transparently communciate the assumptions used in converting data between a model pair.
* Multiple mapping files can be included in a single transformation to move between two models, via the OED format.
* While the mapping files provide an 'industry default', users can easily amend the file to meet the needs of a particular client or portfolio.
* Mapping files can be shared with data around the market, to clearly communicate the transformation assumptions that have been applied.
* Mapping files have clear version control, defining the version of the mapping file and the version of the models the input and output formats relate to.
* Mapping files can be provided as a set, with one mapping file for each of the account, location, and reinsurance files.
* Transformations can be run locally, through a Python Shell, once the package has been downloaded and installed from this GitHub repository.

The Open Exposure Data (OED) standard is at the core of the Open Exposure Data Transformation. Each mapping files facilitates conversion to and from one other model format to OED.
OED is curated by OASIS, under the [Open Data Standards (ODS) Initiative](https://oasislmf.org/open-data-standards).
The OED schema: https://github.com/OasisLMF/OpenDataStandards/tree/master/OpenExposureData/Schema

Full docs can be found [here](https://oasislmf.github.io/OasisDataConverter/).


## Available transformations
### AIR <-> OED
Status: 2nd phase of development. Following the development of a basic tranformation (location information, primary modifiers), the group is now developing and testing a more complex transformation. Further information to follow when second phase mapping published for testing.
Model References: 
AIR CEDE v8 https://unicede.air-worldwide.com/ts-tsre_all/help_ts_exposure-data_val-rules-exposure-data.html

### GFDRR Risk Data LIbrary Project <-> OED
Status: Discovery phase. Investigating the potential for data transformation
Model References 
GED4ALL taxonomy https://wiki.openstreetmap.org/wiki/GED4ALL 
Risk Data Library Exposure Schema https://docs.riskdatalibrary.org/exposure.html



## Documentation
* <a href="https://github.com/OasisLMF/OasisDataConverter/issues">Issues</a>
* <a href="https://github.com/OasisLMF/OasisDataConverter/releases">Releases</a>
* <a href="https://oasislmf.github.io/OasisDataConverter/">General documentation</a>
* <a href="https://oasislmf.github.io/OasisDataConverter/package/converter/index.html">Modules</a>


## Dependencies

### System

python 3.8+

## Setup

To install the latest development version run:

```
pip install git+https://github.com/OasisLMF/OasisDataConverter.git
```


## License

The code in this project is licensed under BSD 3-clause license.
