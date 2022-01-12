CLI
===

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
