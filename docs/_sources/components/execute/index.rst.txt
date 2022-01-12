Executing a data transformation
====================================

A data transformation can be executed via:

1. The User Interface
2. The Command Line 


Either method will allow to use flat file input data, or a database connection.

**Flat files** should be in the source format, with a csv file for each of the account, location, and when relevant the reinsurance data. The path to these source files will be given in the configuration information (either the config file or the user interface).

**Database connection** is a new feature. It will be described in full, in due course.


.. toctree::
   :maxdepth: 2

   ui.rst
   config.rst
   dbConnection.rst