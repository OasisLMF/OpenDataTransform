The Open Data Transformation Framework - User guide
====================================================

The Open Data Transformation Framework provides an open-source, free, and model-agnostic framework to improve the efficiency and transparency of catastrophe modelling data transformations in the insurance market. 

It is maintained through an industry collaboration coordinated by The Insurance Development Forum (IDF) `Risk Modelling Steering Group (RMSG) <https://www.insdevforum.org/working-groups/rmsg/>`_. Technical development has been led by OASIS in partnership with model vendors and users. The project is managed under the IDF RMSG Interoperability Technical Working Group (ITWG) whose members, represent over 30 organisations, have collaborated in the vision and design of this framework. 

A steering committee comprising industry experts is responsible for the direction of the project and considers feedback made via the GitHub issues or RMSG and ITWG forums. The steering committee is chaired by IDF RMSG and the `Catastrophe Resiliency Council <https://www.catastropheresiliency.org/>`_ with industry representation from AIR, AON, Chubb, Guy Carpenter, RenaissanceRe, SCOR, and Oasis.

There is currently an exposure data transformation available to convert data from AIR CEDE to OED and vice versa. An exposure data transformation is under development to convert data between OED and GED4ALL (and open exposure data format used in the development sector), providing easier cross-sector sharing of exposure data for catastrophe (disaster risk) analysis.

There is potential to apply the framework to the transformation of results data, via the ORD (Open Results Data) Standard and to extend its capacity to non-property lines of business.

For a summary and demo of the framework, please watch `this webinar <https://vimeo.com/user14948183/review/676071546/cb29739687>`_.



Benefits of the Framework
-----------------------------

* Mapping files can be trusted. They provide 'industry accepted' transformations between model formats. They are developed, reviewed and tested through collaboration of model vendors and experts users, and are peer reviewed by members of the ITWG. 

* The mapping files are easy-to-read so they transparently communicate the assumptions used in converting data between a model pair.

* Multiple mapping files can be included in a single transformation to move between two models, via the OED format.

* While the mapping files provide an 'industry default', users can easily amend the file to meet the needs of a particular client or portfolio.

* Mapping files can be shared with data around the market, to clearly communicate the transformation assumptions that have been applied.

* Mapping files have clear version control, defining the version of the mapping file and the version of the models the input and output formats relate to.

* Mapping files can be provided as a set, with one mapping file for each of the account, location, and reinsurance files.



Contributing to the project
---------------------------------

We encourage experts in catastrophe data transformation to contribute actively to testing this tool and improving its functionality over time. Future applications may include to transformation of catastrophe results data, a greater number of model-pair mapping files, and capability to transform data for non-property lines of business.

Contributions are welcomed directly via GitHub or through the IDF RMSG and Interoperability Working Group. Contact the IDF RMSG for more information.



License
---------

ODTF code is provided under the BSD 3-Clause License. This license permits commercial use, modification and distribution without notification, provided the License and copyright notice are retained. See the `licence terms `BSD 3-Clause License <https://github.com/OasisLMF/OpenDataTransform/blob/master/LICENSE>`_ for more detail.



The Open Exposure Data (OED) Standard
------------------------------------------

The OED (Open Exposure Data) Standard is at the core of the Open Data Transformation Framework. 

The OED Standard arose from the lack of an industry standard for Oasis LMF-based models. OED assists with solving interoperability problems current in the insurance market, where implementing a model-developer-independent exposure data and results repositories will assist in creating more choice in the use of catastrophe models and analytical tools. 

OED is curated by OASIS, along with ORD (Open Results Data), under the `Open Data Standards (ODS) Initiative <https://oasislmf.org/open-data-standards>`_. The ODS GitHub page is `github.com/OasisLMF/OpenDataStandards/ <https://github.com/OasisLMF/OpenDataStandards/>`_.




.. toctree::
   :maxdepth: 3
   :caption: Contents:

   components/setup/structure.rst
   components/setup/inputs.rst
   components/setup/outputs.rst
   components/execute/index.rst
   components/knownissues/index.rst
   components/releaseNotes/index.rst
   components/testing/index.rst
   components/developer/index.rst
   package/index.rst
   

   
