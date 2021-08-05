The Open Exposure Data Transformation
================================================

The Open Exposure Data Transformation provides an open-source, free, and model-agnostic exposure transformation framework to improve efficiency and transparency of exposure transformations in the insurance market.

It is maintained through an industry collaboration to develop a framework for converting catastrophe model exposure data from one data format to another. 

The collaboration is coordinated by The Insurance Development Forum (IDF) `Risk Modelling Steering Group (RMSG) <https://www.insdevforum.org/working-groups/rmsg/>`_. 
Technical development has been led by OASIS in partnership with model vendors and users. The project is managed under the IDF RMSG Interoperability Technical Working Group (ITWG) whose members, drawn from over 30 organisations, have collaborated in the vision and design of this framework. 


Advantages of the Open Exposure Data Transformation
-------------------------------------------------------

* Mapping files can be trusted. They provide 'industry accepted' transformations between model formats. They are developed, reviewed and tested through collaboration of model vendors and experts users, and are peer reviewed by members of the ITWG. 

* The mapping files are easy-to-read so they transparently communicate the assumptions used in converting data between a model pair.

* Multiple mapping files can be included in a single transformation to move between two models, via the OED format.

* While the mapping files provide an 'industry default', users can easily amend the file to meet the needs of a particular client or portfolio.

* Mapping files can be shared with data around the market, to clearly communicate the transformation assumptions that have been applied.

* Mapping files have clear version control, defining the version of the mapping file and the version of the models the input and output formats relate to.

* Mapping files can be provided as a set, with one mapping file for each of the account, location, and reinsurance files.


Open Exposure Data
---------------------

The OED (Open Exposure Data) Standard  is at the core of the Open Exposure Data Transformation. The OED Standard arose from the lack of an industry standard for Oasis LMF-based models. OED assists with solving interoperability problems current in the insurance market, where implementing a model-developer-independent exposure data and results repositories will assist in creating more choice in the use of catastrophe models and analytical tools. OED is curated by OASIS, under the  `Open Data Standards (ODS) Initiative <https://oasislmf.org/open-data-standards>`_.


User guide
---------------------------

The user guide is under development.

The Open Exposure Data Transformation can be run locally via a Python Shell or command line. 
1. Download and install the Python package from `the project GitHub pages <https://github.com/OasisLMF/OasisDataConverter/>`_. A web-based user interface is under development.
2. Complete a configuration file to point to the source account, location, and reinsurance flat files (in OED or another model format). The configuration file should also point to the mapping files to be used in the transformation. Example config files and source files (AIR CEDE example) are available `here <https://github.com/OasisLMF/OEDtransform/tree/master/examples/cede_test>`_. Example mapping files for CEDE to OED conversion are `here for account files <https://github.com/OasisLMF/OEDtransform/blob/master/examples/cede_test_v3/AIR-OED-ACC_v3.yml>`_ and `here for location files <https://github.com/OasisLMF/OEDtransform/blob/master/examples/cede_test_v3/AIR-OED-LOC_v3.yml>`_.
3. Execute the python package in the command line to produce the converted output .csv files.

Validation and testing procedures are under development to assist in confirming the validity of transformations, and to assist future development.



Further developer information
---------------------------

The Open Exposure Data Transformation is designed to convert exposure data from one format to another as long as both formats can be expressed as an iterable of dictionaries. That is, the possible field values must be mapped to a key (field name) for each model format.

The convertor framework is modular, using several swappable components:

* Data Connections for specifying how the input and output data should be processed by the system. The current version support csv file input and output as csv files only, but a new connection could enable, for example, extracting data directly from a model database.

* Mapping describing how the fields should be transformed to between formats.

* The Runner, which takes the input connection, transforms the data using the mapping and passes the transformed data onto the output connection.

Each of these components are configurable and even swappable to some new implementation.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   config.rst
   components/testing/index.rst
   components/data-connections/index.rst
   components/mappings/index.rst
   components/runners/index.rst
   components/cli/index.rst
   package/index.rst
