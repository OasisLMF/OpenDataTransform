The Open Exposure Data Transformation
================================================

The Open Exposure Data Transformation is an industry collaboration to develop a framework for converting catastrophe model exposure data from one data format to another. 

The collaboration is coordinated by The Insurance Development Forum (IDF) `Risk Modelling Steering Group (RMSG) <https://www.insdevforum.org/working-groups/rmsg/>`_ 
with OASIS leading development of the framework in partnership with model vendors and users. The project is conducted under the IDF RMSG
Interoperability Technical Working Group (ITWG) whose members, drawn from over 30 organisations, have collaborated in the vision and design of this framework. 

The Open Exposure Data Transformation provides an open-source, free, and model-agnostic exposure transformation framework to improve 
efficiency and transparency of exposure transformations in the insurance market.


Advantages of the Open Exposure Data Transformation include:

* Mapping files can be trusted. They provide 'industry accepted' transformations between model formats. They are developed, reviewed and tested through collaboration of model vendors and experts users, and are peer reviewed by members of the ITWG. 

* The mapping files are easy-to-read so they transparently communicate the assumptions used in converting data between a model pair.

* Multiple mapping files can be included in a single transformation to move between two models, via the OED format.

* While the mapping files provide an 'industry default', users can easily amend the file to meet the needs of a particular client or portfolio.

* Mapping files can be shared with data around the market, to clearly communicate the transformation assumptions that have been applied.

* Mapping files have clear version control, defining the version of the mapping file and the version of the models the input and output formats relate to.

* Mapping files can be provided as a set, with one mapping file for each of the account, location, and reinsurance files.

* Transformations can be run locally, through a Python Shell, once the package has been downloaded and installed from `the project GitHub pages <https://github.com/OasisLMF/OasisDataConverter/>`_.

The Open Exposure Data (OED) standard is at the core of the Open Exposure Data Transformation. 
Each mapping files facilitates conversion to and from one other model format to OED.
OED is curated by OASIS, under the  `Open Data Standards (ODS) Initiative <https://oasislmf.org/open-data-standards>`_.


The Open Exposure Data Transformation converter is designed to convert exposure data from one format to another as long as both formats can be expressed as an iterable of dictionaries. That is, the possible field values must be mapped to a key (field name) for each model format.

The convertor framework is modular, using several swappable components:

* Data Connections for specifying how the input and output data should be processed by the system. The current version support csv file input and output as csv files only, but a new connection could enable, for example, extracting data directly from a model database 

* Mapping describing how the fields should be transformed to between formats.

* The Runner, which takes the input connection, transforms the data using the mapping and passes the transformed data onto the output connection.

Each of these components are configurable and even swappable to some new implementation.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   config.rst
   component/testing/index.rst
   components/data-connections/index.rst
   components/mappings/index.rst
   components/runners/index.rst
   components/cli/index.rst
   package/index.rst
