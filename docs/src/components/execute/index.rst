Executing a data transformation
====================================


A data transformation can be executed via the **User Interface** or the **Command Line**. Either method will allow to use flat file input data, or a database connection. 


Either method will allow transformation of flat file data, or via SQL database connection.


Running ODTF via User Interface
---------------------------------

The user interface is accessed by running the executable file `... .exe`

A user can load a configuration .yaml file, which will populate the fields in the UI. 

Alternatively, you can configure the transformation entirely in the UI. These settings can be saved to a text config file for reference.

Enter on the `Location`, `Account`, and `Reinsurance` tabs:
* Mapping: the source and destination mapping
* Extractor: source data path or database connection 
* Loader: destination data path or database connection 
* Runner: pandas is used as the default

Enter portfolio metadata on the `Metadata` tab, and execute the transformation on the `Run` tab.

.. image:: ../../docs_img/UI_Jan2022.png
  :width: 600
  :alt: The ODTF user interface 



Running ODTF via Command Line
---------------------------------

The most basic command is ``converter -c <path to config file> run``.


Command line usage::

    Usage: converter [OPTIONS] COMMAND [ARGS]...

      Initialises the cli grouping with default options.

    Options:
      -o, --option TEXT...  Sets a configuration option, a path and value are
                            required eg -o extractor.options.foo.bar bash

      -c, --config TEXT     Path to the configuration file.
      -v, --verbose         Specifies the verbosity level, if used multiple times
                            the verbosity is increased further

      --no-color            Disables colorised output.
      --help                Show this message and exit.

    Commands:
      run          Runs the data conversion
      show-config  Prints the resolved config to the console





.. toctree::
   :maxdepth: 2
   :caption: Further information on configuration and command line use:

   ../developer/config/index.rst
   ../developer/cli/index.rst


