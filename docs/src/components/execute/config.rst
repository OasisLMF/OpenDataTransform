Running ODTF via Command Line
================


Configuring the transformation tool for use in command line interface
-------------------------------------

The configuration file points the tool to the source account, location, and reinsurance flat files (in OED or another model format). 
The configuration file should also point to the mapping files to be used in the transformation. 

.. image:: docs_img/example_config.png
  :width: 600
  :alt: An excerpt of an example configuration file

Example config files and source files (AIR CEDE example) are available `here <https://github.com/OasisLMF/OEDtransform/tree/master/examples/cede_test>`_. 


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



The most basic command is ``converter -c mapping-file.yaml run`` when located in the file containing the configuration and input files. For example


